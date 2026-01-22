/**
 * HR DSS - Knowledge Graph Viewer Component
 *
 * Neo4j Knowledge Graph 시각화 컴포넌트
 * D3.js force-directed graph 사용
 */

import React, { useEffect, useRef, useState, useCallback } from "react";

// ============================================================
// Types
// ============================================================

export interface GraphNode {
  id: string;
  label: string;
  type: string;
  properties: Record<string, unknown>;
  x?: number;
  y?: number;
  fx?: number | null;
  fy?: number | null;
}

export interface GraphLink {
  source: string | GraphNode;
  target: string | GraphNode;
  type: string;
  properties?: Record<string, unknown>;
}

export interface GraphData {
  nodes: GraphNode[];
  links: GraphLink[];
}

export interface GraphViewerProps {
  data: GraphData;
  width?: number;
  height?: number;
  onNodeClick?: (node: GraphNode) => void;
  onLinkClick?: (link: GraphLink) => void;
  selectedNodeId?: string;
  highlightTypes?: string[];
  showLabels?: boolean;
  showLinkLabels?: boolean;
}

// ============================================================
// Node Color Scheme
// ============================================================

const NODE_COLORS: Record<string, string> = {
  Employee: "#4CAF50",
  OrgUnit: "#2196F3",
  Project: "#FF9800",
  WorkPackage: "#FF5722",
  Opportunity: "#9C27B0",
  Competency: "#00BCD4",
  CompetencyEvidence: "#009688",
  Assignment: "#795548",
  Availability: "#607D8B",
  TimeBucket: "#9E9E9E",
  ResourceDemand: "#E91E63",
  DemandSignal: "#F44336",
  JobRole: "#3F51B5",
  DeliveryRole: "#673AB7",
  Decision: "#FFC107",
  DecisionOption: "#FFEB3B",
  default: "#757575",
};

const LINK_COLORS: Record<string, string> = {
  BELONGS_TO: "#90CAF9",
  ASSIGNED_TO: "#A5D6A7",
  HAS_COMPETENCY: "#80DEEA",
  MANAGED_BY: "#CE93D8",
  OWNS: "#FFCC80",
  PART_OF: "#B0BEC5",
  default: "#BDBDBD",
};

// ============================================================
// GraphViewer Component
// ============================================================

