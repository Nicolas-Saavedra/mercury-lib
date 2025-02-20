from automata.fa.dfa import DFA


class DeterministicFiniteAutomata:

    _automata: DFA

    def __init__(self) -> None:
        self._automata = DFA()
