<script>
export default {
  props: {
    postImages: {
      type: Array,
      default() {
        return [];
      },
    },
    mode: {
      type: String,
      default: "default",
    },
  },
  computed: {
    hasImages() {
      return this.postImages.length > 0;
    },
    imageCount() {
      return this.postImages.length;
    },
    isArticleMode() {
      return this.mode === "article";
    },
    isSingleImage() {
      return this.imageCount === 1;
    },
    gridTemplateColumns() {
      if (this.isSingleImage) return "1fr";
      if (this.imageCount === 2 || this.imageCount === 4) return "1fr 1fr";
      return "1fr 1fr 1fr";
    },
    containerWidth() {
      if (this.isArticleMode) {
        if (this.isSingleImage) return "min(100%, 640px)";
        if (this.imageCount === 2 || this.imageCount === 4) {
          return "min(100%, 560px)";
        }
        return "min(100%, 620px)";
      }
      if (this.isSingleImage) return "min(100%, 280px)";
      if (this.imageCount === 2 || this.imageCount === 4) {
        return "min(100%, 336px)";
      }
      return "min(100%, 348px)";
    },
    imageAspectRatio() {
      if (this.isSingleImage) {
        return this.isArticleMode ? "4 / 3" : "4 / 3";
      }
      return "1 / 1";
    },
  },
};
</script>

<template>
  <div
    v-if="hasImages"
    class="post-image"
    :class="{
      'post-image-article': isArticleMode,
      'post-image-single': isSingleImage,
    }"
    :style="{ width: containerWidth }"
  >
    <div class="preview" :style="{ gridTemplateColumns }">
      <div
        v-for="(url, index) in postImages"
        :key="`${url}-${index}`"
        class="image-frame"
        :style="{ aspectRatio: imageAspectRatio }"
      >
        <el-image
          class="image-item"
          :src="url"
          :preview-src-list="postImages"
          :initial-index="index"
          alt="文章图片"
          lazy
          fit="cover"
          preview-teleported
        >
          <template #placeholder>
            <div class="image-status image-status-loading">
              <span class="loading-shimmer"></span>
            </div>
          </template>
          <template #error>
            <div class="image-status image-status-error">
              <el-icon><i-ep-picture /></el-icon>
              <span>图片暂时无法显示</span>
            </div>
          </template>
        </el-image>
      </div>
    </div>
  </div>
</template>
<style lang="scss" scoped>
@use "./PostReadingTokens.scss" as tokens;

.post-image {
  width: 100%;
  max-width: 100%;
  margin: 0 auto;
  margin-bottom: 10px;

  .preview {
    display: grid;
    gap: 4px;
    width: 100%;
    margin: 0 auto;
  }

  .image-frame {
    position: relative;
    overflow: hidden;
    background: tokens.$reading-fill-softer;
    border: 1px solid tokens.$reading-border;
  }

  .image-item {
    width: 100%;
    height: 100%;

    :deep(.el-image__wrapper) {
      width: 100%;
      height: 100%;
    }

    :deep(.el-image__inner) {
      width: 100%;
      height: 100%;
      transition: transform 0.35s ease, filter 0.35s ease;
    }
  }

  .image-frame:hover {
    .image-item {
      :deep(.el-image__inner) {
        transform: scale(1.015);
        filter: saturate(0.98);
      }
    }
  }

  .image-status {
    position: absolute;
    inset: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 10px;
    padding: 18px;
    text-align: center;
    color: tokens.$reading-text-quaternary;
    background: tokens.$reading-fill-softer;
  }

  .image-status-loading {
    overflow: hidden;
    background: linear-gradient(180deg, #f5f5f5 0%, #efefef 100%);

    .loading-shimmer {
      position: absolute;
      inset: 0;
      background: linear-gradient(
        100deg,
        rgba(255, 255, 255, 0) 10%,
        rgba(255, 255, 255, 0.62) 38%,
        rgba(255, 255, 255, 0) 66%
      );
      transform: translateX(-100%);
      animation: image-skeleton-shimmer 1.9s ease-in-out infinite;
    }
  }

  .image-status-error {
    .el-icon {
      font-size: 28px;
      color: tokens.$reading-text-tertiary;
    }

    span {
      font-size: 12px;
      line-height: 1.6;
    }
  }
}

.post-image-single {
  .image-frame {
    background: #f7f7f7;
  }
}

.post-image-article {
  .preview {
    gap: 6px;
  }
}

@keyframes image-paper-drift {
  0%,
  100% {
    transform: translateX(-16%) translateY(-6%);
  }

  50% {
    transform: translateX(12%) translateY(8%);
  }
}

@keyframes image-grain-pulse {
  0%,
  100% {
    opacity: 0.28;
  }

  50% {
    opacity: 0.48;
  }
}

@keyframes image-frame-float {
  0%,
  100% {
    transform: translateY(0);
  }

  50% {
    transform: translateY(-3px);
  }
}

@keyframes image-hill-breathe {
  0%,
  100% {
    transform: translateY(0);
    opacity: 0.9;
  }

  50% {
    transform: translateY(-1px);
    opacity: 1;
  }
}

@keyframes image-cloud-drift {
  0%,
  100% {
    transform: translateX(0);
    opacity: 0.72;
  }

  50% {
    transform: translateX(4px);
    opacity: 1;
  }
}

@keyframes image-sparkle {
  0%,
  100% {
    opacity: 0.3;
  }

  35% {
    opacity: 1;
  }

  60% {
    opacity: 0.45;
  }
}

@keyframes image-label-breathe {
  0%,
  100% {
    opacity: 0.64;
  }

  50% {
    opacity: 1;
  }
}

@keyframes image-skeleton-shimmer {
  100% {
    transform: translateX(100%);
  }
}

@media (max-width: 768px) {
  .post-image {
    .preview {
      gap: 3px;
    }

    .image-status {
      gap: 8px;
      padding: 14px;
    }

    .image-status-loading {
      .loading-frame {
        width: min(68%, 156px);
      }

      .loading-cloud-left {
        width: 28px;
      }

      .loading-cloud-right {
        width: 24px;
      }

      .loading-spark {
        width: 10px;
        height: 10px;
      }
    }

    .image-status-error {
      .el-icon {
        font-size: 24px;
      }

      span {
        font-size: 11px;
      }
    }
  }
}
</style>
