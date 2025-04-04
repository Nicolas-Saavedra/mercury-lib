from collections.abc import Generator
from starlette.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND
from pygold.automata.deterministic_finite_automata import (
    DeterministicFiniteAutomata as DFA,
)

from fastapi import APIRouter, FastAPI, HTTPException
import uvicorn

from pygold.types.state import State
from pygold.web.dfa.dfa_schema import (
    DFASchema,
    DFAStepResult,
    to_node,
    to_schema,
)


class DFAView:

    _automata: DFA
    _app: FastAPI
    # Records the session's generator, as well as the next state in the generator
    _sessions: dict[str, tuple[Generator[State, None, None], State | None]]
    _router: APIRouter

    def __init__(self, automata: DFA) -> None:
        self._automata = automata
        self._app = FastAPI(
            title="pyGold API Interface",
            description="pyGold API made in order to link the library to a web interface",
        )
        self._router = APIRouter()
        self._sessions = {}
        self._register_routes()
        self._app.include_router(self._router)

    def _register_routes(self):
        @self._router.get("/automata")
        async def fetch_automata() -> DFASchema:
            "Returns basic information about the automata that is currently running"
            return to_schema(self._automata)

        @self._router.post("/automata/execute")
        async def execute_automata(input_string: str):
            "Executes the input string on the DFA at once, returning the final state"
            return self._automata.accepts_input(input_string)

        @self._router.post("/automata/session", status_code=HTTP_201_CREATED)
        async def create_stepwise_session(session_id: str, input_string: str):
            "Creates a new stepwise execution session for the DFA"
            if session_id in self._sessions:
                raise HTTPException(
                    status_code=HTTP_400_BAD_REQUEST, detail="Session already exists"
                )

            self._sessions[session_id] = (
                self._automata.read_input_stepwise(input_string),
                None,
            )

        @self._router.post("/automata/session/{session_id}/execute")
        async def execute_automata_by_step(session_id: str) -> DFAStepResult:
            "Executes the input string step by step on the DFA"
            if session_id not in self._sessions:
                raise HTTPException(
                    status_code=HTTP_404_NOT_FOUND, detail="Session does not exist"
                )

            generator, previous_state = self._sessions[session_id]
            try:
                current_state = next(generator)
            except StopIteration:
                return DFAStepResult(
                    status="finished",
                    result=previous_state in self._automata.final_states,
                )
            self._sessions[session_id] = (generator, current_state)
            return DFAStepResult(status="ongoing", result=to_node(current_state))

    def run(self, host: str = "0.0.0.0", port: int = 8081):
        """Run the FastAPI application using uvicorn"""
        uvicorn.run(self._app, host=host, port=port)
