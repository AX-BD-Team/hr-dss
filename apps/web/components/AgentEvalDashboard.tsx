/**
 * HR DSS - Agent Evaluation Dashboard Component
 *
 * AI Agent 성능 평가 대시보드
 * 완결성, 근거 연결률, 환각률, 재현성, 응답 시간 등 평가
 */

import React, { useState, useEffect, useMemo } from "react";

// ============================================================
// Types
// ============================================================

export interface AgentMetrics {
  agentId: string;
  agentName: string;
  evaluationPeriod: {
    start: string;
    end: string;
  };
  metrics: {
    completeness: MetricScore;
    evidenceCoverage: MetricScore;
    hallucinationRate: MetricScore;
    reproducibility: MetricScore;
    responseTime: MetricScore;
  };
  trend: "IMPROVING" | "STABLE" | "DECLINING";
  lastUpdated: string;
}

export interface MetricScore {
  value: number;
  target: number;
  unit: string;
  status: "PASS" | "WARNING" | "FAIL";
  history: MetricHistoryPoint[];
}

export interface MetricHistoryPoint {
  date: string;
  value: number;
}

export interface EvaluationResult {
  evaluationId: string;
  timestamp: string;
  query: string;
  queryType: string;
  agentResults: AgentResult[];
  overallScore: number;
  issues: EvaluationIssue[];
}

export interface AgentResult {
  agentId: string;
  agentName: string;
  executionTime: number;
  success: boolean;
  outputQuality: number;
  evidenceLinks: number;
  unverifiedClaims: number;
}

export interface EvaluationIssue {
  severity: "HIGH" | "MEDIUM" | "LOW";
  agentId: string;
  message: string;
  recommendation: string;
}

export interface AgentEvalDashboardProps {
  agents: AgentMetrics[];
  recentEvaluations?: EvaluationResult[];
  onRefresh?: () => void;
  onAgentSelect?: (agentId: string) => void;
}

// ============================================================
// Constants
// ============================================================

const METRIC_CONFIG = {
  completeness: {
    label: "완결성",
    description: "질문에 대한 답변 완성도",
    targetLabel: "목표",
    goodDirection: "higher",
  },
  evidenceCoverage: {
    label: "근거 연결률",
    description: "주장에 Evidence 연결 비율",
    targetLabel: "목표",
    goodDirection: "higher",
  },
  hallucinationRate: {
    label: "환각률",
    description: "근거 없는 주장 비율",
    targetLabel: "최대",
    goodDirection: "lower",
  },
  reproducibility: {
    label: "재현성",
    description: "동일 입력 시 동일 결과 비율",
    targetLabel: "목표",
    goodDirection: "higher",
  },
  responseTime: {
    label: "응답 시간",
    description: "답변 생성 시간",
    targetLabel: "최대",
    goodDirection: "lower",
  },
};

const STATUS_COLORS = {
  PASS: "#4CAF50",
  WARNING: "#FF9800",
  FAIL: "#F44336",
};

const TREND_ICONS = {
  IMPROVING: "[^]",
  STABLE: "[-]",
  DECLINING: "[v]",
};

// ============================================================
// Helper Components
// ============================================================

