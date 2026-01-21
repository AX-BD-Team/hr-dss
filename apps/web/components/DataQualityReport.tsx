/**
 * HR DSS - Data Quality Report Component
 *
 * 데이터 품질 평가 리포트 대시보드
 * Data Readiness Scorecard와 연동
 * 트렌드 분석, 이슈 목록, 권장 조치 포함
 */

import React, { useState, useMemo } from "react";

// ============================================================
// Types
// ============================================================

export interface DataQualityMetrics {
  generatedAt: string;
  dataSource: string;
  overallScore: number;
  overallStatus: "READY" | "WARNING" | "NOT_READY";
  summary: DataQualitySummary;
  entityResults: EntityResult[];
  trends?: QualityTrend[];
  issues?: QualityIssue[];
  recommendations?: Recommendation[];
}

export interface DataQualitySummary {
  totalEntities: number;
  totalRecords: number;
  passedEntities: number;
  failedEntities: number;
  readinessLevel: string;
}

export interface EntityResult {
  entityName: string;
  recordCount: number;
  overallStatus: "PASS" | "WARNING" | "FAIL";
  metrics: MetricResult[];
}

export interface MetricResult {
  name: string;
  description: string;
  value: number;
  target: number;
  unit: string;
  status: "PASS" | "WARNING" | "FAIL";
  details?: Record<string, unknown>;
}

export interface PerformanceCorrelation {
  metricName: string;
  entityName: string;
  qualityScore: number;
  agentPerformance: number;
  correlation: "STRONG" | "MODERATE" | "WEAK";
  impact: string;
}

// 새로운 타입 정의
export interface QualityTrend {
  date: string;
  overallScore: number;
  metricScores: Record<string, number>;
}

export interface QualityIssue {
  id: string;
  severity: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";
  category: "MISSING_DATA" | "DUPLICATE" | "INCONSISTENT" | "STALE" | "INVALID_FK";
  entityName: string;
  fieldName?: string;
  description: string;
  affectedRecords: number;
  detectedAt: string;
  suggestedAction?: string;
}

export interface Recommendation {
  id: string;
  priority: "HIGH" | "MEDIUM" | "LOW";
  type: "DATA_FIX" | "PROCESS_IMPROVEMENT" | "MONITORING" | "VALIDATION_RULE";
  title: string;
  description: string;
  expectedImpact: string;
  effort: "LOW" | "MEDIUM" | "HIGH";
  relatedIssues?: string[];
}

export interface DataQualityReportProps {
  metrics: DataQualityMetrics;
  performanceCorrelations?: PerformanceCorrelation[];
  onRefresh?: () => void;
  onEntityClick?: (entityName: string) => void;
  onIssueClick?: (issueId: string) => void;
  onRecommendationAction?: (recommendationId: string) => void;
  showImpactAnalysis?: boolean;
}

// ============================================================
// Constants
// ============================================================

const STATUS_COLORS = {
  PASS: "#4CAF50",
  WARNING: "#FF9800",
  FAIL: "#F44336",
  READY: "#4CAF50",
  NOT_READY: "#F44336",
};

const SEVERITY_COLORS = {
  CRITICAL: "#D32F2F",
  HIGH: "#F44336",
  MEDIUM: "#FF9800",
  LOW: "#2196F3",
};

const CATEGORY_LABELS: Record<string, { label: string; icon: string }> = {
  MISSING_DATA: { label: "결측 데이터", icon: "[!]" },
  DUPLICATE: { label: "중복 데이터", icon: "[=]" },
  INCONSISTENT: { label: "데이터 불일치", icon: "[~]" },
  STALE: { label: "오래된 데이터", icon: "[*]" },
  INVALID_FK: { label: "FK 오류", icon: "[X]" },
};

const PRIORITY_COLORS = {
  HIGH: "#F44336",
  MEDIUM: "#FF9800",
  LOW: "#4CAF50",
};

const TYPE_LABELS: Record<string, { label: string; color: string }> = {
  DATA_FIX: { label: "데이터 수정", color: "#F44336" },
  PROCESS_IMPROVEMENT: { label: "프로세스 개선", color: "#2196F3" },
  MONITORING: { label: "모니터링", color: "#9C27B0" },
  VALIDATION_RULE: { label: "검증 규칙", color: "#FF9800" },
};

const METRIC_LABELS: Record<string, { label: string; goodDirection: "higher" | "lower" }> = {
  missing_rate: { label: "결측률", goodDirection: "lower" },
  duplicate_rate: { label: "중복률", goodDirection: "lower" },
  required_field_rate: { label: "필수필드 충족률", goodDirection: "higher" },
  key_match_rate: { label: "FK 매칭률", goodDirection: "higher" },
};

