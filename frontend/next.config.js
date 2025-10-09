/** @type {import('next').NextConfig} */
const nextConfig = {
  env: {
    // Ensure we're always using HTTPS for the backend
    NEXT_PUBLIC_API_URL: 'http://localhost:8000',
  },
  // Fix for turbopack warning
  turbopack: {
    root: process.cwd(),
  },
  // Proxy API requests through Next.js to avoid CORS issues
  async rewrites() {
    return [
      {
        source: '/api/v1/:path*',
        destination: 'http://localhost:8000/api/v1/:path*',
      },
    ];
  },
  // Security headers
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          { key: 'X-Content-Type-Options', value: 'nosniff' },
          { key: 'X-Frame-Options', value: 'DENY' },
          { key: 'X-XSS-Protection', value: '1; mode=block' },
        ],
      },
    ];
  },
}

module.exports = nextConfig