import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import fs from "fs";
import path from "path";

function syncFlaskTemplatePlugin() {
  return {
    name: "sync-flask-template",
    closeBundle() {
      const generatedHtml = path.resolve(__dirname, "frontend", "static", "index.html");
      const templateTarget = path.resolve(__dirname, "frontend", "templates", "index.html");
      if (fs.existsSync(generatedHtml)) {
        fs.copyFileSync(generatedHtml, templateTarget);
        fs.unlinkSync(generatedHtml);
        console.log("[Vite] Synced minimal React template to frontend/templates/index.html");
      }
    },
  };
}

export default defineConfig({
  plugins: [react(), syncFlaskTemplatePlugin()],
  base: "/static/",
  build: {
    outDir: "frontend/static",
    emptyOutDir: false,
    rollupOptions: {
      output: {
        entryFileNames: "assets/[name].[hash].js",
        chunkFileNames: "assets/[name].[hash].js",
        assetFileNames: "assets/[name].[hash].[ext]",
      },
    },
  },
  server: {
    port: 5173,
    proxy: {
      "/query": "http://127.0.0.1:5000",
      "/health": "http://127.0.0.1:5000",
      "/history": "http://127.0.0.1:5000",
    },
  },
});
