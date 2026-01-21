/** @type {import('next').NextConfig} */
const nextConfig = {
  // Cloudflare Pages 호환성
  output: 'export',

  // 이미지 최적화 (Cloudflare에서는 비활성화)
  images: {
    unoptimized: true,
  },

  // 환경 변수
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
    NEXT_PUBLIC_ENVIRONMENT: process.env.NEXT_PUBLIC_ENVIRONMENT || 'development',
  },

  // 정적 파일 경로
  assetPrefix: process.env.ASSET_PREFIX || '',

  // 트레일링 슬래시
  trailingSlash: false,

  // 실험적 기능
  experimental: {
    // Cloudflare Pages 지원
  },

  // 웹팩 설정
  webpack: (config, { isServer }) => {
    // 클라이언트 사이드 폴리필
    if (!isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
        net: false,
        tls: false,
      };
    }
    return config;
  },
};

module.exports = nextConfig;
