import vue from '@vitejs/plugin-vue'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import Icons from 'unplugin-icons/vite'
import IconsResolver from 'unplugin-icons/resolver'
import AppLoading from 'vite-plugin-app-loading'
import { configCompressPlugin } from './compress'
import svgLoader from 'vite-svg-loader'
import removeConsole from "vite-plugin-remove-console";

export function getPluginsList(VITE_COMPRESSION) {
  return [
    vue(),
    AutoImport({
      imports: ['vue'],
      resolvers: []
    }),
    Components({
      resolvers: [
        // 自动注册图标组件
        IconsResolver({
          enabledCollections: ['ep']
        })
      ]
    }),
    Icons({
      autoInstall: true
    }),
    AppLoading(),
    configCompressPlugin(VITE_COMPRESSION),
    svgLoader(),
    removeConsole()
  ]
}
