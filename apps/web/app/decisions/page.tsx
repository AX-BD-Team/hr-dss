"use client";

import React, { useState, useCallback } from "react";
import {
  ConversationUI,
  createMockMessageHandler,
  Constraint,
  Message,
} from "../../components/ConversationUI";
import {
  ExplanationPanel,
  ExplanationData,
  generateMockExplanationData,
} from "../../components/ExplanationPanel";

// Message를 ExplanationData로 변환하는 함수
const messageToExplanationData = (message: Message): ExplanationData => {
  const baseData = generateMockExplanationData();

  return {
    ...baseData,
    decisionId: message.id,
    query: message.content,
    queryType: message.metadata?.queryType || "GENERAL",
    selectedOption: message.metadata?.recommendation
      ? {
          optionId: message.metadata.recommendation,
          name:
            message.metadata.options?.find(
              (o) => o.optionId === message.metadata?.recommendation,
            )?.name || "추천 대안",
          type:
            message.metadata.options?.find(
              (o) => o.optionId === message.metadata?.recommendation,
            )?.type || "BALANCED",
          rationale: "현재 상황과 제약조건을 종합적으로 고려한 최적 대안",
        }
      : undefined,
    validationResult: {
      ...baseData.validationResult,
      evidenceCoverage: message.metadata?.evidenceCount
        ? Math.min(0.95, 0.7 + message.metadata.evidenceCount * 0.02)
        : 0.92,
    },
  };
};

// 모달 컴포넌트
const DetailModal: React.FC<{
  isOpen: boolean;
  onClose: () => void;
  data: ExplanationData | null;
}> = ({ isOpen, onClose, data }) => {
  if (!isOpen || !data) return null;

  return (
    <div
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: "rgba(0, 0, 0, 0.5)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        zIndex: 1000,
        padding: "20px",
      }}
      onClick={onClose}
    >
      <div
        style={{
          background: "white",
          borderRadius: "16px",
          width: "100%",
          maxWidth: "900px",
          maxHeight: "90vh",
          overflow: "hidden",
          display: "flex",
          flexDirection: "column",
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* 모달 헤더 */}
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            padding: "16px 20px",
            borderBottom: "1px solid #e0e0e0",
            background: "#f9f9f9",
          }}
        >
          <div>
            <h2 style={{ margin: 0, fontSize: "18px", fontWeight: "bold" }}>
              분석 상세 정보
            </h2>
            <p style={{ margin: "4px 0 0", fontSize: "12px", color: "#666" }}>
              {data.queryType} | {data.decisionId}
            </p>
          </div>
          <button
            onClick={onClose}
            style={{
              background: "none",
              border: "none",
              fontSize: "24px",
              cursor: "pointer",
              color: "#666",
              padding: "4px 8px",
            }}
          >
            ×
          </button>
        </div>

        {/* 모달 본문 */}
        <div style={{ flex: 1, overflow: "auto" }}>
          <ExplanationPanel
            data={data}
            onEvidenceClick={(evidenceId) => {
              console.log("Evidence clicked:", evidenceId);
            }}
            onNodeClick={(nodeId) => {
              console.log("Node clicked:", nodeId);
            }}
          />
        </div>
      </div>
    </div>
  );
};

