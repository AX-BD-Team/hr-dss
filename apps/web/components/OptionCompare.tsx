/**
 * HR DSS - Option Compare Dashboard Component
 *
 * 의사결정 대안 비교 대시보드
 * 3가지 대안의 상세 비교, 영향 분석, 추천 근거 시각화
 */

import React, { useState, useMemo } from "react";

// ============================================================
// Types
// ============================================================

export interface DecisionOption {
  optionId: string;
  optionType: "CONSERVATIVE" | "BALANCED" | "AGGRESSIVE";
  name: string;
  description: string;
  actions: string[];
  estimatedCost: number;
  estimatedBenefit: number;
  riskLevel: "LOW" | "MEDIUM" | "HIGH";
  implementationTime: string;
  prerequisites: string[];
  tradeOffs: string[];
  scores: OptionScores;
  successProbability?: number;
  impactAnalysis?: ImpactAnalysis;
}

export interface OptionScores {
  impact: number;
  feasibility: number;
  risk: number;
  cost: number;
  time: number;
}

export interface ImpactAnalysis {
  baseline: MetricValues;
  projected: MetricValues;
  timeSeriesData?: TimeSeriesPoint[];
}

export interface MetricValues {
  utilization: number;
  cost: number;
  headcount?: number;
  productivity?: number;
}

export interface TimeSeriesPoint {
  week: string;
  baseline: number;
  projected: number;
}

export interface OptionCompareProps {
  options: DecisionOption[];
  recommendation: string;
  recommendationReason: string;
  onSelectOption?: (optionId: string) => void;
  onApprove?: (optionId: string) => void;
  onReject?: () => void;
  selectedOptionId?: string;
  showApprovalButtons?: boolean;
}

// ============================================================
// Constants
// ============================================================

const TYPE_COLORS = {
  CONSERVATIVE: { bg: "#E8F5E9", border: "#4CAF50", text: "#2E7D32" },
  BALANCED: { bg: "#FFF3E0", border: "#FF9800", text: "#E65100" },
  AGGRESSIVE: { bg: "#FFEBEE", border: "#F44336", text: "#C62828" },
};

const TYPE_LABELS = {
  CONSERVATIVE: "보수적",
  BALANCED: "균형",
  AGGRESSIVE: "적극적",
};

const RISK_COLORS = {
  LOW: "#4CAF50",
  MEDIUM: "#FF9800",
  HIGH: "#F44336",
};

const SCORE_LABELS: Record<keyof OptionScores, string> = {
  impact: "영향도",
  feasibility: "실현가능성",
  risk: "리스크",
  cost: "비용",
  time: "소요시간",
};

// ============================================================
// Helper Components
// ============================================================

const ScoreBar: React.FC<{
  label: string;
  value: number;
  maxValue?: number;
  inverse?: boolean;
  color?: string;
}> = ({ label, value, maxValue = 100, inverse = false, color }) => {
  const normalizedValue = (value / maxValue) * 100;
  const barColor = color || (inverse ? (value > 50 ? "#F44336" : "#4CAF50") : (value > 50 ? "#4CAF50" : "#FF9800"));

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
        <span>{label}</span>
        <span style={{ fontWeight: "bold" }}>{value}</span>
      </div>
      <div
        style={{
          height: "6px",
          background: "#e0e0e0",
          borderRadius: "3px",
          overflow: "hidden",
        }}
      >
        <div
          style={{
            height: "100%",
            width: `${normalizedValue}%`,
            background: barColor,
            borderRadius: "3px",
            transition: "width 0.3s ease",
          }}
        />
      </div>
    </div>
  );
};

