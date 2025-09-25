/** @type {import('next').NextConfig} */
const nextConfig = {
  env: {
    NEXT_PUBLIC_API_URL: 'https://airms-backend-1013218741719.us-central1.run.app',
  },
  // Fix for turbopack warning
  turbopack: {
    // Set the root directory to the current working directory
    root: process.cwd(),
  },
}

module.exports = nextConfig
