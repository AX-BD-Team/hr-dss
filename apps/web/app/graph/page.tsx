"use client";

import React, { useState, useMemo } from "react";
import {
  GraphViewer,
  GraphData,
  GraphNode,
  GraphLink,
} from "../../components/GraphViewer";

// Mock 데이터 생성
const generateMockGraphData = (): GraphData => {
  const nodes: GraphNode[] = [
    // Organizations
    {
      id: "ORG-0001",
      label: "디지털트랜스포메이션본부",
      type: "OrgUnit",
      properties: { type: "본부" },
    },
    {
      id: "ORG-0010",
      label: "AI솔루션실",
      type: "OrgUnit",
      properties: { type: "실" },
    },
    {
      id: "ORG-0011",
      label: "AI플랫폼팀",
      type: "OrgUnit",
      properties: { type: "팀" },
    },
    {
      id: "ORG-0012",
      label: "MLOps팀",
      type: "OrgUnit",
      properties: { type: "팀" },
    },
    {
      id: "ORG-0020",
      label: "데이터엔지니어링실",
      type: "OrgUnit",
      properties: { type: "실" },
    },

    // Employees
    {
      id: "EMP-000001",
      label: "김영호",
      type: "Employee",
      properties: { grade: "부장", status: "ACTIVE" },
    },
    {
      id: "EMP-000010",
      label: "이정수",
      type: "Employee",
      properties: { grade: "부장", status: "ACTIVE" },
    },
    {
      id: "EMP-000011",
      label: "박민지",
      type: "Employee",
      properties: { grade: "차장", status: "ACTIVE" },
    },
    {
      id: "EMP-000012",
      label: "최서연",
      type: "Employee",
      properties: { grade: "과장", status: "ACTIVE" },
    },
    {
      id: "EMP-000020",
      label: "임하윤",
      type: "Employee",
      properties: { grade: "차장", status: "ACTIVE" },
    },

    // Projects
    {
      id: "PRJ-2024-0001",
      label: "금융권 AI 챗봇",
      type: "Project",
      properties: { status: "ACTIVE", priority: "HIGH" },
    },
    {
      id: "PRJ-2024-0002",
      label: "제조사 MLOps",
      type: "Project",
      properties: { status: "ACTIVE", priority: "HIGH" },
    },

    // Competencies
    {
      id: "CMP-005",
      label: "Machine Learning",
      type: "Competency",
      properties: { domain: "TECHNICAL" },
    },
    {
      id: "CMP-007",
      label: "Generative AI",
      type: "Competency",
      properties: { domain: "TECHNICAL" },
    },
    {
      id: "CMP-008",
      label: "MLOps",
      type: "Competency",
      properties: { domain: "TECHNICAL" },
    },
  ];

  const links: GraphLink[] = [
    // Org hierarchy
    { source: "ORG-0010", target: "ORG-0001", type: "PART_OF" },
    { source: "ORG-0011", target: "ORG-0010", type: "PART_OF" },
    { source: "ORG-0012", target: "ORG-0010", type: "PART_OF" },
    { source: "ORG-0020", target: "ORG-0001", type: "PART_OF" },

    // Employee belongs to org
    { source: "EMP-000001", target: "ORG-0001", type: "BELONGS_TO" },
    { source: "EMP-000010", target: "ORG-0010", type: "BELONGS_TO" },
    { source: "EMP-000011", target: "ORG-0011", type: "BELONGS_TO" },
    { source: "EMP-000012", target: "ORG-0011", type: "BELONGS_TO" },
    { source: "EMP-000020", target: "ORG-0012", type: "BELONGS_TO" },

    // Manager relationships
    { source: "EMP-000010", target: "EMP-000001", type: "MANAGED_BY" },
    { source: "EMP-000011", target: "EMP-000010", type: "MANAGED_BY" },
    { source: "EMP-000012", target: "EMP-000011", type: "MANAGED_BY" },
    { source: "EMP-000020", target: "EMP-000010", type: "MANAGED_BY" },

    // Project assignments
    { source: "EMP-000011", target: "PRJ-2024-0001", type: "ASSIGNED_TO" },
    { source: "EMP-000012", target: "PRJ-2024-0001", type: "ASSIGNED_TO" },
    { source: "EMP-000020", target: "PRJ-2024-0002", type: "ASSIGNED_TO" },

    // Competencies
    { source: "EMP-000011", target: "CMP-005", type: "HAS_COMPETENCY" },
    { source: "EMP-000011", target: "CMP-007", type: "HAS_COMPETENCY" },
    { source: "EMP-000012", target: "CMP-007", type: "HAS_COMPETENCY" },
    { source: "EMP-000020", target: "CMP-008", type: "HAS_COMPETENCY" },
  ];

  return { nodes, links };
};

