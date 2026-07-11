import { expect, test } from "@playwright/test";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { DEFAULT_OPTIONS, layoutGraph } from "../src/graph/layout.js";

const experimentRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

function loadMapPage(fileName) {
  return JSON.parse(fs.readFileSync(path.join(experimentRoot, "src/maps/pages", fileName), "utf8"));
}

async function getNodeTransforms(page) {
  return page.locator(".react-flow__node").evaluateAll((nodes) =>
    Object.fromEntries(nodes.map((node) => [node.getAttribute("data-id"), node.style.transform]))
  );
}

async function getVisibleNodeBoxes(page) {
  return page.locator(".logic-node").evaluateAll((nodes) =>
    nodes.map((node) => {
      const rect = node.getBoundingClientRect();
      return {
        id: node.closest(".react-flow__node")?.getAttribute("data-id"),
        left: rect.left,
        right: rect.right,
        top: rect.top,
        bottom: rect.bottom
      };
    })
  );
}

async function getVisibleEdgeLabelBoxes(page) {
  return page.locator(".causal-edge-label").evaluateAll((labels) =>
    labels.map((label) => {
      const rect = label.getBoundingClientRect();
      return {
        id: label.textContent.trim(),
        left: rect.left,
        right: rect.right,
        top: rect.top,
        bottom: rect.bottom
      };
    })
  );
}

function findOverlaps(boxes) {
  const overlaps = [];

  for (let index = 0; index < boxes.length; index += 1) {
    for (let nextIndex = index + 1; nextIndex < boxes.length; nextIndex += 1) {
      const a = boxes[index];
      const b = boxes[nextIndex];
      const separated = a.right <= b.left || b.right <= a.left || a.bottom <= b.top || b.bottom <= a.top;
      if (!separated) overlaps.push(`${a.id}:${b.id}`);
    }
  }

  return overlaps;
}

function findCrossOverlaps(aBoxes, bBoxes) {
  const overlaps = [];

  for (const a of aBoxes) {
    for (const b of bBoxes) {
      const separated = a.right <= b.left || b.right <= a.left || a.bottom <= b.top || b.bottom <= a.top;
      if (!separated) overlaps.push(`${a.id}:${b.id}`);
    }
  }

  return overlaps;
}

async function getClippedReaderBlocks(page) {
  return page.locator(".inspector").evaluate((inspector) =>
    Array.from(inspector.querySelectorAll("h2, p, blockquote, figcaption, .reader-link span, .reader-link strong, .reader-link small"))
      .filter((element) => element.scrollHeight > element.clientHeight + 1 || element.scrollWidth > element.clientWidth + 1)
      .map((element) => element.textContent.trim().slice(0, 80))
  );
}

async function clickEdgeInteractionPath(page, edgeId) {
  const interactionPath = page.locator(`.react-flow__edge[data-id="${edgeId}"] .react-flow__edge-interaction`);
  await expect(interactionPath).toHaveCount(1);

  const points = await interactionPath.evaluate((path) => {
    const length = path.getTotalLength();
    const matrix = path.getScreenCTM();

    return [0.05, 0.1, 0.25, 0.75, 0.9, 0.95].map((ratio) => {
      const point = path.getPointAtLength(length * ratio);
      return {
        x: point.x * matrix.a + point.y * matrix.c + matrix.e,
        y: point.x * matrix.b + point.y * matrix.d + matrix.f
      };
    });
  });

  const hitTargets = await Promise.all(
    points.map((point) =>
      page.evaluate(({ x, y }) => {
        const element = document.elementFromPoint(x, y);
        return {
          point: { x, y },
          edgeId: element?.closest(".react-flow__edge")?.getAttribute("data-id") ?? null,
          isLabel: Boolean(element?.closest(".causal-edge-label")),
          className: element?.getAttribute("class") ?? ""
        };
      }, point)
    )
  );
  const hitTarget = hitTargets.find((target) => target.edgeId === edgeId && !target.isLabel);

  expect(hitTarget).toBeTruthy();
  expect(hitTarget.edgeId).toBe(edgeId);
  expect(hitTarget.isLabel).toBe(false);
  expect(hitTarget.className).toContain("react-flow__edge-interaction");
  await page.mouse.click(hitTarget.point.x, hitTarget.point.y);
}

