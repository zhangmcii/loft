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
  color: #6f6f6f;
  font-size: 13px;
  line-height: 1.5;
}

.byline-name {
  color: #1f1f1f;
  font-weight: 500;
  cursor: pointer;
}

.byline-separator,
.byline-time {
  color: #8a8a8a;
}

.byline-note {
  margin-top: 4px;
  color: #929292;
  font-size: 11px;
  line-height: 1.5;
  cursor: pointer;
}

.head {
  min-height: 40px;
  margin-bottom: 0;

  .user-info {
    display: flex;
    align-items: center;
    gap: 10px;
    cursor: pointer;

    .el-avatar {
      cursor: pointer;
      width: 28px;
      height: 28px;
      border: 1px solid #e9e9e9;
      transition: opacity 0.2s ease;

      &:hover {
        opacity: 0.75;
      }
    }

    .user-mata {
      display: flex;
      flex-direction: column;
      gap: 3px;

      .nickname {
        font-size: 14px;
        font-weight: 500;
        color: #141414;
        line-height: 1.3;

        &:hover {
          color: #141414;
        }
      }

      .music {
        display: flex;
        align-items: center;
        gap: 4px;
        font-size: 11px;
        color: #7d7d7d;
      }
    }
  }

  .head-time {
    margin-right: 1px;
    color: #7d7d7d;
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
        font-size: 10px;
      }
    }
  }

  .head-time {
    font-size: 11px;
    color: #8a8a8a;
  }
}

@media (max-width: 768px) {
  .byline-line {
    font-size: 12px;
  }

  .byline-note {
    font-size: 10px;
  }
}
</style>
