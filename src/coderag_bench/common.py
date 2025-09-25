from typing import TypedDict
class MapObj(TypedDict):
    repo_name: str
    task_name: str

class ReccevalObj(TypedDict):
    pkg: str
    fpath: str
    input: str
    gt: str

class EvalItem(TypedDict):
    repo_name: str
    task_name: str
    pass_test: bool

class EvalResult(TypedDict):
    total: int
    pass_n: int
    rate: float
    details: list[EvalItem]