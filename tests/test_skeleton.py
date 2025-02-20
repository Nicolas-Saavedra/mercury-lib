import pytest

from pygold.skeleton import fib

__author__ = "Nicolas-Saavedra"
__copyright__ = "Nicolas-Saavedra"
__license__ = "MIT"


def test_fib():
    """API Tests"""
    assert fib(1) == 1
    assert fib(2) == 1
    assert fib(7) == 13

    with pytest.raises(AssertionError):
        _ = fib(-10)
