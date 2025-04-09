import { useState, useEffect, useRef } from "react";
import Graph from "./components/Graph";
import { Automata } from "./types/automata";
import { Node } from "./types/node";

import HUD from "./components/HUD";
import axios from "axios";
import { Execution } from "./types/execution";

const BACKEND_URL = "http://localhost:8081";

export default function App() {
  const [automata, setAutomata] = useState<Automata | null>(null);
  const [currentExecution, setCurrentExecution] = useState<Execution | null>(
    null,
  );

  const [highlightedNodes, setHighlighedNodes] = useState<Node[]>([]);
  const [highlightedErrorNodes, setHighlighedErrorNodes] = useState<Node[]>([]);
  const [highlightedSuccessNodes, setHighlighedSuccessNodes] = useState<Node[]>(
    [],
  );

  // Current step of the execution
  const [currentStep, setCurrentStep] = useState<number | null>(null);

  // Checks if the execution is running, i.e, if the play state is on
  const [executionRunning, setExecutionRunning] = useState(false);

  // Play state interval
  const intervalRef = useRef<number | null>(null);

  const fetchAutomata = async () => {
    try {
      const automataResponse = (
        await axios.get<Automata>(`${BACKEND_URL}/automata`)
      ).data;
      setAutomata(automataResponse);
    } catch (err) {
      console.error("Failed to fetch automata:", err);
    }
  };

  const playAutomata = async (input_string: string) => {
    fetchExecution(input_string);
  };

  const fetchExecution = async (input_string: string) => {
    const executionResponse = (
      await axios.post<Execution>(
        `${BACKEND_URL}/automata/execute`,
        {},
        {
          params: {
            input_string: input_string,
          },
        },
      )
    ).data;
    setCurrentExecution(executionResponse);
    setCurrentStep(0);
    setExecutionRunning(true);
  };

  useEffect(() => {
    fetchAutomata();
  }, []);

  useEffect(() => {
    if (currentStep === null || currentExecution === null) return;

    if (currentStep == currentExecution.nodes.length - 1) {
      const lastNode =
        currentExecution.nodes[currentExecution.nodes.length - 1];

      if (currentExecution.accepted) {
        setHighlighedSuccessNodes([lastNode]);
        setHighlighedErrorNodes([]);
      } else {
        setHighlighedSuccessNodes([]);
        setHighlighedErrorNodes([lastNode]);
      }
      setHighlighedNodes([]);
      return;
    } else if (currentStep == currentExecution.nodes.length) {
      setHighlighedNodes([]);
      setHighlighedSuccessNodes([]);
      setHighlighedErrorNodes([]);
      return;
    }

    setHighlighedNodes([currentExecution.nodes[currentStep]]);
    setHighlighedErrorNodes([]);
    setHighlighedSuccessNodes([]);
  }, [currentStep, currentExecution]);

  useEffect(() => {
    if (executionRunning && currentExecution) {
      intervalRef.current = window.setInterval(() => {
        setCurrentStep((currentStep) =>
          currentStep !== null
            ? Math.min(currentStep + 1, currentExecution.nodes.length)
            : null,
        );
      }, 1000);
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [executionRunning, currentExecution]);

  return (
    <div className="relative w-screen h-screen">
      {automata && (
        <Graph
          nodes={automata.nodes}
          links={automata.links}
          initialNode={automata.initial_node}
          finalNodes={automata.final_nodes}
          highlightedNodes={highlightedNodes}
          highlightedSuccessNodes={highlightedSuccessNodes}
          highlightedErrorNodes={highlightedErrorNodes}
        />
      )}
      <HUD onPlay={playAutomata} />
    </div>
  );
}
