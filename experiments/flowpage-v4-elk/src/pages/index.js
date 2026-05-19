// Auto-discovery built-in страниц. Любой `pages/*.js` (кроме самого index)
// автоматически подхватывается — добавление новой страницы = один файл, без
// импорта и регистрации.
//
// Каждый page-файл должен default-export-ить объект:
//   {
//     id: "unique-slug",          // используется как имя файла раскладки
//     title: "Заголовок",          // в sidebar
//     description: "одна строка",  // в panel канваса
//     nodes: [ /* см. SkillCard data shape */ ],
//     edges: [ ["sourceId", "targetId", "label?"], ... ]
//   }
//
// Порядок страниц определяется alphabetical по filename. Если нужен явный
// порядок — добавляй number-prefix (01-, 02-, ...) к имени файла.

const modules = import.meta.glob("./*.js", { eager: true });

// Файлы с префиксом `_` (например `_helpers.js`) — utility-модули, не страницы.
function isPageFile(path) {
  const name = path.replace(/^\.\//, "");
  return !name.startsWith("_") && name !== "index.js";
}

export const BUILTIN_PAGES = Object.entries(modules)
  .filter(([path]) => isPageFile(path))
  .sort(([a], [b]) => a.localeCompare(b))
  .map(([path, mod]) => {
    const page = mod.default ?? Object.values(mod).find((v) => v && typeof v === "object" && v.id);
    if (!page || !page.id) {
      throw new Error(`pages/${path}: ожидался default export со shape { id, title, nodes, edges }`);
    }
    return page;
  });
