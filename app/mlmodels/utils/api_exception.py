class ApiException(Exception):
    def __init__(self, *args: str) -> None:
        if len(args) > 1:
            self.message: str | None = args[0]
            self.function_name: str | None = args[1]
        elif len(args) == 1:
            self.message = args[0]
        else:
            self.message = None
            self.function_name = None

    def __str__(self) -> str:
        if self.message and self.function_name:
            return f"ApiException.{self.function_name}, {self.message}"
        elif self.message:
            return f"ApiException: {self.message}"
        else:
            return "ApiException has been raised"
