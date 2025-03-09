import pytest

from pygold.automata.deterministic_finite_automata import DeterministicFiniteAutomata
from pygold.types.delta_function import DeltaFunction

__author__ = "Nicolas-Saavedra"
__copyright__ = "Nicolas-Saavedra"
__license__ = "MIT"


def test_automata_creation():
    states = [0, 1]
    input_symbols = "01"
    initial_state = 0
    final_states = [0]

    delta = DeltaFunction()

    @delta.definition()
    def _(_: int, next: str):
        return int(next)

    __ = DeterministicFiniteAutomata(
        states, input_symbols, initial_state, final_states, delta
    )
