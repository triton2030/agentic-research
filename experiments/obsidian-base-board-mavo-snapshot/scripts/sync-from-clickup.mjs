#!/usr/bin/env node

import { execFileSync } from "node:child_process";
import { mkdirSync, readdirSync, rmSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const workspaceId = "25510580";
const lists = new Map([
  ["901819472722", "Бизнес"],
  ["901819472723", "Дизайн"],
  ["901819472726", "Разработка"],
]);
const here = dirname(fileURLToPath(import.meta.url));
const experimentRoot = dirname(here);
const tasksDir = join(experimentRoot, "Задачи");
const clickup = "/Users/triton/Documents/GitHub/agentic-research/experiments/clickup-tool/bin/clickup";

function readAllTasks() {
  const raw = execFileSync(clickup, ["task", "search", workspaceId, "--include-closed", "--all"], {
    encoding: "utf8",
  });
  const tasks = JSON.parse(raw).data?.tasks;
  if (!Array.isArray(tasks)) throw new Error("ClickUp did not return a task array.");
  return tasks;
}

function fileName(task) {
  return `${task.name.replaceAll("/", " — ").replace(/[\\:*?\"<>|]/g, " ").trim()} — ${task.id}.md`;
}

function escapeYaml(value) {
  return JSON.stringify(String(value));
}

function wiki(task) {
  if (!task) return "—";
  const name = task.name ?? task.id;
  return `[[Задачи/${fileName({ id: task.id, name })}|${name}]]`;
}

function taskLink(task, selectedIds) {
  if (selectedIds.has(task.id)) return wiki(task);
  return `[${task.name ?? task.id}](${task.url ?? `https://app.clickup.com/t/${task.id}`})`;
}

function valueOf(field) {
  const value = field.value;
  if (value == null || value === "") return null;
  const options = field.type_config?.options ?? [];
  const optionName = (id) => options.find((option) => option.id === id)?.name ?? id;

  if (field.type === "drop_down") {
    const option = options[Number(value)] ?? options.find((item) => item.id === value);
    return option?.name ?? String(value);
  }
  if (field.type === "labels") {
    return (Array.isArray(value) ? value : [value]).map(optionName).join(", ");
  }
  if (Array.isArray(value)) return value.join(", ");
  return String(value);
}

function customFields(task) {
  const entries = task.custom_fields
    .map((field) => [field.name, valueOf(field)])
    .filter(([, value]) => value);
  const seen = new Map();
  return entries.map(([name, value]) => {
    const count = (seen.get(name) ?? 0) + 1;
    seen.set(name, count);
    return [count === 1 ? name : `${name} ${count}`, value];
  });
}

function markdown(task, tasksById, selectedIds, snapshotAt) {
  const parent = task.parent ? tasksById.get(task.parent) : null;
  const stage = customFields(task).find(([name]) => name === "Стадия")?.[1] ?? "—";
  const fields = customFields(task);
  const dependencies = task.dependencies ?? [];
  const dependencyLines = dependencies.length
    ? dependencies.map(({ depends_on }) => `- ${taskLink(tasksById.get(depends_on) ?? { id: depends_on }, selectedIds)}`).join("\n")
    : "- Нет";
  const fieldRows = fields.length
    ? fields.map(([name, value]) => `| ${name} | ${value.replaceAll("|", "\\|")} |`).join("\n")
    : "| — | — |";
  const description = task.description?.trim() || "Описание в ClickUp не заполнено.";

  return `---
контур: ${escapeYaml(lists.get(task.list.id))}
тип: ${escapeYaml(task.parent ? "Задача" : "Проект")}
статус: ${escapeYaml(task.status?.status ?? "без статуса")}
стадия: ${escapeYaml(stage)}
проект: ${escapeYaml(parent ? wiki(parent) : task.name)}
clickup_id: ${escapeYaml(task.id)}
clickup_url: ${escapeYaml(task.url)}
срез: ${escapeYaml(snapshotAt)}
---

# ${task.name}

${description}

## Связь с портфелем

- Контур: ${lists.get(task.list.id)}
- Тип: ${task.parent ? "задача" : "проект"}
- Родительский проект: ${parent ? wiki(parent) : "эта карточка — проект"}
- Исходник: [ClickUp](${task.url})

## Зависит от

${dependencyLines}

## Поля ClickUp

| Поле | Значение |
| --- | --- |
${fieldRows}
`;
}

const allTasks = readAllTasks();
const tasks = allTasks.filter((task) => lists.has(task.list?.id));
const tasksById = new Map(allTasks.map((task) => [task.id, task]));
const selectedIds = new Set(tasks.map((task) => task.id));
const snapshotAt = new Date().toISOString();

mkdirSync(tasksDir, { recursive: true });
for (const entry of readdirSync(tasksDir, { withFileTypes: true })) {
  if (entry.isFile() && entry.name.endsWith(".md")) rmSync(join(tasksDir, entry.name));
}
for (const task of tasks) {
  writeFileSync(join(tasksDir, fileName(task)), markdown(task, tasksById, selectedIds, snapshotAt), "utf8");
}

const summary = {
  snapshot_at: snapshotAt,
  source: "ClickUp Workspace 25510580",
  tasks: tasks.length,
  projects: tasks.filter((task) => !task.parent).length,
  subtasks: tasks.filter((task) => task.parent).length,
  by_domain: Object.fromEntries([...lists.values()].map((domain) => [domain, tasks.filter((task) => lists.get(task.list.id) === domain).length])),
};
writeFileSync(join(experimentRoot, "snapshot.json"), `${JSON.stringify(summary, null, 2)}\n`, "utf8");
console.log(JSON.stringify(summary, null, 2));
