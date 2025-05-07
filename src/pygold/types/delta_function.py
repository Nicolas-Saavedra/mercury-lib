from typing import Callable

from pygold.types.state import InputState

type Registry = dict[tuple[type, ...], Callable[..., InputState]]
