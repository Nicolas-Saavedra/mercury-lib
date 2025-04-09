import { useEffect, useRef } from "react";
import * as d3 from "d3";
import { Link } from "../types/link";
import { Node } from "../types/node";

type ForceGraphProps = {
  nodes: Node[];
  links: Link[];
  initialNode: Node;
  finalNodes: Node[];
  highlightedNodes: Node[];
  highlightedErrorNodes: Node[];
  highlightedSuccessNodes: Node[];
};

export default function Graph({
  nodes,
  links,
  initialNode,
  finalNodes,
  highlightedNodes,
  highlightedErrorNodes,
  highlightedSuccessNodes,
}: ForceGraphProps) {
  const svgRef = useRef<SVGSVGElement>(null);

  function createMarkers(
    svg: d3.Selection<SVGSVGElement, unknown, null, undefined>,
  ) {
    svg
      .append("defs")
      .selectAll("marker")
      .data(["end"])
      .enter()
      .append("marker")
      .attr("id", (d) => d)
      .attr("viewBox", "0 -5 10 10")
      .attr("refX", 28)
      .attr("refY", 0)
      .attr("markerWidth", 6)
      .attr("markerHeight", 6)
      .attr("orient", "auto")
      .append("path")
      .attr("fill", "#aaa")
      .attr("d", "M0,-5L10,0L0,5");
  }

  function createGlowEffect(
    svg: d3.Selection<SVGSVGElement, unknown, null, undefined>,
    color: string,
    intensity: number,
  ) {
    const defs = svg.append("defs");

    const filter = defs
      .append("filter")
      .attr("id", `glow-${color}`)
      .attr("x", "-50%")
      .attr("y", "-50%")
      .attr("width", "200%")
      .attr("height", "200%");

    // Add blur
    filter
      .append("feGaussianBlur")
      .attr("in", "SourceGraphic")
      .attr("stdDeviation", intensity) // ← Brighter glow by increasing blur
      .attr("result", "blur");

    // Add green color flood
    filter
      .append("feFlood")
      .attr("flood-color", color) // ← Green color
      .attr("flood-opacity", "1")
      .attr("result", "color");

    // Mask the flood over the blur
    filter
      .append("feComposite")
      .attr("in", "color")
      .attr("in2", "blur")
      .attr("operator", "in")
      .attr("result", "coloredBlur");

    // Merge with original graphic
    const merge = filter.append("feMerge");
    merge.append("feMergeNode").attr("in", "coloredBlur");
    merge.append("feMergeNode").attr("in", "SourceGraphic");
  }

  function createLinks(
    svg: d3.Selection<SVGSVGElement, unknown, null, undefined>,
  ) {
    return svg
      .append("g")
      .attr("stroke", "#aaa")
      .selectAll("path")
      .data(links)
      .join("path")
      .attr("fill", "none")
      .attr("stroke-width", 2)
      .attr("marker-end", "url(#end)");
  }

  function createLinkLabels(
    svg: d3.Selection<SVGSVGElement, unknown, null, undefined>,
  ) {
    return svg
      .append("g")
      .selectAll("text")
      .data(links)
      .join("text")
      .text((d) => d.label)
      .attr("font-size", "12px")
      .attr("font-family", "sans-serif")
      .attr("fill", "#555")
      .attr("text-anchor", "middle")
      .attr("dominant-baseline", "central")
      .attr("pointer-events", "none");
  }

  function createNodes(
    svg: d3.Selection<SVGSVGElement, unknown, null, undefined>,
    simulation: d3.Simulation<Node, undefined>,
  ) {
    return svg
      .append("g")
      .selectAll("circle")
      .data(nodes)
      .join("circle")
      .attr("r", 24)
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
          }) as any, // WARNING: Check up on this later
      );
  }
  function createInitialFinalNodeDecorations(
    svg: d3.Selection<SVGSVGElement, unknown, null, undefined>,
    svgNodes: d3.Selection<
      d3.BaseType | SVGCircleElement,
      Node,
      SVGGElement,
      unknown
    >,
  ) {
    svg.selectAll(".final-inner-circle").remove();
    svg.selectAll(".initial-arrow").remove();

    svgNodes
      .filter((d) => finalNodes.map((node) => node.id).includes(d.id))
      .each(function (d) {
        svg
          .append<SVGCircleElement>("circle")
          .datum(d)
          .attr("class", "final-inner-circle")
          .attr("r", 20)
          .attr("fill", "none")
          .attr("stroke", "oklch(37.3% 0.034 259.733)")
          .attr("stroke-width", 1.5);
      });
    svgNodes
      .filter((d) => initialNode.id == d.id)
      .each(function (d) {
        svg
          .append<SVGPathElement>("path")
          .datum(d)
          .attr("class", "initial-arrow")
          .attr("fill", "oklch(37.3% 0.034 259.733)");
      });
  }

  function createNodeLabels(
    svg: d3.Selection<SVGSVGElement, unknown, null, undefined>,
  ) {
    return svg
      .append("g")
      .selectAll("text")
      .data(nodes)
      .join("text")
      .text((d) => d.id)
      .attr("font-size", "10px")
      .attr("font-family", "sans-serif")
      .attr("text-anchor", "middle")
      .attr("dominant-baseline", "central")
      .attr("fill", "oklch(0% 0 0)")
      .attr("pointer-events", "none");
  }

  function computeEdgeGeometry(
    source: Node,
    target: Node,
    hasReverse: boolean,
    strength = 0.3,
  ): {
    start: [number, number];
    end: [number, number];
    control?: [number, number];
  } {
    const x1 = source.x!,
      y1 = source.y!;
    const x2 = target.x!,
      y2 = target.y!;

    const start: [number, number] = [x1, y1];
    const end: [number, number] = [x2, y2];

    if (!hasReverse) {
      return { start, end };
    }

    const dx = x2 - x1;
    const dy = y2 - y1;
    const distance = Math.sqrt(dx * dx + dy * dy);
    const offset = strength * distance;

    const perpX = -dy / distance;
    const perpY = dx / distance;

    const cx = (x1 + x2) / 2 + perpX * offset;
    const cy = (y1 + y2) / 2 + perpY * offset;
    const control: [number, number] = [cx, cy];

    return { start, end, control };
  }

  function calculateCurvedPath(
    source: Node,
    target: Node,
    hasReverse: boolean,
  ): string {
    const { start, end, control } = computeEdgeGeometry(
      source,
      target,
      hasReverse,
    );

    if (control) {
      return `M${start[0]},${start[1]} Q${control[0]},${control[1]} ${end[0]},${end[1]}`;
    }

    return `M${start[0]},${start[1]} L${end[0]},${end[1]}`;
  }

  function calculateLinkLabelPosition(
    source: Node,
    target: Node,
    hasReverse: boolean,
  ): [number, number] {
    const { start, end, control } = computeEdgeGeometry(
      source,
      target,
      hasReverse,
    );

    return control ?? [(start[0] + end[0]) / 2, (start[1] + end[1]) / 2];
  }

  useEffect(() => {
    if (!svgRef.current) return;

    const width = 1920;
    const height = 1080;

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove(); // Clear previous render
    svg.attr("viewBox", `0 0 ${width} ${height}`);

    const simulation = d3
      .forceSimulation<Node>(nodes)
      .force(
        "link",
        d3
          .forceLink<Node, Link>(links)
          .id((d) => d.id)
          .distance(350),
      )
      .force("charge", d3.forceManyBody().strength(-500))
      .force("center", d3.forceCenter(width / 2, height / 2));

    createMarkers(svg);

    createGlowEffect(svg, "green", 10);
    createGlowEffect(svg, "crimson", 8);
    createGlowEffect(svg, "yellow", 12);

    const svgLinks = createLinks(svg);
    const svgNodes = createNodes(svg, simulation);

    const svgLinkLabels = createLinkLabels(svg);
    const svgNodeLabels = createNodeLabels(svg);

    createInitialFinalNodeDecorations(svg, svgNodes);

    simulation.on("tick", () => {
      svgNodes.attr("cx", (d) => d.x!).attr("cy", (d) => d.y!);

      svgLinks.attr("d", (d) => {
        const hasReverse = links.some(
          (l) => l.source === d.target && l.target === d.source,
        );
        return calculateCurvedPath(
          d.source as Node,
          d.target as Node,
          hasReverse,
        );
      });

      svgNodeLabels.attr("x", (d) => d.x!).attr("y", (d) => d.y!);

      svgLinkLabels
        .attr("x", (d) => {
          const hasReverse = links.some(
            (l) => l.source === d.target && l.target === d.source,
          );
          return (
            calculateLinkLabelPosition(
              d.source as Node,
              d.target as Node,
              hasReverse,
            )[0] - 15
          );
        })
        .attr("y", (d) => {
          const hasReverse = links.some(
            (l) => l.source === d.target && l.target === d.source,
          );
          return (
            calculateLinkLabelPosition(
              d.source as Node,
              d.target as Node,
              hasReverse,
            )[1] + 15
          );
        });

      svg
        .selectAll<SVGCircleElement, Node>(".final-inner-circle")
        .attr("cx", (d) => d.x ?? 0)
        .attr("cy", (d) => d.y ?? 0);

      svg.selectAll<SVGCircleElement, Node>(".initial-arrow").attr("d", (d) => {
        const x = d.x ?? 0;
        const y = d.y ?? 0;

        // Triangle head pointing left
        const tipX = x - 30;
        const tipY = y;

        return `M${tipX - 7.5},${tipY - 6} L${tipX},${tipY} L${tipX - 7.5},${tipY + 6} Z`;
      });
    });
  }, []);

  useEffect(() => {
    if (!svgRef.current) return;
    const svg = d3.select(svgRef.current);

    svg
      .selectAll<SVGCircleElement, Node>("circle")
      .attr("filter", (d) =>
        highlightedNodes.map((n) => n.id).includes(d.id)
          ? "url(#glow-yellow)"
          : highlightedErrorNodes.map((n) => n.id).includes(d.id)
            ? "url(#glow-crimson)"
            : highlightedSuccessNodes.map((n) => n.id).includes(d.id)
              ? "url(#glow-green)"
              : null,
      );
  }, [highlightedNodes, highlightedErrorNodes, highlightedSuccessNodes]);

  return <svg ref={svgRef} className="absolute inset-0 z-0 w-full h-full" />;
}
