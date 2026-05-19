import { readFile, writeFile, mkdir } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { D2 } from "@terrastruct/d2";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, "..");
const inputPath = path.resolve(process.argv[2] || path.join(root, "data", "skillmap.d2"));
const outputPath = path.resolve(process.argv[3] || path.join(root, "generated", "skillmap.svg"));

const source = await readFile(inputPath, "utf8");
const d2 = new D2();

const result = await d2.compile(source, {
  layout: "elk",
  themeID: 101,
  pad: 48,
  scale: 1
});

const svg = await d2.render(result.diagram, {
  ...result.renderOptions,
  center: true,
  pad: 48,
  scale: 1
});

await mkdir(path.dirname(outputPath), { recursive: true });
await writeFile(outputPath, svg);
await d2.worker?.terminate?.();

console.log(`generated ${path.relative(root, outputPath)}`);
