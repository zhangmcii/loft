import vue from "@vitejs/plugin-vue";
import AutoImport from "unplugin-auto-import/vite";
import Components from "unplugin-vue-components/vite";
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'
import { VantResolver } from '@vant/auto-import-resolver';
import Icons from "unplugin-icons/vite";
import IconsResolver from "unplugin-icons/resolver";
import AppLoading from "vite-plugin-app-loading";
import { configCompressPlugin } from "./compress";
import svgLoader from "vite-svg-loader";
import removeConsole from "vite-plugin-remove-console";

export function getPluginsList(VITE_COMPRESSION, MODE) {
  const isProd = MODE == 'production'
  return [
    vue(),
    AutoImport({
      imports: ["vue"],
      resolvers: isProd ? [ElementPlusResolver(), VantResolver()] : [],
    }),
    Components({
      resolvers: [
        // 自动注册图标组件
        IconsResolver({
          enabledCollections: ["ep"],
        }),
        ...(isProd ? [ElementPlusResolver(), VantResolver()] : []),
      ],
    }),
    Icons({
      autoInstall: true,
    }),
    AppLoading(),
    configCompressPlugin(VITE_COMPRESSION),
    svgLoader(),
    // removeConsole(),
  ];
}
