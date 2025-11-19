<template>
  <!-- 隐藏的APlayer容器，用于全局音乐播放 -->
  <div
    style="
      position: absolute;
      left: -9999px;
      top: -9999px;
      width: 1px;
      height: 1px;
      overflow: hidden;
    "
  >
    <div ref="aplayerContainer" id="global-aplayer"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, nextTick } from "vue";
import { useMusicStore } from "@/stores/music";
import APlayer from "APlayer";

const musicStore = useMusicStore();
const aplayerContainer = ref(null);
const aplayerInstance = ref(null);

// 事件监听器引用
const eventListeners = {
  play: null,
  pause: null,
  ended: null,
  volumechange: null,
};

// 清理事件监听器
const cleanupEventListeners = () => {
  // APlayer 不支持单独移除事件监听器，直接清理引用即可
  Object.keys(eventListeners).forEach((event) => {
    eventListeners[event] = null;
  });
};

// 初始化APlayer
const initAPlayer = () => {
  if (!aplayerContainer.value) return;

  // 清理现有实例
  if (aplayerInstance.value) {
    cleanupEventListeners();
    aplayerInstance.value.destroy();
    aplayerInstance.value = null;
  }

  try {
    // 创建新的APlayer实例
    aplayerInstance.value = new APlayer({
      container: aplayerContainer.value,
      fixed: false,
      autoplay: false,
      audio: [],
      lrcType: 0,
      mini: false,
      volume: musicStore.volume,
      mutex: true,
      preload: "metadata",
    });

    // 设置APlayer实例到全局状态
    musicStore.setAplayerInstance(aplayerInstance.value);

    // 设置事件监听器 - 只保留播放状态监听
    eventListeners.play = () => {
      musicStore.setPlayingState(true);
    };
    aplayerInstance.value.on("play", eventListeners.play);

    eventListeners.pause = () => {
      musicStore.setPlayingState(false);
    };
    aplayerInstance.value.on("pause", eventListeners.pause);

    eventListeners.ended = () => {
      musicStore.setPlayingState(false);
    };
    aplayerInstance.value.on("ended", eventListeners.ended);

    eventListeners.volumechange = () => {
      musicStore.setVolume(aplayerInstance.value.volume());
    };
    aplayerInstance.value.on("volumechange", eventListeners.volumechange);

    // 如果有保存的音乐，恢复播放
    if (musicStore.currentMusic?.url) {
      aplayerInstance.value.list.clear();
      aplayerInstance.value.list.add([
        {
          name: musicStore.currentMusic.name,
          artist: musicStore.currentMusic.artist,
          url: musicStore.currentMusic.url,
          cover: musicStore.currentMusic.pic,
        },
      ]);
    }
  } catch (error) {
    console.error("APlayer初始化失败:", error);
  }
};

// 优化后的音乐变化监听
const handleMusicChange = (newMusic, oldMusic) => {
  if (!aplayerInstance.value || !newMusic?.url) return;

  // 只有当音乐实际发生变化时才更新
  if (newMusic?.url === oldMusic?.url) return;

  // 更新播放列表
  aplayerInstance.value.list.clear();
  aplayerInstance.value.list.add([
    {
      name: newMusic.name,
      artist: newMusic.artist,
      url: newMusic.url,
      cover: newMusic.pic,
    },
  ]);

  // 等待音频加载后再播放
  setTimeout(() => {
    if (aplayerInstance.value?.audio) {
      aplayerInstance.value.play();
    }
  }, 200);
};

// 监听播放控制
const handlePlayStateChange = (playing) => {
  if (!aplayerInstance.value || !aplayerInstance.value.audio) return;

  if (playing && aplayerInstance.value.audio.paused) {
    aplayerInstance.value.play().catch((error) => {
      console.error("播放失败:", error);
    });
  } else if (!playing && !aplayerInstance.value.audio.paused) {
    aplayerInstance.value.pause();
  }
};

// 使用深度监听和防抖
let musicChangeTimeout = null;
const debouncedMusicChange = (newMusic, oldMusic) => {
  if (musicChangeTimeout) clearTimeout(musicChangeTimeout);
  musicChangeTimeout = setTimeout(() => {
    handleMusicChange(newMusic, oldMusic);
  }, 100);
};

// 简化监听器，避免循环调用
watch(() => musicStore.currentMusic, debouncedMusicChange, {
  immediate: true,
  deep: true,
});

watch(() => musicStore.isPlaying, handlePlayStateChange);

// 生命周期
onMounted(() => {
  nextTick(() => {
    // 延迟初始化，确保DOM加载完成
    setTimeout(() => {
      initAPlayer();
    }, 100);
  });
});

onUnmounted(() => {
  // 清理定时器
  if (musicChangeTimeout) clearTimeout(musicChangeTimeout);

  // 清理APlayer实例
  cleanupEventListeners();
  if (aplayerInstance.value) {
    aplayerInstance.value.destroy();
    aplayerInstance.value = null;
  }

  // 清理全局状态
  musicStore.setAplayerInstance(null);
});
</script>
