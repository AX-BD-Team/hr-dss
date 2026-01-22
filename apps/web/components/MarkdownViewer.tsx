"use client";

import React from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeHighlight from "rehype-highlight";

export interface MarkdownViewerProps {
  content: string;
  className?: string;
}

export const MarkdownViewer: React.FC<MarkdownViewerProps> = ({
  content,
  className = "",
}) => {
  return (
    <div className={`markdown-viewer ${className}`}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        rehypePlugins={[rehypeHighlight]}
        components={{
          // 테이블 스타일링
          table: ({ children }) => (
            <div className="table-wrapper">
              <table className="markdown-table">{children}</table>
            </div>
          ),
          // 코드 블록 스타일링
          code: ({ className, children, ...props }) => {
            const isInline = !className;
            if (isInline) {
              return (
                <code className="inline-code" {...props}>
                  {children}
                </code>
              );
            }
            return (
              <code className={className} {...props}>
                {children}
              </code>
            );
          },
          // 링크 새 탭에서 열기 (외부 링크)
          a: ({ href, children }) => {
            const isExternal = href?.startsWith("http");
            return (
              <a
                href={href}
                target={isExternal ? "_blank" : undefined}
                rel={isExternal ? "noopener noreferrer" : undefined}
              >
                {children}
              </a>
            );
          },
          // 헤딩에 앵커 추가
          h1: ({ children }) => {
            const id = String(children).toLowerCase().replace(/\s+/g, "-");
            return <h1 id={id}>{children}</h1>;
          },
          h2: ({ children }) => {
            const id = String(children).toLowerCase().replace(/\s+/g, "-");
            return <h2 id={id}>{children}</h2>;
          },
          h3: ({ children }) => {
            const id = String(children).toLowerCase().replace(/\s+/g, "-");
            return <h3 id={id}>{children}</h3>;
          },
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
};

export default MarkdownViewer;
