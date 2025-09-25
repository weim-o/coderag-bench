from .interface import ProcessResult

class ExampleEntryFn:
    def process() -> ProcessResult:
        return {
            "test_pass": True
        }