const MetricCard: React.FC<{
  metricKey: string;
  metric: MetricScore;
  config: (typeof METRIC_CONFIG)[keyof typeof METRIC_CONFIG];
}> = ({ metricKey, metric, config }) => {
  const isPercentage = metric.unit === "%";
  const displayValue = isPercentage
    ? `${(metric.value * 100).toFixed(1)}%`
    : `${metric.value.toFixed(1)}${metric.unit}`;
  const displayTarget = isPercentage
    ? `${(metric.target * 100).toFixed(0)}%`
    : `${metric.target}${metric.unit}`;

  return (
    <div
      style={{
        padding: "16px",
        borderRadius: "8px",
        border: `2px solid ${STATUS_COLORS[metric.status]}`,
        background: "white",
      }}
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "8px",
        }}
      >
        <span style={{ fontWeight: "bold", fontSize: "14px" }}>
          {config.label}
        </span>
        <span
          style={{
            fontSize: "12px",
            padding: "2px 8px",
            borderRadius: "4px",
            background: STATUS_COLORS[metric.status],
            color: "white",
          }}
        >
          {metric.status}
        </span>
      </div>

      <div style={{ fontSize: "28px", fontWeight: "bold", marginBottom: "4px" }}>
        {displayValue}
      </div>

      <div style={{ fontSize: "12px", color: "#666" }}>
        {config.targetLabel}: {displayTarget}
      </div>

      {/* Mini Chart */}
      <div
        style={{
          marginTop: "12px",
          height: "40px",
          display: "flex",
          alignItems: "flex-end",
          gap: "2px",
        }}
      >
        {metric.history.slice(-10).map((point, idx) => {
          const height = isPercentage
            ? point.value * 40
            : Math.min((point.value / metric.target) * 40, 40);
          return (
            <div
              key={idx}
              style={{
                flex: 1,
                height: `${height}px`,
                background:
                  config.goodDirection === "higher"
                    ? point.value >= metric.target
                      ? STATUS_COLORS.PASS
                      : STATUS_COLORS.WARNING
                    : point.value <= metric.target
                    ? STATUS_COLORS.PASS
                    : STATUS_COLORS.WARNING,
                borderRadius: "2px",
              }}
              title={`${point.date}: ${isPercentage ? (point.value * 100).toFixed(1) + "%" : point.value}`}
            />
          );
        })}
      </div>
    </div>
  );
};

const AgentCard: React.FC<{
  agent: AgentMetrics;
  onSelect?: (agentId: string) => void;
  selected?: boolean;
}> = ({ agent, onSelect, selected }) => {
  const overallScore = useMemo(() => {
    const metrics = agent.metrics;
    const scores = [
      metrics.completeness.status === "PASS" ? 1 : metrics.completeness.status === "WARNING" ? 0.5 : 0,
      metrics.evidenceCoverage.status === "PASS" ? 1 : metrics.evidenceCoverage.status === "WARNING" ? 0.5 : 0,
      metrics.hallucinationRate.status === "PASS" ? 1 : metrics.hallucinationRate.status === "WARNING" ? 0.5 : 0,
      metrics.reproducibility.status === "PASS" ? 1 : metrics.reproducibility.status === "WARNING" ? 0.5 : 0,
      metrics.responseTime.status === "PASS" ? 1 : metrics.responseTime.status === "WARNING" ? 0.5 : 0,
    ];
    return (scores.reduce((a, b) => a + b, 0) / scores.length) * 100;
  }, [agent.metrics]);

  return (
    <div
      onClick={() => onSelect?.(agent.agentId)}
      style={{
        padding: "16px",
        borderRadius: "8px",
        border: selected ? "2px solid #2196F3" : "1px solid #e0e0e0",
        background: selected ? "#E3F2FD" : "white",
        cursor: "pointer",
        transition: "all 0.2s",
      }}
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "12px",
        }}
      >
        <div>
          <div style={{ fontWeight: "bold", fontSize: "16px" }}>
            {agent.agentName}
          </div>
          <div style={{ fontSize: "12px", color: "#666" }}>
            {agent.agentId}
          </div>
        </div>
        <div style={{ textAlign: "right" }}>
          <div style={{ fontSize: "12px", color: "#666" }}>종합 점수</div>
          <div style={{ fontSize: "20px", fontWeight: "bold" }}>
            {overallScore.toFixed(0)}%
          </div>
        </div>
      </div>

      {/* Metrics Summary */}
      <div
        style={{
          display: "flex",
          gap: "8px",
          flexWrap: "wrap",
        }}
      >
        {Object.entries(agent.metrics).map(([key, metric]) => (
          <div
            key={key}
            style={{
              padding: "4px 8px",
              borderRadius: "4px",
              background: STATUS_COLORS[metric.status] + "20",
              border: `1px solid ${STATUS_COLORS[metric.status]}`,
              fontSize: "11px",
            }}
          >
            {METRIC_CONFIG[key as keyof typeof METRIC_CONFIG]?.label}:{" "}
            {metric.status}
          </div>
        ))}
      </div>

      {/* Trend */}
      <div
        style={{
          marginTop: "12px",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          fontSize: "12px",
          color: "#666",
        }}
      >
        <span>
          트렌드: {TREND_ICONS[agent.trend]} {agent.trend}
        </span>
        <span>업데이트: {new Date(agent.lastUpdated).toLocaleDateString()}</span>
      </div>
    </div>
  );
};