const TAB_ITEMS = [
  { id: "overview", label: "개요" },
  { id: "entities", label: "엔터티별 상세" },
  { id: "issues", label: "이슈 목록" },
  { id: "trends", label: "트렌드" },
  { id: "recommendations", label: "권장 조치" },
  { id: "correlation", label: "영향 분석" },
];

// ============================================================
// Helper Components
// ============================================================

const OverallScoreCard: React.FC<{
  score: number;
  status: string;
  summary: DataQualitySummary;
}> = ({ score, status, summary }) => {
  const statusColor = STATUS_COLORS[status as keyof typeof STATUS_COLORS] || "#666";

  return (
    <div
      style={{
        padding: "24px",
        borderRadius: "12px",
        background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        color: "white",
        marginBottom: "24px",
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <div style={{ fontSize: "14px", opacity: 0.9, marginBottom: "8px" }}>
            Data Readiness Score
          </div>
          <div style={{ fontSize: "48px", fontWeight: "bold" }}>{score.toFixed(0)}%</div>
          <div
            style={{
              display: "inline-block",
              padding: "4px 12px",
              borderRadius: "16px",
              background: statusColor,
              fontSize: "14px",
              fontWeight: "bold",
              marginTop: "8px",
            }}
          >
            {status}
          </div>
        </div>
        <div style={{ textAlign: "right" }}>
          <div style={{ marginBottom: "16px" }}>
            <div style={{ fontSize: "24px", fontWeight: "bold" }}>{summary.totalEntities}</div>
            <div style={{ fontSize: "12px", opacity: 0.9 }}>엔터티</div>
          </div>
          <div style={{ marginBottom: "16px" }}>
            <div style={{ fontSize: "24px", fontWeight: "bold" }}>
              {summary.totalRecords.toLocaleString()}
            </div>
            <div style={{ fontSize: "12px", opacity: 0.9 }}>레코드</div>
          </div>
          <div>
            <div style={{ fontSize: "24px", fontWeight: "bold" }}>
              {summary.passedEntities}/{summary.totalEntities}
            </div>
            <div style={{ fontSize: "12px", opacity: 0.9 }}>통과</div>
          </div>
        </div>
      </div>
    </div>
  );
};

const MetricBar: React.FC<{
  metric: MetricResult;
}> = ({ metric }) => {
  const config = METRIC_LABELS[metric.name] || { label: metric.name, goodDirection: "higher" };
  const isPercentage = metric.unit === "%";
  const displayValue = isPercentage ? `${(metric.value * 100).toFixed(1)}%` : metric.value.toFixed(2);
  const displayTarget = isPercentage
    ? `${(metric.target * 100).toFixed(0)}%`
    : metric.target.toString();

  const progressValue = isPercentage ? metric.value * 100 : Math.min((metric.value / metric.target) * 100, 100);
  const progressColor = STATUS_COLORS[metric.status];

  return (
    <div style={{ marginBottom: "16px" }}>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "6px",
        }}
      >
        <div>
          <span style={{ fontWeight: "500" }}>{config.label}</span>
          <span style={{ fontSize: "12px", color: "#666", marginLeft: "8px" }}>
            ({metric.description})
          </span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <span style={{ fontWeight: "bold" }}>{displayValue}</span>
          <span style={{ fontSize: "12px", color: "#666" }}>목표: {displayTarget}</span>
          <span
            style={{
              padding: "2px 8px",
              borderRadius: "4px",
              background: progressColor,
              color: "white",
              fontSize: "11px",
              fontWeight: "bold",
            }}
          >
            {metric.status}
          </span>
        </div>
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
            width: `${Math.min(progressValue, 100)}%`,
            background: progressColor,
            borderRadius: "4px",
            transition: "width 0.3s ease",
          }}
        />
      </div>
    </div>
  );
};

