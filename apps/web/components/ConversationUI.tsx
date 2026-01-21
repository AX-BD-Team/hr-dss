/**
 * HR DSS - Conversational UI Component
 *
 * 의사결정 지원을 위한 대화형 인터페이스
 * 질문 입력, 제약조건 설정, 시나리오 빌더 포함
 */

import React, { useState, useRef, useEffect, useCallback } from "react";

// ============================================================
// Types
// ============================================================

export interface Message {
  id: string;
  type: "user" | "assistant" | "system";
  content: string;
  timestamp: Date;
  metadata?: MessageMetadata;
}

export interface MessageMetadata {
  queryType?: string;
  options?: OptionSummary[];
  recommendation?: string;
  evidenceCount?: number;
  processingTime?: number;
  workflowStatus?: string;
}

export interface OptionSummary {
  optionId: string;
  name: string;
  type: "CONSERVATIVE" | "BALANCED" | "AGGRESSIVE";
  score: number;
}

export interface Constraint {
  id: string;
  type: ConstraintType;
  label: string;
  value: string | number | boolean;
  unit?: string;
}

export type ConstraintType =
  | "budget"
  | "timeline"
  | "headcount"
  | "utilization"
  | "risk"
  | "custom";

export interface ScenarioPreset {
  id: string;
  name: string;
  description: string;
  queryTemplate: string;
  defaultConstraints: Constraint[];
}

export interface ConversationUIProps {
  onSendMessage: (message: string, constraints: Constraint[]) => Promise<Message>;
  onSelectOption?: (optionId: string) => void;
  onViewDetails?: (messageId: string) => void;
  scenarioPresets?: ScenarioPreset[];
  initialMessages?: Message[];
  placeholder?: string;
  disabled?: boolean;
}

// ============================================================
// Constants
// ============================================================

const DEFAULT_PRESETS: ScenarioPreset[] = [
  {
    id: "capacity",
    name: "가동률 병목 분석",
    description: "향후 12주간 인력 병목 구간 예측 및 해결 방안",
    queryTemplate: "향후 12주간 {org}의 가동률 병목 구간과 해결 방안은?",
    defaultConstraints: [
      { id: "c1", type: "utilization", label: "목표 가동률", value: 85, unit: "%" },
      { id: "c2", type: "timeline", label: "분석 기간", value: 12, unit: "주" },
    ],
  },
  {
    id: "gonogo",
    name: "Go/No-go 의사결정",
    description: "신규 프로젝트/기회 수주 여부 결정",
    queryTemplate: "{opportunity} 기회에 대해 Go/No-go 의사결정을 해주세요.",
    defaultConstraints: [
      { id: "c1", type: "risk", label: "허용 리스크", value: "MEDIUM" },
      { id: "c2", type: "utilization", label: "최소 가용률", value: 20, unit: "%" },
    ],
  },
  {
    id: "headcount",
    name: "증원 타당성 분석",
    description: "인력 증원 요청에 대한 타당성 검토",
    queryTemplate: "{org}에서 {count}명 증원 요청에 대한 타당성을 분석해주세요.",
    defaultConstraints: [
      { id: "c1", type: "budget", label: "연간 예산", value: 500000000, unit: "원" },
      { id: "c2", type: "headcount", label: "요청 인원", value: 3, unit: "명" },
    ],
  },
  {
    id: "competency",
    name: "역량 갭 분석",
    description: "조직의 역량 갭 분석 및 해소 방안",
    queryTemplate: "{org}의 핵심 역량 갭과 해소 방안을 분석해주세요.",
    defaultConstraints: [
      { id: "c1", type: "timeline", label: "목표 달성 기한", value: 6, unit: "개월" },
      { id: "c2", type: "budget", label: "교육 예산", value: 100000000, unit: "원" },
    ],
  },
];

const CONSTRAINT_TYPES: Record<ConstraintType, { icon: string; label: string }> = {
  budget: { icon: "$", label: "예산" },
  timeline: { icon: "T", label: "일정" },
  headcount: { icon: "#", label: "인원" },
  utilization: { icon: "%", label: "가동률" },
  risk: { icon: "!", label: "리스크" },
  custom: { icon: "*", label: "기타" },
};

