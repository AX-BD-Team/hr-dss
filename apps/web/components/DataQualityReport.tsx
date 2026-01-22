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
  category:
    | "MISSING_DATA"
    | "DUPLICATE"
    | "INCONSISTENT"
    | "STALE"
    | "INVALID_FK";
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

const METRIC_LABELS: Record<
  string,
  { label: string; goodDirection: "higher" | "lower" }
> = {
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
  const statusColor =
    STATUS_COLORS[status as keyof typeof STATUS_COLORS] || "#666";

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
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <div>
          <div style={{ fontSize: "14px", opacity: 0.9, marginBottom: "8px" }}>
            Data Readiness Score
          </div>
          <div style={{ fontSize: "48px", fontWeight: "bold" }}>
            {score.toFixed(0)}%
          </div>
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
            <div style={{ fontSize: "24px", fontWeight: "bold" }}>
              {summary.totalEntities}
            </div>
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
  const config = METRIC_LABELS[metric.name] || {
    label: metric.name,
    goodDirection: "higher",
  };
  const isPercentage = metric.unit === "%";
  const displayValue = isPercentage
    ? `${(metric.value * 100).toFixed(1)}%`
    : metric.value.toFixed(2);
  const displayTarget = isPercentage
    ? `${(metric.target * 100).toFixed(0)}%`
    : metric.target.toString();

  const progressValue = isPercentage
    ? metric.value * 100
    : Math.min((metric.value / metric.target) * 100, 100);
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
          <span style={{ fontSize: "12px", color: "#666" }}>
            목표: {displayTarget}
          </span>
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
  const passedMetrics = entity.metrics.filter(
    (m) => m.status === "PASS",
  ).length;

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
              {entity.recordCount.toLocaleString()} 레코드 | {passedMetrics}/
              {entity.metrics.length} 지표 통과
            </div>
          </div>
        </div>
        <span style={{ fontSize: "18px", color: "#999" }}>
          {expanded ? "[-]" : "[+]"}
        </span>
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
      <table
        style={{ width: "100%", borderCollapse: "collapse", fontSize: "13px" }}
      >
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
              <td style={{ padding: "10px", fontSize: "12px", color: "#666" }}>
                {corr.impact}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

// 트렌드 차트 컴포넌트
const TrendChart: React.FC<{
  trends: QualityTrend[];
}> = ({ trends }) => {
  if (trends.length === 0) {
    return (
      <div style={{ padding: "32px", textAlign: "center", color: "#666" }}>
        트렌드 데이터가 없습니다
      </div>
    );
  }

  const maxScore = 100;
  const minScore = Math.min(...trends.map((t) => t.overallScore)) - 5;
  const chartHeight = 200;
  const chartWidth = "100%";

  const getY = (score: number) =>
    chartHeight - ((score - minScore) / (maxScore - minScore)) * chartHeight;

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
        품질 점수 트렌드
      </h3>
      <div
        style={{
          position: "relative",
          height: chartHeight + 40,
          width: chartWidth,
        }}
      >
        {/* Y축 가이드라인 */}
        {[100, 90, 80, 70].map((val) => (
          <div
            key={val}
            style={{
              position: "absolute",
              left: 0,
              right: 0,
              top: getY(val),
              borderTop: "1px dashed #e0e0e0",
              fontSize: "10px",
              color: "#999",
            }}
          >
            <span style={{ position: "absolute", left: -30, top: -8 }}>
              {val}%
            </span>
          </div>
        ))}

        {/* 데이터 포인트 및 라인 */}
        <svg
          style={{
            position: "absolute",
            left: 40,
            top: 0,
            width: "calc(100% - 60px)",
            height: chartHeight,
          }}
          viewBox={`0 0 ${(trends.length - 1) * 60 + 20} ${chartHeight}`}
          preserveAspectRatio="none"
        >
          {/* 라인 */}
          <polyline
            fill="none"
            stroke="#667eea"
            strokeWidth="2"
            points={trends
              .map((t, i) => `${i * 60 + 10},${getY(t.overallScore)}`)
              .join(" ")}
          />
          {/* 포인트 */}
          {trends.map((t, i) => (
            <circle
              key={i}
              cx={i * 60 + 10}
              cy={getY(t.overallScore)}
              r="5"
              fill="#667eea"
              stroke="white"
              strokeWidth="2"
            />
          ))}
        </svg>

        {/* X축 레이블 */}
        <div
          style={{
            position: "absolute",
            bottom: 0,
            left: 40,
            right: 20,
            display: "flex",
            justifyContent: "space-between",
          }}
        >
          {trends.map((t, i) => (
            <div
              key={i}
              style={{ fontSize: "10px", color: "#666", textAlign: "center" }}
            >
              {new Date(t.date).toLocaleDateString("ko-KR", {
                month: "short",
                day: "numeric",
              })}
            </div>
          ))}
        </div>
      </div>

      {/* 점수 요약 */}
      <div
        style={{
          display: "flex",
          gap: "24px",
          marginTop: "16px",
          paddingTop: "16px",
          borderTop: "1px solid #e0e0e0",
        }}
      >
        <div>
          <div style={{ fontSize: "12px", color: "#666" }}>현재 점수</div>
          <div
            style={{ fontSize: "20px", fontWeight: "bold", color: "#667eea" }}
          >
            {trends[trends.length - 1].overallScore.toFixed(1)}%
          </div>
        </div>
        <div>
          <div style={{ fontSize: "12px", color: "#666" }}>7일 전 대비</div>
          <div
            style={{
              fontSize: "20px",
              fontWeight: "bold",
              color:
                trends[trends.length - 1].overallScore >= trends[0].overallScore
                  ? "#4CAF50"
                  : "#F44336",
            }}
          >
            {trends[trends.length - 1].overallScore >= trends[0].overallScore
              ? "+"
              : ""}
            {(
              trends[trends.length - 1].overallScore - trends[0].overallScore
            ).toFixed(1)}
            %
          </div>
        </div>
        <div>
          <div style={{ fontSize: "12px", color: "#666" }}>평균</div>
          <div style={{ fontSize: "20px", fontWeight: "bold" }}>
            {(
              trends.reduce((sum, t) => sum + t.overallScore, 0) / trends.length
            ).toFixed(1)}
            %
          </div>
        </div>
      </div>
    </div>
  );
};

