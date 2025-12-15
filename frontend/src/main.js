import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import pinia from "./stores/index.js";
import dayjs from "./config/dayjsCfg";

// 样式导入
import "@/asset/styles/init.css";
import "undraw-ui/dist/style.css";
import "vant/es/popover/style";

// 插件导入
import { ElMessage } from "element-plus";
import { loadingFadeOut } from "virtual:app-loading";
import vSlideIn from "@/directives/vSlideIn.js";
import { UIcon } from "undraw-ui";

// 解决 Added non-passive event listener to a scroll-blocking 'touchstart' event. 问题
import "default-passive-events";
loadingFadeOut();

const app = createApp(App);

// 全局属性
app.config.globalProperties.$dayjs = dayjs;
app.config.globalProperties.$message = ElMessage;

// 指令注册
app.directive("slide-in", vSlideIn);

// 组件注册
app.component("u-icon", UIcon);

// 插件使用
app.use(pinia);
app.use(router);

if (import.meta.env.DEV) {
  import("./main.dev.js").then(({ setupDevPlugins }) => {
    setupDevPlugins(app);
  });
}

app.mount("#app");
