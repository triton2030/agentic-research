import { expect, test } from "@playwright/test";

async function canvasStats(page) {
  return page.evaluate(async () => {
    const canvas = document.querySelector("canvas");
    if (!canvas) return { ok: false, reason: "missing canvas" };

    const url = canvas.toDataURL("image/png");
    const image = new Image();
    image.src = url;
    await image.decode();

    const probe = document.createElement("canvas");
    probe.width = canvas.width;
    probe.height = canvas.height;
    const context = probe.getContext("2d");
    context.drawImage(image, 0, 0);

    const data = context.getImageData(0, 0, probe.width, probe.height).data;
    let nonDark = 0;
    const distinct = new Set();
    const step = Math.max(4, Math.floor(Math.min(probe.width, probe.height) / 48));

    for (let y = 0; y < probe.height; y += step) {
      for (let x = 0; x < probe.width; x += step) {
        const index = (y * probe.width + x) * 4;
        const r = data[index];
        const g = data[index + 1];
        const b = data[index + 2];
        const a = data[index + 3];
        if (a > 0 && r + g + b > 42) nonDark += 1;
        distinct.add(`${r >> 4}-${g >> 4}-${b >> 4}-${a >> 6}`);
      }
    }

    return { ok: true, width: canvas.width, height: canvas.height, nonDark, distinct: distinct.size };
  });
}

test("renders and responds on mobile", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("http://127.0.0.1:5194/");
  await expect(page.getByRole("heading", { name: "Almaty Altitude" }).first()).toBeVisible();
  await page.waitForSelector("canvas");
  await page.waitForTimeout(900);

  const before = await canvasStats(page);
  expect(before.ok).toBe(true);
  expect(before.nonDark).toBeGreaterThan(200);
  expect(before.distinct).toBeGreaterThan(12);

  await page.getByRole("button", { name: /^Night$/ }).click();
  await page.getByRole("button", { name: /^Select Green Bazaar$/ }).click();
  await page.getByRole("button", { name: /^Toggle Metro$/ }).click();
  await page.getByLabel("Primary app navigation").getByRole("button", { name: /^Explore 3D$/ }).click();
  await page.waitForTimeout(500);

  await expect(page.getByText("Green Bazaar").first()).toBeVisible();

  const layout = await page.evaluate(() => ({
    innerWidth,
    scrollWidth: document.documentElement.scrollWidth,
    bodyScrollWidth: document.body.scrollWidth,
  }));
  expect(layout.scrollWidth).toBe(layout.innerWidth);
  expect(layout.bodyScrollWidth).toBe(layout.innerWidth);

  const after = await canvasStats(page);
  expect(after.nonDark).toBeGreaterThan(200);
  expect(after.distinct).toBeGreaterThan(12);
});
