import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import fs from "fs";
import path from "path";

function syncFlaskTemplatePlugin() {
  return {
    name: "sync-flask-template",
    closeBundle() {
      const generatedHtml = path.resolve(__dirname, "static", "index.html");
      const templateTarget = path.resolve(__dirname, "templates", "index.html");
      if (fs.existsSync(generatedHtml)) {
        if (!fs.existsSync(path.dirname(templateTarget))) {
          fs.mkdirSync(path.dirname(templateTarget), { recursive: true });
        }
        fs.copyFileSync(generatedHtml, templateTarget);
        fs.unlinkSync(generatedHtml);
        console.log("[Vite] Synced minimal React template to templates/index.html");
      }
    },
  };
}

export default defineConfig(({ command }) => ({
  plugins: [react(), syncFlaskTemplatePlugin()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  base: command === "build" ? "/static/" : "/",
  build: {
    outDir: "static",
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
    host: "0.0.0.0",
    port: 5173,
    proxy: {
      "/query": {
        target: "http://127.0.0.1:5000",
        changeOrigin: true,
        configure: (proxy) => {
          proxy.on("error", (err, req, res) => {
            if (res && !res.headersSent && typeof res.writeHead === "function") {
              res.writeHead(503, { "Content-Type": "application/json" });
              res.end(JSON.stringify({ error: "Backend not available." }));
            }
          });
        },
      },
      "/health": {
        target: "http://127.0.0.1:5000",
        changeOrigin: true,
        configure: (proxy) => {
          proxy.on("error", (err, req, res) => {
            if (res && !res.headersSent && typeof res.writeHead === "function") {
              res.writeHead(503, { "Content-Type": "application/json" });
              res.end(JSON.stringify({ status: "unavailable" }));
            }
          });
        },
      },
      "/history": {
        target: "http://127.0.0.1:5000",
        changeOrigin: true,
      },
    },
  },
}));
