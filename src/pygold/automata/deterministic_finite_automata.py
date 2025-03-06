import ast
from collections.abc import Iterable
from typing import Hashable, cast
from automata.fa.dfa import DFA

from pygold.exceptions import MissingStateException
from pygold.types.delta_function import DeltaFunction

type State = tuple[Hashable]
"""
States are the core foundation of DFAs inside of pyGold. These states are simple tuples
of hashable values. Since `automata-python` can only handle states in string format,
states from `pyGold` need to be translated to strings using the python `repr` function.

Do not confuse them with InputState, which are states solely used to provide flexibility
in the constructor such that it's easier to use, but will not be returned by the automaton
at any point
"""

type InputState = Hashable
"""
InputStates are simple abstractions that make it easier for users to provide states
in multiple formats to Deterministic automata. These are simply any value that is
hashable. If the input state is a tuple, it will be treated as such for state management,
otherwise, it will be converted internally into a one-valued tuple as to make transition
function management easier
"""

type InputSymbol = str
"""
Wrapper over string to represent a single input symbol. It should always be a one-character
string value, however, this verification may not be enforced at runtime for now
"""

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
                (
                    self._to_internal_state(
                        state  # pyright: ignore[reportUnknownArgumentType]
                    )
                    if isinstance(state, tuple)
                    else self._to_internal_state((state,))
                )
                for state in states
            }
        )
        self._input_symbols = frozenset(input_symbols)
        self._initial_state = (
            self._to_internal_state(
                initial_state  # pyright: ignore[reportUnknownArgumentType]
            )
            if isinstance(initial_state, tuple)
            else self._to_internal_state((initial_state,))
        )
        self._final_states = frozenset(
            {
                (
                    self._to_internal_state(
                        state  # pyright: ignore[reportUnknownArgumentType]
                    )
                    if isinstance(state, tuple)
                    else repr((state,))
                )
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
                next_state = cast(
                    State, self._transition_function(args=state, next_symbol=symbol)
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
