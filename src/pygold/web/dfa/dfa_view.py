from pygold.automata.deterministic_finite_automata import (
    DeterministicFiniteAutomata as DFA,
)
from fastapi.staticfiles import StaticFiles
from fastapi import APIRouter, FastAPI
import uvicorn
from pathlib import Path

from pygold.web.dfa.dfa_schema import (
    DFASchema,
    to_node,
    to_schema,
)


class DFAView:

    _automata: DFA
    _app: FastAPI
    _router: APIRouter

    def __init__(self, automata: DFA) -> None:
        self._automata = automata
        self._app = FastAPI(
            title="pyGold API Interface",
            description="pyGold API made in order to link the library to a web interface",
        )
        self._router = APIRouter()
        self._register_routes()

        static_dir = Path(__file__).parent.parent.parent / "static"
        self._app.mount(
            "/view", StaticFiles(directory=static_dir, html=True), name="spa"
        )
        self._app.include_router(self._router, prefix="/api")

    def _register_routes(self):

        @self._router.get("/automata")
        async def fetch_automata() -> DFASchema:
            "Returns basic information about the automata that is currently running"
            return to_schema(self._automata)

        @self._router.post("/automata/execute")
        async def execute_automata(input_string: str):
            "Executes the input string on the DFA at once, returning the states it went through"
            states = list(self._automata.read_input_stepwise(input_string))
            return {
                "nodes": [to_node(state) for state in states],
                "accepted": states[-1] in self._automata.final_states,
            }

    def run(self, host: str = "0.0.0.0", port: int = 8081):
        """Run the FastAPI application using uvicorn"""
        uvicorn.run(self._app, host=host, port=port)
