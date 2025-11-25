import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import pinia from "./stores/index.js";
import dayjs from "./config/dayjsCfg";

// 样式导入
import { loadNonCriticalStyles } from "@/utils/loadNonCriticalStyles";
import { lazyInstallUIFrameworks } from "@/utils/lazyInstallUIFrameworks";

// 插件导入
import { loadingFadeOut } from "virtual:app-loading";
import vSlideIn from "@/directives/vSlideIn.js";
import { UIcon } from "undraw-ui";

loadingFadeOut();

const app = createApp(App);

// 全局属性
app.config.globalProperties.$dayjs = dayjs;
app.config.globalProperties.$message = (...args) => {
  if (import.meta.env.DEV) {
    console.warn(
      "[lazy-ui] Element Plus 未加载完成，消息已被忽略。等待首次进入主站页面后即可正常使用。",
      args
    );
  }
};

// 指令注册
app.directive("slide-in", vSlideIn);

// 组件注册
app.component("u-icon", UIcon);

// 插件使用
app.use(pinia);
app.use(router);

lazyInstallUIFrameworks(app, router);

app.mount("#app");

loadNonCriticalStyles();
