from pygold.automata.deterministic_finite_transducer import (
    DeterministicFiniteTransducer,
)
from pygold.decorators.delta_function import DeltaFunction
from pygold.decorators.output_function import OutputFunction
from pygold.operations.sets import S

__author__ = "Nicolas-Saavedra"
__copyright__ = "Nicolas-Saavedra"
__license__ = "MIT"


def test_transducer_moore_example():
    # States
    states = S(["q0", "q1", "q2"])
    input_symbols = "abz"
    output_symbols = "xyz"
    initial_state = "q0"
    final_states = ["q2"]

    # Define transitions
    delta = DeltaFunction()

    @delta.definition()
    def _(state: str, next: str):
        if state == "q0" and next == "a":
            return "q1"
        elif state == "q0" and next == "b":
            return "q2"
        elif state == "q1" and next == "b":
            return "q2"
        return "q0"  # Loop or default fallback

    # Define output for each state (Moore: output only depends on current state)
    output_fn = OutputFunction()

    @output_fn.definition()
    def _(state: str, next: str):
        return {"q0": "z", "q1": "x", "q2": "y"}[state]

    # Build transducer
    transducer = DeterministicFiniteTransducer(
        states=states,
        input_symbols=input_symbols,
        output_symbols=output_symbols,
        initial_state=initial_state,
        final_states=final_states,
        transition_function=delta,
        output_function=output_fn,
    )

    # Test it
    assert transducer.transduce_input("a") == "zx"
    assert transducer.transduce_input("ab") == "zxy"
    assert transducer.transduce_input("b") == "zy"
    assert transducer.transduce_input("ba") == "zyz"
