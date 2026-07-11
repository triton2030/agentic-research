import { expect, test } from "@playwright/test";

const APP_URL = "http://127.0.0.1:5194/";

const pageContracts = [
  { name: "Dashboard", content: /almaty|dashboard|overview|today|guide/i },
  { name: "Routes", content: /route|walk|metro|itinerary|day/i },
  { name: "Neighborhoods", content: /neighborhood|district|almaly|bostandyk|medeu/i },
  { name: "Food", content: /food|cafe|coffee|restaurant|bazaar|lagman|baursak/i },
  { name: "Mobility", content: /mobility|metro|bus|taxi|walk|transport/i },
  { name: "Safety", content: /safety|safe|emergency|weather|risk/i },
  { name: "Budget", content: /budget|tenge|kzt|cost|price/i },
  { name: "Planner", content: /planner|plan|itinerary|day|trip/i },
  { name: "Sources", content: /sources|source|data|reference|official/i },
];

const interactivePages = [
  {
    name: "Routes",
    control: (page) => page.getByPlaceholder("Search mountain, market, airport..."),
  },
  {
    name: "Budget",
    control: (page) => page.getByRole("slider", { name: "Budget level" }),
  },
  {
    name: "Planner",
    control: (page) => page.locator(".page-stack").getByRole("button", { name: /^(Save|Saved)$/ }).first(),
  },
];

function exactName(name) {
  return new RegExp(`^\\s*${escapeRegExp(name)}\\s*$`, "i");
}

function escapeRegExp(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function pageTab(page, name) {
  const label = exactName(name);
  return page
    .getByRole("tab", { name: label })
    .or(page.getByRole("link", { name: label }))
    .or(page.getByRole("button", { name: label }))
    .filter({ visible: true })
    .first();
}

async function openCityGuide(page, viewport) {
  await page.setViewportSize(viewport);
  await page.goto(APP_URL);
  await expect(page.getByRole("main")).toBeVisible();
  await expectNoThreeDimensionalSurface(page, "initial load");
}

async function expectNoThreeDimensionalSurface(page, context) {
  await expect(page.locator("canvas"), `${context}: canvas was removed from the flat guide`).toHaveCount(0);
  await expect(page.getByText(/Explore 3D/i), `${context}: retired 3D navigation text is still present`).toHaveCount(0);
}

async function expectNoHorizontalOverflow(page, context) {
  const overflow = await page.evaluate(() => {
    const viewportWidth = window.innerWidth;
    const documentWidth = Math.max(
      document.documentElement.scrollWidth,
      document.body ? document.body.scrollWidth : 0,
    );

    const offenders = [...document.body.querySelectorAll("*")]
      .map((element) => {
        const rect = element.getBoundingClientRect();
        return {
          tag: element.tagName.toLowerCase(),
          id: element.id,
          className: typeof element.className === "string" ? element.className : "",
          text: (element.textContent || "").replace(/\s+/g, " ").trim().slice(0, 80),
          left: Math.floor(rect.left),
          right: Math.ceil(rect.right),
          width: Math.ceil(rect.width),
        };
      })
      .filter((item) => item.width > 0 && (item.left < -2 || item.right > viewportWidth + 2))
      .slice(0, 6);

    return {
      viewportWidth,
      documentWidth,
      overflowBy: documentWidth - viewportWidth,
      offenders,
    };
  });

  expect(
    overflow.documentWidth,
    `${context}: horizontal overflow ${JSON.stringify(overflow)}`,
  ).toBeLessThanOrEqual(overflow.viewportWidth + 2);
}

async function expectTabAndPageContent(page, contract, viewportLabel) {
  await expect(pageTab(page, contract.name), `${contract.name} tab should be visible on ${viewportLabel}`).toBeVisible();
  await pageTab(page, contract.name).click();

  const main = page.getByRole("main");
  await expect(
    page.locator(".page-kicker"),
    `${contract.name} page should expose its page name`,
  ).toHaveText(exactName(contract.name));
  await expect(main, `${contract.name} page should expose page-specific content`).toContainText(contract.content);
  await expectNoThreeDimensionalSurface(page, contract.name);
  await expectNoHorizontalOverflow(page, `${viewportLabel} ${contract.name}`);
}

async function interactiveState(page) {
  return page.getByRole("main").evaluate((main) => ({
    text: main.innerText.replace(/\s+/g, " ").trim(),
    controls: [...main.querySelectorAll("button, a, input, select, textarea, [role]")]
      .map((element) => ({
        tag: element.tagName.toLowerCase(),
        role: element.getAttribute("role") || "",
        label:
          element.getAttribute("aria-label") ||
          element.getAttribute("title") ||
          element.textContent?.replace(/\s+/g, " ").trim() ||
          "",
        ariaPressed: element.getAttribute("aria-pressed") || "",
        ariaSelected: element.getAttribute("aria-selected") || "",
        ariaCurrent: element.getAttribute("aria-current") || "",
        checked: "checked" in element ? element.checked : null,
        value: "value" in element ? element.value : null,
      }))
      .filter((control) => control.label || control.role || control.value !== null),
  }));
}

async function exercisePageInteraction(page, interaction, viewportLabel) {
  await pageTab(page, interaction.name).click();
  const main = page.getByRole("main");
  await expect(page.locator(".page-kicker")).toHaveText(exactName(interaction.name));

  const control = interaction.control(page);
  await expect(
    control,
    `${interaction.name} should expose at least one accessible control on ${viewportLabel}`,
  ).toBeVisible();

  const before = await interactiveState(page);
  const controlKind = await control.evaluate((element) => ({
    tag: element.tagName.toLowerCase(),
    type: element.getAttribute("type") || "",
    role: element.getAttribute("role") || "",
  }));

  if (controlKind.role === "slider" || controlKind.type === "range") {
    await control.focus();
    await page.keyboard.press("ArrowRight");
  } else if (controlKind.tag === "input" && ["", "number", "text", "search"].includes(controlKind.type)) {
    await control.fill(controlKind.type === "number" ? "2" : "Almaty");
  } else if (controlKind.tag === "textarea") {
    await control.fill("Almaty");
  } else if (controlKind.tag === "select") {
    const options = await control.locator("option").evaluateAll((items) => items.map((item) => item.value));
    if (options.length > 1) await control.selectOption(options[1]);
    else await control.focus();
  } else {
    await control.click();
  }

  await expect(
    page.locator(".page-kicker"),
    `${interaction.name} should remain visible after interaction`,
  ).toHaveText(exactName(interaction.name));
  await expect.poll(() => interactiveState(page), {
    message: `${interaction.name} interaction should update visible text or accessible control state`,
  }).not.toEqual(before);
  await expectNoThreeDimensionalSurface(page, `${interaction.name} interaction`);
  await expectNoHorizontalOverflow(page, `${viewportLabel} ${interaction.name} interaction`);
}

async function runMultiPageSmoke(page, viewportLabel, viewport) {
  await openCityGuide(page, viewport);

  for (const contract of pageContracts) {
    await expectTabAndPageContent(page, contract, viewportLabel);
  }

  for (const interaction of interactivePages) {
    await exercisePageInteraction(page, interaction, viewportLabel);
  }
}

test("desktop flat city guide smoke", async ({ page }) => {
  await runMultiPageSmoke(page, "desktop", { width: 1440, height: 1000 });
});

test("mobile flat city guide smoke", async ({ page }) => {
  await runMultiPageSmoke(page, "mobile", { width: 390, height: 844 });
});
