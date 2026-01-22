import React from "react";
import { notFound } from "next/navigation";
import { DocsSidebar, docsStructure } from "../../../components/DocsSidebar";
import { MarkdownViewer } from "../../../components/MarkdownViewer";
import { getDocBySlug, getAllDocSlugs } from "../../../lib/docs";

interface Props {
  params: Promise<{
    slug: string[];
  }>;
}

// 정적 경로 생성
export async function generateStaticParams() {
  const slugs = getAllDocSlugs();
  return slugs.map((slug) => ({
    slug: slug.split("/"),
  }));
}

export default async function DocPage({ params }: Props) {
  const { slug } = await params;
  const slugPath = slug.join("/");
  const doc = getDocBySlug(slugPath);

  if (!doc) {
    notFound();
  }

  return (
    <div className="docs-layout">
      <DocsSidebar categories={docsStructure} currentSlug={slugPath} />
      <main className="docs-content">
        <article className="doc-article">
          <header className="doc-header">
            <h1>{doc.metadata.title}</h1>
            {doc.metadata.lastUpdated && (
              <p className="doc-meta">
                마지막 업데이트: {doc.metadata.lastUpdated}
              </p>
            )}
          </header>
          <div className="doc-body">
            <MarkdownViewer content={doc.content} />
          </div>
        </article>

        <nav className="doc-nav">
          <a href="/docs" className="doc-nav-link">
            ← 문서 목록으로
          </a>
        </nav>
      </main>
    </div>
  );
}
