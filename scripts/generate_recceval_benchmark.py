# 生成两个文件
# 文件1 repo+task_name
# 文件2 recceval的benchmark格式

from coderag_bench import MapObj, ReccevalObj
from coderag_bench.indocker.interface import Task
from pathlib import Path
from typing import TypedDict
import json
from itertools import tee



def main():
    benchmark_data_path = Path("benchmark_data")
    repos_path = Path("cache/recceval_repos")
    map_objs: list[MapObj] = []
    recceval_objs: list[ReccevalObj] = []
    for child in benchmark_data_path.iterdir():
        repo_name = child.name
        tasks_path = benchmark_data_path / repo_name / "tasks.json"
        with open(tasks_path, "r") as f:
            task_objs: list[Task] = json.load(f)
            for task_obj in task_objs:
                map_objs.append({
                    "repo_name": repo_name,
                    "task_name": task_obj["task_name"]
                })
                src_lines = (repos_path / task_obj["path"]).read_text().splitlines()
                input_lines = src_lines[:task_obj["line"]]
                recceval_objs.append({
                    "pkg": repo_name,
                    "fpath": task_obj["path"],
                    "gt": task_obj["gt"],
                    "input": "\n".join(input_lines) + "\n"
                })
                
    with open("cache/map_file.json", "w") as f:
        json.dump(map_objs, f, indent=4)
    with open("cache/recceval_benchmark.jsonl", "w") as f:
        json_lines: list[str] = []
        for obj in recceval_objs:
            json_lines.append(json.dumps(obj))
        f.write("\n".join(json_lines))

if __name__ == "__main__":
    main()