const RadarChart: React.FC<{
  data: OptionScores;
  color: string;
  size?: number;
}> = ({ data, color, size = 120 }) => {
  const center = size / 2;
  const radius = size * 0.4;
  const labels = Object.keys(data) as (keyof OptionScores)[];
  const angleStep = (2 * Math.PI) / labels.length;

  // Generate polygon points
  const points = labels
    .map((key, i) => {
      const value = data[key] / 100;
      const angle = i * angleStep - Math.PI / 2;
      const x = center + radius * value * Math.cos(angle);
      const y = center + radius * value * Math.sin(angle);
      return `${x},${y}`;
    })
    .join(" ");

  // Generate grid lines
  const gridLevels = [0.25, 0.5, 0.75, 1];

  return (
    <svg width={size} height={size}>
      {/* Grid */}
      {gridLevels.map((level) => (
        <polygon
          key={level}
          points={labels
            .map((_, i) => {
              const angle = i * angleStep - Math.PI / 2;
              const x = center + radius * level * Math.cos(angle);
              const y = center + radius * level * Math.sin(angle);
              return `${x},${y}`;
            })
            .join(" ")}
          fill="none"
          stroke="#e0e0e0"
          strokeWidth="1"
        />
      ))}

      {/* Axes */}
      {labels.map((_, i) => {
        const angle = i * angleStep - Math.PI / 2;
        const x = center + radius * Math.cos(angle);
        const y = center + radius * Math.sin(angle);
        return (
          <line key={i} x1={center} y1={center} x2={x} y2={y} stroke="#e0e0e0" strokeWidth="1" />
        );
      })}

      {/* Data polygon */}
      <polygon points={points} fill={`${color}40`} stroke={color} strokeWidth="2" />

      {/* Labels */}
      {labels.map((key, i) => {
        const angle = i * angleStep - Math.PI / 2;
        const x = center + (radius + 15) * Math.cos(angle);
        const y = center + (radius + 15) * Math.sin(angle);
        return (
          <text
            key={key}
            x={x}
            y={y}
            textAnchor="middle"
            dominantBaseline="middle"
            fontSize="10"
            fill="#666"
          >
            {SCORE_LABELS[key].substring(0, 2)}
          </text>
        );
      })}
    </svg>
  );
};