// 이슈 목록 컴포넌트
const IssueList: React.FC<{
  issues: QualityIssue[];
  onIssueClick?: (issueId: string) => void;
}> = ({ issues, onIssueClick }) => {
  const [filterSeverity, setFilterSeverity] = useState<string>("ALL");
  const [filterCategory, setFilterCategory] = useState<string>("ALL");

  const filteredIssues = useMemo(() => {
    return issues.filter((issue) => {
      if (filterSeverity !== "ALL" && issue.severity !== filterSeverity)
        return false;
      if (filterCategory !== "ALL" && issue.category !== filterCategory)
        return false;
      return true;
    });
  }, [issues, filterSeverity, filterCategory]);

  const severityCounts = useMemo(() => {
    const counts: Record<string, number> = {
      CRITICAL: 0,
      HIGH: 0,
      MEDIUM: 0,
      LOW: 0,
    };
    issues.forEach((i) => counts[i.severity]++);
    return counts;
  }, [issues]);

  if (issues.length === 0) {
    return (
      <div
        style={{
          padding: "32px",
          textAlign: "center",
          background: "white",
          borderRadius: "8px",
          boxShadow: "0 1px 4px rgba(0,0,0,0.05)",
        }}
      >
        <div style={{ fontSize: "48px", marginBottom: "16px" }}>*</div>
        <div style={{ color: "#4CAF50", fontWeight: "bold" }}>
          이슈가 없습니다
        </div>
        <div style={{ color: "#666", fontSize: "14px", marginTop: "8px" }}>
          모든 데이터 품질 검사를 통과했습니다
        </div>
      </div>
    );
  }

  return (
    <div
      style={{
        background: "white",
        borderRadius: "8px",
        boxShadow: "0 1px 4px rgba(0,0,0,0.05)",
        overflow: "hidden",
      }}
    >
      {/* 심각도 요약 */}
      <div
        style={{
          display: "flex",
          gap: "12px",
          padding: "16px",
          background: "#f5f5f5",
          borderBottom: "1px solid #e0e0e0",
        }}
      >
        {Object.entries(severityCounts).map(([severity, count]) => (
          <div
            key={severity}
            onClick={() =>
              setFilterSeverity(filterSeverity === severity ? "ALL" : severity)
            }
            style={{
              padding: "8px 16px",
              borderRadius: "8px",
              background:
                filterSeverity === severity
                  ? SEVERITY_COLORS[severity as keyof typeof SEVERITY_COLORS]
                  : "white",
              color: filterSeverity === severity ? "white" : "#333",
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              gap: "8px",
              border: `1px solid ${SEVERITY_COLORS[severity as keyof typeof SEVERITY_COLORS]}`,
            }}
          >
            <span style={{ fontWeight: "bold" }}>{count}</span>
            <span style={{ fontSize: "12px" }}>{severity}</span>
          </div>
        ))}
      </div>

      {/* 필터 */}
      <div
        style={{
          display: "flex",
          gap: "12px",
          padding: "12px 16px",
          borderBottom: "1px solid #e0e0e0",
        }}
      >
        <select
          value={filterCategory}
          onChange={(e) => setFilterCategory(e.target.value)}
          style={{
            padding: "6px 12px",
            borderRadius: "4px",
            border: "1px solid #ccc",
          }}
        >
          <option value="ALL">전체 카테고리</option>
          {Object.entries(CATEGORY_LABELS).map(([key, val]) => (
            <option key={key} value={key}>
              {val.label}
            </option>
          ))}
        </select>
        <span style={{ fontSize: "13px", color: "#666", alignSelf: "center" }}>
          {filteredIssues.length}건 표시
        </span>
      </div>

      {/* 이슈 목록 */}
      <div style={{ maxHeight: "400px", overflow: "auto" }}>
        {filteredIssues.map((issue) => {
          const categoryConfig = CATEGORY_LABELS[issue.category] || {
            label: issue.category,
            icon: "[?]",
          };
          const severityColor = SEVERITY_COLORS[issue.severity];

          return (
            <div
              key={issue.id}
              onClick={() => onIssueClick?.(issue.id)}
              style={{
                padding: "16px",
                borderBottom: "1px solid #f0f0f0",
                cursor: onIssueClick ? "pointer" : "default",
                borderLeft: `4px solid ${severityColor}`,
              }}
            >
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "flex-start",
                }}
              >
                <div style={{ flex: 1 }}>
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: "8px",
                      marginBottom: "8px",
                    }}
                  >
                    <span
                      style={{
                        padding: "2px 8px",
                        borderRadius: "4px",
                        background: severityColor,
                        color: "white",
                        fontSize: "11px",
                        fontWeight: "bold",
                      }}
                    >
                      {issue.severity}
                    </span>
                    <span
                      style={{
                        padding: "2px 8px",
                        borderRadius: "4px",
                        background: "#e0e0e0",
                        fontSize: "11px",
                      }}
                    >
                      {categoryConfig.icon} {categoryConfig.label}
                    </span>
                    <span style={{ fontSize: "12px", color: "#666" }}>
                      {issue.entityName}
                    </span>
                    {issue.fieldName && (
                      <span style={{ fontSize: "12px", color: "#999" }}>
                        / {issue.fieldName}
                      </span>
                    )}
                  </div>
                  <div style={{ fontSize: "14px", marginBottom: "4px" }}>
                    {issue.description}
                  </div>
                  <div style={{ fontSize: "12px", color: "#666" }}>
                    영향 레코드: {issue.affectedRecords.toLocaleString()}건 |
                    감지: {new Date(issue.detectedAt).toLocaleString("ko-KR")}
                  </div>
                </div>
              </div>
              {issue.suggestedAction && (
                <div
                  style={{
                    marginTop: "8px",
                    padding: "8px 12px",
                    background: "#f5f5f5",
                    borderRadius: "4px",
                    fontSize: "12px",
                    color: "#666",
                  }}
                >
                  권장: {issue.suggestedAction}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

// 권장 조치 패널 컴포넌트
const RecommendationPanel: React.FC<{
  recommendations: Recommendation[];
  onAction?: (recommendationId: string) => void;
}> = ({ recommendations, onAction }) => {
  if (recommendations.length === 0) {
    return (
      <div
        style={{
          padding: "32px",
          textAlign: "center",
          background: "white",
          borderRadius: "8px",
          boxShadow: "0 1px 4px rgba(0,0,0,0.05)",
        }}
      >
        <div style={{ color: "#666" }}>권장 조치가 없습니다</div>
      </div>
    );
  }

  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit, minmax(350px, 1fr))",
        gap: "16px",
      }}
    >
      {recommendations.map((rec) => {
        const typeConfig = TYPE_LABELS[rec.type] || {
          label: rec.type,
          color: "#666",
        };
        const priorityColor = PRIORITY_COLORS[rec.priority];

        return (
          <div
            key={rec.id}
            style={{
              padding: "20px",
              background: "white",
              borderRadius: "8px",
              boxShadow: "0 1px 4px rgba(0,0,0,0.05)",
              borderTop: `4px solid ${priorityColor}`,
            }}
          >
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                marginBottom: "12px",
              }}
            >
              <div style={{ display: "flex", gap: "8px" }}>
                <span
                  style={{
                    padding: "2px 8px",
                    borderRadius: "4px",
                    background: priorityColor,
                    color: "white",
                    fontSize: "11px",
                    fontWeight: "bold",
                  }}
                >
                  {rec.priority}
                </span>
                <span
                  style={{
                    padding: "2px 8px",
                    borderRadius: "4px",
                    background: typeConfig.color,
                    color: "white",
                    fontSize: "11px",
                  }}
                >
                  {typeConfig.label}
                </span>
              </div>
              <span
                style={{
                  padding: "2px 8px",
                  borderRadius: "4px",
                  background: "#e0e0e0",
                  fontSize: "11px",
                }}
              >
                노력: {rec.effort}
              </span>
            </div>

            <h4 style={{ margin: "0 0 8px 0", fontSize: "15px" }}>
              {rec.title}
            </h4>
            <p
              style={{
                margin: "0 0 12px 0",
                fontSize: "13px",
                color: "#666",
                lineHeight: 1.5,
              }}
            >
              {rec.description}
            </p>

            <div
              style={{
                padding: "10px 12px",
                background: "#f0f7ff",
                borderRadius: "4px",
                marginBottom: "12px",
              }}
            >
              <div
                style={{ fontSize: "11px", color: "#666", marginBottom: "4px" }}
              >
                예상 효과
              </div>
              <div style={{ fontSize: "13px", color: "#2196F3" }}>
                {rec.expectedImpact}
              </div>
            </div>

            {rec.relatedIssues && rec.relatedIssues.length > 0 && (
              <div
                style={{
                  fontSize: "12px",
                  color: "#999",
                  marginBottom: "12px",
                }}
              >
                관련 이슈: {rec.relatedIssues.length}건
              </div>
            )}

            {onAction && (
              <button
                onClick={() => onAction(rec.id)}
                style={{
                  width: "100%",
                  padding: "10px",
                  background: "#667eea",
                  color: "white",
                  border: "none",
                  borderRadius: "4px",
                  cursor: "pointer",
                  fontWeight: "bold",
                }}
              >
                조치 실행
              </button>
            )}
          </div>
        );
      })}
    </div>
  );
};

