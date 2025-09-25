from typing import TypedDict
from typing import Protocol

class Task(TypedDict):
    task_name: str
    path: str
    line: int
    gt: str

class ProcessResult(TypedDict):
    test_pass: bool

class EntryFn(Protocol):
    def process(self) -> ProcessResult:
        ...