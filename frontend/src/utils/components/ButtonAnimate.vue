<script>
export default {
  props: {
    // 按钮文字
    content: {
      type: String,
      default: "点击",
    },
    isActive: {
      type: Boolean,
      default: false,
    },
    fontColor: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {};
  },
  methods: {},
};
</script>
<template>
  <div
    class="btn java"
    :class="{ active: isActive, fontColor: fontColor }"
    @click="$emit('click')"
  >
    {{ content }}
  </div>
</template>
<style lang="scss" scoped>
//设置为毛玻璃样式
.glass {
  backdrop-filter: blur(7px);
  color: #fff;
  /* 确保背景透明，显示毛玻璃效果 */
  background-color: transparent;
  /* 移除默认边框 */
}
.btn {
  @extend .glass;
  vertical-align: top;
  margin: 25px 0px 0px 20px;
  display: inline-block;
  text-align: center;
  line-height: 44px;
  border-radius: 20px;
  cursor: pointer;
}

.java {
  color: #fff;
  height: 30px;
  width: 80px;
  font-size: 12px;
  line-height: 30px;
  // border: 1px solid rgb(103, 120, 138);
  border: 1px solid rgb(216.8, 235.6, 255);
  opacity: 1;
  transition: all 0.3s;
}

.java:active {
  opacity: 0.7;
}
.active {
  border: 1px solid rgb(4, 122, 239);
}
.fontColor {
  color: #000;
}
</style>
