from collections.abc import Iterable
from pygold.automata.deterministic_finite_automata import DeterministicFiniteAutomata
from pygold.decorators.delta_function import DeltaFunction
from pygold.types.state import InputState, InputSymbol


class DeterministicFiniteTransducer(DeterministicFiniteAutomata):
    def __init__(
        self,
        states: Iterable[InputState],
        input_symbols: Iterable[InputSymbol],
        initial_state: InputState,
        final_states: Iterable[InputState],
        transition_function: DeltaFunction,
    ) -> None:
        super().__init__(self, states, input_symbols, initial_state, final_states)
