<script setup>
import Header from "./components/Header.vue";
import { Scrollbar } from "vue-amazing-ui";
import { useRoute } from "vue-router";
import { computed } from "vue";
import "vue-amazing-ui/es/scrollbar/Scrollbar.css";
// import MobileRemind from '@/utils/components/MobileRemind.vue'

const route = useRoute();
// 判断是否为 用户资料页面
const isUserPage = computed(() => route.name === "user");
</script>

<template>
  <el-container>
    <el-header>
      <Header />
    </el-header>
    <el-divider />
    <el-main :class="{ 'no-padding': isUserPage }">
      <Scrollbar
        ref="scrollbar"
        class="Scrollbar"
        style="--scrollbar-color: rgba(0, 0, 0, 0)"
      >
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
      </Scrollbar>
    </el-main>
    <!-- <MobileRemind /> -->
  </el-container>
</template>

<style scoped>
body {
  /* 移动端点击可点击元素时，出现蓝色默认背景色 */
  -webkit-tap-highlight-color: transparent;
}
.el-container {
  width: 100%;
  height: 100%;
}
.el-header {
  height: 45px;
  padding: 0px;
}
.el-main {
  padding: 10px 20px 0px 20px;
}
.el-main.no-padding {
  padding: 0 !important;
}

/* 10px是随机添加的，出现阻尼效果 并且页头不会消失 */
.Scrollbar {
  height: calc(100vh - var(--el-main-padding) * 2 - 10px);
}

.el-divider--horizontal {
  margin: 2px 0px 0px 0px;
  height: 0px;
}
</style>
