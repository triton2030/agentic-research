/* Shared project-level Alpine state.
   Add every real page here once; all screens inherit the same navigation. */
const ARTIFACT_PROJECT = {
  pages: [
    { path: "index.html", title: "Обзор" },
  ],
};

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

      navigate(path) {
        if (path && path !== this.herePath) location.href = this.pageHref(path);
      },

      currentPageTitle() {
        return this.pages.find((page) => page.path === this.herePath)?.title || "Страница";
      },
    };

    /* Preserve getters and methods supplied by a page. Object spread would
       eagerly evaluate getters and silently break Alpine reactivity. */
    return Object.defineProperties(base, Object.getOwnPropertyDescriptors(own));
  });
});
