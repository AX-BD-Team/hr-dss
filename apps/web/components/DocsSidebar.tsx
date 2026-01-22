"use client";

import React, { useState } from "react";

export interface DocItem {
  slug: string;
  title: string;
  path: string;
}

export interface DocCategory {
  name: string;
  icon: string;
  items: DocItem[];
}

export interface DocsSidebarProps {
  categories: DocCategory[];
  currentSlug?: string;
}

// 문서 구조 정의
export const docsStructure: DocCategory[] = [
  {
    name: "개요",
    icon: "📋",
    items: [
      { slug: "INDEX", title: "문서 인덱스", path: "INDEX.md" },
      { slug: "user-guide", title: "사용자 가이드", path: "user-guide.md" },
      { slug: "api-docs", title: "API 문서", path: "api-docs.md" },
    ],
  },
  {
    name: "명세 (Specs)",
    icon: "📝",
    items: [
      {
        slug: "specs/poc-charter",
        title: "PoC Charter",
        path: "specs/poc-charter.md",
      },
      {
        slug: "specs/question-set",
        title: "Question Set",
        path: "specs/question-set.md",
      },
      {
        slug: "specs/decision-criteria",
        title: "Decision Criteria",
        path: "specs/decision-criteria.md",
      },
      {
        slug: "specs/kpi-acceptance",
        title: "KPI & Acceptance",
        path: "specs/kpi-acceptance.md",
      },
      {
        slug: "specs/data-catalog",
        title: "Data Catalog",
        path: "specs/data-catalog.md",
      },
      {
        slug: "specs/join-key-standard",
        title: "Join Key Standard",
        path: "specs/join-key-standard.md",
      },
      {
        slug: "specs/data-classification",
        title: "Data Classification",
        path: "specs/data-classification.md",
      },
      {
        slug: "specs/outcome-definition",
        title: "Outcome Definition",
        path: "specs/outcome-definition.md",
      },
      {
        slug: "specs/demand-data-spec",
        title: "Demand Data Spec",
        path: "specs/demand-data-spec.md",
      },
      {
        slug: "specs/phase1-plan",
        title: "Phase 1 계획",
        path: "specs/phase1-plan.md",
      },
      {
        slug: "specs/cloudflare-deployment-plan",
        title: "Cloudflare 배포 계획",
        path: "specs/cloudflare-deployment-plan.md",
      },
    ],
  },
  {
    name: "리포트 (Reports)",
    icon: "📊",
    items: [
      {
        slug: "reports/poc-final-report",
        title: "PoC 최종 보고서",
        path: "reports/poc-final-report.md",
      },
      {
        slug: "reports/comparison-report",
        title: "비교 분석 리포트",
        path: "reports/comparison-report.md",
      },
    ],
  },
  {
    name: "가이드 (Guides)",
    icon: "📚",
    items: [
      {
        slug: "guides/phase1-fastapi-implementation",
        title: "FastAPI 구현 가이드",
        path: "guides/phase1-fastapi-implementation.md",
      },
      {
        slug: "guides/phase2-infrastructure-setup",
        title: "인프라 설정 가이드",
        path: "guides/phase2-infrastructure-setup.md",
      },
    ],
  },
];

export const DocsSidebar: React.FC<DocsSidebarProps> = ({
  categories,
  currentSlug,
}) => {
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(
    new Set(categories.map((c) => c.name)),
  );

  const toggleCategory = (categoryName: string) => {
    setExpandedCategories((prev) => {
      const next = new Set(prev);
      if (next.has(categoryName)) {
        next.delete(categoryName);
      } else {
        next.add(categoryName);
      }
      return next;
    });
  };

  return (
    <aside className="docs-sidebar">
      <div className="docs-sidebar-header">
        <h2>문서 목록</h2>
      </div>
      <nav className="docs-nav">
        {categories.map((category) => (
          <div key={category.name} className="docs-category">
            <button
              className="docs-category-header"
              onClick={() => toggleCategory(category.name)}
            >
              <span className="docs-category-icon">{category.icon}</span>
              <span className="docs-category-name">{category.name}</span>
              <span
                className={`docs-category-arrow ${
                  expandedCategories.has(category.name) ? "expanded" : ""
                }`}
              >
                ▶
              </span>
            </button>
            {expandedCategories.has(category.name) && (
              <ul className="docs-items">
                {category.items.map((item) => (
                  <li key={item.slug}>
                    <a
                      href={`/docs/${item.slug}`}
                      className={`docs-item-link ${
                        currentSlug === item.slug ? "active" : ""
                      }`}
                    >
                      {item.title}
                    </a>
                  </li>
                ))}
              </ul>
            )}
          </div>
        ))}
      </nav>
    </aside>
  );
};

export default DocsSidebar;
