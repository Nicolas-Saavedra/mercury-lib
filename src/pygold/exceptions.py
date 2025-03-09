from collections.abc import Hashable
from inspect import Parameter
from typing import Callable


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
        func: Callable[..., tuple[Hashable, ...] | Hashable],
    ) -> None:
        super().__init__(
            f"Missing parameter `next` in {func.__name__} for DeltaFunction()"
        )


class MissingStateException(Exception):
    def __init__(
        self, state: tuple[Hashable], symbol: str, next_state: tuple[Hashable]
    ) -> None:
        super().__init__(
            f"Could not transition from state {state}, symbol {symbol}, to {next_state}, \
            because {next_state} is not a valid state in the definition of the automata"
        )