// ============================================================
// Helper Components
// ============================================================

const MessageBubble: React.FC<{
  message: Message;
  onViewDetails?: (messageId: string) => void;
  onSelectOption?: (optionId: string) => void;
}> = ({ message, onViewDetails, onSelectOption }) => {
  const isUser = message.type === "user";
  const isSystem = message.type === "system";

  return (
    <div
      style={{
        display: "flex",
        justifyContent: isUser ? "flex-end" : "flex-start",
        marginBottom: "16px",
      }}
    >
      <div
        style={{
          maxWidth: isSystem ? "100%" : "80%",
          padding: "12px 16px",
          borderRadius: isUser ? "16px 16px 4px 16px" : "16px 16px 16px 4px",
          background: isUser ? "#2196F3" : isSystem ? "#FFF3E0" : "#f5f5f5",
          color: isUser ? "white" : "#333",
          boxShadow: "0 1px 2px rgba(0,0,0,0.1)",
        }}
      >
        {/* Message Content */}
        <div style={{ whiteSpace: "pre-wrap", lineHeight: 1.5 }}>{message.content}</div>

        {/* Options Summary */}
        {message.metadata?.options && message.metadata.options.length > 0 && (
          <div
            style={{
              marginTop: "12px",
              padding: "12px",
              background: "white",
              borderRadius: "8px",
              border: "1px solid #e0e0e0",
            }}
          >
            <div style={{ fontSize: "12px", fontWeight: "bold", marginBottom: "8px" }}>
              생성된 대안
            </div>
            {message.metadata.options.map((opt) => (
              <div
                key={opt.optionId}
                onClick={() => onSelectOption?.(opt.optionId)}
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  padding: "8px",
                  marginBottom: "4px",
                  background:
                    opt.optionId === message.metadata?.recommendation ? "#E3F2FD" : "#fafafa",
                  borderRadius: "4px",
                  cursor: "pointer",
                  border:
                    opt.optionId === message.metadata?.recommendation
                      ? "1px solid #2196F3"
                      : "1px solid transparent",
                }}
              >
                <div>
                  <span
                    style={{
                      fontSize: "10px",
                      padding: "2px 6px",
                      borderRadius: "4px",
                      background:
                        opt.type === "CONSERVATIVE"
                          ? "#4CAF50"
                          : opt.type === "BALANCED"
                          ? "#FF9800"
                          : "#F44336",
                      color: "white",
                      marginRight: "8px",
                    }}
                  >
                    {opt.type === "CONSERVATIVE"
                      ? "보수적"
                      : opt.type === "BALANCED"
                      ? "균형"
                      : "적극적"}
                  </span>
                  <span style={{ fontWeight: "500" }}>{opt.name}</span>
                  {opt.optionId === message.metadata?.recommendation && (
                    <span
                      style={{
                        marginLeft: "8px",
                        fontSize: "11px",
                        color: "#2196F3",
                      }}
                    >
                      [추천]
                    </span>
                  )}
                </div>
                <span style={{ fontSize: "14px", fontWeight: "bold" }}>
                  {opt.score.toFixed(0)}점
                </span>
              </div>
            ))}
          </div>
        )}

        {/* Metadata */}
        <div
          style={{
            marginTop: "8px",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            fontSize: "11px",
            color: isUser ? "rgba(255,255,255,0.7)" : "#999",
          }}
        >
          <span>{message.timestamp.toLocaleTimeString()}</span>
          <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
            {message.metadata?.evidenceCount !== undefined && (
              <span>근거 {message.metadata.evidenceCount}건</span>
            )}
            {message.metadata?.processingTime !== undefined && (
              <span>{(message.metadata.processingTime / 1000).toFixed(1)}s</span>
            )}
            {!isUser && onViewDetails && (
              <button
                onClick={() => onViewDetails(message.id)}
                style={{
                  background: "none",
                  border: "none",
                  color: "#2196F3",
                  cursor: "pointer",
                  fontSize: "11px",
                  textDecoration: "underline",
                }}
              >
                상세 보기
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

const ConstraintEditor: React.FC<{
  constraints: Constraint[];
  onChange: (constraints: Constraint[]) => void;
}> = ({ constraints, onChange }) => {
  const addConstraint = () => {
    const newConstraint: Constraint = {
      id: `c${Date.now()}`,
      type: "custom",
      label: "새 제약조건",
      value: "",
    };
    onChange([...constraints, newConstraint]);
  };

  const updateConstraint = (id: string, updates: Partial<Constraint>) => {
    onChange(constraints.map((c) => (c.id === id ? { ...c, ...updates } : c)));
  };

  const removeConstraint = (id: string) => {
    onChange(constraints.filter((c) => c.id !== id));
  };

  return (
    <div
      style={{
        padding: "12px",
        background: "#f9f9f9",
        borderRadius: "8px",
        marginBottom: "12px",
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
        <span style={{ fontSize: "13px", fontWeight: "bold" }}>제약조건</span>
        <button
          onClick={addConstraint}
          style={{
            padding: "4px 8px",
            border: "1px solid #ccc",
            borderRadius: "4px",
            background: "white",
            cursor: "pointer",
            fontSize: "12px",
          }}
        >
          + 추가
        </button>
      </div>

      {constraints.length === 0 ? (
        <div style={{ fontSize: "12px", color: "#999", textAlign: "center", padding: "8px" }}>
          제약조건이 없습니다
        </div>
      ) : (
        <div style={{ display: "flex", flexWrap: "wrap", gap: "8px" }}>
          {constraints.map((constraint) => (
            <div
              key={constraint.id}
              style={{
                display: "flex",
                alignItems: "center",
                gap: "4px",
                padding: "6px 10px",
                background: "white",
                borderRadius: "16px",
                border: "1px solid #e0e0e0",
                fontSize: "12px",
              }}
            >
              <span
                style={{
                  width: "18px",
                  height: "18px",
                  borderRadius: "50%",
                  background: "#E3F2FD",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontSize: "10px",
                  fontWeight: "bold",
                  color: "#2196F3",
                }}
              >
                {CONSTRAINT_TYPES[constraint.type]?.icon || "*"}
              </span>
              <input
                type="text"
                value={constraint.label}
                onChange={(e) => updateConstraint(constraint.id, { label: e.target.value })}
                style={{
                  border: "none",
                  background: "transparent",
                  width: "80px",
                  fontSize: "12px",
                }}
                placeholder="라벨"
              />
              <span>:</span>
              <input
                type="text"
                value={String(constraint.value)}
                onChange={(e) => updateConstraint(constraint.id, { value: e.target.value })}
                style={{
                  border: "none",
                  background: "transparent",
                  width: "60px",
                  fontSize: "12px",
                  fontWeight: "bold",
                }}
                placeholder="값"
              />
              {constraint.unit && <span style={{ color: "#666" }}>{constraint.unit}</span>}
              <button
                onClick={() => removeConstraint(constraint.id)}
                style={{
                  background: "none",
                  border: "none",
                  cursor: "pointer",
                  color: "#999",
                  fontSize: "14px",
                  padding: "0 4px",
                }}
              >
                x
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

const ScenarioSelector: React.FC<{
  presets: ScenarioPreset[];
  onSelect: (preset: ScenarioPreset) => void;
}> = ({ presets, onSelect }) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div style={{ position: "relative" }}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        style={{
          padding: "8px 12px",
          border: "1px solid #ccc",
          borderRadius: "4px",
          background: "white",
          cursor: "pointer",
          fontSize: "13px",
          display: "flex",
          alignItems: "center",
          gap: "8px",
        }}
      >
        <span>[S]</span>
        <span>시나리오</span>
        <span>{isOpen ? "^" : "v"}</span>
      </button>

      {isOpen && (
        <div
          style={{
            position: "absolute",
            bottom: "100%",
            left: 0,
            marginBottom: "8px",
            background: "white",
            borderRadius: "8px",
            boxShadow: "0 4px 12px rgba(0,0,0,0.15)",
            minWidth: "300px",
            zIndex: 100,
          }}
        >
          {presets.map((preset) => (
            <div
              key={preset.id}
              onClick={() => {
                onSelect(preset);
                setIsOpen(false);
              }}
              style={{
                padding: "12px 16px",
                cursor: "pointer",
                borderBottom: "1px solid #f0f0f0",
              }}
              onMouseOver={(e) => (e.currentTarget.style.background = "#f5f5f5")}
              onMouseOut={(e) => (e.currentTarget.style.background = "white")}
            >
              <div style={{ fontWeight: "bold", marginBottom: "4px" }}>{preset.name}</div>
              <div style={{ fontSize: "12px", color: "#666" }}>{preset.description}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

// ============================================================
// Main Component
// ============================================================

export const ConversationUI: React.FC<ConversationUIProps> = ({
  onSendMessage,
  onSelectOption,
  onViewDetails,
  scenarioPresets = DEFAULT_PRESETS,
  initialMessages = [],
  placeholder = "HR 의사결정에 대해 질문해 주세요...",
  disabled = false,
}) => {
  const [messages, setMessages] = useState<Message[]>(initialMessages);
  const [inputValue, setInputValue] = useState("");
  const [constraints, setConstraints] = useState<Constraint[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showConstraints, setShowConstraints] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Handle scenario selection
  const handleScenarioSelect = useCallback((preset: ScenarioPreset) => {
    setInputValue(preset.queryTemplate);
    setConstraints(preset.defaultConstraints);
    setShowConstraints(true);
    inputRef.current?.focus();
  }, []);

  // Handle send message
  const handleSend = useCallback(async () => {
    if (!inputValue.trim() || isLoading || disabled) return;

    const userMessage: Message = {
      id: `msg-${Date.now()}`,
      type: "user",
      content: inputValue.trim(),
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue("");
    setIsLoading(true);

    try {
      const response = await onSendMessage(userMessage.content, constraints);
      setMessages((prev) => [...prev, response]);
    } catch (error) {
      const errorMessage: Message = {
        id: `msg-err-${Date.now()}`,
        type: "system",
        content: `오류가 발생했습니다: ${error instanceof Error ? error.message : "알 수 없는 오류"}`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  }, [inputValue, constraints, isLoading, disabled, onSendMessage]);

  // Handle key press
  const handleKeyPress = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        handleSend();
      }
    },
    [handleSend]
  );

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        height: "100%",
        maxHeight: "800px",
        background: "white",
        borderRadius: "12px",
        boxShadow: "0 2px 12px rgba(0,0,0,0.08)",
        overflow: "hidden",
      }}
    >
      {/* Header */}
      <div
        style={{
          padding: "16px 20px",
          borderBottom: "1px solid #e0e0e0",
          background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
          color: "white",
        }}
      >
        <div style={{ fontWeight: "bold", fontSize: "18px" }}>HR 의사결정 지원</div>
        <div style={{ fontSize: "12px", opacity: 0.9, marginTop: "4px" }}>
          AI 기반 의사결정 분석 및 대안 제시
        </div>
      </div>

      {/* Messages */}
      <div
        style={{
          flex: 1,
          overflowY: "auto",
          padding: "20px",
          background: "#fafafa",
        }}
      >
        {messages.length === 0 ? (
          <div
            style={{
              textAlign: "center",
              color: "#999",
              padding: "40px 20px",
            }}
          >
            <div style={{ fontSize: "48px", marginBottom: "16px" }}>[?]</div>
            <div style={{ fontSize: "16px", marginBottom: "8px" }}>
              HR 의사결정에 대해 질문해 주세요
            </div>
            <div style={{ fontSize: "13px", color: "#bbb" }}>
              예: "향후 12주간 AI팀의 가동률 병목 구간과 해결 방안은?"
            </div>
          </div>
        ) : (
          messages.map((msg) => (
            <MessageBubble
              key={msg.id}
              message={msg}
              onViewDetails={onViewDetails}
              onSelectOption={onSelectOption}
            />
          ))
        )}

        {isLoading && (
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "8px",
              padding: "12px",
              color: "#666",
            }}
          >
            <div
              style={{
                width: "8px",
                height: "8px",
                borderRadius: "50%",
                background: "#2196F3",
                animation: "pulse 1s infinite",
              }}
            />
            <span>분석 중...</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Constraints Panel */}
      {showConstraints && (
        <ConstraintEditor constraints={constraints} onChange={setConstraints} />
      )}

      {/* Input Area */}
      <div
        style={{
          padding: "16px",
          borderTop: "1px solid #e0e0e0",
          background: "white",
        }}
      >
        <div style={{ display: "flex", gap: "8px", marginBottom: "12px" }}>
          <ScenarioSelector presets={scenarioPresets} onSelect={handleScenarioSelect} />
          <button
            onClick={() => setShowConstraints(!showConstraints)}
            style={{
              padding: "8px 12px",
              border: showConstraints ? "2px solid #2196F3" : "1px solid #ccc",
              borderRadius: "4px",
              background: showConstraints ? "#E3F2FD" : "white",
              cursor: "pointer",
              fontSize: "13px",
            }}
          >
            [C] 제약조건 {constraints.length > 0 && `(${constraints.length})`}
          </button>
        </div>

        <div style={{ display: "flex", gap: "8px" }}>
          <textarea
            ref={inputRef}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={placeholder}
            disabled={disabled || isLoading}
            style={{
              flex: 1,
              padding: "12px",
              border: "1px solid #e0e0e0",
              borderRadius: "8px",
              resize: "none",
              fontSize: "14px",
              minHeight: "48px",
              maxHeight: "120px",
              fontFamily: "inherit",
            }}
            rows={2}
          />
          <button
            onClick={handleSend}
            disabled={!inputValue.trim() || isLoading || disabled}
            style={{
              padding: "12px 24px",
              background:
                inputValue.trim() && !isLoading && !disabled ? "#2196F3" : "#ccc",
              color: "white",
              border: "none",
              borderRadius: "8px",
              cursor:
                inputValue.trim() && !isLoading && !disabled ? "pointer" : "not-allowed",
              fontWeight: "bold",
              fontSize: "14px",
            }}
          >
            {isLoading ? "..." : "전송"}
          </button>
        </div>
      </div>

      {/* CSS for animation */}
      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }
      `}</style>
    </div>
  );
};

// ============================================================
// Mock Handler for Testing
// ============================================================

export const createMockMessageHandler = () => {
  return async (message: string, constraints: Constraint[]): Promise<Message> => {
    // Simulate processing delay
    await new Promise((resolve) => setTimeout(resolve, 1500));

    const queryType = message.includes("가동률")
      ? "CAPACITY"
      : message.includes("Go") || message.includes("No-go")
      ? "GO_NOGO"
      : message.includes("증원")
      ? "HEADCOUNT"
      : "COMPETENCY_GAP";

    const options: OptionSummary[] = [
      { optionId: "OPT-01", name: "내부 재배치", type: "CONSERVATIVE", score: 72 },
      { optionId: "OPT-02", name: "외부 인력 활용", type: "BALANCED", score: 78 },
      { optionId: "OPT-03", name: "정규직 채용", type: "AGGRESSIVE", score: 65 },
    ];

    return {
      id: `msg-${Date.now()}`,
      type: "assistant",
      content: `분석 결과를 안내드립니다.

질문 유형: ${queryType}
적용된 제약조건: ${constraints.length}개

분석 결과, 3가지 대안을 도출했습니다. 현재 상황과 제약조건을 고려할 때 "외부 인력 활용" 옵션을 추천드립니다.

각 대안의 상세 내용과 영향 분석을 확인하시려면 아래에서 대안을 선택해주세요.`,
      timestamp: new Date(),
      metadata: {
        queryType,
        options,
        recommendation: "OPT-02",
        evidenceCount: 12,
        processingTime: 1500,
        workflowStatus: "COMPLETED",
      },
    };
  };
};

export default ConversationUI;
