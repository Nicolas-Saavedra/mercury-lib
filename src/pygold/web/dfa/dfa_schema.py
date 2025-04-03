from pydantic import BaseModel

from pygold.automata.deterministic_finite_automata import DeterministicFiniteAutomata
from pygold.types.state import State


class DFANode(BaseModel):
    label: str
    identifier: str


class DFALink(BaseModel):
    label: str
    from_node: str
    to_node: str


class DFASchema(BaseModel):
    nodes: list[DFANode]
    links: list[DFALink]
    initial_node: DFANode
    final_nodes: list[DFANode]


def to_schema(dfa: DeterministicFiniteAutomata) -> DFASchema:
    nodes: list[DFANode] = []
    links: list[DFALink] = []
    for state in dfa.states:
        nodes.append(to_node(state))
    for initial_conditions, next_state in dfa.transitions.items():
        links.append(
            DFALink(
                label=initial_conditions[1],
                from_node=str(initial_conditions[0]),
                to_node=str(next_state),
            )
        )
    return DFASchema(
        nodes=nodes,
        links=links,
        initial_node=DFANode(
            label="".join([str(cmp) for cmp in dfa.initial_state]),
            identifier=str(dfa.initial_state),
        ),
        final_nodes=[
            DFANode(
                label="".join([str(cmp) for cmp in state]),
                identifier=str(state),
            )
            for state in dfa.final_states
        ],
    )


def to_node(state: State) -> DFANode:
    return DFANode(label="".join([str(cmp) for cmp in state]), identifier=str(state))
