from inspect import Parameter
from typing import Any, Callable


class MissingTypeHintException(Exception):

    def __init__(self, parameters: list[Parameter]) -> None:
        trobule_parameters = [
            p.name
            for p in parameters
            if p.default == p.empty  # pyright: ignore[reportAny]
        ]
        super().__init__(f"Missing type hint for parameters: {trobule_parameters}")


class MissingNextParameterException(Exception):
    def __init__(
        self,
        func: Callable[..., tuple[Any, ...]],  # pyright: ignore[reportExplicitAny]
    ) -> None:
        super().__init__(
            f"Missing parameter `next` in {func.__name__} for DeltaFunction()"
        )
