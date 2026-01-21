/**
 * HR DSS - Ontology/KG Evaluation Scorecard Component
 *
 * Knowledge Graph 품질 평가 대시보드
 * 엔터티 커버리지, 링크율, 중복/충돌, 최신성 등 평가
 */

import React, { useState, useMemo } from "react";

// ============================================================
// Types
// ============================================================

export interface OntologyMetrics {
  lastUpdated: string;
  evaluationPeriod: {
    start: string;
    end: string;
  };
  overallScore: number;
  overallStatus: "HEALTHY" | "WARNING" | "CRITICAL";
  metrics: {
    entityCoverage: EntityCoverageMetric;
    linkRate: LinkRateMetric;
    duplicateConflict: DuplicateConflictMetric;
    freshness: FreshnessMetric;
  };
  nodeStats: NodeStats;
  relationshipStats: RelationshipStats;
}

export interface EntityCoverageMetric {
  value: number;
  target: number;
  status: "PASS" | "WARNING" | "FAIL";
  details: EntityCoverageDetail[];
}

export interface EntityCoverageDetail {
  entityType: string;
  required: boolean;
  exists: boolean;
  count: number;
  expectedMin: number;
}

export interface LinkRateMetric {
  value: number;
  target: number;
  status: "PASS" | "WARNING" | "FAIL";
  orphanNodes: OrphanNode[];
  totalNodes: number;
  linkedNodes: number;
}

export interface OrphanNode {
  nodeId: string;
  nodeType: string;
  label: string;
}

export interface DuplicateConflictMetric {
  value: number;
  target: number;
  status: "PASS" | "WARNING" | "FAIL";
  duplicates: DuplicateEntry[];
  conflicts: ConflictEntry[];
}

export interface DuplicateEntry {
  key: string;
  nodeType: string;
  count: number;
  nodeIds: string[];
}

export interface ConflictEntry {
  nodeId: string;
  nodeType: string;
  field: string;
  values: string[];
}

export interface FreshnessMetric {
  value: number;
  target: number;
  status: "PASS" | "WARNING" | "FAIL";
  staleEntities: StaleEntity[];
  avgAge: number;
  maxAge: number;
}

export interface StaleEntity {
  nodeId: string;
  nodeType: string;
  lastUpdated: string;
  ageInDays: number;
}

export interface NodeStats {
  total: number;
  byType: Record<string, number>;
}

export interface RelationshipStats {
  total: number;
  byType: Record<string, number>;
}

export interface OntologyScoreCardProps {
  metrics: OntologyMetrics;
  onRefresh?: () => void;
  onNodeClick?: (nodeId: string, nodeType: string) => void;
  showDetails?: boolean;
}

// ============================================================
// Constants
// ============================================================

const STATUS_COLORS = {
  PASS: "#4CAF50",
  WARNING: "#FF9800",
  FAIL: "#F44336",
  HEALTHY: "#4CAF50",
  CRITICAL: "#F44336",
};

const NODE_TYPE_COLORS: Record<string, string> = {
  Employee: "#4CAF50",
  OrgUnit: "#2196F3",
  Project: "#FF9800",
  WorkPackage: "#FF5722",
  Opportunity: "#9C27B0",
  Competency: "#00BCD4",
  Assignment: "#795548",
  Availability: "#607D8B",
  TimeBucket: "#9E9E9E",
  ResourceDemand: "#E91E63",
  default: "#757575",
};

// ============================================================
// Helper Components
// ============================================================

