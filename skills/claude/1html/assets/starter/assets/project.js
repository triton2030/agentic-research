/* Shared artifact-project runtime.
   Edit assets/pages.js for the page tree. Keep HTML files flat in pages/. */
(() => {
  "use strict";

  const project = window.ARTIFACT_PROJECT || {};
  const pages = Array.isArray(project.pages) ? project.pages : [];
  const inPagesDirectory = location.pathname.includes("/pages/");
  const currentFile = location.pathname.split("/").pop() || "index.html";
  const herePath = inPagesDirectory ? `pages/${currentFile}` : "index.html";

  const pageChildren = (page) =>
    Array.isArray(page?.children) ? page.children : [];

  const flattenPages = (items) =>
    items.flatMap((page) => [page, ...flattenPages(pageChildren(page))]);

  const findPageTrail = (items, path, trail = []) => {
    for (const page of items) {
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

  const pageHref = (path) => (inPagesDirectory ? `../${path}` : path);

  const pageLinkHtml = (page, label = page.title) => {
    if (!page.path) return `<span>${escapeHtml(label)}</span>`;
    const current = page.path === herePath;
    const currentAttributes = current
      ? ' class="active" aria-current="page"'
      : "";
    return (
      `<a href="${escapeHtml(pageHref(page.path))}"${currentAttributes}>`
      + `${escapeHtml(label)}</a>`
    );
  };

  const navigationItemHtml = (page, depth = 0, mode = "desktop") => {
    const children = pageChildren(page);
    if (!children.length) return `<li>${pageLinkHtml(page)}</li>`;

    const branchActive = branchContains(page, herePath);
    const summaryClass = branchActive ? ' class="active"' : "";
    const overview = page.path
      ? `<li>${pageLinkHtml(page, `Обзор: ${page.title}`)}</li>`
      : "";
    const childItems = children
      .map((child) => navigationItemHtml(child, depth + 1, mode))
      .join("");
    const submenuClass =
      mode === "desktop" && depth === 0
        ? ' class="artifact-project-submenu bg-base-100 rounded-box p-2 shadow-sm"'
        : "";
    const open =
      branchActive && (mode === "mobile" || depth > 0) ? " open" : "";

    return (
      `<li><details${open}><summary${summaryClass}>`
      + `${escapeHtml(page.title)}</summary><ul${submenuClass}>`
      + `${overview}${childItems}</ul></details></li>`
    );
  };

  const navigationItemsHtml = (mode) =>
    pages.map((page) => navigationItemHtml(page, 0, mode)).join("");

  const currentTrail = () => findPageTrail(pages, herePath);

  const breadcrumbTrail = () => {
    if (herePath === "index.html") return [];
    const trail = currentTrail();
    if (!trail.length) return [];
    const overview = flattenPages(pages).find(
      (page) => page.path === "index.html",
    );
    if (!overview || trail[0]?.path === overview.path) return trail;
    return [overview, ...trail];
  };

  const breadcrumbItemsHtml = () =>
    breadcrumbTrail()
      .map((page, index, trail) => {
        const current = index === trail.length - 1;
        if (current) {
          return (
            `<li><span aria-current="page">`
            + `${escapeHtml(page.title)}</span></li>`
          );
        }
        return `<li>${pageLinkHtml(page)}</li>`;
      })
      .join("");

  const metaContent = (name) =>
    document.querySelector(`meta[name="${name}"]`)?.content?.trim() || "";

  const firstHeading = () =>
    document.querySelector("h1")?.textContent?.trim() || "";

  const projectTitle =
    project.title || metaContent("artifact-title") || firstHeading() || "HTML-проект";
  const projectIcon = project.icon || metaContent("artifact-icon") || "layout-grid";
  const currentPageTitle =
    currentTrail().at(-1)?.title || firstHeading() || document.title || "Страница";
  const projectEntryHref = pageHref("index.html");
  const catalogHref = inPagesDirectory ? "../../index.html" : "../index.html";

  const projectNavigationHtml = () => {
    if (flattenPages(pages).length <= 1) return "";
    return (
      '<nav class="navbar-center artifact-project-nav" '
      + 'aria-label="Страницы проекта">'
      + '<details class="dropdown artifact-project-mobile md:hidden">'
      + `<summary class="btn btn-sm btn-ghost">${escapeHtml(currentPageTitle)}</summary>`
      + '<ul class="menu menu-sm dropdown-content bg-base-100 rounded-box shadow-sm">'
      + `${navigationItemsHtml("mobile")}</ul></details>`
      + '<ul class="menu menu-horizontal artifact-project-menu hidden md:flex">'
      + `${navigationItemsHtml("desktop")}</ul></nav>`
    );
  };

  const projectShellHtml = () => {
    const trail = breadcrumbTrail();
    const breadcrumbs = trail.length
      ? (
          '<nav class="breadcrumbs artifact-breadcrumbs" '
          + 'aria-label="Путь к текущей странице"><ul>'
          + `${breadcrumbItemsHtml()}</ul></nav>`
        )
      : "";

    return (
      '<header class="navbar artifact-topbar">'
      + '<div class="navbar-start w-auto">'
      + `<a class="artifact-home-link" href="${escapeHtml(projectEntryHref)}">`
      + `<i data-lucide="${escapeHtml(projectIcon)}" class="size-4" aria-hidden="true"></i>`
      + `${escapeHtml(projectTitle)}</a></div>`
      + projectNavigationHtml()
      + '<div class="navbar-end w-auto">'
      + `<a class="btn btn-ghost btn-sm artifact-topbar-action" href="${escapeHtml(catalogHref)}">`
      + "Все проекты</a></div></header>"
      + breadcrumbs
    );
  };

  const mountProjectShell = () => {
    const host = document.querySelector("[data-artifact-project-shell]");
    if (!host) return;
    host.innerHTML = projectShellHtml();
    window.lucide?.createIcons();
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", mountProjectShell, {
      once: true,
    });
  } else {
    mountProjectShell();
  }

  document.addEventListener("alpine:init", () => {
    Alpine.data("prototypeViewer", (own = {}) => {
      const defaultStates =
        Array.isArray(own.states) && own.states.length ? own.states : ["default"];
      const base = {
        state: own.state || defaultStates[0],
        states: defaultStates,
        commentsOpen: false,
        panelOpen: true,
        comments: [],

        init() {
          this.$nextTick(() => window.lucide?.createIcons());
        },
      };

      /* Preserve getters and methods supplied by a page. Object spread would
         eagerly evaluate getters and silently break Alpine reactivity. */
      return Object.defineProperties(
        base,
        Object.getOwnPropertyDescriptors(own),
      );
    });
  });
})();
