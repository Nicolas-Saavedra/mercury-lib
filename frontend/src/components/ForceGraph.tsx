import { useEffect, useRef } from "react";
import * as d3 from "d3";
import { SimulationLinkDatum } from "d3";

type Node = {
        id: string;
} & d3.SimulationNodeDatum;

type Link = SimulationLinkDatum<Node> & {
        label: string
}

export default function ForceGraph() {
        const svgRef = useRef<SVGSVGElement>(null);

        useEffect(() => {
                if (!svgRef.current) return;

                const width = 1920;
                const height = 1080;

                const nodes: Node[] = [
                        { id: "A" },
                        { id: "B" },
                        { id: "C" },
                        { id: "D" },
                        { id: "E" },
                        { id: "F" },
                ].map((d) => ({ ...d, x: Math.random() * width, y: Math.random() * height }));

                const links: Link[] = [
                        { source: "A", target: "B", label: "a" },
                        { source: "B", target: "A", label: "a" },
                        { source: "C", target: "A", label: "a" },
                        { source: "D", target: "E", label: "a" },
                        { source: "E", target: "F", label: "a" },
                        { source: "F", target: "B", label: "a" },
                ];

                const svg = d3.select(svgRef.current);
                svg.selectAll("*").remove(); // Clear previous render
                svg.attr("viewBox", `0 0 ${width} ${height}`);

                const simulation = d3
                        .forceSimulation<Node>(nodes)
                        .force("link", d3.forceLink<Node, Link>(links).id((d) => d.id).distance(200))
                        .force("charge", d3.forceManyBody().strength(-300))
                        .force("center", d3.forceCenter(width / 2, height / 2));

                svg.append("defs").selectAll("marker")
                        .data(["end"])
                        .enter().append("marker")
                        .attr("id", d => d)
                        .attr("viewBox", "0 -5 10 10")
                        .attr("refX", 22)
                        .attr("refY", 0)
                        .attr("markerWidth", 6)
                        .attr("markerHeight", 6)
                        .attr("orient", "auto")
                        .append("path")
                        .attr("fill", "#aaa")
                        .attr("d", "M0,-5L10,0L0,5");

                const link = svg
                        .append("g")
                        .attr("stroke", "#aaa")
                        .selectAll("path")
                        .data(links)
                        .join("path")
                        .attr("fill", "none")
                        .attr("stroke-width", 2)
                        .attr("marker-end", "url(#end)")

                const linkLabels = svg
                        .append("g")
                        .selectAll("text")
                        .data(links)
                        .join("text")
                        .text(d => d.label)
                        .attr("font-size", "12px")
                        .attr("font-family", "sans-serif")
                        .attr("fill", "#555")
                        .attr("text-anchor", "middle")
                        .attr("dominant-baseline", "central")
                        .attr("pointer-events", "none");

                const node = svg
                        .append("g")
                        .selectAll("circle")
                        .data(nodes)
                        .join("circle")
                        .attr("r", 20)
                        .attr("fill", "oklch(96.7% 0.003 264.542)")
                        .attr("stroke", "oklch(37.3% 0.034 259.733)")
                        .attr("stroke-width", 1.5)
                        .call(
                                d3
                                        .drag<SVGCircleElement, Node>()
                                        .on("start", (event, d) => {
                                                if (!event.active) simulation.alphaTarget(0.3).restart();
                                                d.fx = d.x;
                                                d.fy = d.y;
                                        })
                                        .on("drag", (event, d) => {
                                                d.fx = event.x;
                                                d.fy = event.y;
                                        })
                                        .on("end", (event, d) => {
                                                if (!event.active) simulation.alphaTarget(0);
                                                d.fx = null;
                                                d.fy = null;
                                        })
                        );

                const labels = svg
                        .append("g")
                        .selectAll("text")
                        .data(nodes)
                        .join("text")
                        .text(d => d.id)
                        .attr("font-size", "10px")
                        .attr("font-family", "sans-serif")
                        .attr("text-anchor", "middle")
                        .attr("dominant-baseline", "central")
                        .attr("fill", "oklch(0% 0 0)")
                        .attr("pointer-events", "none");

                simulation.on("tick", () => {
                        link.attr("d", (d) => {
                                const x1 = (d.source as Node).x!, y1 = (d.source as Node).y!;
                                const x2 = (d.target as Node).x!, y2 = (d.target as Node).y!;

                                const dx = x2 - x1, dy = y2 - y1;
                                const distance = Math.sqrt(dx * dx + dy * dy);
                                const strength = 0.3;
                                const offset = strength * distance;

                                const hasReverse = links.some(l => l.source === d.target && l.target === d.source);

                                if (!hasReverse) {
                                        return `M${x1},${y1} L${x2},${y2}`;
                                }

                                const perpX = -dy / distance, perpY = dx / distance;

                                const cx = (x1 + x2) / 2 + perpX * offset;
                                const cy = (y1 + y2) / 2 + perpY * offset;

                                console.log(cx, cy)

                                return `M${x1},${y1} Q${cx},${cy} ${x2},${y2}`;
                        });
                        node.attr("cx", (d) => d.x!).attr("cy", (d) => d.y!);
                        linkLabels
                                .attr("x", (d) => {
                                        const x1 = (d.source as Node).x!, y1 = (d.source as Node).y!;
                                        const x2 = (d.target as Node).x!, y2 = (d.target as Node).y!;

                                        const hasReverse = links.some(l => l.source === d.target && l.target === d.source);
                                        if (!hasReverse) return (x1 + x2) / 2; // Middle of a straight link

                                        const dx = x2 - x1, dy = y2 - y1;
                                        const distance = Math.sqrt(dx * dx + dy * dy);
                                        const strength = 0.3;
                                        const offset = strength * distance * 0.5;
                                        const perpX = -dy / distance

                                        const cx = (x1 + x2) / 2 + perpX * offset;

                                        return cx;
                                })
                                .attr("y", (d) => {
                                        const x1 = (d.source as Node).x!, y1 = (d.source as Node).y!;
                                        const x2 = (d.target as Node).x!, y2 = (d.target as Node).y!;

                                        const hasReverse = links.some(l => l.source === d.target && l.target === d.source);
                                        if (!hasReverse) return (y1 + y2) / 2 + 10;

                                        const dx = x2 - x1, dy = y2 - y1;
                                        const distance = Math.sqrt(dx * dx + dy * dy);
                                        const strength = 0.3;
                                        const offset = strength * distance * 0.6;
                                        const perpY = dx / distance;

                                        const cy = (y1 + y2) / 2 + perpY * offset;

                                        return cy;
                                });

                        labels
                                .attr("x", (d) => d.x!)
                                .attr("y", (d) => d.y!);

                });
        }, []);

        return (
                <svg ref={svgRef} className="w-full h-full" />
        );
}
