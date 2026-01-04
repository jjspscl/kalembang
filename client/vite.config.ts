import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  const isDemo = env.VITE_DEMO_MODE === "true";

  return {
    plugins: [react()],
    base: "/",
    build: {
      outDir: "dist",
      sourcemap: false,
      minify: "esbuild",
      rollupOptions: {
        output: {
          manualChunks: {
            vendor: ["react", "react-dom"],
            router: ["@tanstack/react-router"],
            query: ["@tanstack/react-query"],
            motion: ["motion"],
          },
        },
      },
    },
    server: {
      host: "0.0.0.0",
      port: 5173,
      proxy: isDemo
        ? undefined
        : {
            "/api": {
              target: "http://localhost:8088",
              changeOrigin: true,
            },
          },
    },
    preview: {
      host: "0.0.0.0",
      port: 5173,
    },
  };
});
