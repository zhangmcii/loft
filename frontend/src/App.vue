<script setup>
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import { useCurrentUserStore } from '@/stores/user'
import { onMounted } from 'vue'

const currentUser = useCurrentUserStore()

onMounted(() => {
  // 如果用户已登录，自动连接WebSocket
  if (currentUser.isLogin) {
    console.log('App mounted: 用户已登录，自动连接WebSocket')
    currentUser.connectSocket()
  }
})
</script>

<template>
  <el-config-provider :locale="zhCn">
    <RouterView />
  </el-config-provider>
</template>
