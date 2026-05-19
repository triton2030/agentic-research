import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const LAYOUTS_DIR = path.join(__dirname, "data", "layouts");

// Custom dev-сервер plugin: позволяет фронту читать/писать snapshot раскладки
// прямо в файл. Файлы коммитятся в git, чтобы другой человек открыл проект и
// получил тот же граф, viewport и ELK-пресет.
function layoutFileApi() {
  return {
    name: "flowpage-layout-api",
    configureServer(server) {
      server.middlewares.use("/api/layout/", async (req, res) => {
        try {
          const url = new URL(req.url, "http://localhost");
          const pageId = decodeURIComponent(url.pathname.replace(/^\//, "").replace(/\/$/, ""));
          if (!pageId || /[\/\\]/.test(pageId)) {
            res.statusCode = 400;
            res.end('{"error":"bad pageId"}');
            return;
          }
          const filePath = path.join(LAYOUTS_DIR, `${pageId}.json`);

          if (req.method === "GET") {
            try {
              const content = await fs.promises.readFile(filePath, "utf-8");
              res.setHeader("Content-Type", "application/json");
              res.end(content);
            } catch (e) {
              if (e.code === "ENOENT") {
                res.statusCode = 404;
                res.end('{"error":"not found"}');
              } else {
                res.statusCode = 500;
                res.end(JSON.stringify({ error: e.message }));
              }
            }
            return;
          }

          if (req.method === "POST" || req.method === "PUT") {
            const chunks = [];
            for await (const chunk of req) chunks.push(chunk);
            const body = Buffer.concat(chunks).toString("utf-8");
            // Validate JSON
            try {
              JSON.parse(body);
            } catch (e) {
              res.statusCode = 400;
              res.end('{"error":"invalid json"}');
              return;
            }
            await fs.promises.mkdir(LAYOUTS_DIR, { recursive: true });
            await fs.promises.writeFile(filePath, body, "utf-8");
            res.setHeader("Content-Type", "application/json");
            res.end(JSON.stringify({ ok: true, path: `data/layouts/${pageId}.json` }));
            return;
          }

          res.statusCode = 405;
          res.end('{"error":"method not allowed"}');
        } catch (e) {
          res.statusCode = 500;
          res.end(JSON.stringify({ error: String(e) }));
        }
      });
    }
  };
}

export default defineConfig({
  base: "./",
  plugins: [react(), layoutFileApi()],
  build: {
    outDir: "dist",
    emptyOutDir: true
  },
  server: {
    host: "127.0.0.1",
    port: 5176
  }
});