const ScoreGauge: React.FC<{
  score: number;
  status: string;
  size?: number;
}> = ({ score, status, size = 120 }) => {
  const strokeWidth = 12;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference * (1 - score / 100);

  const color =
    status === "HEALTHY" || status === "PASS"
      ? STATUS_COLORS.PASS
      : status === "WARNING"
      ? STATUS_COLORS.WARNING
      : STATUS_COLORS.FAIL;

  return (
    <div style={{ position: "relative", width: size, height: size }}>
      <svg width={size} height={size}>
        {/* Background circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="#e0e0e0"
          strokeWidth={strokeWidth}
        />
        {/* Progress circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          transform={`rotate(-90 ${size / 2} ${size / 2})`}
          style={{ transition: "stroke-dashoffset 0.5s ease" }}
        />
      </svg>
      <div
        style={{
          position: "absolute",
          top: "50%",
          left: "50%",
          transform: "translate(-50%, -50%)",
          textAlign: "center",
        }}
      >
        <div style={{ fontSize: size / 4, fontWeight: "bold" }}>
          {score.toFixed(0)}%
        </div>
        <div style={{ fontSize: size / 10, color: "#666" }}>{status}</div>
      </div>
    </div>
  );
};

const MetricCard: React.FC<{
  title: string;
  description: string;
  value: number;
  target: number;
  status: string;
  unit?: string;
  children?: React.ReactNode;
}> = ({ title, description, value, target, status, unit = "%", children }) => {
  const displayValue = unit === "%" ? `${(value * 100).toFixed(1)}%` : value.toFixed(1);
  const displayTarget = unit === "%" ? `${(target * 100).toFixed(0)}%` : target.toString();

  return (
    <div
      style={{
        padding: "20px",
        borderRadius: "8px",
        border: `2px solid ${STATUS_COLORS[status as keyof typeof STATUS_COLORS] || "#ccc"}`,
        background: "white",
      }}
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "flex-start",
          marginBottom: "12px",
        }}
      >
        <div>
          <div style={{ fontWeight: "bold", fontSize: "16px" }}>{title}</div>
          <div style={{ fontSize: "12px", color: "#666", marginTop: "4px" }}>
            {description}
          </div>
        </div>
        <span
          style={{
            padding: "4px 8px",
            borderRadius: "4px",
            background: STATUS_COLORS[status as keyof typeof STATUS_COLORS] || "#ccc",
            color: "white",
            fontSize: "12px",
            fontWeight: "bold",
          }}
        >
          {status}
        </span>
      </div>

      <div style={{ display: "flex", alignItems: "baseline", gap: "8px" }}>
        <span style={{ fontSize: "36px", fontWeight: "bold" }}>{displayValue}</span>
        <span style={{ fontSize: "14px", color: "#666" }}>/ 목표: {displayTarget}</span>
      </div>

      {children}
    </div>
  );
};

const NodeTypeBar: React.FC<{
  type: string;
  count: number;
  total: number;
  color: string;
}> = ({ type, count, total, color }) => {
  const percentage = (count / total) * 100;

  return (
    <div style={{ marginBottom: "8px" }}>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          fontSize: "12px",
          marginBottom: "4px",
        }}
      >
        <span>{type}</span>
        <span>{count}</span>
      </div>
      <div
        style={{
          height: "8px",
          background: "#e0e0e0",
          borderRadius: "4px",
          overflow: "hidden",
        }}
      >
        <div
          style={{
            height: "100%",
            width: `${percentage}%`,
            background: color,
            borderRadius: "4px",
            transition: "width 0.3s ease",
          }}
        />
      </div>
    </div>
  );
};

const IssueList: React.FC<{
  title: string;
  items: Array<{ id: string; type: string; label: string; detail?: string }>;
  onItemClick?: (id: string, type: string) => void;
  emptyMessage?: string;
  maxItems?: number;
}> = ({ title, items, onItemClick, emptyMessage = "이슈 없음", maxItems = 5 }) => {
  const [showAll, setShowAll] = useState(false);
  const displayItems = showAll ? items : items.slice(0, maxItems);

  return (
    <div style={{ marginTop: "16px" }}>
      <div
        style={{
          fontSize: "12px",
          fontWeight: "bold",
          color: "#666",
          marginBottom: "8px",
        }}
      >
        {title} ({items.length})
      </div>
      {items.length > 0 ? (
        <>
          {displayItems.map((item, idx) => (
            <div
              key={idx}
              onClick={() => onItemClick?.(item.id, item.type)}
              style={{
                padding: "8px 12px",
                marginBottom: "4px",
                background: "#f5f5f5",
                borderRadius: "4px",
                fontSize: "12px",
                cursor: onItemClick ? "pointer" : "default",
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
              }}
            >
              <div>
                <span
                  style={{
                    padding: "2px 6px",
                    borderRadius: "2px",
                    background: NODE_TYPE_COLORS[item.type] || NODE_TYPE_COLORS.default,
                    color: "white",
                    fontSize: "10px",
                    marginRight: "8px",
                  }}
                >
                  {item.type}
                </span>
                {item.label}
              </div>
              {item.detail && (
                <span style={{ color: "#999", fontSize: "11px" }}>{item.detail}</span>
              )}
            </div>
          ))}
          {items.length > maxItems && (
            <button
              onClick={() => setShowAll(!showAll)}
              style={{
                width: "100%",
                padding: "8px",
                border: "none",
                background: "none",
                color: "#2196F3",
                cursor: "pointer",
                fontSize: "12px",
              }}
            >
              {showAll ? "접기" : `+ ${items.length - maxItems}개 더 보기`}
            </button>
          )}
        </>
      ) : (
        <div
          style={{
            padding: "12px",
            textAlign: "center",
            color: "#999",
            fontSize: "12px",
          }}
        >
          {emptyMessage}
        </div>
      )}
    </div>
  );
};

// ============================================================
// Main Component
// ============================================================

export const OntologyScoreCard: React.FC<OntologyScoreCardProps> = ({
  metrics,
  onRefresh,
  onNodeClick,
  showDetails = true,
}) => {
  const [activeTab, setActiveTab] = useState<
    "entityCoverage" | "linkRate" | "duplicateConflict" | "freshness"
  >("entityCoverage");

  // Calculate total nodes for percentage calculation
  const maxNodeCount = useMemo(() => {
    return Math.max(...Object.values(metrics.nodeStats.byType));
  }, [metrics.nodeStats]);

  return (
    <div style={{ padding: "24px", maxWidth: "1200px", margin: "0 auto" }}>
      {/* Header */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "24px",
        }}
      >
        <div>
          <h1 style={{ margin: 0, fontSize: "24px" }}>Ontology/KG Scorecard</h1>
          <p style={{ margin: "4px 0 0", color: "#666" }}>
            Knowledge Graph 품질 평가 대시보드
          </p>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
          <span style={{ fontSize: "12px", color: "#666" }}>
            마지막 업데이트: {new Date(metrics.lastUpdated).toLocaleString()}
          </span>
          {onRefresh && (
            <button
              onClick={onRefresh}
              style={{
                padding: "8px 16px",
                border: "1px solid #ccc",
                borderRadius: "4px",
                background: "white",
                cursor: "pointer",
              }}
            >
              Refresh
            </button>
          )}
        </div>
      </div>

      {/* Overall Score */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: "32px",
          padding: "24px",
          background: "white",
          borderRadius: "12px",
          boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
          marginBottom: "24px",
        }}
      >
        <ScoreGauge
          score={metrics.overallScore}
          status={metrics.overallStatus}
          size={140}
        />
        <div style={{ flex: 1 }}>
          <div style={{ fontSize: "14px", color: "#666", marginBottom: "16px" }}>
            평가 기간: {new Date(metrics.evaluationPeriod.start).toLocaleDateString()} -{" "}
            {new Date(metrics.evaluationPeriod.end).toLocaleDateString()}
          </div>
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(4, 1fr)",
              gap: "16px",
            }}
          >
            <div style={{ textAlign: "center", padding: "12px", background: "#f5f5f5", borderRadius: "8px" }}>
              <div style={{ fontSize: "24px", fontWeight: "bold" }}>
                {(metrics.metrics.entityCoverage.value * 100).toFixed(0)}%
              </div>
              <div style={{ fontSize: "12px", color: "#666" }}>엔터티 커버리지</div>
            </div>
            <div style={{ textAlign: "center", padding: "12px", background: "#f5f5f5", borderRadius: "8px" }}>
              <div style={{ fontSize: "24px", fontWeight: "bold" }}>
                {(metrics.metrics.linkRate.value * 100).toFixed(0)}%
              </div>
              <div style={{ fontSize: "12px", color: "#666" }}>링크율</div>
            </div>
            <div style={{ textAlign: "center", padding: "12px", background: "#f5f5f5", borderRadius: "8px" }}>
              <div style={{ fontSize: "24px", fontWeight: "bold" }}>
                {(metrics.metrics.duplicateConflict.value * 100).toFixed(1)}%
              </div>
              <div style={{ fontSize: "12px", color: "#666" }}>중복/충돌률</div>
            </div>
            <div style={{ textAlign: "center", padding: "12px", background: "#f5f5f5", borderRadius: "8px" }}>
              <div style={{ fontSize: "24px", fontWeight: "bold" }}>
                {(metrics.metrics.freshness.value * 100).toFixed(0)}%
              </div>
              <div style={{ fontSize: "12px", color: "#666" }}>최신성</div>
            </div>
          </div>
        </div>
      </div>

      {/* Node & Relationship Stats */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: "24px",
          marginBottom: "24px",
        }}
      >
        {/* Node Stats */}
        <div
          style={{
            padding: "20px",
            background: "white",
            borderRadius: "8px",
            boxShadow: "0 1px 4px rgba(0,0,0,0.05)",
          }}
        >
          <div style={{ fontWeight: "bold", marginBottom: "16px" }}>
            노드 현황 (총 {metrics.nodeStats.total.toLocaleString()}개)
          </div>
          {Object.entries(metrics.nodeStats.byType)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 8)
            .map(([type, count]) => (
              <NodeTypeBar
                key={type}
                type={type}
                count={count}
                total={maxNodeCount}
                color={NODE_TYPE_COLORS[type] || NODE_TYPE_COLORS.default}
              />
            ))}
        </div>

        {/* Relationship Stats */}
        <div
          style={{
            padding: "20px",
            background: "white",
            borderRadius: "8px",
            boxShadow: "0 1px 4px rgba(0,0,0,0.05)",
          }}
        >
          <div style={{ fontWeight: "bold", marginBottom: "16px" }}>
            관계 현황 (총 {metrics.relationshipStats.total.toLocaleString()}개)
          </div>
          {Object.entries(metrics.relationshipStats.byType)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 8)
            .map(([type, count]) => (
              <NodeTypeBar
                key={type}
                type={type}
                count={count}
                total={Math.max(...Object.values(metrics.relationshipStats.byType))}
                color="#607D8B"
              />
            ))}
        </div>
      </div>

      {showDetails && (
        <>
          {/* Metric Tabs */}
          <div
            style={{
              display: "flex",
              gap: "8px",
              marginBottom: "16px",
              borderBottom: "1px solid #e0e0e0",
              paddingBottom: "8px",
            }}
          >
            {[
              { key: "entityCoverage", label: "엔터티 커버리지" },
              { key: "linkRate", label: "링크율" },
              { key: "duplicateConflict", label: "중복/충돌" },
              { key: "freshness", label: "최신성" },
            ].map((tab) => (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key as typeof activeTab)}
                style={{
                  padding: "8px 16px",
                  border: "none",
                  borderBottom:
                    activeTab === tab.key ? "2px solid #2196F3" : "2px solid transparent",
                  background: "none",
                  color: activeTab === tab.key ? "#2196F3" : "#666",
                  fontWeight: activeTab === tab.key ? "bold" : "normal",
                  cursor: "pointer",
                }}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {/* Detail Cards */}
          {activeTab === "entityCoverage" && (
            <MetricCard
              title="엔터티 커버리지"
              description="필수 노드 존재 비율"
              value={metrics.metrics.entityCoverage.value}
              target={metrics.metrics.entityCoverage.target}
              status={metrics.metrics.entityCoverage.status}
            >
              <div style={{ marginTop: "16px" }}>
                <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "13px" }}>
                  <thead>
                    <tr style={{ background: "#f5f5f5" }}>
                      <th style={{ padding: "8px", textAlign: "left" }}>엔터티 타입</th>
                      <th style={{ padding: "8px", textAlign: "center" }}>필수</th>
                      <th style={{ padding: "8px", textAlign: "center" }}>존재</th>
                      <th style={{ padding: "8px", textAlign: "right" }}>개수</th>
                      <th style={{ padding: "8px", textAlign: "right" }}>최소 기대</th>
                    </tr>
                  </thead>
                  <tbody>
                    {metrics.metrics.entityCoverage.details.map((detail) => (
                      <tr
                        key={detail.entityType}
                        style={{
                          borderBottom: "1px solid #e0e0e0",
                          background: detail.required && !detail.exists ? "#FFEBEE" : "white",
                        }}
                      >
                        <td style={{ padding: "8px" }}>{detail.entityType}</td>
                        <td style={{ padding: "8px", textAlign: "center" }}>
                          {detail.required ? "[O]" : "[-]"}
                        </td>
                        <td style={{ padding: "8px", textAlign: "center" }}>
                          <span style={{ color: detail.exists ? STATUS_COLORS.PASS : STATUS_COLORS.FAIL }}>
                            {detail.exists ? "[O]" : "[X]"}
                          </span>
                        </td>
                        <td style={{ padding: "8px", textAlign: "right" }}>{detail.count}</td>
                        <td style={{ padding: "8px", textAlign: "right" }}>{detail.expectedMin}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </MetricCard>
          )}

          {activeTab === "linkRate" && (
            <MetricCard
              title="링크율"
              description="고아 노드 없는 비율"
              value={metrics.metrics.linkRate.value}
              target={metrics.metrics.linkRate.target}
              status={metrics.metrics.linkRate.status}
            >
              <div
                style={{
                  marginTop: "12px",
                  fontSize: "13px",
                  color: "#666",
                }}
              >
                연결된 노드: {metrics.metrics.linkRate.linkedNodes.toLocaleString()} /{" "}
                {metrics.metrics.linkRate.totalNodes.toLocaleString()}
              </div>
              <IssueList
                title="고아 노드"
                items={metrics.metrics.linkRate.orphanNodes.map((node) => ({
                  id: node.nodeId,
                  type: node.nodeType,
                  label: node.label,
                }))}
                onItemClick={onNodeClick}
                emptyMessage="고아 노드 없음"
              />
            </MetricCard>
          )}

          {activeTab === "duplicateConflict" && (
            <MetricCard
              title="중복/충돌"
              description="키 충돌 비율"
              value={metrics.metrics.duplicateConflict.value}
              target={metrics.metrics.duplicateConflict.target}
              status={metrics.metrics.duplicateConflict.status}
            >
              <IssueList
                title="중복 항목"
                items={metrics.metrics.duplicateConflict.duplicates.map((dup) => ({
                  id: dup.nodeIds[0],
                  type: dup.nodeType,
                  label: dup.key,
                  detail: `${dup.count}건 중복`,
                }))}
                onItemClick={onNodeClick}
                emptyMessage="중복 항목 없음"
              />
              <IssueList
                title="충돌 항목"
                items={metrics.metrics.duplicateConflict.conflicts.map((conf) => ({
                  id: conf.nodeId,
                  type: conf.nodeType,
                  label: `${conf.field}: ${conf.values.join(" vs ")}`,
                }))}
                onItemClick={onNodeClick}
                emptyMessage="충돌 항목 없음"
              />
            </MetricCard>
          )}

          {activeTab === "freshness" && (
            <MetricCard
              title="최신성"
              description="데이터 갱신 주기 준수"
              value={metrics.metrics.freshness.value}
              target={metrics.metrics.freshness.target}
              status={metrics.metrics.freshness.status}
            >
              <div
                style={{
                  display: "flex",
                  gap: "24px",
                  marginTop: "12px",
                  fontSize: "13px",
                }}
              >
                <div>
                  평균 경과일: <strong>{metrics.metrics.freshness.avgAge.toFixed(1)}일</strong>
                </div>
                <div>
                  최대 경과일: <strong>{metrics.metrics.freshness.maxAge}일</strong>
                </div>
              </div>
              <IssueList
                title="오래된 엔터티"
                items={metrics.metrics.freshness.staleEntities.map((entity) => ({
                  id: entity.nodeId,
                  type: entity.nodeType,
                  label: entity.nodeId,
                  detail: `${entity.ageInDays}일 전`,
                }))}
                onItemClick={onNodeClick}
                emptyMessage="오래된 엔터티 없음"
              />
            </MetricCard>
          )}
        </>
      )}
    </div>
  );
};

