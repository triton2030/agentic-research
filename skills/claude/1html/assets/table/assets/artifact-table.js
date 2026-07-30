(function () {
  "use strict";

  const tableState = new WeakMap();

  const normalize = (value) =>
    String(value ?? "")
      .normalize("NFKC")
      .trim()
      .toLocaleLowerCase("ru");

  const cloneFilters = (filters) =>
    Object.fromEntries(
      Object.entries(filters || {}).map(([key, value]) => [
        key,
        Array.isArray(value) ? [...value] : value ?? "",
      ]),
    );

  const selectedValues = (value) =>
    (Array.isArray(value) ? value : [value])
      .map(normalize)
      .filter(Boolean);

  const cellFor = (row, key) =>
    Array.from(row.element.querySelectorAll("[data-table-key]")).find(
      (cell) => cell.dataset.tableKey === key,
    );

  const valueFor = (row, key) => {
    const cell = cellFor(row, key);
    return cell?.dataset.tableValue ?? cell?.textContent ?? "";
  };

  const filterTokensFor = (row, key) =>
    String(valueFor(row, key))
      .split("|")
      .map(normalize)
      .filter(Boolean);

  const numberValue = (value) => {
    const parsed = Number(
      String(value)
        .replace(/\s+/g, "")
        .replace(",", "."),
    );
    return Number.isFinite(parsed) ? parsed : null;
  };

  const dateValue = (value) => {
    const parsed = Date.parse(String(value));
    return Number.isFinite(parsed) ? parsed : null;
  };

  const comparableValue = (value, type) => {
    if (type === "number") return numberValue(value);
    if (type === "date") return dateValue(value);
    return normalize(value);
  };

  const compareRows = (left, right, key, type, direction) => {
    const leftValue = comparableValue(valueFor(left, key), type);
    const rightValue = comparableValue(valueFor(right, key), type);
    const leftMissing = leftValue === null || leftValue === "";
    const rightMissing = rightValue === null || rightValue === "";

    if (leftMissing !== rightMissing) return leftMissing ? 1 : -1;

    let result = 0;
    if (type === "string") {
      result = leftValue.localeCompare(rightValue, "ru", {
        numeric: true,
        sensitivity: "base",
      });
    } else {
      result = leftValue - rightValue;
    }

    if (result === 0) result = left.index - right.index;
    return direction === "desc" ? -result : result;
  };

  document.addEventListener("alpine:init", () => {
    Alpine.data("artifactTable", (options = {}) => {
      const initialFilters = cloneFilters(options.filters);
      const initialSortKey = options.sortKey || "";
      const initialSortType = options.sortType || "string";
      const initialSortDirection =
        initialSortKey && options.sortDirection === "desc" ? "desc" : "asc";

      return {
        query: "",
        filters: cloneFilters(initialFilters),
        sortKey: initialSortKey,
        sortType: initialSortType,
        sortDirection: initialSortDirection,
        rowCount: 0,
        visibleCount: 0,

        init() {
          const body = this.$root.querySelector("[data-table-body]");
          if (!body) return;

          const rows = Array.from(body.children)
            .filter((element) => element.matches("[data-table-row]"))
            .map((element, index) => {
              const explicitValues = Array.from(
                element.querySelectorAll("[data-table-value]"),
                (cell) => cell.dataset.tableValue,
              ).join(" ");

              return {
                element,
                index,
                search: normalize(`${element.textContent} ${explicitValues}`),
              };
            });

          tableState.set(this, { body, rows });
          this.rowCount = rows.length;
          this.$watch("query", () => this.refresh());
          this.$watch("filters", () => this.refresh());
          this.refresh();
        },

        matches(row) {
          const words = normalize(this.query).split(/\s+/).filter(Boolean);
          const matchesQuery = words.every((word) => row.search.includes(word));
          if (!matchesQuery) return false;

          return Object.entries(this.filters).every(([key, value]) => {
            const selected = selectedValues(value);
            if (!selected.length) return true;
            const rowTokens = filterTokensFor(row, key);
            return selected.every((item) => rowTokens.includes(item));
          });
        },

        refresh() {
          const state = tableState.get(this);
          if (!state) return;

          const ordered = [...state.rows];
          if (this.sortKey) {
            ordered.sort((left, right) =>
              compareRows(
                left,
                right,
                this.sortKey,
                this.sortType,
                this.sortDirection,
              ),
            );
          } else {
            ordered.sort((left, right) => left.index - right.index);
          }

          let visibleCount = 0;
          for (const row of ordered) {
            const visible = this.matches(row);
            row.element.hidden = !visible;
            if (visible) visibleCount += 1;
            state.body.append(row.element);
          }
          this.visibleCount = visibleCount;
        },

        toggleSort(key, type = "string") {
          if (this.sortKey === key) {
            this.sortDirection = this.sortDirection === "asc" ? "desc" : "asc";
          } else {
            this.sortKey = key;
            this.sortType = type;
            this.sortDirection = "asc";
          }
          this.refresh();
        },

        sortAria(key) {
          if (this.sortKey !== key) return null;
          return this.sortDirection === "desc" ? "descending" : "ascending";
        },

        toggleFilter(key, value) {
          const current = Array.isArray(this.filters[key])
            ? this.filters[key]
            : [];
          const next = current.includes(value)
            ? current.filter((item) => item !== value)
            : [...current, value];
          this.filters = { ...this.filters, [key]: next };
        },

        filterActive(key, value) {
          const current = this.filters[key];
          return Array.isArray(current)
            ? current.includes(value)
            : current === value;
        },

        reset() {
          this.query = "";
          this.filters = cloneFilters(initialFilters);
          this.sortKey = initialSortKey;
          this.sortType = initialSortType;
          this.sortDirection = initialSortDirection;
          this.$nextTick(() => this.refresh());
        },
      };
    });
  });
})();