export const GraphViewer: React.FC<GraphViewerProps> = ({
  data,
  width = 800,
  height = 600,
  onNodeClick,
  onLinkClick,
  selectedNodeId,
  highlightTypes = [],
  showLabels = true,
  showLinkLabels = false,
}) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const [hoveredNode, setHoveredNode] = useState<GraphNode | null>(null);
  const [transform, setTransform] = useState({ x: 0, y: 0, k: 1 });

  // D3 시뮬레이션 상태
  const simulationRef = useRef<d3.Simulation<GraphNode, GraphLink> | null>(
    null,
  );

  // 노드 색상 가져오기
  const getNodeColor = useCallback((node: GraphNode): string => {
    return NODE_COLORS[node.type] || NODE_COLORS.default;
  }, []);

  // 링크 색상 가져오기
  const getLinkColor = useCallback((link: GraphLink): string => {
    return LINK_COLORS[link.type] || LINK_COLORS.default;
  }, []);

  // 노드 크기 계산
  const getNodeRadius = useCallback(
    (node: GraphNode): number => {
      const baseSize = 20;
      if (selectedNodeId === node.id) return baseSize * 1.5;
      if (highlightTypes.includes(node.type)) return baseSize * 1.2;
      return baseSize;
    },
    [selectedNodeId, highlightTypes],
  );

  // D3 초기화 및 업데이트
  useEffect(() => {
    if (!svgRef.current || !data.nodes.length) return;

    // D3 동적 import (SSR 대응)
    import("d3").then((d3) => {
      const svg = d3.select(svgRef.current);

      // 기존 요소 제거
      svg.selectAll("*").remove();

      // 컨테이너 그룹
      const container = svg.append("g").attr("class", "graph-container");

      // 줌 동작
      const zoom = d3
        .zoom<SVGSVGElement, unknown>()
        .scaleExtent([0.1, 4])
        .on("zoom", (event) => {
          container.attr("transform", event.transform);
          setTransform({
            x: event.transform.x,
            y: event.transform.y,
            k: event.transform.k,
          });
        });

      svg.call(zoom as any);

      // 화살표 마커 정의
      svg
        .append("defs")
        .selectAll("marker")
        .data(["arrow"])
        .join("marker")
        .attr("id", "arrow")
        .attr("viewBox", "0 -5 10 10")
        .attr("refX", 25)
        .attr("refY", 0)
        .attr("markerWidth", 6)
        .attr("markerHeight", 6)
        .attr("orient", "auto")
        .append("path")
        .attr("fill", "#999")
        .attr("d", "M0,-5L10,0L0,5");

      // 시뮬레이션 설정
      const simulation = d3
        .forceSimulation<GraphNode>(data.nodes)
        .force(
          "link",
          d3
            .forceLink<GraphNode, GraphLink>(data.links)
            .id((d) => d.id)
            .distance(100),
        )
        .force("charge", d3.forceManyBody().strength(-300))
        .force("center", d3.forceCenter(width / 2, height / 2))
        .force("collision", d3.forceCollide().radius(30));

      simulationRef.current = simulation;

      // 링크 그리기
      const link = container
        .append("g")
        .attr("class", "links")
        .selectAll("line")
        .data(data.links)
        .join("line")
        .attr("stroke", (d) => getLinkColor(d))
        .attr("stroke-width", 2)
        .attr("stroke-opacity", 0.6)
        .attr("marker-end", "url(#arrow)")
        .style("cursor", "pointer")
        .on("click", (_event, d) => onLinkClick?.(d));

      // 링크 라벨
      const linkLabel = showLinkLabels
        ? container
            .append("g")
            .attr("class", "link-labels")
            .selectAll("text")
            .data(data.links)
            .join("text")
            .attr("font-size", "10px")
            .attr("fill", "#666")
            .attr("text-anchor", "middle")
            .text((d) => d.type)
        : null;

      // 노드 그룹
      const node = container
        .append("g")
        .attr("class", "nodes")
        .selectAll("g")
        .data(data.nodes)
        .join("g")
        .style("cursor", "pointer")
        .call(
          d3
            .drag<SVGGElement, GraphNode>()
            .on("start", (event: any, d: any) => {
              if (!event.active) simulation.alphaTarget(0.3).restart();
              d.fx = d.x;
              d.fy = d.y;
            })
            .on("drag", (event: any, d: any) => {
              d.fx = event.x;
              d.fy = event.y;
            })
            .on("end", (event: any, d: any) => {
              if (!event.active) simulation.alphaTarget(0);
              d.fx = null;
              d.fy = null;
            }) as any,
        );

      // 노드 원
      node
        .append("circle")
        .attr("r", (d) => getNodeRadius(d))
        .attr("fill", (d) => getNodeColor(d))
        .attr("stroke", (d) => (selectedNodeId === d.id ? "#000" : "#fff"))
        .attr("stroke-width", (d) => (selectedNodeId === d.id ? 3 : 2))
        .on("mouseover", (_event, d) => setHoveredNode(d))
        .on("mouseout", () => setHoveredNode(null))
        .on("click", (_event, d) => onNodeClick?.(d));

      // 노드 라벨
      if (showLabels) {
        node
          .append("text")
          .attr("dy", 35)
          .attr("text-anchor", "middle")
          .attr("font-size", "12px")
          .attr("fill", "#333")
          .text((d) => d.label || d.id);
      }

      // 노드 타입 아이콘/약자
      node
        .append("text")
        .attr("dy", 5)
        .attr("text-anchor", "middle")
        .attr("font-size", "10px")
        .attr("fill", "#fff")
        .attr("font-weight", "bold")
        .text((d) => d.type.substring(0, 2).toUpperCase());

      // 시뮬레이션 틱
      simulation.on("tick", () => {
        link
          .attr("x1", (d) => (d.source as GraphNode).x || 0)
          .attr("y1", (d) => (d.source as GraphNode).y || 0)
          .attr("x2", (d) => (d.target as GraphNode).x || 0)
          .attr("y2", (d) => (d.target as GraphNode).y || 0);

        if (linkLabel) {
          linkLabel
            .attr(
              "x",
              (d) =>
                ((d.source as GraphNode).x! + (d.target as GraphNode).x!) / 2,
            )
            .attr(
              "y",
              (d) =>
                ((d.source as GraphNode).y! + (d.target as GraphNode).y!) / 2,
            );
        }

        node.attr("transform", (d) => `translate(${d.x || 0},${d.y || 0})`);
      });

      // 클린업
      return () => {
        simulation.stop();
      };
    });
  }, [
    data,
    width,
    height,
    selectedNodeId,
    highlightTypes,
    showLabels,
    showLinkLabels,
    getNodeColor,
    getLinkColor,
    getNodeRadius,
    onNodeClick,
    onLinkClick,
  ]);

  return (
    <div className="graph-viewer">
      <svg
        ref={svgRef}
        width={width}
        height={height}
        style={{
          border: "1px solid #e0e0e0",
          borderRadius: "8px",
          background: "#fafafa",
        }}
      />

      {/* 범례 */}
      <div
        style={{
          position: "absolute",
          top: 10,
          left: 10,
          background: "white",
          padding: "10px",
          borderRadius: "4px",
          boxShadow: "0 2px 4px rgba(0,0,0,0.1)",
          fontSize: "12px",
        }}
      >
        <div style={{ fontWeight: "bold", marginBottom: "8px" }}>노드 타입</div>
        {Object.entries(NODE_COLORS)
          .filter(([key]) => key !== "default")
          .slice(0, 8)
          .map(([type, color]) => (
            <div
              key={type}
              style={{
                display: "flex",
                alignItems: "center",
                marginBottom: "4px",
              }}
            >
              <div
                style={{
                  width: 12,
                  height: 12,
                  borderRadius: "50%",
                  background: color,
                  marginRight: 8,
                }}
              />
              <span>{type}</span>
            </div>
          ))}
      </div>

      {/* 호버 툴팁 */}
      {hoveredNode && (
        <div
          style={{
            position: "absolute",
            bottom: 10,
            right: 10,
            background: "white",
            padding: "12px",
            borderRadius: "4px",
            boxShadow: "0 2px 8px rgba(0,0,0,0.15)",
            maxWidth: 300,
          }}
        >
          <div style={{ fontWeight: "bold", marginBottom: "8px" }}>
            {hoveredNode.label || hoveredNode.id}
          </div>
          <div style={{ fontSize: "12px", color: "#666", marginBottom: "4px" }}>
            타입: {hoveredNode.type}
          </div>
          <div style={{ fontSize: "11px", color: "#888" }}>
            {Object.entries(hoveredNode.properties || {})
              .slice(0, 5)
              .map(([key, value]) => (
                <div key={key}>
                  {key}: {String(value)}
                </div>
              ))}
          </div>
        </div>
      )}

      {/* 줌 컨트롤 */}
      <div
        style={{
          position: "absolute",
          bottom: 10,
          left: 10,
          display: "flex",
          gap: "4px",
        }}
      >
        <button
          onClick={() => {
            if (svgRef.current) {
              import("d3").then((d3) => {
                d3.select(svgRef.current)
                  .transition()
                  .call(
                    d3.zoom<SVGSVGElement, unknown>().transform as any,
                    d3.zoomIdentity.scale(transform.k * 1.2),
                  );
              });
            }
          }}
          style={{
            padding: "4px 8px",
            border: "1px solid #ccc",
            borderRadius: "4px",
            background: "white",
            cursor: "pointer",
          }}
        >
          +
        </button>
        <button
          onClick={() => {
            if (svgRef.current) {
              import("d3").then((d3) => {
                d3.select(svgRef.current)
                  .transition()
                  .call(
                    d3.zoom<SVGSVGElement, unknown>().transform as any,
                    d3.zoomIdentity.scale(transform.k / 1.2),
                  );
              });
            }
          }}
          style={{
            padding: "4px 8px",
            border: "1px solid #ccc",
            borderRadius: "4px",
            background: "white",
            cursor: "pointer",
          }}
        >
          -
        </button>
        <button
          onClick={() => {
            if (svgRef.current) {
              import("d3").then((d3) => {
                d3.select(svgRef.current)
                  .transition()
                  .call(
                    d3.zoom<SVGSVGElement, unknown>().transform as any,
                    d3.zoomIdentity,
                  );
              });
            }
          }}
          style={{
            padding: "4px 8px",
            border: "1px solid #ccc",
            borderRadius: "4px",
            background: "white",
            cursor: "pointer",
          }}
        >
          Reset
        </button>
      </div>
    </div>
  );
};