test("layoutGraph returns finite ELK label centers", async () => {
  for (const fileName of ["agent-map-authoring.json", "mavo-render-factory.json", "mavo-short-profitability.json"]) {
    const map = loadMapPage(fileName);
    const { edgeLayouts } = await layoutGraph(map.nodes, map.edges, DEFAULT_OPTIONS);

    expect(edgeLayouts.size, fileName).toBe(map.edges.length);
    for (const edge of map.edges) {
      const labelCenter = edgeLayouts.get(edge.id)?.labelCenter;
      expect(labelCenter, `${fileName}:${edge.id}`).toBeTruthy();
      expect(Number.isFinite(labelCenter.x), `${fileName}:${edge.id}:x`).toBeTruthy();
      expect(Number.isFinite(labelCenter.y), `${fileName}:${edge.id}:y`).toBeTruthy();
    }
  }
});

test("logic map supports the core reading flow", async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 900 });
  await page.goto("http://127.0.0.1:5182/");

  await expect(page.locator(".app-shell")).toHaveClass(/theme-light/);
  await page.getByRole("button", { name: "Включить ночную тему" }).click();
  await expect(page.locator("html")).toHaveAttribute("data-theme", "dark");
  await expect(page.locator(".app-shell")).toHaveClass(/theme-dark/);

  await page.getByRole("button", { name: "Скрыть левое меню" }).click();
  await expect(page.locator(".app-shell")).toHaveClass(/app-shell--sidebar-collapsed/);
  await expect(page.getByRole("button", { name: "Показать левое меню" })).toBeVisible();
  await expect(page.getByLabel("Карта")).toHaveCount(0);

  await page.getByRole("button", { name: "Показать левое меню" }).click();
  await expect(page.locator(".app-shell")).not.toHaveClass(/app-shell--sidebar-collapsed/);
  await expect(page.getByLabel("Карта")).toBeVisible();

  await expect(page.locator('.react-flow__node[data-id="vision"] h3')).toHaveText("Видение: фабрика одного владельца");
  await expect(page.locator(".logic-node--collapsed")).toHaveCount(13);
  await expect(page.locator(".logic-node--expanded")).toHaveCount(0);
  await expect(page.locator(".causal-edge-label")).toHaveCount(18);
  const reader = page.locator(".inspector");
  await expect(reader.getByText("Связи этой ноды")).toBeVisible();
  await expect(reader.locator(".detail-block--link")).toHaveCount(0);

  const initialTransforms = await getNodeTransforms(page);
  await page.locator('.react-flow__node[data-id="vision"] .logic-node').click();
  await expect(page.locator(".logic-node--expanded")).toHaveCount(0);
  await expect(reader.getByText("Что из этого следует")).toBeVisible();
  await expect(reader.getByRole("button", { name: /правила вместо ручной работы/ })).toBeVisible();
  await expect(reader.getByText("Если владелец должен масштабировать каталог")).toHaveCount(0);
  expect(await getNodeTransforms(page)).toEqual(initialTransforms);
  const nodeBoxes = await getVisibleNodeBoxes(page);
  const edgeLabelBoxes = await getVisibleEdgeLabelBoxes(page);
  expect(findOverlaps(nodeBoxes)).toEqual([]);
  expect(findOverlaps(edgeLabelBoxes)).toEqual([]);
  expect(findCrossOverlaps(edgeLabelBoxes, nodeBoxes)).toEqual([]);
  expect(await getClippedReaderBlocks(page)).toEqual([]);

  const afterFirstClickTransforms = await getNodeTransforms(page);
  await page.locator('.react-flow__node[data-id="template-language"] .logic-node').click();
  await expect(page.locator(".logic-node--expanded")).toHaveCount(0);
  await expect(reader.getByText("Что ведёт сюда")).toBeVisible();
  await expect(reader.getByText("правила вместо ручной работы")).toBeVisible();
  expect(await getNodeTransforms(page)).toEqual(afterFirstClickTransforms);
  const nodeBoxesAfterSecondClick = await getVisibleNodeBoxes(page);
  const edgeLabelBoxesAfterSecondClick = await getVisibleEdgeLabelBoxes(page);
  expect(findOverlaps(nodeBoxesAfterSecondClick)).toEqual([]);
  expect(findOverlaps(edgeLabelBoxesAfterSecondClick)).toEqual([]);
  expect(findCrossOverlaps(edgeLabelBoxesAfterSecondClick, nodeBoxesAfterSecondClick)).toEqual([]);
  expect(await getClippedReaderBlocks(page)).toEqual([]);

  await page.getByRole("button", { name: "Показать главную цепочку" }).click();
  await expect(page.getByRole("button", { name: "Показать всё" })).toBeVisible();
  await expect(page.getByText("Главная цепочка")).toBeVisible();

  await reader.getByRole("button", { name: /правила вместо ручной работы/ }).click();
  await expect(reader.getByText("Ребро · задаёт")).toBeVisible();
  await expect(reader.getByRole("heading", { name: "правила вместо ручной работы" })).toBeVisible();
  await expect(reader.getByText("Если владелец должен масштабировать каталог")).toBeVisible();
  await expect(reader.getByText("Цитаты для этой связи")).toBeVisible();
  await expect(reader.getByText("00_Основа/01_Видение.md:42")).toBeVisible();
  await expect(reader.getByText("Что это за нода")).toHaveCount(0);

  await page.locator('.react-flow__node[data-id="vision"] .logic-node').click();
  await page.locator(".causal-edge-label", { hasText: "правила вместо ручной работы" }).click();
  await expect(reader.getByText("Ребро · задаёт")).toBeVisible();
  await expect(reader.getByRole("heading", { name: "правила вместо ручной работы" })).toBeVisible();
  await expect(reader.getByText("Что это за нода")).toHaveCount(0);

  await page.locator('.react-flow__node[data-id="vision"] .logic-node').click();
  await clickEdgeInteractionPath(page, "e1");
  await expect(reader.getByText("Ребро · задаёт")).toBeVisible();
  await expect(reader.getByText("00_Основа/01_Видение.md:42")).toBeVisible();
  await expect(reader.getByText("Что это за нода")).toHaveCount(0);

  await expect(page.locator(".logic-node__handle")).toHaveCount(104);
  const edgePaths = await page.locator(".react-flow__edge-path").evaluateAll((paths) =>
    paths.map((path) => path.getAttribute("d") ?? "")
  );
  expect(edgePaths.length).toBeGreaterThan(0);
  expect(edgePaths.every((path) => path.includes(" C"))).toBeTruthy();

  await expect(page.getByText("Настройки графа")).toBeVisible();
  await expect(page.getByLabel("Между слоями")).toBeVisible();
  await expect(page.getByLabel("Маршрут рёбер")).toBeVisible();
  await expect(page.getByLabel("Маршрут рёбер")).toHaveValue("SPLINES");

  await page.getByLabel("Карта").selectOption("agent-map-authoring");
  await expect(page.getByRole("heading", { name: "Формат записи нод, рёбер и обоснований" })).toBeVisible();
  await expect(page.locator(".logic-node--collapsed")).toHaveCount(6);
  expect(findOverlaps(await getVisibleEdgeLabelBoxes(page))).toEqual([]);
  await page.locator('.react-flow__node[data-id="source"] .logic-node').click();
  await expect(page.locator(".logic-node--expanded")).toHaveCount(0);
  await expect(reader.getByText("Связи этой ноды")).toBeVisible();

  await page.getByLabel("Карта").selectOption("mavo-short-profitability");
  await expect(page.getByText("15 нод / 18 связей")).toBeVisible();
  await expect(page.locator('.react-flow__node[data-id="studio-pain"] h3')).toHaveText("Малой студии больно делать ручной prepress до денег");
  await expect(page.locator(".logic-node--collapsed")).toHaveCount(15);
  await expect(page.locator(".causal-edge-label")).toHaveCount(18);
  await expect(page.locator('.react-flow__node[data-id="profit-verdict-owner"]')).toHaveCount(1);
  const profitabilityNodeBoxes = await getVisibleNodeBoxes(page);
  const profitabilityLabelBoxes = await getVisibleEdgeLabelBoxes(page);
  expect(findOverlaps(profitabilityNodeBoxes)).toEqual([]);
  expect(findOverlaps(profitabilityLabelBoxes)).toEqual([]);
  expect(findCrossOverlaps(profitabilityLabelBoxes, profitabilityNodeBoxes)).toEqual([]);

  await reader.getByRole("button", { name: /боль требует принятой заявки/ }).click();
  await expect(reader.getByText("Ребро · задаёт")).toBeVisible();
  await expect(reader.getByRole("heading", { name: "боль требует принятой заявки" })).toBeVisible();
  await expect(reader.getByText("Цитаты для этой связи")).toBeVisible();
  await expect(reader.getByText("Проблемы_студий.md:21")).toBeVisible();
  await expect(reader.getByText("Что это за нода")).toHaveCount(0);
});
