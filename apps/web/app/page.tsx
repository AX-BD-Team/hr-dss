'use client';

import React from 'react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function HomePage() {
  const [systemStatus, setSystemStatus] = React.useState<'loading' | 'healthy' | 'error'>('loading');

  React.useEffect(() => {
    // API 상태 확인 (타임아웃 3초)
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 3000);

    fetch(`${API_URL}/health`, { signal: controller.signal })
      .then((res) => res.ok ? setSystemStatus('healthy') : setSystemStatus('error'))
      .catch(() => setSystemStatus('error'))
      .finally(() => clearTimeout(timeoutId));
  }, []);

  return (
    <div>
      {/* Hero Section */}
      <section className="hero">
        <h1>HR 의사결정 지원 시스템</h1>
        <p>AI 기반 예측과 근거 중심의 의사결정을 지원합니다</p>
        <div className="hero-actions">
          <a href="/decisions" className="btn btn-primary">
            의사결정 시작하기
          </a>
          <a href="/dashboard" className="btn btn-secondary">
            대시보드 보기
          </a>
        </div>
      </section>

      {/* System Status */}
      <section className="status-section">
        <div className="card">
          <h2 className="card-title">시스템 상태</h2>
          <div className="status-indicator">
            <span
              className={`badge ${
                systemStatus === 'healthy'
                  ? 'badge-success'
                  : systemStatus === 'error'
                  ? 'badge-warning'
                  : 'badge-info'
              }`}
            >
              {systemStatus === 'healthy'
                ? '정상 운영 중'
                : systemStatus === 'error'
                ? '백엔드 미연결'
                : '확인 중...'}
            </span>
            {systemStatus === 'error' && (
              <span className="status-hint">
                (프론트엔드 전용 모드로 실행 중)
              </span>
            )}
          </div>
        </div>
      </section>

      {/* Feature Cards */}
      <section className="features">
        <h2 className="section-title">주요 기능</h2>
        <div className="grid grid-4">
          <div className="card feature-card">
            <div className="feature-icon">📊</div>
            <h3>가동률 분석</h3>
            <p>12주 내 병목 예측 및 사전 대응 방안 제시</p>
            <span className="badge badge-info">A-1</span>
          </div>

          <div className="card feature-card">
            <div className="feature-icon">✅</div>
            <h3>Go/No-go 분석</h3>
            <p>프로젝트 수주 결정을 위한 다각적 분석</p>
            <span className="badge badge-info">B-1</span>
          </div>

          <div className="card feature-card">
            <div className="feature-icon">👥</div>
            <h3>증원 분석</h3>
            <p>증원 필요성 분석 및 원인 분해</p>
            <span className="badge badge-info">C-1</span>
          </div>

          <div className="card feature-card">
            <div className="feature-icon">🎯</div>
            <h3>역량 갭 분석</h3>
            <p>조직 역량 갭 분석 및 육성 계획</p>
            <span className="badge badge-info">D-1</span>
          </div>
        </div>
      </section>

      {/* Metrics */}
      <section className="metrics-section">
        <h2 className="section-title">시스템 지표</h2>
        <div className="grid grid-4">
          <div className="card metric">
            <div className="metric-value">&gt;95%</div>
            <div className="metric-label">근거 연결률</div>
          </div>
          <div className="card metric">
            <div className="metric-value">&lt;5%</div>
            <div className="metric-label">환각률</div>
          </div>
          <div className="card metric">
            <div className="metric-value">3안</div>
            <div className="metric-label">대안 생성</div>
          </div>
          <div className="card metric">
            <div className="metric-value">&lt;30s</div>
            <div className="metric-label">응답 시간</div>
          </div>
        </div>
      </section>

      <style jsx>{`
        .hero {
          text-align: center;
          padding: 64px 0;
          margin-bottom: 48px;
        }

        .hero h1 {
          font-size: 48px;
          font-weight: 700;
          margin-bottom: 16px;
          background: linear-gradient(135deg, #2563eb, #7c3aed);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
        }

        .hero p {
          font-size: 20px;
          color: var(--text-secondary);
          margin-bottom: 32px;
        }

        .hero-actions {
          display: flex;
          gap: 16px;
          justify-content: center;
        }

        .status-section {
          margin-bottom: 48px;
        }

        .status-indicator {
          display: flex;
          align-items: center;
          gap: 8px;
          flex-wrap: wrap;
        }

        .status-hint {
          font-size: 12px;
          color: var(--text-secondary);
        }

        .section-title {
          font-size: 24px;
          font-weight: 600;
          margin-bottom: 24px;
        }

        .features {
          margin-bottom: 48px;
        }

        .feature-card {
          text-align: center;
        }

        .feature-icon {
          font-size: 48px;
          margin-bottom: 16px;
        }

        .feature-card h3 {
          font-size: 18px;
          font-weight: 600;
          margin-bottom: 8px;
        }

        .feature-card p {
          font-size: 14px;
          color: var(--text-secondary);
          margin-bottom: 12px;
        }

        .metrics-section {
          margin-bottom: 48px;
        }
      `}</style>
    </div>
  );
}
