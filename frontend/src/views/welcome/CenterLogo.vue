<script setup>
import { GLOBAL_CONFIG } from "@/config/welcomeCfg.js";
import { randomNum } from "@/utils/common";
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";
// import LocalLogo from '@/asset/logo.svg?component'

defineOptions({
  name: "CenterLogo",
});

defineProps({
  drawerVisible: Boolean,
  touchable: Boolean,
});

const emit = defineEmits({
  backgroundLoaded: [],
});

const bgLoaded = ref(false);
const slogan = ref("");
const backgroundReady = ref(false);
const currentBackgroundUrl = ref("");
const optimizedBackgroundUrl = ref("");
let resizeRaf = 0;
let currentLoadToken = 0;
let lastViewportWidth = 0;

// 根据 backgroundReady 和 currentBackgroundUrl 返回最终内联样式对象（背景图片或渐变占位）
const backgroundInlineStyle = computed(() => {
  const baseStyle = {
    backgroundSize: "cover",
    backgroundPosition: "center",
  };
  if (backgroundReady.value && currentBackgroundUrl.value) {
    return {
      ...baseStyle,
      backgroundImage: `url(${currentBackgroundUrl.value})`,
    };
  }
  return {
    ...baseStyle,
    background:
      "radial-gradient(circle at 35% 25%, rgba(253,160,133,0.9), rgba(246,211,101,0.75))",
    backgroundColor: "#f6d365",
  };
});

// GLOBAL_CONFIG.BACKGROUND_IMG_URL 生成一个按设备像素比与窗口宽度优化的图片请求
//（例如七牛的 imageView2/2/w/…/q/75）。
function getOptimizedBackgroundUrl() {
  if (typeof window === "undefined") {
    return GLOBAL_CONFIG.BACKGROUND_IMG_URL;
  }
  const pixelRatio = window.devicePixelRatio || 1;
  const maxWidth = Math.min(1920, Math.round(window.innerWidth * pixelRatio));
  const query = `imageView2/2/w/${maxWidth}/q/75`;
  const joiner = GLOBAL_CONFIG.BACKGROUND_IMG_URL.includes("?") ? "&" : "?";
  return `${GLOBAL_CONFIG.BACKGROUND_IMG_URL}${joiner}${query}`;
}
// 把实际的图片加载任务推迟到浏览器空闲或下一帧，降低对关键渲染的干扰。
function scheduleBackgroundLoad() {
  const targetUrl = optimizedBackgroundUrl.value;
  const schedule =
    typeof window !== "undefined"
      ? window.requestIdleCallback || window.requestAnimationFrame
      : null;
  const runner = () => startBackgroundLoad(targetUrl);
  if (schedule) {
    schedule(runner);
    return;
  }
  setTimeout(runner, 16);
}

// 通过创建 Image 对象异步预加载图片，并在成功/失败时更新状态与发出事件。
function startBackgroundLoad(url) {
  if (!url) {
    return;
  }
  const token = ++currentLoadToken;
  const img = new Image();
  img.decoding = "async";
  img.src = url;
  img.onload = () => {
    if (token !== currentLoadToken) return;
    currentBackgroundUrl.value = url;
    backgroundReady.value = true;
    bgLoaded.value = true;
    emit("backgroundLoaded");
  };
  img.onerror = () => {
    if (token !== currentLoadToken) return;
    backgroundReady.value = false;
    // 允许遮罩消失避免界面长期保持暗色
    bgLoaded.value = true;
    emit("backgroundLoaded");
  };
}

// 响应窗口 resize，按需重算 optimizedBackgroundUrl 并触发重新加载，
// 避免在轻微尺寸变化时重复加载。
function handleResize() {
  if (typeof window === "undefined") {
    return;
  }
  const width = window.innerWidth;
  if (Math.abs(width - lastViewportWidth) < 80) {
    return;
  }
  lastViewportWidth = width;
  if (resizeRaf) {
    window.cancelAnimationFrame(resizeRaf);
  }
  resizeRaf = window.requestAnimationFrame(() => {
    backgroundReady.value = false;
    bgLoaded.value = false;
    optimizedBackgroundUrl.value = getOptimizedBackgroundUrl();
  });
}

function randomSlogan() {
  const slogans = GLOBAL_CONFIG.SLOGANS;
  slogan.value = slogans[randomNum(0, slogans.length - 1)];
}

watch(optimizedBackgroundUrl, (newUrl, oldUrl) => {
  if (!newUrl || newUrl === oldUrl) return;
  backgroundReady.value = false;
  bgLoaded.value = false;
  scheduleBackgroundLoad();
});

onMounted(() => {
  randomSlogan();
  optimizedBackgroundUrl.value = getOptimizedBackgroundUrl();
  if (typeof window !== "undefined") {
    lastViewportWidth = window.innerWidth;
    window.addEventListener("resize", handleResize, { passive: true });
  }
});

onBeforeUnmount(() => {
  if (typeof window !== "undefined") {
    window.removeEventListener("resize", handleResize);
    if (resizeRaf) {
      window.cancelAnimationFrame(resizeRaf);
    }
  }
});
</script>

<template>
  <div
    :class="['logo-area', { 'is-blur': drawerVisible }]"
    :style="backgroundInlineStyle"
  >
    <div :class="['img-shadow', { 'img-shadow-show': bgLoaded }]"></div>
    <div class="inner" style="cursor: pointer" @click="$router.push('/posts')">
      <!-- <LocalLogo :class="['main-logo', { 'main-logo-top': touchable }]" /> -->
      <div :class="['hello', { hello_bottom: touchable }]">
        <div>{{ slogan }}</div>
        <div class="hello_bottom_text">
          <div class="slide-up">访问 随想阁楼</div>
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
@import url("@/asset/css/animate.scss");
.logo-area {
  background-size: cover !important;
  background-position: center !important;
  overflow: hidden;
  align-items: center;
  justify-content: center;
  display: flex;
  border-radius: 100%;
  /* 初始展开动画 */
  animation: logoEnter 1.2s;
  animation-fill-mode: forwards;
  transition: all 0.8s;
  &.is-blur {
    filter: blur(5px);
  }
  .img-shadow {
    content: "";
    width: 100%;
    height: 100%;
    position: absolute;
    background-color: #fda085;
    overflow: hidden;
    transition: background-color 0.5s;
    border-radius: 100%;
    animation: shadowEnter 1.2s;
    animation-fill-mode: forwards;
  }
  .img-shadow-show {
    background-color: rgba(0, 0, 0, 0.5);
  }
  .inner {
    position: relative;
    .main-logo {
      height: 6rem;
      position: absolute;
      transform: translate(-50%, -50%);
      transition: all 1s;
      top: 0;
    }
    .main-logo-top {
      top: -3.2rem;
    }
    .hello {
      color: #ffffff;
      width: 18.75rem;
      text-align: center;
      position: absolute;
      transform: translate(-50%, -50%);
      font-size: 21px;
      opacity: 0;
      top: 100px;
      transition: all 1s;
    }
    .hello_bottom {
      opacity: 1;
      top: 3.5rem;
      .hello_bottom_text {
        font-size: 14px;
        margin-top: 0.5rem;
        padding-top: 0.5rem;
        border-top: 1px solid #fff;
        .slide-up {
          margin-top: 15px;
          animation: float 4s infinite ease-in-out;
        }
      }
    }
  }
}
</style>
