<script setup>
import BaseMask from '@/utils/components/BaseMask.vue'

const isMobile = ref(/Mobi|Android|iPhone/i.test(navigator.userAgent))
</script>

<template>
  <BaseMask v-if="!isMobile" @click="isMobile = true" />
  <div v-if="!isMobile" class="guide">
    <el-icon class="danger"> <i-ep-WarnTriangleFilled /></el-icon>
    <el-icon class="close"> <i-ep-CircleClose @click="isMobile = true" /></el-icon>

    <div class="txt">
      <h2>切换至手机模式获取最佳体验</h2>
      <h3>1. 按 F12 调出控制台</h3>
      <h3>2. 按 Ctrl+Shift+M，或点击下面图标</h3>
    </div>
    <img src="@/asset/guide.png" alt="" />
  </div>
</template>

<style lang="scss" scoped>
.guide {
  color: white;
  z-index: 999;
  background: rgb(31, 37, 52);
  position: fixed;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  border-radius: 16px;
  overflow: hidden;
  text-align: center;

  .danger {
    margin-top: 10px;
    font-size: 40px;
    color: red;
  }

  .close {
    cursor: pointer;
    font-size: 18px;
    color: white;
    position: absolute;
    right: 15px;
    top: 15px;
  }

  .txt {
    text-align: left;
    padding: 0 24px;
  }

  img {
    display: block;
    width: 350px;
  }
}
</style>