// ============================================================
// Mock Data Generator
// ============================================================

export const generateMockOntologyMetrics = (): OntologyMetrics => {
  const nodeTypes = [
    "Employee",
    "OrgUnit",
    "Project",
    "WorkPackage",
    "Opportunity",
    "Competency",
    "Assignment",
    "Availability",
  ];

  const relationshipTypes = [
    "BELONGS_TO",
    "ASSIGNED_TO",
    "HAS_COMPETENCY",
    "MANAGED_BY",
    "OWNS",
    "PART_OF",
    "REQUIRES",
    "REPORTS_TO",
  ];

  const nodeStats: Record<string, number> = {};
  nodeTypes.forEach((type) => {
    nodeStats[type] = Math.floor(Math.random() * 100) + 10;
  });

  const relationshipStats: Record<string, number> = {};
  relationshipTypes.forEach((type) => {
    relationshipStats[type] = Math.floor(Math.random() * 200) + 20;
  });

  const totalNodes = Object.values(nodeStats).reduce((a, b) => a + b, 0);

  return {
    lastUpdated: new Date().toISOString(),
    evaluationPeriod: {
      start: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
      end: new Date().toISOString(),
    },
    overallScore: 92,
    overallStatus: "HEALTHY",
    metrics: {
      entityCoverage: {
        value: 1.0,
        target: 1.0,
        status: "PASS",
        details: nodeTypes.map((type) => ({
          entityType: type,
          required: true,
          exists: true,
          count: nodeStats[type],
          expectedMin: 5,
        })),
      },
      linkRate: {
        value: 0.96,
        target: 0.95,
        status: "PASS",
        totalNodes,
        linkedNodes: Math.floor(totalNodes * 0.96),
        orphanNodes: [
          { nodeId: "EMP-099", nodeType: "Employee", label: "미배치 직원" },
          { nodeId: "PROJ-045", nodeType: "Project", label: "보류 프로젝트" },
        ],
      },
      duplicateConflict: {
        value: 0.0,
        target: 0.0,
        status: "PASS",
        duplicates: [],
        conflicts: [],
      },
      freshness: {
        value: 0.95,
        target: 0.9,
        status: "PASS",
        avgAge: 2.3,
        maxAge: 7,
        staleEntities: [
          {
            nodeId: "EMP-001",
            nodeType: "Employee",
            lastUpdated: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
            ageInDays: 7,
          },
        ],
      },
    },
    nodeStats: {
      total: totalNodes,
      byType: nodeStats,
    },
    relationshipStats: {
      total: Object.values(relationshipStats).reduce((a, b) => a + b, 0),
      byType: relationshipStats,
    },
  };
};

export default OntologyScoreCard;