const OptionCard: React.FC<{
  option: DecisionOption;
  isRecommended: boolean;
  isSelected: boolean;
  onSelect: () => void;
  expanded: boolean;
  onToggleExpand: () => void;
}> = ({ option, isRecommended, isSelected, onSelect, expanded, onToggleExpand }) => {
  const typeStyle = TYPE_COLORS[option.optionType];
  const totalScore = useMemo(() => {
    const weights = { impact: 0.35, feasibility: 0.25, risk: -0.2, cost: -0.1, time: -0.1 };
    return Object.entries(option.scores).reduce(
      (sum, [key, value]) => sum + value * (weights[key as keyof typeof weights] || 0),
      0
    );
  }, [option.scores]);

  return (
    <div
      style={{
        flex: 1,
        minWidth: "280px",
        border: isSelected ? `3px solid ${typeStyle.border}` : "1px solid #e0e0e0",
        borderRadius: "12px",
        overflow: "hidden",
        background: "white",
        boxShadow: isSelected ? "0 4px 12px rgba(0,0,0,0.15)" : "0 1px 4px rgba(0,0,0,0.05)",
        transition: "all 0.2s ease",
      }}
    >
      {/* Header */}
      <div
        style={{
          padding: "16px",
          background: typeStyle.bg,
          borderBottom: `2px solid ${typeStyle.border}`,
        }}
      >
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "flex-start",
            marginBottom: "8px",
          }}
        >
          <span
            style={{
              padding: "4px 10px",
              borderRadius: "12px",
              background: typeStyle.border,
              color: "white",
              fontSize: "11px",
              fontWeight: "bold",
            }}
          >
            {TYPE_LABELS[option.optionType]}
          </span>
          {isRecommended && (
            <span
              style={{
                padding: "4px 8px",
                borderRadius: "4px",
                background: "#2196F3",
                color: "white",
                fontSize: "10px",
                fontWeight: "bold",
              }}
            >
              [추천]
            </span>
          )}
        </div>
        <div style={{ fontWeight: "bold", fontSize: "18px", color: typeStyle.text }}>
          {option.name}
        </div>
        <div style={{ fontSize: "13px", color: "#666", marginTop: "4px" }}>
          {option.description}
        </div>
      </div>

      {/* Scores Summary */}
      <div style={{ padding: "16px" }}>
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginBottom: "16px",
          }}
        >
          <div>
            <div style={{ fontSize: "12px", color: "#666" }}>종합 점수</div>
            <div style={{ fontSize: "28px", fontWeight: "bold" }}>{totalScore.toFixed(0)}</div>
          </div>
          <RadarChart data={option.scores} color={typeStyle.border} size={100} />
        </div>

        {/* Key Metrics */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "1fr 1fr",
            gap: "12px",
            marginBottom: "16px",
          }}
        >
          <div
            style={{
              padding: "10px",
              background: "#f5f5f5",
              borderRadius: "8px",
              textAlign: "center",
            }}
          >
            <div style={{ fontSize: "11px", color: "#666" }}>성공 확률</div>
            <div style={{ fontSize: "20px", fontWeight: "bold" }}>
              {option.successProbability
                ? `${(option.successProbability * 100).toFixed(0)}%`
                : "N/A"}
            </div>
          </div>
          <div
            style={{
              padding: "10px",
              background: "#f5f5f5",
              borderRadius: "8px",
              textAlign: "center",
            }}
          >
            <div style={{ fontSize: "11px", color: "#666" }}>리스크</div>
            <div
              style={{
                fontSize: "16px",
                fontWeight: "bold",
                color: RISK_COLORS[option.riskLevel],
              }}
            >
              {option.riskLevel}
            </div>
          </div>
        </div>

        {/* Cost/Benefit */}
        <div style={{ marginBottom: "16px" }}>
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              fontSize: "13px",
              marginBottom: "4px",
            }}
          >
            <span>예상 비용</span>
            <span style={{ fontWeight: "bold" }}>
              {(option.estimatedCost / 100000000).toFixed(1)}억원
            </span>
          </div>
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              fontSize: "13px",
            }}
          >
            <span>예상 효과</span>
            <span style={{ fontWeight: "bold", color: "#4CAF50" }}>
              {(option.estimatedBenefit / 100000000).toFixed(1)}억원
            </span>
          </div>
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              fontSize: "13px",
              marginTop: "4px",
              paddingTop: "4px",
              borderTop: "1px solid #e0e0e0",
            }}
          >
            <span>ROI</span>
            <span
              style={{
                fontWeight: "bold",
                color:
                  option.estimatedBenefit > option.estimatedCost ? "#4CAF50" : "#F44336",
              }}
            >
              {option.estimatedCost > 0
                ? `${(((option.estimatedBenefit - option.estimatedCost) / option.estimatedCost) * 100).toFixed(0)}%`
                : "N/A"}
            </span>
          </div>
        </div>

        {/* Implementation Time */}
        <div
          style={{
            padding: "10px",
            background: "#E3F2FD",
            borderRadius: "8px",
            textAlign: "center",
            marginBottom: "16px",
          }}
        >
          <div style={{ fontSize: "11px", color: "#666" }}>구현 기간</div>
          <div style={{ fontSize: "16px", fontWeight: "bold" }}>{option.implementationTime}</div>
        </div>

        {/* Expand/Collapse */}
        <button
          onClick={onToggleExpand}
          style={{
            width: "100%",
            padding: "8px",
            border: "1px solid #e0e0e0",
            borderRadius: "4px",
            background: "white",
            cursor: "pointer",
            fontSize: "13px",
          }}
        >
          {expanded ? "상세 정보 접기 [-]" : "상세 정보 보기 [+]"}
        </button>

        {/* Expanded Details */}
        {expanded && (
          <div style={{ marginTop: "16px" }}>
            {/* Actions */}
            <div style={{ marginBottom: "16px" }}>
              <div
                style={{ fontSize: "13px", fontWeight: "bold", marginBottom: "8px" }}
              >
                실행 항목
              </div>
              {option.actions.map((action, idx) => (
                <div
                  key={idx}
                  style={{
                    padding: "8px 12px",
                    background: "#f9f9f9",
                    borderRadius: "4px",
                    marginBottom: "4px",
                    fontSize: "12px",
                    display: "flex",
                    alignItems: "flex-start",
                    gap: "8px",
                  }}
                >
                  <span style={{ color: "#4CAF50" }}>[{idx + 1}]</span>
                  <span>{action}</span>
                </div>
              ))}
            </div>

            {/* Prerequisites */}
            {option.prerequisites.length > 0 && (
              <div style={{ marginBottom: "16px" }}>
                <div
                  style={{ fontSize: "13px", fontWeight: "bold", marginBottom: "8px" }}
                >
                  전제조건
                </div>
                {option.prerequisites.map((prereq, idx) => (
                  <div
                    key={idx}
                    style={{
                      padding: "6px 10px",
                      background: "#FFF3E0",
                      borderRadius: "4px",
                      marginBottom: "4px",
                      fontSize: "12px",
                    }}
                  >
                    [!] {prereq}
                  </div>
                ))}
              </div>
            )}

            {/* Trade-offs */}
            {option.tradeOffs.length > 0 && (
              <div style={{ marginBottom: "16px" }}>
                <div
                  style={{ fontSize: "13px", fontWeight: "bold", marginBottom: "8px" }}
                >
                  트레이드오프
                </div>
                {option.tradeOffs.map((tradeoff, idx) => (
                  <div
                    key={idx}
                    style={{
                      padding: "6px 10px",
                      background: "#FFEBEE",
                      borderRadius: "4px",
                      marginBottom: "4px",
                      fontSize: "12px",
                    }}
                  >
                    [-] {tradeoff}
                  </div>
                ))}
              </div>
            )}

            {/* Detailed Scores */}
            <div>
              <div
                style={{ fontSize: "13px", fontWeight: "bold", marginBottom: "8px" }}
              >
                상세 점수
              </div>
              {Object.entries(option.scores).map(([key, value]) => (
                <ScoreBar
                  key={key}
                  label={SCORE_LABELS[key as keyof OptionScores]}
                  value={value}
                  inverse={key === "risk" || key === "cost" || key === "time"}
                />
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Select Button */}
      <div style={{ padding: "0 16px 16px" }}>
        <button
          onClick={onSelect}
          style={{
            width: "100%",
            padding: "12px",
            border: "none",
            borderRadius: "8px",
            background: isSelected ? typeStyle.border : "#f5f5f5",
            color: isSelected ? "white" : "#333",
            fontWeight: "bold",
            cursor: "pointer",
            fontSize: "14px",
          }}
        >
          {isSelected ? "[V] 선택됨" : "이 대안 선택"}
        </button>
      </div>
    </div>
  );
};

// ============================================================
// Main Component
// ============================================================

export const OptionCompare: React.FC<OptionCompareProps> = ({
  options,
  recommendation,
  recommendationReason,
  onSelectOption,
  onApprove,
  onReject,
  selectedOptionId,
  showApprovalButtons = true,
}) => {
  const [expandedOptions, setExpandedOptions] = useState<Set<string>>(new Set());
  const [localSelectedId, setLocalSelectedId] = useState<string | undefined>(selectedOptionId);

  const handleSelect = (optionId: string) => {
    setLocalSelectedId(optionId);
    onSelectOption?.(optionId);
  };

  const toggleExpand = (optionId: string) => {
    const newExpanded = new Set(expandedOptions);
    if (newExpanded.has(optionId)) {
      newExpanded.delete(optionId);
    } else {
      newExpanded.add(optionId);
    }
    setExpandedOptions(newExpanded);
  };

  const selectedOption = options.find((o) => o.optionId === localSelectedId);

  return (
    <div style={{ padding: "24px" }}>
      {/* Header */}
      <div style={{ marginBottom: "24px" }}>
        <h2 style={{ margin: "0 0 8px 0", fontSize: "24px" }}>대안 비교</h2>
        <p style={{ margin: 0, color: "#666" }}>
          3가지 대안을 비교하고 최적의 의사결정을 선택하세요
        </p>
      </div>

      {/* Recommendation Banner */}
      <div
        style={{
          padding: "16px 20px",
          background: "linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%)",
          borderRadius: "12px",
          marginBottom: "24px",
          border: "1px solid #90CAF9",
        }}
      >
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "12px",
            marginBottom: "8px",
          }}
        >
          <span
            style={{
              width: "32px",
              height: "32px",
              borderRadius: "50%",
              background: "#2196F3",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "white",
              fontWeight: "bold",
            }}
          >
            [R]
          </span>
          <span style={{ fontWeight: "bold", fontSize: "16px" }}>
            추천: {options.find((o) => o.optionId === recommendation)?.name}
          </span>
        </div>
        <p style={{ margin: 0, fontSize: "14px", color: "#1565C0" }}>
          {recommendationReason}
        </p>
      </div>

      {/* Options Grid */}
      <div
        style={{
          display: "flex",
          gap: "20px",
          marginBottom: "24px",
          flexWrap: "wrap",
        }}
      >
        {options.map((option) => (
          <OptionCard
            key={option.optionId}
            option={option}
            isRecommended={option.optionId === recommendation}
            isSelected={option.optionId === localSelectedId}
            onSelect={() => handleSelect(option.optionId)}
            expanded={expandedOptions.has(option.optionId)}
            onToggleExpand={() => toggleExpand(option.optionId)}
          />
        ))}
      </div>

      {/* Approval Section */}
      {showApprovalButtons && (
        <div
          style={{
            padding: "20px",
            background: "#f9f9f9",
            borderRadius: "12px",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <div>
            {selectedOption ? (
              <>
                <div style={{ fontSize: "14px", color: "#666" }}>선택된 대안</div>
                <div style={{ fontWeight: "bold", fontSize: "18px" }}>
                  {selectedOption.name}
                </div>
              </>
            ) : (
              <div style={{ color: "#999" }}>대안을 선택해주세요</div>
            )}
          </div>
          <div style={{ display: "flex", gap: "12px" }}>
            <button
              onClick={onReject}
              style={{
                padding: "12px 24px",
                border: "1px solid #ccc",
                borderRadius: "8px",
                background: "white",
                cursor: "pointer",
                fontSize: "14px",
              }}
            >
              재검토 요청
            </button>
            <button
              onClick={() => localSelectedId && onApprove?.(localSelectedId)}
              disabled={!localSelectedId}
              style={{
                padding: "12px 32px",
                border: "none",
                borderRadius: "8px",
                background: localSelectedId ? "#4CAF50" : "#ccc",
                color: "white",
                fontWeight: "bold",
                cursor: localSelectedId ? "pointer" : "not-allowed",
                fontSize: "14px",
              }}
            >
              승인 및 실행
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

// ============================================================
// Mock Data Generator
// ============================================================

export const generateMockOptions = (): DecisionOption[] => {
  return [
    {
      optionId: "OPT-01",
      optionType: "CONSERVATIVE",
      name: "내부 재배치",
      description: "유휴 인력을 병목 구간으로 재배치하여 해결",
      actions: [
        "유휴 인력 2명 병목 조직으로 임시 배치",
        "비핵심 프로젝트 일정 조정 (2-4주 연기)",
        "크로스 트레이닝을 통한 역량 전환",
      ],
      estimatedCost: 25000000,
      estimatedBenefit: 75000000,
      riskLevel: "LOW",
      implementationTime: "2-4주",
      prerequisites: ["유휴 인력 존재", "역량 전환 가능성"],
      tradeOffs: ["원래 프로젝트 일정 지연 가능", "재배치 인력의 생산성 저하"],
      scores: { impact: 65, feasibility: 85, risk: 25, cost: 30, time: 20 },
      successProbability: 0.78,
    },
    {
      optionId: "OPT-02",
      optionType: "BALANCED",
      name: "외부 인력 활용",
      description: "외주/파견 인력을 활용하여 단기 병목 해소",
      actions: [
        "외주 인력 3명 투입 (3개월 계약)",
        "내부 핵심 인력은 기술 리드 역할 유지",
        "지식 이전 계획 수립",
      ],
      estimatedCost: 100000000,
      estimatedBenefit: 125000000,
      riskLevel: "MEDIUM",
      implementationTime: "4-6주",
      prerequisites: ["예산 확보", "외주사 풀 존재"],
      tradeOffs: ["비용 증가", "품질 관리 필요", "보안/지적재산권 이슈"],
      scores: { impact: 80, feasibility: 70, risk: 45, cost: 60, time: 40 },
      successProbability: 0.72,
    },
    {
      optionId: "OPT-03",
      optionType: "AGGRESSIVE",
      name: "정규직 채용",
      description: "병목 해소를 위한 정규직 채용 진행",
      actions: [
        "정규직 4명 채용 (역량 갭 고려)",
        "채용 파이프라인 구축 및 JD 작성",
        "온보딩 프로그램 준비",
      ],
      estimatedCost: 400000000,
      estimatedBenefit: 250000000,
      riskLevel: "HIGH",
      implementationTime: "8-12주",
      prerequisites: ["채용 승인", "인력 계획 반영"],
      tradeOffs: ["채용까지 시간 소요", "고정비 증가", "인력 적합성 리스크"],
      scores: { impact: 95, feasibility: 50, risk: 65, cost: 80, time: 70 },
      successProbability: 0.58,
    },
  ];
};

export default OptionCompare;
