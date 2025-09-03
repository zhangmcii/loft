import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import pinia from "./stores/index.js";
import dayjs from "./config/dayjsCfg";

// 样式导入
import "@wangeditor/editor/dist/css/style.css";
import "vue3-photo-preview/dist/index.css";
import "element-plus/dist/index.css";
import "vant/lib/index.css";
import "undraw-ui/dist/style.css";
import "mavon-editor/dist/css/index.css";

// 插件导入
import { ElMessage } from "element-plus";
import { loadingFadeOut } from "virtual:app-loading";
import vue3PhotoPreview from "vue3-photo-preview";
import { useElementPlus } from "@/plugins/elementPlus";
import { useVant } from "@/plugins/vant";
import vSlideIn from "@/directives/vSlideIn.js";
import { UIcon } from "undraw-ui";
import mavonEditor from "mavon-editor";

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
app.use(useElementPlus);
app.use(useVant);
app.use(vue3PhotoPreview);
app.use(mavonEditor);

app.mount("#app");
