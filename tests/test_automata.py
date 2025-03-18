from pygold.automata.deterministic_finite_automata import DeterministicFiniteAutomata
from pygold.decorators.delta_function import DeltaFunction
from pygold.operations.sets import S

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


def test_automata_simple_scenario():
    states = [0, 1]
    input_symbols = "01"
    initial_state = 0
    final_states = [0]

    delta = DeltaFunction()

    @delta.definition()
    def _(_: int, next: str):
        return int(next)

    automata = DeterministicFiniteAutomata(
        states, input_symbols, initial_state, final_states, delta
    )

    assert automata.accepts_input("010")
    assert automata.accepts_input("1111111111111111110")
    assert not automata.accepts_input("01")
    assert not automata.accepts_input("1")
    assert automata.accepts_input("")


def test_automata_Amod3xBmod3_scenario():
    states = S({"a", "b"}) * S(range(3)) | S({0})
    input_symbols = "abx"
    initial_state = ("a", 0)
    final_states = [("b", 0)]

    delta = DeltaFunction()

    @delta.definition()
    def _(_: int, next: str):
        return 0

    @delta.definition()
    def _(w: str, y: int, next: str):
        if w == "a" and next == "a":
            return (w, (y + 1) % 3)
        elif w == "a" and next == "b":
            return (w, y)
        elif w == "a" and next == "x":
            return ("b", (3 - y) % 3)
        elif w == "b" and next == "b":
            return (w, (y + 1) % 3)
        elif w == "b" and next == "a":
            return (w, y)
        else:
            return 0

    automata = DeterministicFiniteAutomata(
        states, input_symbols, initial_state, final_states, delta
    )

    assert automata.accepts_input("x")
    assert automata.accepts_input("aaaxbbb")
    assert automata.accepts_input("aaax")
    assert not automata.accepts_input("axbb")
