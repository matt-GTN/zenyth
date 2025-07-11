// ./frontend/next.config.mjs

/** @type {import('next').NextConfig} */
const nextConfig = {
  // Add this rewrites configuration
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        // This proxies any request from /api/... to your backend container.
        // It uses the environment variable we set in docker-compose.
        destination: `${process.env.NEXT_PUBLIC_API_URL}/:path*`,
      },
    ];
  },
};

export default nextConfig;