// 탭 컴포넌트
const TabNavigation: React.FC<{
  activeTab: string;
  onTabChange: (tabId: string) => void;
  tabs: typeof TAB_ITEMS;
  issueCounts?: { issues: number; recommendations: number };
}> = ({ activeTab, onTabChange, tabs, issueCounts }) => {
  return (
    <div
      style={{
        display: "flex",
        borderBottom: "2px solid #e0e0e0",
        marginBottom: "24px",
        overflowX: "auto",
      }}
    >
      {tabs.map((tab) => {
        const isActive = activeTab === tab.id;
        const count =
          tab.id === "issues"
            ? issueCounts?.issues
            : tab.id === "recommendations"
              ? issueCounts?.recommendations
              : undefined;

        return (
          <button
            key={tab.id}
            onClick={() => onTabChange(tab.id)}
            style={{
              padding: "12px 20px",
              border: "none",
              background: "none",
              cursor: "pointer",
              fontSize: "14px",
              fontWeight: isActive ? "bold" : "normal",
              color: isActive ? "#667eea" : "#666",
              borderBottom: isActive
                ? "2px solid #667eea"
                : "2px solid transparent",
              marginBottom: "-2px",
              whiteSpace: "nowrap",
              display: "flex",
              alignItems: "center",
              gap: "8px",
            }}
          >
            {tab.label}
            {count !== undefined && count > 0 && (
              <span
                style={{
                  padding: "2px 6px",
                  borderRadius: "10px",
                  background: tab.id === "issues" ? "#F44336" : "#FF9800",
                  color: "white",
                  fontSize: "11px",
                }}
              >
                {count}
              </span>
            )}
          </button>
        );
      })}
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
  onIssueClick,
  onRecommendationAction,
  showImpactAnalysis = true,
}) => {
  const [expandedEntities, setExpandedEntities] = useState<Set<string>>(
    new Set(),
  );
  const [filterStatus, setFilterStatus] = useState<"ALL" | "PASS" | "FAIL">(
    "ALL",
  );
  const [sortBy, setSortBy] = useState<"name" | "score" | "records">("name");
  const [activeTab, setActiveTab] = useState<string>("overview");

  // Filter and sort entities
  const filteredEntities = useMemo(() => {
    let entities = [...metrics.entityResults];

    // Filter
    if (filterStatus !== "ALL") {
      entities = entities.filter((e) =>
        filterStatus === "PASS"
          ? e.overallStatus === "PASS"
          : e.overallStatus !== "PASS",
      );
    }

    // Sort
    entities.sort((a, b) => {
      switch (sortBy) {
        case "score":
          const aScore =
            a.metrics.filter((m) => m.status === "PASS").length /
            a.metrics.length;
          const bScore =
            b.metrics.filter((m) => m.status === "PASS").length /
            b.metrics.length;
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
  type MetricSummary = { passed: number; total: number; avgValue: number };
  const metricSummaries = useMemo((): Record<string, MetricSummary> => {
    const summaries: Record<string, MetricSummary> = {};

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
    setExpandedEntities(
      new Set(metrics.entityResults.map((e) => e.entityName)),
    );
  };

  const collapseAll = () => {
    setExpandedEntities(new Set());
  };

  // 이슈 및 권장조치 카운트
  const issueCounts = useMemo(
    () => ({
      issues: metrics.issues?.length || 0,
      recommendations: metrics.recommendations?.length || 0,
    }),
    [metrics.issues, metrics.recommendations],
  );

  // 개요 탭 콘텐츠
  const renderOverviewTab = () => (
    <>
      {/* Metric Summary Cards */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
          gap: "16px",
          marginBottom: "24px",
        }}
      >
        {(Object.entries(metricSummaries) as [string, MetricSummary][]).map(
          ([name, summary]) => {
            const config = METRIC_LABELS[name] || { label: name };
            const passRate = (summary.passed / summary.total) * 100;
            const avgDisplay = name.includes("rate")
              ? `${(summary.avgValue * 100).toFixed(1)}%`
              : summary.avgValue.toFixed(2);

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
                <div
                  style={{
                    fontSize: "12px",
                    color: "#666",
                    marginBottom: "8px",
                  }}
                >
                  {config.label}
                </div>
                <div
                  style={{
                    fontSize: "24px",
                    fontWeight: "bold",
                    marginBottom: "4px",
                  }}
                >
                  {avgDisplay}
                </div>
                <div style={{ fontSize: "12px" }}>
                  <span style={{ color: STATUS_COLORS.PASS }}>
                    {summary.passed}
                  </span>
                  <span style={{ color: "#666" }}> / {summary.total} 통과</span>
                  <span
                    style={{
                      marginLeft: "8px",
                      color:
                        passRate === 100
                          ? STATUS_COLORS.PASS
                          : STATUS_COLORS.WARNING,
                    }}
                  >
                    ({passRate.toFixed(0)}%)
                  </span>
                </div>
              </div>
            );
          },
        )}
      </div>

      {/* 빠른 상태 요약 */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))",
          gap: "16px",
          marginBottom: "24px",
        }}
      >
        {/* 이슈 요약 카드 */}
        <div
          onClick={() => setActiveTab("issues")}
          style={{
            padding: "20px",
            background: "white",
            borderRadius: "8px",
            boxShadow: "0 1px 4px rgba(0,0,0,0.05)",
            cursor: "pointer",
            borderLeft: `4px solid ${issueCounts.issues > 0 ? "#F44336" : "#4CAF50"}`,
          }}
        >
          <div style={{ fontSize: "12px", color: "#666", marginBottom: "8px" }}>
            발견된 이슈
          </div>
          <div
            style={{
              fontSize: "32px",
              fontWeight: "bold",
              color: issueCounts.issues > 0 ? "#F44336" : "#4CAF50",
            }}
          >
            {issueCounts.issues}
          </div>
          <div style={{ fontSize: "12px", color: "#666" }}>
            {issueCounts.issues > 0 ? "조치 필요" : "이슈 없음"}
          </div>
        </div>

        {/* 권장조치 요약 카드 */}
        <div
          onClick={() => setActiveTab("recommendations")}
          style={{
            padding: "20px",
            background: "white",
            borderRadius: "8px",
            boxShadow: "0 1px 4px rgba(0,0,0,0.05)",
            cursor: "pointer",
            borderLeft: `4px solid ${issueCounts.recommendations > 0 ? "#FF9800" : "#4CAF50"}`,
          }}
        >
          <div style={{ fontSize: "12px", color: "#666", marginBottom: "8px" }}>
            권장 조치
          </div>
          <div
            style={{
              fontSize: "32px",
              fontWeight: "bold",
              color: issueCounts.recommendations > 0 ? "#FF9800" : "#4CAF50",
            }}
          >
            {issueCounts.recommendations}
          </div>
          <div style={{ fontSize: "12px", color: "#666" }}>
            {issueCounts.recommendations > 0 ? "개선 가능" : "최적 상태"}
          </div>
        </div>

        {/* 엔터티 상태 요약 카드 */}
        <div
          onClick={() => setActiveTab("entities")}
          style={{
            padding: "20px",
            background: "white",
            borderRadius: "8px",
            boxShadow: "0 1px 4px rgba(0,0,0,0.05)",
            cursor: "pointer",
            borderLeft: `4px solid #2196F3`,
          }}
        >
          <div style={{ fontSize: "12px", color: "#666", marginBottom: "8px" }}>
            엔터티 상태
          </div>
          <div style={{ fontSize: "32px", fontWeight: "bold" }}>
            {metrics.summary.passedEntities}/{metrics.summary.totalEntities}
          </div>
          <div style={{ fontSize: "12px", color: "#666" }}>
            통과 (
            {(
              (metrics.summary.passedEntities / metrics.summary.totalEntities) *
              100
            ).toFixed(0)}
            %)
          </div>
        </div>
      </div>

      {/* 미니 트렌드 (있는 경우) */}
      {metrics.trends && metrics.trends.length > 0 && (
        <div
          onClick={() => setActiveTab("trends")}
          style={{
            padding: "20px",
            background: "white",
            borderRadius: "8px",
            boxShadow: "0 1px 4px rgba(0,0,0,0.05)",
            cursor: "pointer",
            marginBottom: "24px",
          }}
        >
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
            }}
          >
            <div>
              <div
                style={{
                  fontSize: "14px",
                  fontWeight: "bold",
                  marginBottom: "4px",
                }}
              >
                품질 트렌드
              </div>
              <div style={{ fontSize: "12px", color: "#666" }}>
                최근 7일 변화 추이
              </div>
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
              <div style={{ textAlign: "right" }}>
                <div style={{ fontSize: "12px", color: "#666" }}>현재</div>
                <div
                  style={{
                    fontSize: "20px",
                    fontWeight: "bold",
                    color: "#667eea",
                  }}
                >
                  {metrics.trends[
                    metrics.trends.length - 1
                  ].overallScore.toFixed(1)}
                  %
                </div>
              </div>
              <div
                style={{
                  padding: "8px 12px",
                  borderRadius: "4px",
                  background:
                    metrics.trends[metrics.trends.length - 1].overallScore >=
                    metrics.trends[0].overallScore
                      ? "#E8F5E9"
                      : "#FFEBEE",
                  color:
                    metrics.trends[metrics.trends.length - 1].overallScore >=
                    metrics.trends[0].overallScore
                      ? "#4CAF50"
                      : "#F44336",
                  fontWeight: "bold",
                }}
              >
                {metrics.trends[metrics.trends.length - 1].overallScore >=
                metrics.trends[0].overallScore
                  ? "+"
                  : ""}
                {(
                  metrics.trends[metrics.trends.length - 1].overallScore -
                  metrics.trends[0].overallScore
                ).toFixed(1)}
                %
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );

  // 엔터티 탭 콘텐츠
  const renderEntitiesTab = () => (
    <div
      style={{
        background: "white",
        borderRadius: "8px",
        boxShadow: "0 1px 4px rgba(0,0,0,0.05)",
        padding: "20px",
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
            onChange={(e) =>
              setFilterStatus(e.target.value as typeof filterStatus)
            }
            style={{
              padding: "6px 12px",
              borderRadius: "4px",
              border: "1px solid #ccc",
            }}
          >
            <option value="ALL">전체</option>
            <option value="PASS">통과만</option>
            <option value="FAIL">실패만</option>
          </select>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as typeof sortBy)}
            style={{
              padding: "6px 12px",
              borderRadius: "4px",
              border: "1px solid #ccc",
            }}
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
  );

  // 탭별 콘텐츠 렌더링
  const renderTabContent = () => {
    switch (activeTab) {
      case "overview":
        return renderOverviewTab();
      case "entities":
        return renderEntitiesTab();
      case "issues":
        return (
          <IssueList
            issues={metrics.issues || []}
            onIssueClick={onIssueClick}
          />
        );
      case "trends":
        return <TrendChart trends={metrics.trends || []} />;
      case "recommendations":
        return (
          <RecommendationPanel
            recommendations={metrics.recommendations || []}
            onAction={onRecommendationAction}
          />
        );
      case "correlation":
        return showImpactAnalysis && performanceCorrelations.length > 0 ? (
          <CorrelationChart correlations={performanceCorrelations} />
        ) : (
          <div
            style={{
              padding: "32px",
              textAlign: "center",
              background: "white",
              borderRadius: "8px",
              boxShadow: "0 1px 4px rgba(0,0,0,0.05)",
              color: "#666",
            }}
          >
            영향 분석 데이터가 없습니다
          </div>
        );
      default:
        return null;
    }
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

      {/* Tab Navigation */}
      <TabNavigation
        activeTab={activeTab}
        onTabChange={setActiveTab}
        tabs={TAB_ITEMS}
        issueCounts={issueCounts}
      />

      {/* Tab Content */}
      {renderTabContent()}
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
  const passedEntities = entityResults.filter(
    (e) => e.overallStatus === "PASS",
  ).length;
  const overallScore =
    (entityResults.reduce(
      (sum, e) =>
        sum +
        e.metrics.filter((m) => m.status === "PASS").length / e.metrics.length,
      0,
    ) /
      entityResults.length) *
    100;

  // 트렌드 데이터 생성 (최근 7일)
  const trends: QualityTrend[] = Array.from({ length: 7 }, (_, i) => {
    const date = new Date();
    date.setDate(date.getDate() - (6 - i));
    const baseScore = overallScore - 5 + Math.random() * 10;
    return {
      date: date.toISOString(),
      overallScore: Math.min(100, Math.max(0, baseScore + i * 0.5)),
      metricScores: {
        missing_rate: 0.92 + Math.random() * 0.08,
        duplicate_rate: 0.98 + Math.random() * 0.02,
        required_field_rate: 0.85 + Math.random() * 0.15,
        key_match_rate: 0.93 + Math.random() * 0.07,
      },
    };
  });

  // 이슈 데이터 생성
  const issueCategories: QualityIssue["category"][] = [
    "MISSING_DATA",
    "DUPLICATE",
    "INCONSISTENT",
    "STALE",
    "INVALID_FK",
  ];
  const issueSeverities: QualityIssue["severity"][] = [
    "CRITICAL",
    "HIGH",
    "MEDIUM",
    "LOW",
  ];

  const issues: QualityIssue[] = entityResults
    .filter((e) => e.overallStatus !== "PASS")
    .slice(0, 5)
    .map((entity, idx) => {
      const severity = issueSeverities[Math.min(idx, 3)];
      const category = issueCategories[idx % issueCategories.length];
      return {
        id: `issue-${idx + 1}`,
        severity,
        category,
        entityName: entity.entityName,
        fieldName: idx % 2 === 0 ? "employeeId" : undefined,
        description: getIssueDescription(category, entity.entityName),
        affectedRecords: Math.floor(Math.random() * 50) + 5,
        detectedAt: new Date(
          Date.now() - Math.random() * 86400000 * 3,
        ).toISOString(),
        suggestedAction: getIssueSuggestedAction(category),
      };
    });

  // 권장 조치 생성
  const recommendations: Recommendation[] =
    issues.length > 0
      ? [
          {
            id: "rec-1",
            priority: "HIGH",
            type: "DATA_FIX",
            title: "FK 참조 무결성 복구",
            description:
              "assignments 테이블의 employeeId 필드에서 존재하지 않는 직원 ID 참조를 수정합니다.",
            expectedImpact: "KG 쿼리 정확도 15% 향상 예상",
            effort: "MEDIUM",
            relatedIssues: issues
              .filter((i) => i.category === "INVALID_FK")
              .map((i) => i.id),
          },
          {
            id: "rec-2",
            priority: "MEDIUM",
            type: "PROCESS_IMPROVEMENT",
            title: "데이터 입력 검증 강화",
            description:
              "필수 필드 누락을 방지하기 위해 입력 단계에서 유효성 검사를 추가합니다.",
            expectedImpact: "데이터 결측률 50% 감소 예상",
            effort: "LOW",
            relatedIssues: issues
              .filter((i) => i.category === "MISSING_DATA")
              .map((i) => i.id),
          },
          {
            id: "rec-3",
            priority: "LOW",
            type: "MONITORING",
            title: "중복 데이터 모니터링 알림 설정",
            description:
              "중복 레코드 발생 시 실시간 알림을 받을 수 있도록 모니터링 규칙을 설정합니다.",
            expectedImpact: "중복 데이터 조기 발견으로 품질 유지",
            effort: "LOW",
          },
        ]
      : [];

  return {
    generatedAt: new Date().toISOString(),
    dataSource: "data/mock",
    overallScore,
    overallStatus:
      overallScore >= 90
        ? "READY"
        : overallScore >= 70
          ? "WARNING"
          : "NOT_READY",
    summary: {
      totalEntities: entityResults.length,
      totalRecords,
      passedEntities,
      failedEntities: entityResults.length - passedEntities,
      readinessLevel:
        overallScore >= 90
          ? "READY"
          : overallScore >= 70
            ? "WARNING"
            : "NOT_READY",
    },
    entityResults,
    trends,
    issues,
    recommendations,
  };
};

// 이슈 설명 생성 헬퍼
function getIssueDescription(
  category: QualityIssue["category"],
  entityName: string,
): string {
  const descriptions: Record<QualityIssue["category"], string> = {
    MISSING_DATA: `${entityName} 테이블에서 필수 필드 값이 누락된 레코드가 발견되었습니다.`,
    DUPLICATE: `${entityName} 테이블에서 동일한 키를 가진 중복 레코드가 발견되었습니다.`,
    INCONSISTENT: `${entityName} 테이블에서 다른 테이블과 불일치하는 데이터가 발견되었습니다.`,
    STALE: `${entityName} 테이블의 일부 레코드가 30일 이상 업데이트되지 않았습니다.`,
    INVALID_FK: `${entityName} 테이블에서 존재하지 않는 외래 키 참조가 발견되었습니다.`,
  };
  return descriptions[category];
}

// 이슈 권장 조치 생성 헬퍼
function getIssueSuggestedAction(category: QualityIssue["category"]): string {
  const actions: Record<QualityIssue["category"], string> = {
    MISSING_DATA: "데이터 소스를 확인하고 누락된 필드를 채워주세요.",
    DUPLICATE: "중복 레코드를 검토하고 하나만 남기고 삭제하세요.",
    INCONSISTENT: "관련 테이블 간의 데이터 정합성을 검토하세요.",
    STALE: "데이터 갱신 프로세스를 확인하고 필요시 수동 업데이트하세요.",
    INVALID_FK: "참조하는 레코드가 존재하는지 확인하고 수정하세요.",
  };
  return actions[category];
}

export const generateMockPerformanceCorrelations =
  (): PerformanceCorrelation[] => {
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