// ============================================================
// Helper Hooks
// ============================================================

/**
 * GraphData를 API에서 가져오는 훅
 */
export const useGraphData = (endpoint: string) => {
  const [data, setData] = useState<GraphData>({ nodes: [], links: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const response = await fetch(endpoint);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const json = await response.json();
        setData(json);
      } catch (err) {
        setError(err instanceof Error ? err : new Error(String(err)));
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [endpoint]);

  return { data, loading, error };
};

/**
 * Neo4j 쿼리 결과를 GraphData로 변환하는 유틸리티
 */
export const convertNeo4jToGraphData = (neo4jResult: {
  nodes: Array<{
    id: string;
    labels: string[];
    properties: Record<string, unknown>;
  }>;
  relationships: Array<{
    startNodeId: string;
    endNodeId: string;
    type: string;
    properties?: Record<string, unknown>;
  }>;
}): GraphData => {
  const nodes: GraphNode[] = neo4jResult.nodes.map((n) => ({
    id: n.id,
    label: String(n.properties.name || n.properties.employeeId || n.id),
    type: n.labels[0] || "Unknown",
    properties: n.properties,
  }));

  const links: GraphLink[] = neo4jResult.relationships.map((r) => ({
    source: r.startNodeId,
    target: r.endNodeId,
    type: r.type,
    properties: r.properties,
  }));

  return { nodes, links };
};

export default GraphViewer;