const EvaluationResultRow: React.FC<{
  result: EvaluationResult;
  expanded?: boolean;
  onToggle?: () => void;
}> = ({ result, expanded, onToggle }) => {
  return (
    <div
      style={{
        border: "1px solid #e0e0e0",
        borderRadius: "8px",
        marginBottom: "8px",
        overflow: "hidden",
      }}
    >
      {/* Header */}
      <div
        onClick={onToggle}
        style={{
          padding: "12px 16px",
          background: "#f5f5f5",
          cursor: "pointer",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <div>
          <div style={{ fontWeight: "bold" }}>{result.query}</div>
          <div style={{ fontSize: "12px", color: "#666" }}>
            {result.queryType} | {new Date(result.timestamp).toLocaleString()}
          </div>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
          <div
            style={{
              padding: "4px 12px",
              borderRadius: "4px",
              background:
                result.overallScore >= 80
                  ? STATUS_COLORS.PASS
                  : result.overallScore >= 60
                  ? STATUS_COLORS.WARNING
                  : STATUS_COLORS.FAIL,
              color: "white",
              fontWeight: "bold",
            }}
          >
            {result.overallScore.toFixed(0)}%
          </div>
          <span>{expanded ? "[-]" : "[+]"}</span>
        </div>
      </div>

      {/* Details */}
      {expanded && (
        <div style={{ padding: "16px" }}>
          {/* Agent Results */}
          <div style={{ marginBottom: "16px" }}>
            <div style={{ fontWeight: "bold", marginBottom: "8px" }}>
              Agent 결과
            </div>
            <table style={{ width: "100%", borderCollapse: "collapse" }}>
              <thead>
                <tr style={{ background: "#f5f5f5" }}>
                  <th style={{ padding: "8px", textAlign: "left" }}>Agent</th>
                  <th style={{ padding: "8px", textAlign: "center" }}>상태</th>
                  <th style={{ padding: "8px", textAlign: "center" }}>품질</th>
                  <th style={{ padding: "8px", textAlign: "center" }}>근거</th>
                  <th style={{ padding: "8px", textAlign: "center" }}>미검증</th>
                  <th style={{ padding: "8px", textAlign: "center" }}>시간</th>
                </tr>
              </thead>
              <tbody>
                {result.agentResults.map((ar) => (
                  <tr key={ar.agentId} style={{ borderBottom: "1px solid #e0e0e0" }}>
                    <td style={{ padding: "8px" }}>{ar.agentName}</td>
                    <td style={{ padding: "8px", textAlign: "center" }}>
                      <span
                        style={{
                          color: ar.success ? STATUS_COLORS.PASS : STATUS_COLORS.FAIL,
                        }}
                      >
                        {ar.success ? "[PASS]" : "[FAIL]"}
                      </span>
                    </td>
                    <td style={{ padding: "8px", textAlign: "center" }}>
                      {(ar.outputQuality * 100).toFixed(0)}%
                    </td>
                    <td style={{ padding: "8px", textAlign: "center" }}>
                      {ar.evidenceLinks}
                    </td>
                    <td style={{ padding: "8px", textAlign: "center" }}>
                      {ar.unverifiedClaims}
                    </td>
                    <td style={{ padding: "8px", textAlign: "center" }}>
                      {ar.executionTime.toFixed(0)}ms
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Issues */}
          {result.issues.length > 0 && (
            <div>
              <div style={{ fontWeight: "bold", marginBottom: "8px" }}>
                이슈 ({result.issues.length})
              </div>
              {result.issues.map((issue, idx) => (
                <div
                  key={idx}
                  style={{
                    padding: "12px",
                    marginBottom: "8px",
                    borderRadius: "4px",
                    borderLeft: `4px solid ${
                      issue.severity === "HIGH"
                        ? STATUS_COLORS.FAIL
                        : issue.severity === "MEDIUM"
                        ? STATUS_COLORS.WARNING
                        : "#2196F3"
                    }`,
                    background: "#f9f9f9",
                  }}
                >
                  <div style={{ display: "flex", gap: "8px", marginBottom: "4px" }}>
                    <span
                      style={{
                        fontSize: "11px",
                        padding: "2px 6px",
                        borderRadius: "2px",
                        background:
                          issue.severity === "HIGH"
                            ? STATUS_COLORS.FAIL
                            : issue.severity === "MEDIUM"
                            ? STATUS_COLORS.WARNING
                            : "#2196F3",
                        color: "white",
                      }}
                    >
                      {issue.severity}
                    </span>
                    <span style={{ fontSize: "12px", color: "#666" }}>
                      {issue.agentId}
                    </span>
                  </div>
                  <div style={{ marginBottom: "4px" }}>{issue.message}</div>
                  <div style={{ fontSize: "12px", color: "#666" }}>
                    권장: {issue.recommendation}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

// ============================================================
// Main Component
// ============================================================

export const AgentEvalDashboard: React.FC<AgentEvalDashboardProps> = ({
  agents,
  recentEvaluations = [],
  onRefresh,
  onAgentSelect,
}) => {
  const [selectedAgentId, setSelectedAgentId] = useState<string | null>(null);
  const [expandedEvalId, setExpandedEvalId] = useState<string | null>(null);
  const [view, setView] = useState<"overview" | "details">("overview");

  const selectedAgent = useMemo(
    () => agents.find((a) => a.agentId === selectedAgentId),
    [agents, selectedAgentId]
  );

  const handleAgentSelect = (agentId: string) => {
    setSelectedAgentId(agentId);
    setView("details");
    onAgentSelect?.(agentId);
  };

  // Summary Stats
  const summaryStats = useMemo(() => {
    const totalAgents = agents.length;
    const passingAgents = agents.filter(
      (a) =>
        Object.values(a.metrics).filter((m) => m.status === "PASS").length >= 4
    ).length;
    const avgCompleteness =
      agents.reduce((sum, a) => sum + a.metrics.completeness.value, 0) /
      totalAgents;
    const avgEvidenceCoverage =
      agents.reduce((sum, a) => sum + a.metrics.evidenceCoverage.value, 0) /
      totalAgents;
    const avgHallucinationRate =
      agents.reduce((sum, a) => sum + a.metrics.hallucinationRate.value, 0) /
      totalAgents;

    return {
      totalAgents,
      passingAgents,
      avgCompleteness,
      avgEvidenceCoverage,
      avgHallucinationRate,
    };
  }, [agents]);

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
          <h1 style={{ margin: 0, fontSize: "24px" }}>Agent Evaluation Dashboard</h1>
          <p style={{ margin: "4px 0 0", color: "#666" }}>
            AI Agent 성능 모니터링 및 평가
          </p>
        </div>
        <div style={{ display: "flex", gap: "8px" }}>
          <button
            onClick={() => setView("overview")}
            style={{
              padding: "8px 16px",
              border: view === "overview" ? "2px solid #2196F3" : "1px solid #ccc",
              borderRadius: "4px",
              background: view === "overview" ? "#E3F2FD" : "white",
              cursor: "pointer",
            }}
          >
            Overview
          </button>
          <button
            onClick={() => setView("details")}
            style={{
              padding: "8px 16px",
              border: view === "details" ? "2px solid #2196F3" : "1px solid #ccc",
              borderRadius: "4px",
              background: view === "details" ? "#E3F2FD" : "white",
              cursor: "pointer",
            }}
          >
            Details
          </button>
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

      {/* Summary Stats */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
          gap: "16px",
          marginBottom: "24px",
        }}
      >
        <div
          style={{
            padding: "16px",
            borderRadius: "8px",
            background: "#E3F2FD",
            textAlign: "center",
          }}
        >
          <div style={{ fontSize: "12px", color: "#666" }}>전체 Agent</div>
          <div style={{ fontSize: "32px", fontWeight: "bold" }}>
            {summaryStats.totalAgents}
          </div>
        </div>
        <div
          style={{
            padding: "16px",
            borderRadius: "8px",
            background: "#E8F5E9",
            textAlign: "center",
          }}
        >
          <div style={{ fontSize: "12px", color: "#666" }}>정상 Agent</div>
          <div style={{ fontSize: "32px", fontWeight: "bold", color: STATUS_COLORS.PASS }}>
            {summaryStats.passingAgents}
          </div>
        </div>
        <div
          style={{
            padding: "16px",
            borderRadius: "8px",
            background: "#FFF3E0",
            textAlign: "center",
          }}
        >
          <div style={{ fontSize: "12px", color: "#666" }}>평균 완결성</div>
          <div style={{ fontSize: "32px", fontWeight: "bold" }}>
            {(summaryStats.avgCompleteness * 100).toFixed(0)}%
          </div>
        </div>
        <div
          style={{
            padding: "16px",
            borderRadius: "8px",
            background: "#E8F5E9",
            textAlign: "center",
          }}
        >
          <div style={{ fontSize: "12px", color: "#666" }}>평균 근거 연결률</div>
          <div style={{ fontSize: "32px", fontWeight: "bold" }}>
            {(summaryStats.avgEvidenceCoverage * 100).toFixed(0)}%
          </div>
        </div>
        <div
          style={{
            padding: "16px",
            borderRadius: "8px",
            background:
              summaryStats.avgHallucinationRate <= 0.05
                ? "#E8F5E9"
                : "#FFEBEE",
            textAlign: "center",
          }}
        >
          <div style={{ fontSize: "12px", color: "#666" }}>평균 환각률</div>
          <div
            style={{
              fontSize: "32px",
              fontWeight: "bold",
              color:
                summaryStats.avgHallucinationRate <= 0.05
                  ? STATUS_COLORS.PASS
                  : STATUS_COLORS.FAIL,
            }}
          >
            {(summaryStats.avgHallucinationRate * 100).toFixed(1)}%
          </div>
        </div>
      </div>

      {view === "overview" ? (
        <>
          {/* Agent Grid */}
          <div style={{ marginBottom: "32px" }}>
            <h2 style={{ fontSize: "18px", marginBottom: "16px" }}>Agent 현황</h2>
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))",
                gap: "16px",
              }}
            >
              {agents.map((agent) => (
                <AgentCard
                  key={agent.agentId}
                  agent={agent}
                  onSelect={handleAgentSelect}
                  selected={agent.agentId === selectedAgentId}
                />
              ))}
            </div>
          </div>

          {/* Recent Evaluations */}
          <div>
            <h2 style={{ fontSize: "18px", marginBottom: "16px" }}>
              최근 평가 결과
            </h2>
            {recentEvaluations.length > 0 ? (
              recentEvaluations.slice(0, 5).map((result) => (
                <EvaluationResultRow
                  key={result.evaluationId}
                  result={result}
                  expanded={expandedEvalId === result.evaluationId}
                  onToggle={() =>
                    setExpandedEvalId(
                      expandedEvalId === result.evaluationId
                        ? null
                        : result.evaluationId
                    )
                  }
                />
              ))
            ) : (
              <div
                style={{
                  padding: "32px",
                  textAlign: "center",
                  color: "#666",
                  background: "#f5f5f5",
                  borderRadius: "8px",
                }}
              >
                최근 평가 결과가 없습니다
              </div>
            )}
          </div>
        </>
      ) : (
        /* Details View */
        <div>
          {selectedAgent ? (
            <>
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  marginBottom: "24px",
                }}
              >
                <div>
                  <h2 style={{ margin: 0 }}>{selectedAgent.agentName}</h2>
                  <p style={{ margin: "4px 0 0", color: "#666" }}>
                    {selectedAgent.agentId} | 평가 기간:{" "}
                    {new Date(selectedAgent.evaluationPeriod.start).toLocaleDateString()} -{" "}
                    {new Date(selectedAgent.evaluationPeriod.end).toLocaleDateString()}
                  </p>
                </div>
                <div style={{ display: "flex", gap: "8px" }}>
                  {agents.map((a) => (
                    <button
                      key={a.agentId}
                      onClick={() => setSelectedAgentId(a.agentId)}
                      style={{
                        padding: "4px 8px",
                        border:
                          a.agentId === selectedAgentId
                            ? "2px solid #2196F3"
                            : "1px solid #ccc",
                        borderRadius: "4px",
                        background: a.agentId === selectedAgentId ? "#E3F2FD" : "white",
                        fontSize: "12px",
                        cursor: "pointer",
                      }}
                    >
                      {a.agentName.substring(0, 10)}
                    </button>
                  ))}
                </div>
              </div>

              {/* Metric Cards */}
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
                  gap: "16px",
                }}
              >
                {Object.entries(selectedAgent.metrics).map(([key, metric]) => (
                  <MetricCard
                    key={key}
                    metricKey={key}
                    metric={metric}
                    config={METRIC_CONFIG[key as keyof typeof METRIC_CONFIG]}
                  />
                ))}
              </div>
            </>
          ) : (
            <div
              style={{
                padding: "64px",
                textAlign: "center",
                color: "#666",
                background: "#f5f5f5",
                borderRadius: "8px",
              }}
            >
              Agent를 선택하여 상세 정보를 확인하세요
            </div>
          )}
        </div>
      )}
    </div>
  );
};

// ============================================================
// Mock Data Generator (for testing)
// ============================================================

export const generateMockAgentMetrics = (): AgentMetrics[] => {
  const agents = [
    { id: "query-decomposition", name: "Query Decomposition" },
    { id: "option-generator", name: "Option Generator" },
    { id: "impact-simulator", name: "Impact Simulator" },
    { id: "success-probability", name: "Success Probability" },
    { id: "validator", name: "Validator" },
  ];

  const generateHistory = (baseValue: number, variance: number): MetricHistoryPoint[] => {
    const history: MetricHistoryPoint[] = [];
    const now = new Date();
    for (let i = 9; i >= 0; i--) {
      const date = new Date(now);
      date.setDate(date.getDate() - i);
      history.push({
        date: date.toISOString().split("T")[0],
        value: Math.max(0, Math.min(1, baseValue + (Math.random() - 0.5) * variance)),
      });
    }
    return history;
  };

  return agents.map((agent) => ({
    agentId: agent.id,
    agentName: agent.name,
    evaluationPeriod: {
      start: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
      end: new Date().toISOString(),
    },
    metrics: {
      completeness: {
        value: 0.92 + Math.random() * 0.06,
        target: 0.9,
        unit: "%",
        status: "PASS",
        history: generateHistory(0.92, 0.1),
      },
      evidenceCoverage: {
        value: 0.95 + Math.random() * 0.04,
        target: 0.95,
        unit: "%",
        status: Math.random() > 0.3 ? "PASS" : "WARNING",
        history: generateHistory(0.95, 0.08),
      },
      hallucinationRate: {
        value: 0.03 + Math.random() * 0.04,
        target: 0.05,
        unit: "%",
        status: Math.random() > 0.2 ? "PASS" : "WARNING",
        history: generateHistory(0.04, 0.03),
      },
      reproducibility: {
        value: 0.96 + Math.random() * 0.03,
        target: 0.95,
        unit: "%",
        status: "PASS",
        history: generateHistory(0.96, 0.05),
      },
      responseTime: {
        value: 15 + Math.random() * 20,
        target: 30,
        unit: "s",
        status: "PASS",
        history: generateHistory(0.6, 0.3).map((p) => ({ ...p, value: p.value * 30 })),
      },
    },
    trend: ["IMPROVING", "STABLE", "DECLINING"][Math.floor(Math.random() * 3)] as AgentMetrics["trend"],
    lastUpdated: new Date().toISOString(),
  }));
};

export default AgentEvalDashboard;
