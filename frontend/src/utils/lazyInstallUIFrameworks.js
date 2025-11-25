// 按需延迟安装/挂载大型 UI 框架（Element Plus、Vant、mavon-editor），
// 减少首屏体积并在必要时再安装。

let installPromise = null;
let installed = false;

const LIGHT_ROUTES = new Set(["/welcome", "/welcome/"]);

async function installFrameworks(app) {
  if (installed) return;
  const [
    { useElementPlus },
    { useVant },
    { default: mavonEditor },
    { ElMessage },
  ] = await Promise.all([
    import("@/plugins/elementPlus"),
    import("@/plugins/vant"),
    import("mavon-editor"),
    import("element-plus"),
  ]);
  app.use(useElementPlus);
  app.use(useVant);
  app.use(mavonEditor);
  app.config.globalProperties.$message = ElMessage;
  installed = true;
}

function ensureInstall(app) {
  if (installed) return Promise.resolve();
  if (!installPromise) {
    installPromise = installFrameworks(app).finally(() => {
      installPromise = null;
    });
  }
  return installPromise;
}

export function lazyInstallUIFrameworks(app, router) {
  if (!router) {
    return ensureInstall(app);
  }
  const currentPath = router.currentRoute?.value?.path || "";
  if (!LIGHT_ROUTES.has(currentPath)) {
    ensureInstall(app);
    return;
  }
  router.beforeResolve((to) => {
    if (!LIGHT_ROUTES.has(to.path || "")) {
      ensureInstall(app);
    }
  });
}
