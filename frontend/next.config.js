/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // 添加这个配置确保静态文件被正确处理
  assetPrefix: process.env.NODE_ENV === 'production' ? '' : '',
  trailingSlash: false,
  images: {
    domains: [
      'i.scdn.co', 
      'upload.wikimedia.org', 
      'supabase.co', 
      'images.unsplash.com', 
      'via.placeholder.com',
      'cdn.fujirockfestival.com'
    ],
    // 添加这个配置
    unoptimized: true
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://127.0.0.1:8000/api/:path*',
      },
      {
        source: '/health',
        destination: 'http://127.0.0.1:8000/health',
      },
    ];
  },
};

module.exports = nextConfig;