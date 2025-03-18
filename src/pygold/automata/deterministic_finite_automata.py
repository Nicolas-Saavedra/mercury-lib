import ast
from collections.abc import Hashable, Iterable
from typing import cast
from automata.fa.dfa import DFA

from pygold.exceptions import MissingStateException
from pygold.decorators.delta_function import DeltaFunction
from pygold.types.state import State, InputSymbol, InputState

type _InternalState = str
"""
Internal state that can be directly parsed by `automata-python`. This is a `repr` of the
State type shown externally to library users. While this state can be used as is, it is
not recommended, as a translation needs to occur that is provided by public properties
already in the automata
"""

type _InternalMappingStates = dict[_InternalState, dict[InputSymbol, _InternalState]]
"""
Transition table used internally by the `automata-python`, receives a state and returns
a separate mapping that receives input symbols and returns what state it turns into
"""


class DeterministicFiniteAutomata:
    """
    A deterministic finite automaton (DFA) defined with a transition function.

    This class wraps around an DFA object from the `automata-python` library,
    providing additional functionality and flexibility through the use of
    a transition function instead of raw transition tables.

    Attributes:
        automata: The underlying DFA instance.
        internal_states: A set containing string representations of internal states.
        input_symbols: A collection of allowed input symbols as strings.
        initial_state: String representation of the initial state.
        final_states: Set of string representations of accepting states.
        transition_function: Transition function mapping current states to other states based on input symbols.
    """

    _automata: DFA
    _states: frozenset[_InternalState]
    _input_symbols: frozenset[InputSymbol]
    _initial_state: _InternalState
    _final_states: frozenset[_InternalState]
    _transition_function: DeltaFunction

    def __init__(
        self,
        states: Iterable[InputState],
        input_symbols: Iterable[InputSymbol],
        initial_state: InputState,
        final_states: Iterable[InputState],
        transition_function: DeltaFunction,
    ) -> None:
        """
        Initialize the DFA with the specified states, input symbols, initial state,
        accepting states, and transition function.

        Args:
            states: An iterable of all possible internal states (strings).
            input_symbols: An iterable of allowed input symbols.
            initial_state: String representation of the initial state.
            final_states: An iterable containing string representations of accepting states.
            transition_function: A DeltaFunction mapping current states to other states based on input symbols.
        """
        self._states = frozenset(
            {
                self._to_internal_state(self._collapse_into_state(state))
                for state in states
            }
        )
        self._input_symbols = frozenset(input_symbols)
        self._initial_state = self._to_internal_state(
            self._collapse_into_state(initial_state)
        )
        self._final_states = frozenset(
            {
                self._to_internal_state(self._collapse_into_state(state))
                for state in final_states
            }
        )
        self._transition_function = transition_function

        self._automata = DFA(
            states=self._states,
            input_symbols=self._input_symbols,
            transitions=self._generate_mappings(),
            initial_state=self._initial_state,
            final_states=self._final_states,
            allow_partial=True,
        )

    def _generate_mappings(self) -> _InternalMappingStates:
        mappings: _InternalMappingStates = {}
        for state in self.states:
            mappings[self._to_internal_state(state)] = {}
            for symbol in self._input_symbols:
                next_state = self._collapse_into_state(
                    self._transition_function(args=state, next_symbol=symbol)
                )
                if next_state not in self.states:
                    raise MissingStateException(state, symbol, next_state)
                mappings[self._to_internal_state(state)][symbol] = (
                    self._to_internal_state(next_state)
                )
        return mappings

    @property
    def states(self) -> frozenset[State]:
        """Frozenset of the states for this automata."""
        return frozenset(
            {self._to_state(internal_state) for internal_state in self._states}
        )

    @property
    def input_symbols(self) -> frozenset[InputSymbol]:
        """Frozenset containing all allowed input symbols as strings."""
        return self._input_symbols

    @property
    def initial_state(self) -> State:
        """String representation of the initial state."""
        return self._to_state(self._initial_state)

    @property
    def final_states(self) -> frozenset[State]:
        """Frozenset of string representations of accepting states."""
        return frozenset(
            {self._to_state(internal_state) for internal_state in self._final_states}
        )

    def _to_internal_state(self, state: State) -> _InternalState:
        return repr(state)

    def _to_state(self, internal_state: _InternalState) -> State:
        return cast(State, ast.literal_eval(internal_state))

    def _collapse_into_state(self, input_state: InputState) -> State:
        return (
            input_state
            if isinstance(input_state, tuple)
            and all(
                isinstance(element, Hashable)
                for element in input_state  # pyright: ignore[reportUnknownVariableType]
            )
            else (input_state,)
        )
