// Auto-discovery node types. Каждый файл `nodes/*.jsx` (кроме index) должен:
//   - default-export-ить React-компонент;
//   - named-export-ить `nodeType` (строка-идентификатор для React Flow);
//   - named-export-ить `nodeSize(data)` → `{ width, height }` для ELK
//     layout-input.
//
// Чтобы добавить новый тип узла:
//   1. Создать `nodes/MyNode.jsx` с тремя экспортами.
//   2. Использовать в page: `{ id, type: "myNode", data: {...} }`.
// Никакой регистрации — index подхватит автоматически.

const modules = import.meta.glob("./*.jsx", { eager: true });

const collected = Object.entries(modules)
  .filter(([path]) => !path.endsWith("/index.jsx"))
  .map(([path, mod]) => {
    if (!mod.default || !mod.nodeType || !mod.nodeSize) {
      throw new Error(
        `nodes/${path}: required exports — default (component), nodeType (string), nodeSize (function)`
      );
    }
    return [mod.nodeType, mod];
  });

export const nodeTypes = Object.fromEntries(
  collected.map(([type, mod]) => [type, mod.default])
);

export const nodeSizes = Object.fromEntries(
  collected.map(([type, mod]) => [type, mod.nodeSize])
);
