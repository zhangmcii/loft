import { defineStore } from "pinia";
import { ref, computed } from "vue";

/**
 * 全局音乐播放器状态管理
 */
export const useMusicStore = defineStore("music", () => {
  // 状态
  const isPlaying = ref(false);
  const currentMusic = ref(null);
  const aplayerInstance = ref(null);
  // 底部迷你播放器显示状态（移动端和PC端）
  const isMiniPlayerVisible = ref(false);
  const volume = ref(1);
  
  // 计算属性
  const hasMusic = computed(() => !!currentMusic.value?.url);
  const currentSongInfo = computed(() => ({
    name: currentMusic.value?.name || "",
    artist: currentMusic.value?.artist || "",
    cover: currentMusic.value?.pic || "",
    url: currentMusic.value?.url || "",
    lrc: currentMusic.value?.lrc || ""
  }));

  // 移动端检测
  const isMobile = computed(() => {
    if (typeof window === 'undefined') return false;
    return /Mobi|Android|iPhone/i.test(navigator.userAgent);
  });

  // 动作
  const setAplayerInstance = (instance) => {
    aplayerInstance.value = instance;
  };

  const setCurrentMusic = (music) => {
    currentMusic.value = music;
    // isMiniPlayerVisible.value = true;
    showMiniPlayer()
  };

  const playMusic = (music) => {
    if (!music?.url) return;

    // 如果是同一首歌，切换播放/暂停状态
    if (currentMusic.value?.url === music.url) {
      togglePlay();
      return;
    }

    // 设置新音乐，但不自动播放
    setCurrentMusic(music);

    // 如果APlayer实例存在，只更新播放列表，不自动播放
    // 播放由GlobalPlayer中的监听器控制
    if (aplayerInstance.value) {
      aplayerInstance.value.list.clear();
      aplayerInstance.value.list.add([currentSongInfo.value]);
      // 不在这里调用play()，避免循环调用
    }
  };

  const togglePlay = () => {
    if (!aplayerInstance.value || !hasMusic.value) return;

    if (isPlaying.value) {
      aplayerInstance.value.pause();
    } else {
      aplayerInstance.value.play();
      // 用户关闭了（底部或悬浮）迷你播放器，播放时自动显示
      if (!isMiniPlayerVisible.value) {
        showMiniPlayer();
      }
    }
  };

  const stop = () => {
    if (aplayerInstance.value) {
      aplayerInstance.value.pause();
    }
    isPlaying.value = false;
  };

  const setPlayingState = (playing) => {
    isPlaying.value = playing;
  };

   const setVolume = (newVolume) => {
    volume.value = Math.max(0, Math.min(1, newVolume));
    if (aplayerInstance.value) {
      aplayerInstance.value.volume(volume.value);
    }
  };
  
  const hideMiniPlayer = () => {
    isMiniPlayerVisible.value = false;
    if (aplayerInstance.value) {
      aplayerInstance.value.pause();
    }
  };

  const showMiniPlayer = () => {
    if (hasMusic.value) {
      isMiniPlayerVisible.value = true;
    }
  };

  return {
    // 状态
    isPlaying,
    currentMusic,
    aplayerInstance,
    isMiniPlayerVisible,
    volume,

    // 计算属性
    hasMusic,
    currentSongInfo,
    isMobile,

    // 动作
    setAplayerInstance,
    setCurrentMusic,
    playMusic,
    togglePlay,
    stop,
    setPlayingState,
    setVolume,
    hideMiniPlayer,
    showMiniPlayer
  };
});