// 开发环境下全局加载以提升热更新速度，生产环境下启用按需加载
import { useElementPlus } from "@/plugins/elementPlus";
import { useVant } from "@/plugins/vant";

import "element-plus/dist/index.css";
import "vant/lib/index.css";

export function setupDevPlugins(app) {
  app.use(useElementPlus);
  app.use(useVant);
}
