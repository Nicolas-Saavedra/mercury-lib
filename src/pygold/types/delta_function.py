from typing import Callable
from .state import InputState

type Registry = dict[tuple[type, ...], Callable[..., InputState]]
