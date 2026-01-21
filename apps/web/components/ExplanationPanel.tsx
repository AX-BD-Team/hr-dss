/**
 * HR DSS - Explanation Panel Component
 *
 * 의사결정 근거, 추론 경로, 가정 설명 패널
 * KG 뷰, Evidence 링크, 추론 체인 시각화
 */

import React, { useState, useMemo } from "react";

// ============================================================
// Types
// ============================================================

export interface ExplanationData {
  decisionId: string;
  query: string;
  queryType: string;
  selectedOption?: SelectedOptionInfo;
  reasoningChain: ReasoningStep[];
  evidenceList: Evidence[];
  assumptions: Assumption[];
  validationResult: ValidationSummary;
  kgContext?: KGContext;
}

export interface SelectedOptionInfo {
  optionId: string;
  name: string;
  type: string;
  rationale: string;
}

export interface ReasoningStep {
  stepId: string;
  stepNumber: number;
  type: "QUERY_ANALYSIS" | "DATA_RETRIEVAL" | "OPTION_GENERATION" | "IMPACT_ANALYSIS" | "VALIDATION";
  title: string;
  description: string;
  input: string;
  output: string;
  confidence: number;
  duration: number;
  evidenceRefs: string[];
}

export interface Evidence {
  evidenceId: string;
  type: "KG_NODE" | "KG_RELATIONSHIP" | "DATA_RECORD" | "CALCULATION" | "RULE";
  source: string;
  content: string;
  confidence: number;
  timestamp: string;
  linkedClaims: string[];
}

export interface Assumption {
  assumptionId: string;
  category: "DATA" | "MODEL" | "BUSINESS" | "CONSTRAINT";
  statement: string;
  basis: string;
  impact: "HIGH" | "MEDIUM" | "LOW";
  isVerifiable: boolean;
}

export interface ValidationSummary {
  isValid: boolean;
  evidenceCoverage: number;
  hallucinationRisk: number;
  unverifiedClaims: UnverifiedClaim[];
  confidenceScore: number;
}

export interface UnverifiedClaim {
  claimId: string;
  text: string;
  reason: string;
}

export interface KGContext {
  centerNode: KGNode;
  relatedNodes: KGNode[];
  relationships: KGRelationship[];
}

export interface KGNode {
  nodeId: string;
  type: string;
  label: string;
  properties: Record<string, unknown>;
}

export interface KGRelationship {
  from: string;
  to: string;
  type: string;
  properties?: Record<string, unknown>;
}

export interface ExplanationPanelProps {
  data: ExplanationData;
  onEvidenceClick?: (evidenceId: string) => void;
  onNodeClick?: (nodeId: string) => void;
  defaultTab?: TabType;
}

type TabType = "reasoning" | "evidence" | "assumptions" | "validation" | "kg";

// ============================================================
// Constants
// ============================================================

const TAB_CONFIG: Record<TabType, { label: string; icon: string }> = {
  reasoning: { label: "추론 경로", icon: "[>]" },
  evidence: { label: "근거", icon: "[E]" },
  assumptions: { label: "가정", icon: "[A]" },
  validation: { label: "검증", icon: "[V]" },
  kg: { label: "KG 뷰", icon: "[G]" },
};

const STEP_TYPE_COLORS: Record<ReasoningStep["type"], string> = {
  QUERY_ANALYSIS: "#9C27B0",
  DATA_RETRIEVAL: "#2196F3",
  OPTION_GENERATION: "#FF9800",
  IMPACT_ANALYSIS: "#4CAF50",
  VALIDATION: "#F44336",
};

const EVIDENCE_TYPE_ICONS: Record<Evidence["type"], string> = {
  KG_NODE: "[N]",
  KG_RELATIONSHIP: "[R]",
  DATA_RECORD: "[D]",
  CALCULATION: "[C]",
  RULE: "[L]",
};

const ASSUMPTION_COLORS: Record<Assumption["impact"], string> = {
  HIGH: "#F44336",
  MEDIUM: "#FF9800",
  LOW: "#4CAF50",
};

// ============================================================
// Helper Components
// ============================================================

