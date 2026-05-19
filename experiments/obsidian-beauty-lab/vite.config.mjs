import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  base: "./",
  plugins: [react()],
  build: {
    outDir: "dist/flowpage",
    emptyOutDir: true,
    rollupOptions: {
      input: "flowpage.html"
    }
  },
  server: {
    host: "127.0.0.1"
  }
});
