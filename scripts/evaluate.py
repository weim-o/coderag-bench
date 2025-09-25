import docker
import json
import uuid
import os
from pathlib import Path
import json
from coderag_bench import MapObj, EvalResult, ReccevalObj
import argparse

client = docker.from_env()

def run_tar_container(
    tar_path: str,
    command_args: dict,
    volumes: dict,
    stream_logs: bool = True
) -> None:
    """
    加载 .tar Docker 镜像，运行容器，执行命令，完成后删除镜像。
    
    :param tar_path: tar 文件路径
    :param command_args: 命令参数字典，例如 {"python": "entry.py", "--output": "/output/result.json", "--prediction": {...}}
    :param volumes: 卷映射字典，例如 {"/host/path": {"bind": "/container/path", "mode": "rw"}}
    :param stream_logs: 是否实时打印日志
    """
    # 1️⃣ 加载 tar 镜像
    with open(tar_path, "rb") as f:
        images = client.images.load(f.read())
        image = images[0]

    # 2️⃣ 给镜像打唯一 tag 避免冲突
    unique_tag = f"temp_image:{uuid.uuid4().hex}"
    image.tag(unique_tag)

    try:
        # 3️⃣ 构造命令列表
        cmd = []
        for k, v in command_args.items():
            cmd.append(k)
            # 如果值是 dict 或 list，自动转成 JSON 字符串
            if isinstance(v, (dict, list)):
                cmd.append(json.dumps(v))
            else:
                cmd.append(str(v))

        # 4️⃣ 运行容器
        container = client.containers.run(
            image=unique_tag,
            command=cmd,
            volumes=volumes,
            remove=True,  # 容器退出后自动删除
            stdout=True,
            stderr=True,
            tty=False,
            detach=stream_logs
        )

        # 5️⃣ 打印日志
        if stream_logs:
            for line in container.logs(stream=True):
                print(line.decode(), end="")
            container.wait()  # 等待容器退出
        else:
            print(container.decode())

    finally:
        # 6️⃣ 删除镜像，确保不占磁盘
        client.images.remove(image=unique_tag, force=True)
        print(f"\n镜像 {unique_tag} 已删除。")

def main():
    parser = argparse.ArgumentParser(description="boolean --gt argument")
    
    # --gt 出现时为 True，不出现时为 False
    parser.add_argument(
        "--gt",
        action="store_true",
        help="Enable ground truth mode"
    )
    
    args = parser.parse_args()
    
    gt: bool = args.gt

    with open("cache/map_file.json", "r") as f:
        map_objs: list[MapObj] = json.load(f)

    if gt:
        print("Ground truth mode. Result is expected to true.")
        predictions: list[str] = []
        with open("cache/recceval_benchmark.jsonl", "r") as f:
            lines = f.read().splitlines()
            for line in lines:
                recceval_obj: ReccevalObj = json.loads(line)
                predictions.append(recceval_obj["gt"])
    else:
        with open("cache/predictions.json", "r") as f:
            predictions: list[str] = json.load(f)
    
    benchmark_data_path = Path("benchmark_data")
    pass_n = 0
    eval_result: EvalResult = {
        "details": [],
        "total": len(map_objs),
        "pass_n": 0,
        "rate": 0
    }
    for map_obj, prediction in zip(map_objs, predictions, strict=True):
        image_path = benchmark_data_path / map_obj["repo_name"] / "image.tar"
        
        tar_file = str(image_path)
        pwd = os.getcwd()
        volumes = {f"{pwd}/cache": {"bind": "/output", "mode": "rw"}}
        # prediction = '    options.authority = "https://login.microsoftonline.com/tenant_id"'
        # prediction = ""
        command_args = {
            "python": "entry.py",
            "--output": "/output/result.json",
            "--prediction": json.dumps(prediction),
            "--task": map_obj["task_name"]
        }
        result_file_path = Path("cache/result.json")
        result_file_path.unlink(missing_ok=True)
        run_tar_container(tar_file, command_args, volumes)
        assert result_file_path.exists()
        with open(result_file_path, "r") as f:
            test_result = json.load(f)
            test_pass: bool = test_result["test_pass"]
        if test_pass:
            pass_n += 1
        eval_result["details"].append({
            "pass_test": test_pass,
            "repo_name": map_obj["repo_name"],
            "task_name": map_obj["task_name"]
        })
    eval_result["pass_n"] = pass_n
    if eval_result["total"] != 0:
        eval_result["rate"] = eval_result["pass_n"] / eval_result["total"]
    with open("cache/eval_result.json", "w") as f:
        json.dump(eval_result, f, indent=4)
        
            

if __name__ == "__main__":
    main()