const ConfidenceBadge: React.FC<{ confidence: number }> = ({ confidence }) => {
  const color =
    confidence >= 0.8 ? "#4CAF50" : confidence >= 0.6 ? "#FF9800" : "#F44336";

  return (
    <span
      style={{
        padding: "2px 8px",
        borderRadius: "12px",
        background: `${color}20`,
        color: color,
        fontSize: "11px",
        fontWeight: "bold",
      }}
    >
      {(confidence * 100).toFixed(0)}%
    </span>
  );
};

const ReasoningChain: React.FC<{
  steps: ReasoningStep[];
  onEvidenceClick?: (evidenceId: string) => void;
}> = ({ steps, onEvidenceClick }) => {
  const [expandedSteps, setExpandedSteps] = useState<Set<string>>(new Set());

  const toggleStep = (stepId: string) => {
    const newExpanded = new Set(expandedSteps);
    if (newExpanded.has(stepId)) {
      newExpanded.delete(stepId);
    } else {
      newExpanded.add(stepId);
    }
    setExpandedSteps(newExpanded);
  };

  return (
    <div>
      {steps.map((step, idx) => {
        const isExpanded = expandedSteps.has(step.stepId);
        const color = STEP_TYPE_COLORS[step.type];

        return (
          <div key={step.stepId} style={{ marginBottom: "12px" }}>
            {/* Connector Line */}
            {idx > 0 && (
              <div
                style={{
                  width: "2px",
                  height: "20px",
                  background: "#e0e0e0",
                  marginLeft: "19px",
                }}
              />
            )}

            {/* Step Card */}
            <div
              style={{
                display: "flex",
                gap: "12px",
                padding: "12px",
                background: "white",
                border: "1px solid #e0e0e0",
                borderRadius: "8px",
                borderLeft: `4px solid ${color}`,
              }}
            >
              {/* Step Number */}
              <div
                style={{
                  width: "40px",
                  height: "40px",
                  borderRadius: "50%",
                  background: color,
                  color: "white",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontWeight: "bold",
                  flexShrink: 0,
                }}
              >
                {step.stepNumber}
              </div>

              {/* Content */}
              <div style={{ flex: 1 }}>
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "flex-start",
                    marginBottom: "4px",
                  }}
                >
                  <div>
                    <div style={{ fontWeight: "bold", fontSize: "14px" }}>{step.title}</div>
                    <div style={{ fontSize: "11px", color: "#666" }}>{step.type}</div>
                  </div>
                  <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
                    <ConfidenceBadge confidence={step.confidence} />
                    <span style={{ fontSize: "11px", color: "#999" }}>
                      {step.duration}ms
                    </span>
                  </div>
                </div>

                <p style={{ margin: "8px 0", fontSize: "13px", color: "#333" }}>
                  {step.description}
                </p>

                {/* Expand/Collapse */}
                <button
                  onClick={() => toggleStep(step.stepId)}
                  style={{
                    background: "none",
                    border: "none",
                    color: "#2196F3",
                    cursor: "pointer",
                    fontSize: "12px",
                    padding: 0,
                  }}
                >
                  {isExpanded ? "상세 접기 [-]" : "상세 보기 [+]"}
                </button>

                {/* Expanded Details */}
                {isExpanded && (
                  <div
                    style={{
                      marginTop: "12px",
                      padding: "12px",
                      background: "#f9f9f9",
                      borderRadius: "4px",
                    }}
                  >
                    <div style={{ marginBottom: "8px" }}>
                      <div style={{ fontSize: "11px", fontWeight: "bold", color: "#666" }}>
                        입력
                      </div>
                      <div style={{ fontSize: "12px", fontFamily: "monospace" }}>
                        {step.input}
                      </div>
                    </div>
                    <div style={{ marginBottom: "8px" }}>
                      <div style={{ fontSize: "11px", fontWeight: "bold", color: "#666" }}>
                        출력
                      </div>
                      <div style={{ fontSize: "12px", fontFamily: "monospace" }}>
                        {step.output}
                      </div>
                    </div>
                    {step.evidenceRefs.length > 0 && (
                      <div>
                        <div style={{ fontSize: "11px", fontWeight: "bold", color: "#666" }}>
                          참조 근거
                        </div>
                        <div style={{ display: "flex", gap: "4px", flexWrap: "wrap" }}>
                          {step.evidenceRefs.map((ref) => (
                            <button
                              key={ref}
                              onClick={() => onEvidenceClick?.(ref)}
                              style={{
                                padding: "2px 8px",
                                background: "#E3F2FD",
                                border: "none",
                                borderRadius: "4px",
                                fontSize: "11px",
                                cursor: "pointer",
                              }}
                            >
                              {ref}
                            </button>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};

const EvidenceList: React.FC<{
  evidence: Evidence[];
  onEvidenceClick?: (evidenceId: string) => void;
}> = ({ evidence, onEvidenceClick }) => {
  const groupedEvidence = useMemo(() => {
    const groups: Record<Evidence["type"], Evidence[]> = {
      KG_NODE: [],
      KG_RELATIONSHIP: [],
      DATA_RECORD: [],
      CALCULATION: [],
      RULE: [],
    };
    evidence.forEach((e) => groups[e.type].push(e));
    return groups;
  }, [evidence]);

  return (
    <div>
      {Object.entries(groupedEvidence).map(
        ([type, items]) =>
          items.length > 0 && (
            <div key={type} style={{ marginBottom: "20px" }}>
              <div
                style={{
                  fontSize: "14px",
                  fontWeight: "bold",
                  marginBottom: "12px",
                  display: "flex",
                  alignItems: "center",
                  gap: "8px",
                }}
              >
                <span style={{ color: "#2196F3" }}>
                  {EVIDENCE_TYPE_ICONS[type as Evidence["type"]]}
                </span>
                {type.replace("_", " ")} ({items.length})
              </div>
              {items.map((item) => (
                <div
                  key={item.evidenceId}
                  onClick={() => onEvidenceClick?.(item.evidenceId)}
                  style={{
                    padding: "12px",
                    background: "white",
                    border: "1px solid #e0e0e0",
                    borderRadius: "8px",
                    marginBottom: "8px",
                    cursor: "pointer",
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
                    <span style={{ fontWeight: "bold", fontSize: "13px" }}>
                      {item.evidenceId}
                    </span>
                    <ConfidenceBadge confidence={item.confidence} />
                  </div>
                  <div style={{ fontSize: "12px", color: "#666", marginBottom: "4px" }}>
                    출처: {item.source}
                  </div>
                  <div style={{ fontSize: "13px" }}>{item.content}</div>
                  {item.linkedClaims.length > 0 && (
                    <div style={{ marginTop: "8px", fontSize: "11px", color: "#999" }}>
                      연결된 주장: {item.linkedClaims.join(", ")}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )
      )}
    </div>
  );
};

const AssumptionsList: React.FC<{
  assumptions: Assumption[];
}> = ({ assumptions }) => {
  const groupedAssumptions = useMemo(() => {
    const groups: Record<Assumption["category"], Assumption[]> = {
      DATA: [],
      MODEL: [],
      BUSINESS: [],
      CONSTRAINT: [],
    };
    assumptions.forEach((a) => groups[a.category].push(a));
    return groups;
  }, [assumptions]);

  const categoryLabels: Record<Assumption["category"], string> = {
    DATA: "데이터 가정",
    MODEL: "모델 가정",
    BUSINESS: "비즈니스 가정",
    CONSTRAINT: "제약 조건",
  };

  return (
    <div>
      {Object.entries(groupedAssumptions).map(
        ([category, items]) =>
          items.length > 0 && (
            <div key={category} style={{ marginBottom: "20px" }}>
              <div
                style={{
                  fontSize: "14px",
                  fontWeight: "bold",
                  marginBottom: "12px",
                }}
              >
                {categoryLabels[category as Assumption["category"]]} ({items.length})
              </div>
              {items.map((item) => (
                <div
                  key={item.assumptionId}
                  style={{
                    padding: "12px",
                    background: "white",
                    border: "1px solid #e0e0e0",
                    borderRadius: "8px",
                    marginBottom: "8px",
                    borderLeft: `4px solid ${ASSUMPTION_COLORS[item.impact]}`,
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
                    <div style={{ fontWeight: "500", fontSize: "13px" }}>
                      {item.statement}
                    </div>
                    <div style={{ display: "flex", gap: "4px" }}>
                      <span
                        style={{
                          padding: "2px 6px",
                          borderRadius: "4px",
                          background: ASSUMPTION_COLORS[item.impact],
                          color: "white",
                          fontSize: "10px",
                        }}
                      >
                        {item.impact}
                      </span>
                      {item.isVerifiable && (
                        <span
                          style={{
                            padding: "2px 6px",
                            borderRadius: "4px",
                            background: "#E3F2FD",
                            color: "#2196F3",
                            fontSize: "10px",
                          }}
                        >
                          검증가능
                        </span>
                      )}
                    </div>
                  </div>
                  <div style={{ fontSize: "12px", color: "#666" }}>
                    근거: {item.basis}
                  </div>
                </div>
              ))}
            </div>
          )
      )}
    </div>
  );
};

const ValidationPanel: React.FC<{
  validation: ValidationSummary;
}> = ({ validation }) => {
  return (
    <div>
      {/* Summary Cards */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))",
          gap: "16px",
          marginBottom: "24px",
        }}
      >
        <div
          style={{
            padding: "16px",
            background: validation.isValid ? "#E8F5E9" : "#FFEBEE",
            borderRadius: "8px",
            textAlign: "center",
          }}
        >
          <div style={{ fontSize: "24px", marginBottom: "4px" }}>
            {validation.isValid ? "[V]" : "[X]"}
          </div>
          <div style={{ fontSize: "12px", color: "#666" }}>검증 상태</div>
          <div
            style={{
              fontWeight: "bold",
              color: validation.isValid ? "#4CAF50" : "#F44336",
            }}
          >
            {validation.isValid ? "통과" : "미통과"}
          </div>
        </div>

        <div
          style={{
            padding: "16px",
            background: "#f5f5f5",
            borderRadius: "8px",
            textAlign: "center",
          }}
        >
          <div
            style={{
              fontSize: "24px",
              fontWeight: "bold",
              color:
                validation.evidenceCoverage >= 0.95 ? "#4CAF50" : "#FF9800",
            }}
          >
            {(validation.evidenceCoverage * 100).toFixed(0)}%
          </div>
          <div style={{ fontSize: "12px", color: "#666" }}>근거 연결률</div>
        </div>

        <div
          style={{
            padding: "16px",
            background: "#f5f5f5",
            borderRadius: "8px",
            textAlign: "center",
          }}
        >
          <div
            style={{
              fontSize: "24px",
              fontWeight: "bold",
              color: validation.hallucinationRisk <= 0.05 ? "#4CAF50" : "#F44336",
            }}
          >
            {(validation.hallucinationRisk * 100).toFixed(1)}%
          </div>
          <div style={{ fontSize: "12px", color: "#666" }}>환각 위험도</div>
        </div>

        <div
          style={{
            padding: "16px",
            background: "#f5f5f5",
            borderRadius: "8px",
            textAlign: "center",
          }}
        >
          <div
            style={{
              fontSize: "24px",
              fontWeight: "bold",
              color: validation.confidenceScore >= 0.8 ? "#4CAF50" : "#FF9800",
            }}
          >
            {(validation.confidenceScore * 100).toFixed(0)}%
          </div>
          <div style={{ fontSize: "12px", color: "#666" }}>신뢰도</div>
        </div>
      </div>

      {/* Unverified Claims */}
      {validation.unverifiedClaims.length > 0 && (
        <div>
          <div
            style={{
              fontSize: "14px",
              fontWeight: "bold",
              marginBottom: "12px",
              color: "#F44336",
            }}
          >
            [!] 미검증 주장 ({validation.unverifiedClaims.length})
          </div>
          {validation.unverifiedClaims.map((claim) => (
            <div
              key={claim.claimId}
              style={{
                padding: "12px",
                background: "#FFEBEE",
                borderRadius: "8px",
                marginBottom: "8px",
                borderLeft: "4px solid #F44336",
              }}
            >
              <div style={{ fontWeight: "500", fontSize: "13px", marginBottom: "4px" }}>
                {claim.text}
              </div>
              <div style={{ fontSize: "12px", color: "#666" }}>
                사유: {claim.reason}
              </div>
            </div>
          ))}
        </div>
      )}

      {validation.unverifiedClaims.length === 0 && (
        <div
          style={{
            padding: "24px",
            background: "#E8F5E9",
            borderRadius: "8px",
            textAlign: "center",
          }}
        >
          <div style={{ fontSize: "24px", marginBottom: "8px" }}>[OK]</div>
          <div style={{ color: "#4CAF50", fontWeight: "bold" }}>
            모든 주장이 근거와 연결되었습니다
          </div>
        </div>
      )}
    </div>
  );
};

const SimpleKGView: React.FC<{
  context: KGContext;
  onNodeClick?: (nodeId: string) => void;
}> = ({ context, onNodeClick }) => {
  return (
    <div>
      {/* Center Node */}
      <div
        style={{
          padding: "16px",
          background: "#E3F2FD",
          borderRadius: "8px",
          marginBottom: "16px",
          textAlign: "center",
        }}
      >
        <div style={{ fontSize: "12px", color: "#666", marginBottom: "4px" }}>
          중심 노드
        </div>
        <div
          style={{
            fontWeight: "bold",
            fontSize: "16px",
            cursor: "pointer",
          }}
          onClick={() => onNodeClick?.(context.centerNode.nodeId)}
        >
          [{context.centerNode.type}] {context.centerNode.label}
        </div>
      </div>

      {/* Relationships */}
      <div style={{ marginBottom: "16px" }}>
        <div style={{ fontWeight: "bold", marginBottom: "8px" }}>
          관계 ({context.relationships.length})
        </div>
        {context.relationships.map((rel, idx) => (
          <div
            key={idx}
            style={{
              display: "flex",
              alignItems: "center",
              gap: "8px",
              padding: "8px",
              background: "#f5f5f5",
              borderRadius: "4px",
              marginBottom: "4px",
              fontSize: "12px",
            }}
          >
            <span
              style={{ cursor: "pointer", color: "#2196F3" }}
              onClick={() => onNodeClick?.(rel.from)}
            >
              {rel.from}
            </span>
            <span style={{ color: "#999" }}>--[{rel.type}]--&gt;</span>
            <span
              style={{ cursor: "pointer", color: "#2196F3" }}
              onClick={() => onNodeClick?.(rel.to)}
            >
              {rel.to}
            </span>
          </div>
        ))}
      </div>

      {/* Related Nodes */}
      <div>
        <div style={{ fontWeight: "bold", marginBottom: "8px" }}>
          연관 노드 ({context.relatedNodes.length})
        </div>
        <div style={{ display: "flex", flexWrap: "wrap", gap: "8px" }}>
          {context.relatedNodes.map((node) => (
            <div
              key={node.nodeId}
              onClick={() => onNodeClick?.(node.nodeId)}
              style={{
                padding: "8px 12px",
                background: "#f5f5f5",
                borderRadius: "16px",
                fontSize: "12px",
                cursor: "pointer",
              }}
            >
              <span style={{ color: "#666" }}>[{node.type.substring(0, 2)}]</span>{" "}
              {node.label}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// ============================================================
// Main Component
// ============================================================

export const ExplanationPanel: React.FC<ExplanationPanelProps> = ({
  data,
  onEvidenceClick,
  onNodeClick,
  defaultTab = "reasoning",
}) => {
  const [activeTab, setActiveTab] = useState<TabType>(defaultTab);

  return (
    <div
      style={{
        background: "white",
        borderRadius: "12px",
        boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
        overflow: "hidden",
      }}
    >
      {/* Header */}
      <div
        style={{
          padding: "16px 20px",
          background: "#f5f5f5",
          borderBottom: "1px solid #e0e0e0",
        }}
      >
        <div style={{ fontWeight: "bold", fontSize: "18px", marginBottom: "4px" }}>
          의사결정 설명
        </div>
        <div style={{ fontSize: "12px", color: "#666" }}>
          {data.queryType} | {data.decisionId}
        </div>
        {data.selectedOption && (
          <div
            style={{
              marginTop: "12px",
              padding: "12px",
              background: "#E3F2FD",
              borderRadius: "8px",
            }}
          >
            <div style={{ fontSize: "12px", color: "#666" }}>선택된 대안</div>
            <div style={{ fontWeight: "bold" }}>{data.selectedOption.name}</div>
            <div style={{ fontSize: "13px", marginTop: "4px" }}>
              {data.selectedOption.rationale}
            </div>
          </div>
        )}
      </div>

      {/* Tabs */}
      <div
        style={{
          display: "flex",
          borderBottom: "1px solid #e0e0e0",
          background: "#fafafa",
        }}
      >
        {(Object.keys(TAB_CONFIG) as TabType[]).map((tab) => {
          const config = TAB_CONFIG[tab];
          const isActive = activeTab === tab;

          // Skip KG tab if no context
          if (tab === "kg" && !data.kgContext) return null;

          return (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              style={{
                flex: 1,
                padding: "12px",
                border: "none",
                borderBottom: isActive ? "2px solid #2196F3" : "2px solid transparent",
                background: isActive ? "white" : "transparent",
                color: isActive ? "#2196F3" : "#666",
                fontWeight: isActive ? "bold" : "normal",
                cursor: "pointer",
                fontSize: "13px",
              }}
            >
              <span style={{ marginRight: "4px" }}>{config.icon}</span>
              {config.label}
            </button>
          );
        })}
      </div>

      {/* Content */}
      <div style={{ padding: "20px", background: "#fafafa", minHeight: "400px" }}>
        {activeTab === "reasoning" && (
          <ReasoningChain steps={data.reasoningChain} onEvidenceClick={onEvidenceClick} />
        )}

        {activeTab === "evidence" && (
          <EvidenceList evidence={data.evidenceList} onEvidenceClick={onEvidenceClick} />
        )}

        {activeTab === "assumptions" && (
          <AssumptionsList assumptions={data.assumptions} />
        )}

        {activeTab === "validation" && (
          <ValidationPanel validation={data.validationResult} />
        )}

        {activeTab === "kg" && data.kgContext && (
          <SimpleKGView context={data.kgContext} onNodeClick={onNodeClick} />
        )}
      </div>
    </div>
  );
};

// ============================================================
// Mock Data Generator
// ============================================================

export const generateMockExplanationData = (): ExplanationData => {
  return {
    decisionId: "DEC-2025-001",
    query: "향후 12주간 AI팀의 가동률 병목 구간과 해결 방안은?",
    queryType: "CAPACITY",
    selectedOption: {
      optionId: "OPT-02",
      name: "외부 인력 활용",
      type: "BALANCED",
      rationale: "비용 대비 효과가 적절하고 리스크가 관리 가능한 수준임",
    },
    reasoningChain: [
      {
        stepId: "RS-01",
        stepNumber: 1,
        type: "QUERY_ANALYSIS",
        title: "질문 분석",
        description: "사용자 질문을 분석하여 CAPACITY 유형으로 분류하고 하위 쿼리로 분해",
        input: "향후 12주간 AI팀의 가동률 병목 구간과 해결 방안은?",
        output: "queryType: CAPACITY, subQueries: [utilization, forecast, bottleneck]",
        confidence: 0.95,
        duration: 120,
        evidenceRefs: [],
      },
      {
        stepId: "RS-02",
        stepNumber: 2,
        type: "DATA_RETRIEVAL",
        title: "KG 데이터 조회",
        description: "AI팀의 현재 가동률, 배치 현황, 프로젝트 일정 데이터 조회",
        input: "orgUnitId: ORG-AI-001, period: 12weeks",
        output: "utilization: 85%, assignments: 42, projects: 5",
        confidence: 0.98,
        duration: 350,
        evidenceRefs: ["EV-001", "EV-002", "EV-003"],
      },
      {
        stepId: "RS-03",
        stepNumber: 3,
        type: "OPTION_GENERATION",
        title: "대안 생성",
        description: "3가지 대안 (보수적/균형/적극적) 생성 및 점수 산정",
        input: "bottleneckWeeks: [W05, W06], gapFTE: 2.5",
        output: "options: [내부재배치, 외부인력, 정규직채용]",
        confidence: 0.88,
        duration: 280,
        evidenceRefs: ["EV-004", "EV-005"],
      },
      {
        stepId: "RS-04",
        stepNumber: 4,
        type: "IMPACT_ANALYSIS",
        title: "영향 분석",
        description: "각 대안별 As-Is vs To-Be 시뮬레이션",
        input: "baseline: {utilization: 0.85, cost: 100M}",
        output: "projections: [{opt1: 78%}, {opt2: 75%}, {opt3: 70%}]",
        confidence: 0.82,
        duration: 420,
        evidenceRefs: ["EV-006"],
      },
      {
        stepId: "RS-05",
        stepNumber: 5,
        type: "VALIDATION",
        title: "검증",
        description: "생성된 결과의 근거 연결 및 환각 검사",
        input: "claims: 15, evidence: 12",
        output: "evidenceCoverage: 92%, hallucinationRisk: 8%",
        confidence: 0.92,
        duration: 180,
        evidenceRefs: [],
      },
    ],
    evidenceList: [
      {
        evidenceId: "EV-001",
        type: "KG_NODE",
        source: "Neo4j: OrgUnit",
        content: "AI팀 (ORG-AI-001): 정원 15명, 현원 14명",
        confidence: 1.0,
        timestamp: new Date().toISOString(),
        linkedClaims: ["현재 인력 현황"],
      },
      {
        evidenceId: "EV-002",
        type: "DATA_RECORD",
        source: "assignments.json",
        content: "현재 배치: 42건, 평균 FTE: 0.85",
        confidence: 0.98,
        timestamp: new Date().toISOString(),
        linkedClaims: ["가동률 85%"],
      },
      {
        evidenceId: "EV-003",
        type: "CALCULATION",
        source: "Impact Simulator",
        content: "W05-W06 병목 예측: 수요 17.5 FTE vs 공급 15 FTE",
        confidence: 0.85,
        timestamp: new Date().toISOString(),
        linkedClaims: ["병목 구간 예측"],
      },
    ],
    assumptions: [
      {
        assumptionId: "AS-001",
        category: "DATA",
        statement: "현재 배치 데이터가 최신 상태임",
        basis: "데이터 갱신 주기: 일간",
        impact: "HIGH",
        isVerifiable: true,
      },
      {
        assumptionId: "AS-002",
        category: "MODEL",
        statement: "과거 패턴이 향후 12주간 유지됨",
        basis: "지난 6개월 추세 분석",
        impact: "MEDIUM",
        isVerifiable: false,
      },
      {
        assumptionId: "AS-003",
        category: "BUSINESS",
        statement: "외주 인력 수급이 4주 내 가능",
        basis: "현재 파트너사 상황",
        impact: "MEDIUM",
        isVerifiable: true,
      },
    ],
    validationResult: {
      isValid: true,
      evidenceCoverage: 0.92,
      hallucinationRisk: 0.08,
      unverifiedClaims: [],
      confidenceScore: 0.88,
    },
    kgContext: {
      centerNode: {
        nodeId: "ORG-AI-001",
        type: "OrgUnit",
        label: "AI팀",
        properties: { headcount: 15, status: "ACTIVE" },
      },
      relatedNodes: [
        { nodeId: "EMP-001", type: "Employee", label: "홍길동", properties: {} },
        { nodeId: "PROJ-001", type: "Project", label: "AI 플랫폼", properties: {} },
        { nodeId: "COMP-001", type: "Competency", label: "ML Engineering", properties: {} },
      ],
      relationships: [
        { from: "EMP-001", to: "ORG-AI-001", type: "BELONGS_TO" },
        { from: "ORG-AI-001", to: "PROJ-001", type: "OWNS" },
        { from: "EMP-001", to: "COMP-001", type: "HAS_COMPETENCY" },
      ],
    },
  };
};

export default ExplanationPanel;
