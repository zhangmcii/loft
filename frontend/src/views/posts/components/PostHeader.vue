<script>
import date from "@/utils/date.js";
import { useOtherUserStore } from "@/stores/otherUser";
export default {
  props: {
    post: {
      type: Object,
      default() {
        return {
          id: 1,
          content: "",
          post_type: "text",
          timestamp: "",
          author: "--",
          nick_name: "",
          user_id: 1,
          commentCount: 20,
          disabled: false,
          image: "",
          comment_count: 0,
          praise_num: 0,
          has_praised: false,
          post_images: [],
        };
      },
    },
    compact: {
      type: Boolean,
      default: false,
    },
    mode: {
      type: String,
      default: "default",
    },
  },
  data() {
    return {
      touchTimer: null,
    };
  },
  setup() {
    const otherUser = useOtherUserStore();
    return { otherUser };
  },
  computed: {
    from_now() {
      return date.dateShow(this.post.timestamp);
    },
    displayName() {
      return this.post.nick_name ? this.post.nick_name : this.post.author;
    },
    isByline() {
      return this.mode === "byline";
    },
  },
  methods: {
    handleUserClick(event) {
      // 阻止事件冒泡和默认行为
      if (event) {
        event.preventDefault();
        event.stopPropagation();
      }
      this.toUser(false);
    },

    handleMusicClick(event) {
      // 阻止事件冒泡和默认行为
      if (event) {
        event.preventDefault();
        event.stopPropagation();
      }
      this.toUser(true);
    },

    handleTouchStart(event) {
      if (this.touchTimer) {
        clearTimeout(this.touchTimer);
      }
      this.touchTimer = setTimeout(() => {
        // 长按逻辑（如果需要）
      }, 300);
    },

    handleTouchEnd(event) {
      if (this.touchTimer) {
        clearTimeout(this.touchTimer);
      }
    },

    toUser(playMusic = false) {
      this.otherUser.userInfo.id = this.post.user_id;
      const url = playMusic
        ? `/user/${this.post.author}?playMusic=true`
        : `/user/${this.post.author}`;
      this.$router.push(url);
    },
  },
};
</script>

<template>
  <div v-if="isByline" class="byline">
    <p class="byline-line">
      <span
        @click="handleUserClick"
        @touchstart="handleTouchStart"
        @touchend="handleTouchEnd"
        class="byline-name"
        >{{ displayName }}</span
      >
      <span class="byline-separator">·</span>
      <span class="byline-time">{{ from_now }}</span>
    </p>
    <p
      v-if="post.music?.name"
      @click="handleMusicClick"
      @touchstart="handleTouchStart"
      @touchend="handleTouchEnd"
      class="byline-note"
    >
      <span>{{ post.music.name }}-{{ post.music.artist }}</span>
    </p>
  </div>
  <el-row
    v-else
    class="head"
    :class="{ 'head-compact': compact }"
    justify="space-between"
    align="middle"
  >
    <div class="user-info">
      <el-avatar
        alt="用户图像"
        :src="post.image"
        @click="handleUserClick"
        @touchstart="handleTouchStart"
        @touchend="handleTouchEnd"
      />
      <div class="user-mata">
        <span
          @click="handleUserClick"
          @touchstart="handleTouchStart"
          @touchend="handleTouchEnd"
          class="nickname"
          >{{ displayName }}</span
        >
        <div
          v-if="post.music?.name"
          @click="handleMusicClick"
          @touchstart="handleTouchStart"
          @touchend="handleTouchEnd"
          class="music"
        >
          <el-icon><i-ep-Headset /></el-icon>
          <span>{{ post.music.name }}-{{ post.music.artist }}</span>
        </div>
      </div>
    </div>
    <div>
      <el-text size="small" class="head-time">{{ from_now }}</el-text>
    </div>
  </el-row>
</template>

<style lang="scss" scoped>
@use "./PostReadingTokens.scss" as tokens;

.byline {
  margin: 0;
}

.byline-line,
.byline-note {
  margin: 0;
}

.byline-line {
  display: flex;
  align-items: baseline;
  gap: 6px;
  color: tokens.$reading-text-tertiary;
  font-size: 13px;
  line-height: 1.6;
}

.byline-name {
  color: tokens.$reading-text-primary;
  font-weight: 500;
  cursor: pointer;
}

.byline-separator,
.byline-time {
  color: tokens.$reading-text-quaternary;
}

.byline-note {
  margin-top: 6px;
  color: tokens.$reading-text-quaternary;
  font-size: tokens.$reading-font-size-meta;
  line-height: 1.6;
  cursor: pointer;
}

.head {
  min-height: 42px;
  margin-bottom: 0;

  .user-info {
    display: flex;
    align-items: center;
    gap: 12px;
    cursor: pointer;

    .el-avatar {
      cursor: pointer;
      width: 30px;
      height: 30px;
      border: 1px solid tokens.$reading-border;
      transition: opacity 0.2s ease, border-color 0.2s ease;

      &:hover {
        opacity: 0.92;
        border-color: tokens.$reading-border-strong;
      }
    }

    .user-mata {
      display: flex;
      flex-direction: column;
      gap: 2px;

      .nickname {
        font-size: tokens.$reading-font-size-author;
        font-weight: 500;
        color: tokens.$reading-text-primary;
        line-height: 1.35;

        &:hover {
          color: tokens.$reading-text-primary;
        }
      }

      .music {
        display: flex;
        align-items: center;
        gap: 4px;
        font-size: tokens.$reading-font-size-caption;
        color: tokens.$reading-text-quaternary;
      }
    }
  }

  .head-time {
    margin-right: 1px;
    color: tokens.$reading-text-quaternary;
    letter-spacing: 0.02em;
  }
}

.head-compact {
  min-height: 32px;

  .user-info {
    gap: 8px;

    .el-avatar {
      width: 24px;
      height: 24px;
    }

    .user-mata {
      gap: 2px;

      .nickname {
        font-size: 13px;
      }

      .music {
        font-size: tokens.$reading-font-size-caption;
      }
    }
  }

  .head-time {
    font-size: tokens.$reading-font-size-caption;
    color: tokens.$reading-text-quaternary;
  }
}

@media (max-width: 768px) {
  .byline-line {
    font-size: 12px;
  }

  .byline-note {
    font-size: 11px;
  }
}
</style>