const EntityCard: React.FC<{
  entity: EntityResult;
  expanded: boolean;
  onToggle: () => void;
  onEntityClick?: (entityName: string) => void;
}> = ({ entity, expanded, onToggle, onEntityClick }) => {
  const statusColor = STATUS_COLORS[entity.overallStatus];
  const passedMetrics = entity.metrics.filter((m) => m.status === "PASS").length;

  return (
    <div
      style={{
        border: "1px solid #e0e0e0",
        borderRadius: "8px",
        marginBottom: "12px",
        overflow: "hidden",
        background: "white",
      }}
    >
      {/* Header */}
      <div
        onClick={onToggle}
        style={{
          padding: "16px",
          background: "#fafafa",
          cursor: "pointer",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          borderLeft: `4px solid ${statusColor}`,
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
          <span
            style={{
              width: "32px",
              height: "32px",
              borderRadius: "50%",
              background: statusColor,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "white",
              fontWeight: "bold",
              fontSize: "12px",
            }}
          >
            {entity.overallStatus === "PASS" ? "OK" : "NG"}
          </span>
          <div>
            <div
              style={{ fontWeight: "bold", cursor: "pointer" }}
              onClick={(e) => {
                e.stopPropagation();
                onEntityClick?.(entity.entityName);
              }}
            >
              {entity.entityName}
            </div>
            <div style={{ fontSize: "12px", color: "#666" }}>
              {entity.recordCount.toLocaleString()} 레코드 | {passedMetrics}/{entity.metrics.length}{" "}
              지표 통과
            </div>
          </div>
        </div>
        <span style={{ fontSize: "18px", color: "#999" }}>{expanded ? "[-]" : "[+]"}</span>
      </div>

      {/* Metrics */}
      {expanded && (
        <div style={{ padding: "16px" }}>
          {entity.metrics.map((metric, idx) => (
            <MetricBar key={idx} metric={metric} />
          ))}
        </div>
      )}
    </div>
  );
};

const CorrelationChart: React.FC<{
  correlations: PerformanceCorrelation[];
}> = ({ correlations }) => {
  const correlationColors = {
    STRONG: "#F44336",
    MODERATE: "#FF9800",
    WEAK: "#4CAF50",
  };

  return (
    <div
      style={{
        padding: "20px",
        background: "white",
        borderRadius: "8px",
        boxShadow: "0 1px 4px rgba(0,0,0,0.05)",
      }}
    >
      <h3 style={{ margin: "0 0 16px 0", fontSize: "16px" }}>
        데이터 품질 - Agent 성능 상관관계
      </h3>
      <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "13px" }}>
        <thead>
          <tr style={{ background: "#f5f5f5" }}>
            <th style={{ padding: "10px", textAlign: "left" }}>엔터티</th>
            <th style={{ padding: "10px", textAlign: "left" }}>지표</th>
            <th style={{ padding: "10px", textAlign: "center" }}>품질 점수</th>
            <th style={{ padding: "10px", textAlign: "center" }}>Agent 성능</th>
            <th style={{ padding: "10px", textAlign: "center" }}>상관관계</th>
            <th style={{ padding: "10px", textAlign: "left" }}>영향</th>
          </tr>
        </thead>
        <tbody>
          {correlations.map((corr, idx) => (
            <tr key={idx} style={{ borderBottom: "1px solid #e0e0e0" }}>
              <td style={{ padding: "10px" }}>{corr.entityName}</td>
              <td style={{ padding: "10px" }}>{corr.metricName}</td>
              <td style={{ padding: "10px", textAlign: "center" }}>
                {(corr.qualityScore * 100).toFixed(0)}%
              </td>
              <td style={{ padding: "10px", textAlign: "center" }}>
                {(corr.agentPerformance * 100).toFixed(0)}%
              </td>
              <td style={{ padding: "10px", textAlign: "center" }}>
                <span
                  style={{
                    padding: "2px 8px",
                    borderRadius: "4px",
                    background: correlationColors[corr.correlation],
                    color: "white",
                    fontSize: "11px",
                  }}
                >
                  {corr.correlation}
                </span>
              </td>
              <td style={{ padding: "10px", fontSize: "12px", color: "#666" }}>{corr.impact}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

// ============================================================
// Main Component
// ============================================================

export const DataQualityReport: React.FC<DataQualityReportProps> = ({
  metrics,
  performanceCorrelations = [],
  onRefresh,
  onEntityClick,
  showImpactAnalysis = true,
}) => {
  const [expandedEntities, setExpandedEntities] = useState<Set<string>>(new Set());
  const [filterStatus, setFilterStatus] = useState<"ALL" | "PASS" | "FAIL">("ALL");
  const [sortBy, setSortBy] = useState<"name" | "score" | "records">("name");

  // Filter and sort entities
  const filteredEntities = useMemo(() => {
    let entities = [...metrics.entityResults];

    // Filter
    if (filterStatus !== "ALL") {
      entities = entities.filter((e) =>
        filterStatus === "PASS" ? e.overallStatus === "PASS" : e.overallStatus !== "PASS"
      );
    }

    // Sort
    entities.sort((a, b) => {
      switch (sortBy) {
        case "score":
          const aScore = a.metrics.filter((m) => m.status === "PASS").length / a.metrics.length;
          const bScore = b.metrics.filter((m) => m.status === "PASS").length / b.metrics.length;
          return bScore - aScore;
        case "records":
          return b.recordCount - a.recordCount;
        default:
          return a.entityName.localeCompare(b.entityName);
      }
    });

    return entities;
  }, [metrics.entityResults, filterStatus, sortBy]);

  // Calculate metric summaries
  const metricSummaries = useMemo(() => {
    const summaries: Record<string, { passed: number; total: number; avgValue: number }> = {};

    metrics.entityResults.forEach((entity) => {
      entity.metrics.forEach((metric) => {
        if (!summaries[metric.name]) {
          summaries[metric.name] = { passed: 0, total: 0, avgValue: 0 };
        }
        summaries[metric.name].total++;
        if (metric.status === "PASS") {
          summaries[metric.name].passed++;
        }
        summaries[metric.name].avgValue += metric.value;
      });
    });

    Object.keys(summaries).forEach((key) => {
      summaries[key].avgValue /= summaries[key].total;
    });

    return summaries;
  }, [metrics.entityResults]);

  const toggleEntity = (entityName: string) => {
    const newExpanded = new Set(expandedEntities);
    if (newExpanded.has(entityName)) {
      newExpanded.delete(entityName);
    } else {
      newExpanded.add(entityName);
    }
    setExpandedEntities(newExpanded);
  };

  const expandAll = () => {
    setExpandedEntities(new Set(metrics.entityResults.map((e) => e.entityName)));
  };

  const collapseAll = () => {
    setExpandedEntities(new Set());
  };

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
          <h1 style={{ margin: 0, fontSize: "24px" }}>Data Quality Report</h1>
          <p style={{ margin: "4px 0 0", color: "#666" }}>
            데이터 품질 평가 및 Agent 성능 영향 분석
          </p>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
          <span style={{ fontSize: "12px", color: "#666" }}>
            생성: {new Date(metrics.generatedAt).toLocaleString()}
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
      <OverallScoreCard
        score={metrics.overallScore}
        status={metrics.overallStatus}
        summary={metrics.summary}
      />

      {/* Metric Summary Cards */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
          gap: "16px",
          marginBottom: "24px",
        }}
      >
        {Object.entries(metricSummaries).map(([name, summary]) => {
          const config = METRIC_LABELS[name] || { label: name };
          const passRate = (summary.passed / summary.total) * 100;
          const avgDisplay =
            name.includes("rate") ? `${(summary.avgValue * 100).toFixed(1)}%` : summary.avgValue.toFixed(2);

          return (
            <div
              key={name}
              style={{
                padding: "16px",
                background: "white",
                borderRadius: "8px",
                boxShadow: "0 1px 4px rgba(0,0,0,0.05)",
              }}
            >
              <div style={{ fontSize: "12px", color: "#666", marginBottom: "8px" }}>
                {config.label}
              </div>
              <div style={{ fontSize: "24px", fontWeight: "bold", marginBottom: "4px" }}>
                {avgDisplay}
              </div>
              <div style={{ fontSize: "12px" }}>
                <span style={{ color: STATUS_COLORS.PASS }}>{summary.passed}</span>
                <span style={{ color: "#666" }}> / {summary.total} 통과</span>
                <span style={{ marginLeft: "8px", color: passRate === 100 ? STATUS_COLORS.PASS : STATUS_COLORS.WARNING }}>
                  ({passRate.toFixed(0)}%)
                </span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Entity List */}
      <div
        style={{
          background: "white",
          borderRadius: "8px",
          boxShadow: "0 1px 4px rgba(0,0,0,0.05)",
          padding: "20px",
          marginBottom: "24px",
        }}
      >
        {/* Controls */}
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginBottom: "16px",
          }}
        >
          <h3 style={{ margin: 0, fontSize: "16px" }}>엔터티별 상세</h3>
          <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value as typeof filterStatus)}
              style={{ padding: "6px 12px", borderRadius: "4px", border: "1px solid #ccc" }}
            >
              <option value="ALL">전체</option>
              <option value="PASS">통과만</option>
              <option value="FAIL">실패만</option>
            </select>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as typeof sortBy)}
              style={{ padding: "6px 12px", borderRadius: "4px", border: "1px solid #ccc" }}
            >
              <option value="name">이름순</option>
              <option value="score">점수순</option>
              <option value="records">레코드순</option>
            </select>
            <button
              onClick={expandAll}
              style={{
                padding: "6px 12px",
                border: "1px solid #ccc",
                borderRadius: "4px",
                background: "white",
                cursor: "pointer",
              }}
            >
              모두 펼치기
            </button>
            <button
              onClick={collapseAll}
              style={{
                padding: "6px 12px",
                border: "1px solid #ccc",
                borderRadius: "4px",
                background: "white",
                cursor: "pointer",
              }}
            >
              모두 접기
            </button>
          </div>
        </div>

        {/* Entity Cards */}
        {filteredEntities.map((entity) => (
          <EntityCard
            key={entity.entityName}
            entity={entity}
            expanded={expandedEntities.has(entity.entityName)}
            onToggle={() => toggleEntity(entity.entityName)}
            onEntityClick={onEntityClick}
          />
        ))}

        {filteredEntities.length === 0 && (
          <div
            style={{
              padding: "32px",
              textAlign: "center",
              color: "#666",
            }}
          >
            조건에 맞는 엔터티가 없습니다
          </div>
        )}
      </div>

      {/* Performance Correlation */}
      {showImpactAnalysis && performanceCorrelations.length > 0 && (
        <CorrelationChart correlations={performanceCorrelations} />
      )}
    </div>
  );
};

