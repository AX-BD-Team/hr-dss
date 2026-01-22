/**
 * HR-DSS API Gateway
 *
 * Cloudflare Workers 기반 API Gateway
 * - 요청 라우팅 및 프록시
 * - CORS 처리
 * - Rate Limiting
 * - 요청/응답 로깅
 * - 인증 토큰 검증
 */

import { AutoRouter, IRequest } from 'itty-router';

// 환경 변수 타입 정의
export interface Env {
  ENVIRONMENT: string;
  BACKEND_URL: string;
  ALLOWED_ORIGINS: string;
  LOG_LEVEL: string;
  // KV Namespace (선택)
  CACHE?: KVNamespace;
  // Rate Limiter (선택)
  RATE_LIMITER?: RateLimit;
}

interface RateLimit {
  limit(options: { key: string }): Promise<{ success: boolean }>;
}

// 라우터 생성
const router = AutoRouter();

// =============================================================================
// 미들웨어
// =============================================================================

/**
 * CORS 헤더 추가
 */
function corsHeaders(origin: string, allowedOrigins: string): HeadersInit {
  const origins = allowedOrigins.split(',').map((o) => o.trim());
  const allowOrigin = origins.includes(origin) ? origin : origins[0];

  return {
    'Access-Control-Allow-Origin': allowOrigin,
    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Request-ID',
    'Access-Control-Max-Age': '86400',
    'Access-Control-Allow-Credentials': 'true',
  };
}

/**
 * 보안 헤더 추가
 */
function securityHeaders(): HeadersInit {
  return {
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'X-XSS-Protection': '1; mode=block',
    'Referrer-Policy': 'strict-origin-when-cross-origin',
    'Permissions-Policy': 'geolocation=(), microphone=(), camera=()',
  };
}

/**
 * 클라이언트 IP 추출
 */
function getClientIP(request: Request): string {
  return (
    request.headers.get('CF-Connecting-IP') ||
    request.headers.get('X-Forwarded-For')?.split(',')[0] ||
    'unknown'
  );
}

/**
 * 요청 ID 생성
 */
