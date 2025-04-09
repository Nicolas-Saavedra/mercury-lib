import { useState, useEffect } from "react";
import Graph from "./components/Graph";
import { Automata } from "./types/automata";
import HUD from "./components/HUD";

const BACKEND_URL = "http://localhost:8081";

export default function App() {
  const [automata, setAutomata] = useState<Automata | null>(null);

  useEffect(() => {
    fetch(`${BACKEND_URL}/automata`)
      .then((res) => res.json())
      .then((json) => setAutomata(json))
      .catch((err) => console.error("Failed to fetch automata:", err));
  }, []);

  return (
    <div className="relative w-screen h-screen">
      {automata && (
        <Graph
          nodes={automata.nodes}
          links={automata.links}
          initialNode={automata.initial_node}
          finalNodes={automata.final_nodes}
        />
      )}
      <HUD />
    </div>
  );
}
