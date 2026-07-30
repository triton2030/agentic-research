/* Shared project-level Alpine state.
   Keep page files flat in pages/. Express hierarchy only through children. */
const ARTIFACT_PROJECT = {
  pages: [
    { path: "index.html", title: "Обзор" },
    // {
    //   path: "pages/system.html",
    //   title: "Система",
    //   children: [
    //     { path: "pages/states.html", title: "Состояния" },
    //   ],
    // },
  ],
};

const pageChildren = (page) =>
  Array.isArray(page?.children) ? page.children : [];

const flattenPages = (pages) =>
  pages.flatMap((page) => [page, ...flattenPages(pageChildren(page))]);

const findPageTrail = (pages, path, trail = []) => {
  for (const page of pages) {
    const nextTrail = [...trail, page];
    if (page.path === path) return nextTrail;
    const childTrail = findPageTrail(pageChildren(page), path, nextTrail);
    if (childTrail.length) return childTrail;
  }
  return [];
};

const branchContains = (page, path) =>
  page.path === path
  || pageChildren(page).some((child) => branchContains(child, path));

const escapeHtml = (value) =>
  String(value).replace(
    /[&<>"']/g,
    (character) =>
      ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#039;",
      })[character],
  );

document.addEventListener("alpine:init", () => {
  Alpine.data("prototypeViewer", (own = {}) => {
    const defaultStates =
      Array.isArray(own.states) && own.states.length ? own.states : ["default"];
    const inPagesDirectory = location.pathname.includes("/pages/");
    const herePath = inPagesDirectory
      ? `pages/${location.pathname.split("/").pop()}`
      : "index.html";

    const base = {
      state: own.state || defaultStates[0],
      states: defaultStates,
      commentsOpen: false,
      panelOpen: true,
      comments: [],
      pages: ARTIFACT_PROJECT.pages,
      herePath,

      init() {
        this.$nextTick(() => window.lucide?.createIcons());
      },

      pageHref(path) {
        return inPagesDirectory ? `../${path}` : path;
      },

      pageCount() {
        return flattenPages(this.pages).length;
      },

      currentTrail() {
        return findPageTrail(this.pages, this.herePath);
      },

      currentPageTitle() {
        return this.currentTrail().at(-1)?.title || "Страница";
      },

      pageLinkHtml(page, label = page.title) {
        if (!page.path) return `<span>${escapeHtml(label)}</span>`;
        const current = page.path === this.herePath;
        const currentAttributes = current
          ? ' class="active" aria-current="page"'
          : "";
        return (
          `<a href="${escapeHtml(this.pageHref(page.path))}"${currentAttributes}>`
          + `${escapeHtml(label)}</a>`
        );
      },

      navigationItemHtml(page, depth = 0, mode = "desktop") {
        const children = pageChildren(page);
        if (!children.length) return `<li>${this.pageLinkHtml(page)}</li>`;

        const branchActive = branchContains(page, this.herePath);
        const summaryClass = branchActive ? ' class="active"' : "";
        const overview = page.path
          ? `<li>${this.pageLinkHtml(page, `Обзор: ${page.title}`)}</li>`
          : "";
        const childItems = children
          .map((child) => this.navigationItemHtml(child, depth + 1, mode))
          .join("");
        const submenuClass =
          mode === "desktop" && depth === 0
            ? ' class="artifact-project-submenu bg-base-100 rounded-box p-2 shadow-sm"'
            : "";
        const open = depth > 0 && branchActive ? " open" : "";

        return (
          `<li><details${open}><summary${summaryClass}>`
          + `${escapeHtml(page.title)}</summary><ul${submenuClass}>`
          + `${overview}${childItems}</ul></details></li>`
        );
      },

      navigationItemsHtml(mode = "desktop") {
        return this.pages
          .map((page) => this.navigationItemHtml(page, 0, mode))
          .join("");
      },

      breadcrumbItemsHtml() {
        return this.currentTrail()
          .map((page, index, trail) => {
            const current = index === trail.length - 1;
            if (current) {
              return `<li><span aria-current="page">${escapeHtml(page.title)}</span></li>`;
            }
            return `<li>${this.pageLinkHtml(page)}</li>`;
          })
          .join("");
      },
    };

    /* Preserve getters and methods supplied by a page. Object spread would
       eagerly evaluate getters and silently break Alpine reactivity. */
    return Object.defineProperties(base, Object.getOwnPropertyDescriptors(own));
  });
});
