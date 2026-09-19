/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  // For Turso DB
  webpack: (config) => {
    config.externals.push({
      '@libsql/client': 'commonjs @libsql/client',
    });
    return config;
  },
  // Rewrite API calls to local backend during development
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/api/:path*',
      },
    ];
  },
};

module.exports = nextConfig;