export default function GraphPage() {
  const [graphData] = useState<GraphData>(generateMockGraphData);
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [filterType, setFilterType] = useState<string>("all");

  const filteredData = useMemo(() => {
    if (filterType === "all") return graphData;

    const filteredNodes = graphData.nodes.filter((n) => n.type === filterType);
    const nodeIds = new Set(filteredNodes.map((n) => n.id));
    const filteredLinks = graphData.links.filter((l) => {
      const sourceId = typeof l.source === "string" ? l.source : l.source.id;
      const targetId = typeof l.target === "string" ? l.target : l.target.id;
      return nodeIds.has(sourceId) && nodeIds.has(targetId);
    });

    return { nodes: filteredNodes, links: filteredLinks };
  }, [graphData, filterType]);

  const nodeTypes = useMemo(() => {
    const types = new Set(graphData.nodes.map((n) => n.type));
    return ["all", ...Array.from(types)];
  }, [graphData]);

  const handleNodeClick = (node: GraphNode) => {
    setSelectedNode(node);
  };

  return (
    <div>
      <div style={{ marginBottom: "24px" }}>
        <h1
          style={{ fontSize: "28px", fontWeight: "700", marginBottom: "8px" }}
        >
          Knowledge Graph 뷰어
        </h1>
        <p style={{ color: "var(--text-secondary)" }}>
          HR 데이터 관계 시각화 - Neo4j Knowledge Graph
        </p>
      </div>

      {/* Controls */}
      <div className="card" style={{ marginBottom: "24px" }}>
        <div
          style={{
            display: "flex",
            gap: "16px",
            alignItems: "center",
            flexWrap: "wrap",
          }}
        >
          <div>
            <label
              style={{
                fontSize: "14px",
                fontWeight: "500",
                marginRight: "8px",
              }}
            >
              노드 필터:
            </label>
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              style={{
                padding: "8px 12px",
                border: "1px solid var(--border-color)",
                borderRadius: "var(--radius)",
                background: "white",
              }}
            >
              {nodeTypes.map((type) => (
                <option key={type} value={type}>
                  {type === "all" ? "전체" : type}
                </option>
              ))}
            </select>
          </div>

          <div style={{ display: "flex", gap: "8px" }}>
            <span className="badge badge-info">
              노드: {filteredData.nodes.length}
            </span>
            <span className="badge badge-info">
              관계: {filteredData.links.length}
            </span>
          </div>
        </div>
      </div>

      {/* Graph Viewer */}
      <div
        className="card"
        style={{ position: "relative", padding: 0, overflow: "hidden" }}
      >
        <GraphViewer
          data={filteredData}
          width={1200}
          height={600}
          onNodeClick={handleNodeClick}
          selectedNodeId={selectedNode?.id}
          showLabels={true}
          showLinkLabels={false}
        />
      </div>

      {/* Selected Node Details */}
      {selectedNode && (
        <div className="card" style={{ marginTop: "24px" }}>
          <h2 className="card-title">선택된 노드 정보</h2>
          <div className="grid grid-3">
            <div>
              <div style={{ fontSize: "12px", color: "var(--text-secondary)" }}>
                ID
              </div>
              <div style={{ fontWeight: "500" }}>{selectedNode.id}</div>
            </div>
            <div>
              <div style={{ fontSize: "12px", color: "var(--text-secondary)" }}>
                라벨
              </div>
              <div style={{ fontWeight: "500" }}>{selectedNode.label}</div>
            </div>
            <div>
              <div style={{ fontSize: "12px", color: "var(--text-secondary)" }}>
                타입
              </div>
              <div>
                <span className="badge badge-info">{selectedNode.type}</span>
              </div>
            </div>
          </div>

          {Object.keys(selectedNode.properties).length > 0 && (
            <div style={{ marginTop: "16px" }}>
              <div
                style={{
                  fontSize: "14px",
                  fontWeight: "600",
                  marginBottom: "8px",
                }}
              >
                속성
              </div>
              <table className="table">
                <thead>
                  <tr>
                    <th>키</th>
                    <th>값</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(selectedNode.properties).map(
                    ([key, value]) => (
                      <tr key={key}>
                        <td>{key}</td>
                        <td>{String(value)}</td>
                      </tr>
                    ),
                  )}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* Node Types Legend */}
      <div className="card" style={{ marginTop: "24px" }}>
        <h2 className="card-title">노드 타입 범례</h2>
        <div className="grid grid-4">
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <div
              style={{
                width: 16,
                height: 16,
                borderRadius: "50%",
                background: "#4CAF50",
              }}
            />
            <span>Employee (직원)</span>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <div
              style={{
                width: 16,
                height: 16,
                borderRadius: "50%",
                background: "#2196F3",
              }}
            />
            <span>OrgUnit (조직)</span>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <div
              style={{
                width: 16,
                height: 16,
                borderRadius: "50%",
                background: "#FF9800",
              }}
            />
            <span>Project (프로젝트)</span>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <div
              style={{
                width: 16,
                height: 16,
                borderRadius: "50%",
                background: "#00BCD4",
              }}
            />
            <span>Competency (역량)</span>
          </div>
        </div>
      </div>
    </div>
  );
}