// ============================================================
// Mock Data Generator
// ============================================================

export const generateMockDataQualityMetrics = (): DataQualityMetrics => {
  const entities = [
    "employees",
    "orgUnits",
    "projects",
    "workPackages",
    "opportunities",
    "competencies",
    "assignments",
    "availabilities",
  ];

  const entityResults: EntityResult[] = entities.map((name) => {
    const recordCount = Math.floor(Math.random() * 100) + 20;
    const metrics: MetricResult[] = [
      {
        name: "missing_rate",
        description: "필수 필드 결측 비율",
        value: Math.random() * 0.08,
        target: 0.1,
        unit: "%",
        status: Math.random() > 0.2 ? "PASS" : "WARNING",
      },
      {
        name: "duplicate_rate",
        description: "키 중복 비율",
        value: Math.random() * 0.005,
        target: 0.01,
        unit: "%",
        status: "PASS",
      },
      {
        name: "required_field_rate",
        description: "필수 필드 충족률",
        value: 0.85 + Math.random() * 0.15,
        target: 0.8,
        unit: "%",
        status: Math.random() > 0.1 ? "PASS" : "WARNING",
      },
      {
        name: "key_match_rate",
        description: "FK 매칭률",
        value: 0.95 + Math.random() * 0.05,
        target: 0.95,
        unit: "%",
        status: Math.random() > 0.15 ? "PASS" : "FAIL",
      },
    ];

    const overallStatus =
      metrics.filter((m) => m.status !== "PASS").length === 0
        ? "PASS"
        : metrics.some((m) => m.status === "FAIL")
        ? "FAIL"
        : "WARNING";

    return {
      entityName: name,
      recordCount,
      overallStatus,
      metrics,
    };
  });

  const totalRecords = entityResults.reduce((sum, e) => sum + e.recordCount, 0);
  const passedEntities = entityResults.filter((e) => e.overallStatus === "PASS").length;
  const overallScore =
    (entityResults.reduce(
      (sum, e) => sum + e.metrics.filter((m) => m.status === "PASS").length / e.metrics.length,
      0
    ) /
      entityResults.length) *
    100;

  return {
    generatedAt: new Date().toISOString(),
    dataSource: "data/mock",
    overallScore,
    overallStatus: overallScore >= 90 ? "READY" : overallScore >= 70 ? "WARNING" : "NOT_READY",
    summary: {
      totalEntities: entityResults.length,
      totalRecords,
      passedEntities,
      failedEntities: entityResults.length - passedEntities,
      readinessLevel: overallScore >= 90 ? "READY" : overallScore >= 70 ? "WARNING" : "NOT_READY",
    },
    entityResults,
  };
};

export const generateMockPerformanceCorrelations = (): PerformanceCorrelation[] => {
  return [
    {
      metricName: "key_match_rate",
      entityName: "assignments",
      qualityScore: 0.97,
      agentPerformance: 0.95,
      correlation: "STRONG",
      impact: "FK 매칭률이 낮으면 KG 쿼리 정확도 저하",
    },
    {
      metricName: "missing_rate",
      entityName: "employees",
      qualityScore: 0.98,
      agentPerformance: 0.92,
      correlation: "MODERATE",
      impact: "직원 정보 결측 시 역량 분석 정확도 감소",
    },
    {
      metricName: "required_field_rate",
      entityName: "projects",
      qualityScore: 0.88,
      agentPerformance: 0.85,
      correlation: "STRONG",
      impact: "프로젝트 필수 정보 미충족 시 영향 분석 불가",
    },
  ];
};

export default DataQualityReport;
