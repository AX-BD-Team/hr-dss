import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "HR 의사결정 지원 시스템",
  description: "AI 기반 HR 의사결정 지원 시스템 - 팔란티어 수준의 예측 가능성",
  keywords: ["HR", "의사결정", "AI", "Knowledge Graph", "예측"],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ko">
      <body>
        <div className="app-container">
          <header className="app-header">
            <div className="header-content">
              <h1 className="logo">HR-DSS</h1>
              <nav className="nav-menu">
                <a href="/" className="nav-link">
                  홈
                </a>
                <a href="/decisions" className="nav-link">
                  의사결정
                </a>
                <a href="/dashboard" className="nav-link">
                  대시보드
                </a>
                <a href="/graph" className="nav-link">
                  KG 뷰어
                </a>
                <a href="/docs" className="nav-link">
                  Docs
                </a>
              </nav>
            </div>
          </header>
          <main className="app-main">{children}</main>
          <footer className="app-footer">
            <p>&copy; 2025 HR-DSS. AI 기반 의사결정 지원 시스템</p>
          </footer>
        </div>
      </body>
    </html>
  );
}
