"use client";

import React from "react";
import { DocsSidebar, docsStructure } from "../../components/DocsSidebar";

export default function DocsIndexPage() {
  return (
    <div className="docs-layout">
      <DocsSidebar categories={docsStructure} />
      <main className="docs-content">
        <div className="docs-header">
          <h1>HR-DSS 문서</h1>
          <p className="docs-description">
            HR 의사결정 지원 시스템의 기술 문서, 명세, 가이드를 확인하세요.
          </p>
        </div>

        <div className="docs-overview">
          {docsStructure.map((category) => (
            <section key={category.name} className="docs-section">
              <h2>
                <span className="section-icon">{category.icon}</span>
                {category.name}
              </h2>
              <div className="docs-grid">
                {category.items.map((item) => (
                  <a
                    key={item.slug}
                    href={`/docs/${item.slug}`}
                    className="doc-card"
                  >
                    <h3>{item.title}</h3>
                    <span className="doc-card-arrow">→</span>
                  </a>
                ))}
              </div>
            </section>
          ))}
        </div>

        <div className="docs-info">
          <h2>빠른 링크</h2>
          <div className="quick-links">
            <a href="/docs/user-guide" className="quick-link">
              <span className="quick-link-icon">📖</span>
              <div>
                <strong>사용자 가이드</strong>
                <p>시스템 사용 방법 안내</p>
              </div>
            </a>
            <a href="/docs/api-docs" className="quick-link">
              <span className="quick-link-icon">🔧</span>
              <div>
                <strong>API 문서</strong>
                <p>API 엔드포인트 레퍼런스</p>
              </div>
            </a>
            <a href="/docs/reports/poc-final-report" className="quick-link">
              <span className="quick-link-icon">📊</span>
              <div>
                <strong>PoC 최종 보고서</strong>
                <p>프로젝트 결과 및 성과</p>
              </div>
            </a>
          </div>
        </div>
      </main>
    </div>
  );
}
