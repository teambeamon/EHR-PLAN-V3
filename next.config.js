/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  // Enable experimental app directory
  experimental: {
    appDir: true,
  },
  // For Turso DB
  webpack: (config) => {
    config.externals.push({
      '@libsql/client': 'commonjs @libsql/client',
    });
    return config;
  },
};

module.exports = nextConfig;