export default function DecisionsPage() {
  const mockHandler = createMockMessageHandler();

  // 메시지 목록을 직접 관리
  const [messages, setMessages] = useState<Message[]>([]);

  // 모달 상태
  const [selectedMessage, setSelectedMessage] = useState<Message | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const handleSendMessage = useCallback(
    async (message: string, constraints: Constraint[]): Promise<Message> => {
      const response = await mockHandler(message, constraints);
      // 응답 메시지를 저장 (나중에 상세 보기에서 사용)
      setMessages((prev) => [...prev, response]);
      return response;
    },
    [mockHandler],
  );

  const handleSelectOption = useCallback((optionId: string) => {
    console.log("Selected option:", optionId);
    alert(`선택된 옵션: ${optionId}\n\n상세 분석 화면으로 이동합니다.`);
  }, []);

  const handleViewDetails = useCallback(
    (messageId: string) => {
      console.log("View details for message:", messageId);

      // 저장된 메시지에서 찾기
      const message = messages.find((m) => m.id === messageId);

      if (message) {
        setSelectedMessage(message);
        setIsModalOpen(true);
      } else {
        // 메시지를 찾지 못한 경우 Mock 데이터로 모달 표시
        const mockMessage: Message = {
          id: messageId,
          type: "assistant",
          content: "분석 결과를 확인하세요.",
          timestamp: new Date(),
          metadata: {
            queryType: "CAPACITY",
            options: [
              {
                optionId: "OPT-01",
                name: "내부 재배치",
                type: "CONSERVATIVE",
                score: 72,
              },
              {
                optionId: "OPT-02",
                name: "외부 인력 활용",
                type: "BALANCED",
                score: 78,
              },
              {
                optionId: "OPT-03",
                name: "정규직 채용",
                type: "AGGRESSIVE",
                score: 65,
              },
            ],
            recommendation: "OPT-02",
            evidenceCount: 12,
            processingTime: 1500,
          },
        };
        setSelectedMessage(mockMessage);
        setIsModalOpen(true);
      }
    },
    [messages],
  );

  const handleCloseModal = useCallback(() => {
    setIsModalOpen(false);
    setSelectedMessage(null);
  }, []);

  // ExplanationData 변환
  const explanationData = selectedMessage
    ? messageToExplanationData(selectedMessage)
    : null;

  return (
    <div>
      <div style={{ marginBottom: "24px" }}>
        <h1
          style={{ fontSize: "28px", fontWeight: "700", marginBottom: "8px" }}
        >
          의사결정 지원
        </h1>
        <p style={{ color: "var(--text-secondary)" }}>
          AI 기반 HR 의사결정 분석 및 대안 제시
        </p>
      </div>

      <div style={{ height: "700px" }}>
        <ConversationUI
          onSendMessage={handleSendMessage}
          onSelectOption={handleSelectOption}
          onViewDetails={handleViewDetails}
          placeholder="HR 의사결정에 대해 질문해 주세요... (예: 향후 12주 AI팀 가동률 병목은?)"
        />
      </div>

      <div style={{ marginTop: "24px" }}>
        <div className="card">
          <h2 className="card-title">지원 질문 유형</h2>
          <div className="grid grid-4">
            <div
              style={{
                padding: "12px",
                background: "#f8fafc",
                borderRadius: "8px",
              }}
            >
              <strong>A-1: 가동률 분석</strong>
              <p
                style={{
                  fontSize: "13px",
                  color: "var(--text-secondary)",
                  marginTop: "4px",
                }}
              >
                12주 병목 예측
              </p>
            </div>
            <div
              style={{
                padding: "12px",
                background: "#f8fafc",
                borderRadius: "8px",
              }}
            >
              <strong>B-1: Go/No-go</strong>
              <p
                style={{
                  fontSize: "13px",
                  color: "var(--text-secondary)",
                  marginTop: "4px",
                }}
              >
                수주 의사결정
              </p>
            </div>
            <div
              style={{
                padding: "12px",
                background: "#f8fafc",
                borderRadius: "8px",
              }}
            >
              <strong>C-1: 증원 분석</strong>
              <p
                style={{
                  fontSize: "13px",
                  color: "var(--text-secondary)",
                  marginTop: "4px",
                }}
              >
                인력 증원 타당성
              </p>
            </div>
            <div
              style={{
                padding: "12px",
                background: "#f8fafc",
                borderRadius: "8px",
              }}
            >
              <strong>D-1: 역량 갭</strong>
              <p
                style={{
                  fontSize: "13px",
                  color: "var(--text-secondary)",
                  marginTop: "4px",
                }}
              >
                역량 갭 분석
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* 상세 보기 모달 */}
      <DetailModal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        data={explanationData}
      />
    </div>
  );
}
