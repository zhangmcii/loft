import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import pinia from "./stores/index.js";
import dayjs from "./config/dayjsCfg";

// 样式导入
import "undraw-ui/dist/style.css";

// 插件导入
import { ElMessage } from "element-plus";
import { loadingFadeOut } from "virtual:app-loading";
import vSlideIn from "@/directives/vSlideIn.js";
import { UIcon } from "undraw-ui";

// 解决 Added non-passive event listener to a scroll-blocking 'touchstart' event. 问题
import 'default-passive-events'
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

// 开发环境下全局加载以提升热更新速度，生产环境下启用按需加载
if (import.meta.env.DEV == true) {
    import('@/plugins/elementPlus')
        // 导入成功后，它返回一个模块对象 (Module)，我们通常需要取它的 default 或命名导出
        .then(pluginModule => {
            const { useElementPlus } = pluginModule;
            app.use(useElementPlus);
        })
        .catch(error => {
            console.error('动态加载 ElementPlus 插件失败:', error);
        });

    import('@/plugins/vant')
        .then(pluginModule => {
            const { useVant } = pluginModule;
            app.use(useVant);
        })
        .catch(error => {
            console.error('动态加载 Vant 插件失败:', error);
        });

    import('element-plus/dist/index.css'),
    import('vant/lib/index.css');
}
app.mount("#app");
