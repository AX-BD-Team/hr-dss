'use client';

import React from 'react';
import { ConversationUI, createMockMessageHandler, Constraint, Message } from '../../components/ConversationUI';

export default function DecisionsPage() {
  const mockHandler = createMockMessageHandler();

  const handleSendMessage = async (message: string, constraints: Constraint[]): Promise<Message> => {
    return mockHandler(message, constraints);
  };

  const handleSelectOption = (optionId: string) => {
    console.log('Selected option:', optionId);
    alert(`선택된 옵션: ${optionId}\n\n상세 분석 화면으로 이동합니다.`);
  };

  const handleViewDetails = (messageId: string) => {
    console.log('View details for message:', messageId);
    alert(`메시지 ID: ${messageId}\n\n근거 및 상세 정보를 표시합니다.`);
  };

  return (
    <div>
      <div style={{ marginBottom: '24px' }}>
        <h1 style={{ fontSize: '28px', fontWeight: '700', marginBottom: '8px' }}>
          의사결정 지원
        </h1>
        <p style={{ color: 'var(--text-secondary)' }}>
          AI 기반 HR 의사결정 분석 및 대안 제시
        </p>
      </div>

      <div style={{ height: '700px' }}>
        <ConversationUI
          onSendMessage={handleSendMessage}
          onSelectOption={handleSelectOption}
          onViewDetails={handleViewDetails}
          placeholder="HR 의사결정에 대해 질문해 주세요... (예: 향후 12주 AI팀 가동률 병목은?)"
        />
      </div>

      <div style={{ marginTop: '24px' }}>
        <div className="card">
          <h2 className="card-title">지원 질문 유형</h2>
          <div className="grid grid-4">
            <div style={{ padding: '12px', background: '#f8fafc', borderRadius: '8px' }}>
              <strong>A-1: 가동률 분석</strong>
              <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginTop: '4px' }}>
                12주 병목 예측
              </p>
            </div>
            <div style={{ padding: '12px', background: '#f8fafc', borderRadius: '8px' }}>
              <strong>B-1: Go/No-go</strong>
              <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginTop: '4px' }}>
                수주 의사결정
              </p>
            </div>
            <div style={{ padding: '12px', background: '#f8fafc', borderRadius: '8px' }}>
              <strong>C-1: 증원 분석</strong>
              <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginTop: '4px' }}>
                인력 증원 타당성
              </p>
            </div>
            <div style={{ padding: '12px', background: '#f8fafc', borderRadius: '8px' }}>
              <strong>D-1: 역량 갭</strong>
              <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginTop: '4px' }}>
                역량 갭 분석
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
