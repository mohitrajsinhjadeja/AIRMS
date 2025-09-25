import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  env: {
    NEXT_PUBLIC_API_URL: 'https://airms-backend-1013218741719.us-central1.run.app',
  },
  output: 'standalone',
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'https://airms-backend-1013218741719.us-central1.run.app/api/:path*',
      },
    ];
  },
  experimental: {
    // Remove the outputStandalone property as it's deprecated
    // and you're already using output: 'standalone' above
  },
};

export default nextConfig;
