from collections.abc import Hashable
import inspect
from types import NoneType
from typing import Callable, cast

from pygold.exceptions import (
    MissingDefinitionException,
    MissingNextParameterException,
    MissingTypeHintException,
)
from pygold.types.delta_function import Registry
from pygold.types.state import InputState

NEXT_SYMBOL_KEYWORD_NAME = "next"


class DeltaFunction:

    _registry: Registry

    def __init__(self) -> None:
        self._registry = {}

    def __call__(
        self,
        args: tuple[Hashable],
        next_symbol: str,
    ):
        type_args = tuple([type(arg) for arg in args])

        if type_args not in self._registry:
            raise MissingDefinitionException(self._registry, args, next_symbol)

        resolver = self._registry[type_args]
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
                    if p.annotation != p.empty  # pyright: ignore[reportAny]
                    else NoneType  # NOTE: This means we don't support (a: NoneType)
                )
                for p in parameters
            ]

            # Report any missing typehints for parameters
            if NoneType in type_hints:
                raise MissingTypeHintException(parameters)

            self._registry[tuple(type_hints)] = func
            return func

        return decorator
