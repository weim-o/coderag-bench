import argparse
from pathlib import Path
import json
from coderag_bench.indocker.interface import Task, EntryFn
from coderag_bench.indocker.entry1 import ExampleEntryFn

fun_table: dict[str, EntryFn] = {
    "task1": ExampleEntryFn(),
    "task2": {}
}
tasks_path = "/home/coderag_bench/tasks.json"
    

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=str, help="output filename")
    parser.add_argument("--prediction", type=str, help="prediction json representation")
    parser.add_argument("--task", type=str, help="task name")
    args = parser.parse_args()

    output: str = args.output
    prediction: str = args.prediction
    task: str = args.task

    output_path = Path(output)
    prediction = json.loads(prediction)
    with open(tasks_path, "r") as f:
        tasks: list[Task] = json.load(f)
    task_map: dict[str, Task] = {}
    for it in tasks:
        if it["task_name"] in task_map:
            raise ValueError("2 tasks have same name")
        task_map[it["task_name"]] = it

    task_obj = task_map.get(task, None)
    if task_obj is None:
        raise ValueError("task doesn't exist")

    src_file_path = Path(tasks_path).parent / task_obj["path"]
    with open(src_file_path, "r") as f:
        lines = f.readlines()
        original = lines[task_obj["line"]].rstrip('\n')
        print("original line is:")
        print(original)
        print("replaced to")
        print(prediction)
        lines[task_obj["line"]] = prediction + '\n'
    with open(src_file_path, "w") as f:
        f.writelines(lines)

    entry_fn = fun_table.get(task, None)
    if entry_fn is None:
        raise ValueError(f"Process function of task {task} doesn't not exist")
    result = entry_fn.process()
    print("result is")
    print(result)

    lines[task_obj["line"]] = original + '\n'
    with open(src_file_path, "w") as f:
        f.writelines(lines)
        print("rollback")
    

    with open(output_path, "w") as f:
        json.dump(result, f)
    

if __name__ == "__main__":
    main()