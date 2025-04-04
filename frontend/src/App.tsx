import { useState, useEffect } from "react";
import ForceGraph from "./components/ForceGraph";
import { Automata } from "./types/automata";

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
    <>
      {automata && <ForceGraph nodes={automata.nodes} links={automata.links} initialNode={automata.initial_node} finalNodes={automata.final_nodes} />}
    </>
  );
}

