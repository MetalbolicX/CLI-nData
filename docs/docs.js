window.$docsify = {
  name: "cli-ndata",
  repo: "https://github.com/MetalbolicX/cli-ndata.git",
  loadSidebar: true,
  subMaxLevel: 2,
  coverpage: true,
  tabs: {
    persist: true,
    sync: true,
    theme: "classic",
    tabComments: true,
    tabHeadings: true,
  },
  search: {
    noData: "No results found",
    paths: ["/api-reference"],
    placeholder: "Search...",
    depth: 2,
    maxAge: 86400000, // 1 day
  },
};