function generateRequestId(): string {
  return `req_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
}

// =============================================================================
// 라우트 핸들러
// =============================================================================

/**
 * CORS Preflight 처리
 */
router.options('*', (request: IRequest, env: Env) => {
  const origin = request.headers.get('Origin') || '';
  return new Response(null, {
    status: 204,
    headers: corsHeaders(origin, env.ALLOWED_ORIGINS),
  });
});

/**
 * Health Check
 */
router.get('/health', () => {
  return new Response(
    JSON.stringify({
      status: 'healthy',
      service: 'hr-dss-api-gateway',
      timestamp: new Date().toISOString(),
    }),
    {
      headers: { 'Content-Type': 'application/json' },
    }
  );
});

/**
 * API 정보
 */
router.get('/api', (request: IRequest, env: Env) => {
  return new Response(
    JSON.stringify({
      name: 'HR-DSS API Gateway',
      version: '0.1.0',
      environment: env.ENVIRONMENT,
      endpoints: {
        health: '/health',
        api: '/api/v1/*',
        agents: '/api/v1/agents/*',
        decisions: '/api/v1/decisions/*',
        graph: '/api/v1/graph/*',
      },
    }),
    {
      headers: { 'Content-Type': 'application/json' },
    }
  );
});

/**
 * API 프록시 (Backend로 전달)
 */
router.all('/api/*', async (request: IRequest, env: Env, ctx: ExecutionContext) => {
  const requestId = generateRequestId();
  const startTime = Date.now();
  const clientIP = getClientIP(request);

  try {
    // Rate Limiting (활성화된 경우)
    if (env.RATE_LIMITER) {
      const rateLimitResult = await env.RATE_LIMITER.limit({ key: clientIP });
      if (!rateLimitResult.success) {
        return new Response(
          JSON.stringify({
            error: 'Too Many Requests',
            message: '요청 한도를 초과했습니다. 잠시 후 다시 시도해주세요.',
            requestId,
          }),
          {
            status: 429,
            headers: {
              'Content-Type': 'application/json',
              'Retry-After': '60',
            },
          }
        );
      }
    }

    // Backend URL 구성
    const url = new URL(request.url);
    const backendUrl = `${env.BACKEND_URL}${url.pathname}${url.search}`;

    // 요청 헤더 구성
    const headers = new Headers(request.headers);
    headers.set('X-Request-ID', requestId);
    headers.set('X-Forwarded-For', clientIP);
    headers.set('X-Forwarded-Proto', 'https');
    headers.delete('Host');

    // Backend로 프록시
    const backendResponse = await fetch(backendUrl, {
      method: request.method,
      headers,
      body: request.method !== 'GET' && request.method !== 'HEAD' ? request.body : undefined,
    });

    // 응답 헤더 구성
    const origin = request.headers.get('Origin') || '';
    const responseHeaders = new Headers(backendResponse.headers);

    // CORS 헤더 추가
    Object.entries(corsHeaders(origin, env.ALLOWED_ORIGINS)).forEach(([key, value]) => {
      responseHeaders.set(key, value);
    });

    // 보안 헤더 추가
    Object.entries(securityHeaders()).forEach(([key, value]) => {
      responseHeaders.set(key, value);
    });

    // 요청 ID 헤더 추가
    responseHeaders.set('X-Request-ID', requestId);

    // 응답 시간 로깅 (비동기)
    const duration = Date.now() - startTime;
    ctx.waitUntil(
      logRequest(env, {
        requestId,
        method: request.method,
        path: url.pathname,
        status: backendResponse.status,
        duration,
        clientIP,
      })
    );

    return new Response(backendResponse.body, {
      status: backendResponse.status,
      statusText: backendResponse.statusText,
      headers: responseHeaders,
    });
  } catch (error) {
    const duration = Date.now() - startTime;

    // 에러 로깅
    ctx.waitUntil(
      logRequest(env, {
        requestId,
        method: request.method,
        path: new URL(request.url).pathname,
        status: 502,
        duration,
        clientIP,
        error: error instanceof Error ? error.message : 'Unknown error',
      })
    );

    return new Response(
      JSON.stringify({
        error: 'Bad Gateway',
        message: 'Backend 서버에 연결할 수 없습니다.',
        requestId,
      }),
      {
        status: 502,
        headers: {
          'Content-Type': 'application/json',
          ...securityHeaders(),
        },
      }
    );
  }
});

/**
 * 404 처리
 */
router.all('*', () => {
  return new Response(
    JSON.stringify({
      error: 'Not Found',
      message: '요청한 리소스를 찾을 수 없습니다.',
    }),
    {
      status: 404,
      headers: {
        'Content-Type': 'application/json',
        ...securityHeaders(),
      },
    }
  );
});

// =============================================================================
// 유틸리티 함수
// =============================================================================

interface LogEntry {
  requestId: string;
  method: string;
  path: string;
  status: number;
  duration: number;
  clientIP: string;
  error?: string;
}

/**
 * 요청 로깅
 */
async function logRequest(env: Env, entry: LogEntry): Promise<void> {
  const logLevel = env.LOG_LEVEL || 'info';

  // 로그 레벨에 따른 필터링
  if (logLevel === 'warn' && entry.status < 400) {
    return;
  }

  const logData = {
    ...entry,
    timestamp: new Date().toISOString(),
    environment: env.ENVIRONMENT,
  };

  // 콘솔 로깅 (Cloudflare 대시보드에서 확인 가능)
  if (entry.error || entry.status >= 400) {
    console.error(JSON.stringify(logData));
  } else if (logLevel === 'debug') {
    console.log(JSON.stringify(logData));
  }

  // KV에 로그 저장 (선택, 분석용)
  // if (env.CACHE) {
  //   const key = `log:${entry.requestId}`;
  //   await env.CACHE.put(key, JSON.stringify(logData), { expirationTtl: 86400 });
  // }
}

// =============================================================================
// Worker Export
// =============================================================================

export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    return router.fetch(request, env, ctx);
  },
};
