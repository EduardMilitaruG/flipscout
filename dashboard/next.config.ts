import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  images: {
    remotePatterns: [
      { protocol: "https", hostname: "zenmarket.jp" },
      { protocol: "https", hostname: "**.mercari.com" },
    ],
  },
};

export default nextConfig;
