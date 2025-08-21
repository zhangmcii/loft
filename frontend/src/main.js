import { createApp } from 'vue'

import App from './App.vue'
import router from './router'
import pinia from './stores/index.js'
import dayjs from './config/dayjsCfg'

import { ElMessage } from 'element-plus'

import '@wangeditor/editor/dist/css/style.css'

// 全局loading
import { loadingFadeOut } from 'virtual:app-loading'
loadingFadeOut()

import vue3PhotoPreview from 'vue3-photo-preview'
import 'vue3-photo-preview/dist/index.css'

import { useElementPlus } from '@/plugins/elementPlus'
import 'element-plus/dist/index.css'

import { useVant } from '@/plugins/vant'
import 'vant/lib/index.css'
import vSlideIn from '@/directives/vSlideIn.js'

import { UIcon } from 'undraw-ui'
import 'undraw-ui/dist/style.css'

import mavonEditor from 'mavon-editor'
import 'mavon-editor/dist/css/index.css'

const app = createApp(App)
app.directive('slide-in',vSlideIn)

app.config.globalProperties.$dayjs = dayjs
app.config.globalProperties.$message = ElMessage
app.use(useElementPlus)
app.use(useVant)
app.use(router)
app.use(pinia)
app.use(vue3PhotoPreview)
app.use(mavonEditor)
app.component('u-icon', UIcon)
app.mount('#app')
