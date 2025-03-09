import inspect
from types import NoneType
from typing import Any, Callable, cast

from pygold.exceptions import MissingNextParameterException, MissingTypeHintException
from pygold.types.state import InputState

NEXT_SYMBOL_KEYWORD_NAME = "next"


class DeltaFunction:

    _registry: dict[tuple[type, ...], Callable[..., InputState]]

    def __init__(self) -> None:
        self._registry = {}

    def __call__(
        self,
        args: tuple[Any, ...],  # pyright: ignore[reportExplicitAny]
        next_symbol: str,
    ):
        resolver = self._registry[args]
        return resolver(*args, **{NEXT_SYMBOL_KEYWORD_NAME: next_symbol})

    def definition(self):
        def decorator(func: Callable[..., InputState]):
            signature = inspect.signature(func)
            parameters = list(signature.parameters.values())

            if NEXT_SYMBOL_KEYWORD_NAME not in [p.name for p in parameters]:
                raise MissingNextParameterException(func)

            parameters.remove(
                [p for p in parameters if p.name == NEXT_SYMBOL_KEYWORD_NAME][0]
            )

            type_hints = [
                (
                    cast(type, p.annotation)
                    if p.default != p.empty  # pyright: ignore[reportAny]
                    else NoneType  # NOTE: This means we don't support (a: NoneType)
                )
                for p in parameters
            ]

            if NoneType in type_hints:  # Report any missing typehints for parameters
                raise MissingTypeHintException(parameters)

            self._registry[tuple(type_hints)] = func
            return func

        return decorator
