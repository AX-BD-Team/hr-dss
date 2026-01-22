import fs from 'fs';
import path from 'path';
import matter from 'gray-matter';

// docs 폴더 경로 (프로젝트 루트 기준)
const docsDirectory = path.join(process.cwd(), '../../docs');

export interface DocMetadata {
  title: string;
  description?: string;
  lastUpdated?: string;
  version?: string;
}

export interface DocContent {
  slug: string;
  content: string;
  metadata: DocMetadata;
}

/**
 * 문서 파일 읽기
 */
export function getDocBySlug(slug: string): DocContent | null {
  try {
    // slug를 파일 경로로 변환
    const filePath = path.join(docsDirectory, `${slug}.md`);

    if (!fs.existsSync(filePath)) {
      return null;
    }

    const fileContents = fs.readFileSync(filePath, 'utf8');
    const { data, content } = matter(fileContents);

    // 제목 추출 (frontmatter 또는 첫 번째 h1)
    let title = data.title;
    if (!title) {
      const h1Match = content.match(/^#\s+(.+)$/m);
      title = h1Match ? h1Match[1] : slug.split('/').pop() || 'Untitled';
    }

    return {
      slug,
      content,
      metadata: {
        title,
        description: data.description,
        lastUpdated: data.lastUpdated || data['마지막 업데이트'],
        version: data.version,
      },
    };
  } catch (error) {
    console.error(`Error reading doc: ${slug}`, error);
    return null;
  }
}

/**
 * 모든 문서 슬러그 가져오기
 */
export function getAllDocSlugs(): string[] {
  const slugs: string[] = [];

  function scanDirectory(dir: string, prefix: string = '') {
    try {
      const items = fs.readdirSync(dir);

      for (const item of items) {
        const fullPath = path.join(dir, item);
        const stat = fs.statSync(fullPath);

        if (stat.isDirectory()) {
          // archive 폴더는 제외
          if (item !== 'archive') {
            scanDirectory(fullPath, prefix ? `${prefix}/${item}` : item);
          }
        } else if (item.endsWith('.md')) {
          const slug = prefix
            ? `${prefix}/${item.replace('.md', '')}`
            : item.replace('.md', '');
          slugs.push(slug);
        }
      }
    } catch (error) {
      console.error(`Error scanning directory: ${dir}`, error);
    }
  }

  scanDirectory(docsDirectory);
  return slugs;
}

/**
 * 문서 존재 여부 확인
 */
export function docExists(slug: string): boolean {
  const filePath = path.join(docsDirectory, `${slug}.md`);
  return fs.existsSync(filePath);
}
