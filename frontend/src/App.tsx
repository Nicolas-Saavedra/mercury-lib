import { useState, useEffect } from "react";
import ForceGraph from "./components/ForceGraph";
import { Automata } from "./types/automata";
import { FastForward, Play, StepForward } from "lucide-react";

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
        <ForceGraph
          nodes={automata.nodes}
          links={automata.links}
          initialNode={automata.initial_node}
          finalNodes={automata.final_nodes}
        />
      )}

      <div className="absolute z-10 flex flex-col w-full h-full justify-between pointer-events-none">
        <div className="flex justify-between">
          <a href="#" className="pointer-events-auto">
            <img
              src="/pyGold.svg"
              className="h-16 px-4 py-2 m-4 bg-gray-100 rounded-2xl"
              alt="pyGold Logo"
            />
          </a>
          <div className="flex items-center">
            <input
              type="text"
              className="bg-gray-100 text-gray-700 tracking-widest font-mono rounded-2xl w-80 h-16 m-4 px-8 pointer-events-auto"
              placeholder="Enter input..."
            />
            <button className="flex items-center justify-center bg-gray-100 rounded-2xl w-16 h-16 mr-4 px-8 pointer-events-auto hover:cursor-pointer">
              <StepForward className="min-w-12 text-gray-600" />
            </button>
            <button className="flex items-center justify-center bg-gray-100 rounded-2xl w-16 h-16 mr-4 pointer-events-auto hover:cursor-pointer">
              <Play className="min-w-12 text-gray-600" />
            </button>
            <button className="flex items-center justify-center bg-gray-100 rounded-2xl w-16 h-16 mr-4 pointer-events-auto hover:cursor-pointer">
              <FastForward className="min-w-12 text-gray-600" />
            </button>
          </div>
        </div>
        <div className="flex"></div>
      </div>
    </div>
  );
}
