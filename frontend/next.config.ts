import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,

  // Environment variables
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },

  // API rewrites for development
  async rewrites() {
    // In production, frontend calls backend directly via NEXT_PUBLIC_API_URL
    // In development, proxy API requests to avoid CORS
    if (process.env.NODE_ENV === 'development') {
      return [
        {
          source: '/api/:path*',
          destination: `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/:path*`,
        },
      ];
    }
    return [];
  },
};

export default nextConfig;
