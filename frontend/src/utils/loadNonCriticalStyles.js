// 延迟加载“非关键”样式文件（通过动态 import），
// 在不阻塞首屏渲染的情况下把大体积或第三方库的 CSS 异步注入页面，提升首屏性能。

const styleImporters = [
  () => import("@wangeditor/editor/dist/css/style.css"),
  () => import("element-plus/dist/index.css"),
  () => import("vant/lib/index.css"),
  () => import("undraw-ui/dist/style.css"),
  () => import("mavon-editor/dist/css/index.css"),
];

let loadPromise;

function scheduleTask(cb) {
  if (typeof window === "undefined") {
    cb();
    return;
  }
  const schedule =
    window.requestIdleCallback ||
    window.requestAnimationFrame ||
    ((handler) => setTimeout(handler, 16));
  schedule(cb);
}

export function loadNonCriticalStyles() {
  if (loadPromise || typeof document === "undefined") {
    return loadPromise || Promise.resolve();
  }
  loadPromise = new Promise((resolve) => {
    scheduleTask(async () => {
      try {
        await Promise.all(
          styleImporters.map((importer) =>
            importer().catch((error) => {
              console.warn("[lazy-style] failed to load style chunk", error);
            })
          )
        );
      } finally {
        resolve();
      }
    });
  });
  return loadPromise;
}
