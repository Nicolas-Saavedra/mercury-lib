import logging

from pygold import __version__

__author__ = "Nicolas-Saavedra"
__copyright__ = "Nicolas-Saavedra"
__license__ = "MIT"

_logger = logging.getLogger(__name__)


def fib(n):
    """Fibonacci example function

    Args:
      n (int): integer

    Returns:
      int: n-th Fibonacci number
    """
    assert n > 0
    a, b = 1, 1
    for _i in range(n - 1):
        a, b = b, a + b
    return a
