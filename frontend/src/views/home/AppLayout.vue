<script setup>
import Header from "./components/Header.vue";
import GlobalPlayer from "@/views/user/components/music/GlobalPlayer.vue";
import MiniPlayer from "@/views/user/components/music/MiniPlayer.vue";
import MobileFloatingPlayer from "@/views/user/components/music/MobileFloatingPlayer.vue";
import zhCn from "element-plus/es/locale/lang/zh-cn";
</script>

<template>
  <el-config-provider :locale="zhCn">
    <el-container>
      <el-header>
        <Header />
      </el-header>
      <el-divider />
      <el-main>
        <router-view v-slot="{ Component, route }">
          <keep-alive>
            <component
              v-if="route.meta.keepAlive"
              :is="Component"
              :key="route.name"
            />
          </keep-alive>
          <component
            v-if="!route.meta.keepAlive"
            :is="Component"
            :key="route.name"
          />
        </router-view>
      </el-main>

      <!-- 全局音乐播放器 -->
      <GlobalPlayer />
      <!-- PC端底部迷你播放器 -->
      <MiniPlayer />
      <!-- 移动端悬浮播放按钮 -->
      <MobileFloatingPlayer />
    </el-container>
  </el-config-provider>
</template>

<style lang="scss" scoped>
body {
  -webkit-tap-highlight-color: transparent;
}

.el-container {
  width: 100%;
  height: 100%;
}

.el-header {
  height: 56px;
  padding: 0;
}

.el-main {
  padding: 0;
}

.el-divider--horizontal {
  height: 0;
  margin: 0;
}
</style>
