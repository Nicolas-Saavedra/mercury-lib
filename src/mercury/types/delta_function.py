from typing import Callable

from mercury.types.state import InputState

type Registry = dict[tuple[type, ...], Callable[..., InputState]]
