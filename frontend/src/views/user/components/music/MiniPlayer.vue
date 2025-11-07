<template>
  <transition name="slide-up">
    <div v-show="isMiniPlayerVisible && hasMusic" class="mini-player">
      <!-- 播放器内容 -->
      <div class="mini-player-content">
        <!-- 左侧：封面和歌曲信息 -->
        <div class="player-left">
          <div class="album-cover" :class="{ 'album-spin': isPlaying }">
            <el-image
              :src="currentSongInfo.cover"
              fit="cover"
              class="cover-image"
              :preview-src-list="currentSongInfo.cover ? [currentSongInfo.cover] : []"
              :preview-teleported="true"
              :hide-on-click-modal="true"
            >
              <template #error>
                <div class="cover-error">
                  <el-icon><i-ep-Headset /></el-icon>
                </div>
              </template>
            </el-image>
          </div>
          
          <div class="song-info">
            <div class="song-title" :title="currentSongInfo.name">
              {{ currentSongInfo.name || '暂无歌曲' }}
            </div>
            <div class="song-artist" :title="currentSongInfo.artist">
              {{ currentSongInfo.artist || '未知艺术家' }}
            </div>
          </div>
        </div>

        <!-- 中间：播放控制 -->
        <div class="player-center">
          <div class="control-buttons">
            <el-button
              circle
              size="small"
              :type="isPlaying ? 'primary' : 'default'"
              @click="togglePlay"
              class="play-btn"
            >
              <el-icon>
                <i-ep-VideoPlay v-if="!isPlaying" />
                <i-ep-VideoPause v-else />
              </el-icon>
            </el-button>
          </div>
        </div>

        <!-- 右侧：音量控制和关闭 -->
        <div class="player-right">
          <div class="volume-control">
            <el-icon><i-ep-Microphone /></el-icon>
            <el-slider
              v-model="volume"
              :max="1"
              :step="0.1"
              :show-tooltip="false"
              @change="handleVolumeChange"
              class="volume-slider"
            />
          </div>
          
          <el-button
            circle
            size="small"
            @click="hidePlayer"
            class="close-btn"
          >
            <el-icon><i-ep-Close /></el-icon>
          </el-button>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup>
import { computed } from 'vue';
import { useMusicStore } from '@/stores/music';

const musicStore = useMusicStore();

// 计算属性
const isMiniPlayerVisible = computed(() => musicStore.isMiniPlayerVisible);
const hasMusic = computed(() => musicStore.hasMusic);
const isPlaying = computed(() => musicStore.isPlaying);
const currentSongInfo = computed(() => musicStore.currentSongInfo);
const volume = computed({
  get: () => musicStore.volume,
  set: (value) => musicStore.setVolume(value)
});

// 方法
const togglePlay = () => {
  musicStore.togglePlay();
};

const hidePlayer = () => {
  musicStore.hideMiniPlayer();
};



const handleVolumeChange = (value) => {
  musicStore.setVolume(value);
};
</script>

<style lang="scss" scoped>
.mini-player {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 2000;
  background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
  border-top: 1px solid #e8e8e8;
  box-shadow: 0 -2px 20px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  
  .mini-player-content {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 8px 16px;
    max-width: 1200px;
    margin: 0 auto;
    height: 70px;
  }
}

.player-left {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  min-width: 0;
  
  .album-cover {
    width: 50px;
    height: 50px;
    border-radius: 8px;
    overflow: hidden;
    flex-shrink: 0;
    transition: all 0.3s ease;
    
    &.album-spin {
      animation: spin 8s linear infinite;
    }
    
    .cover-image {
      width: 100%;
      height: 100%;
      border-radius: 8px;
    }
    
    .cover-error {
      width: 100%;
      height: 100%;
      display: flex;
      align-items: center;
      justify-content: center;
      background: linear-gradient(135deg, #f5f7fa 0%, #e4e7ed 100%);
      color: #c0c4cc;
      border-radius: 8px;
      
      .el-icon {
        font-size: 24px;
      }
    }
  }
  
  .song-info {
    flex: 1;
    min-width: 0;
    
    .song-title {
      font-size: 14px;
      font-weight: 600;
      color: #303133;
      margin-bottom: 2px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      line-height: 1.2;
    }
    
    .song-artist {
      font-size: 12px;
      color: #606266;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      line-height: 1.2;
    }
  }
}

.player-center {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  flex: 2;
  max-width: 400px;
  
  .control-buttons {
    display: flex;
    align-items: center;
    gap: 8px;
    
    .play-btn, .stop-btn {
      width: 32px;
      height: 32px;
      
      .el-icon {
        font-size: 16px;
      }
    }
  }
  

}

.player-right {
  display: flex;
  align-items: center;
  gap: 16px;
  flex: 1;
  justify-content: flex-end;
  
  .volume-control {
    display: flex;
    align-items: center;
    gap: 8px;
    min-width: 120px;
    
    .el-icon {
      color: #606266;
      font-size: 16px;
    }
    
    .volume-slider {
      flex: 1;
      
      :deep(.el-slider__runway) {
        background-color: #e4e7ed;
        height: 4px;
      }
      
      :deep(.el-slider__bar) {
        background-color: #409eff;
        height: 4px;
      }
      
      :deep(.el-slider__button) {
        width: 10px;
        height: 10px;
        border: 2px solid #409eff;
      }
    }
  }
  
  .close-btn {
    width: 32px;
    height: 32px;
    
    .el-icon {
      font-size: 16px;
    }
  }
}

// 动画
.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.3s ease;
}

.slide-up-enter-from,
.slide-up-leave-to {
  transform: translateY(100%);
  opacity: 0;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

// 响应式适配
@media (max-width: 768px) {
  .mini-player {
    display: none; // 移动端不显示迷你播放器
  }
}

@media (max-width: 1024px) {
  .mini-player-content {
    padding: 8px 12px;
    
    .player-left {
      gap: 8px;
      
      .album-cover {
        width: 40px;
        height: 40px;
      }
      
      .song-info {
        .song-title {
          font-size: 13px;
        }
        
        .song-artist {
          font-size: 11px;
        }
      }
    }
    
    .player-center {
      max-width: 300px;
      
      .progress-container {
        .time-current, .time-total {
          font-size: 10px;
          min-width: 30px;
        }
      }
    }
    
    .player-right {
      .volume-control {
        min-width: 100px;
      }
    }
  }
}
</style>