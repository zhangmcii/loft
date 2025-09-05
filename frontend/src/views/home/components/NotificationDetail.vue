<script>
import NotificationTitle from "./NotificationTitle.vue";
import date from "@/utils/date.js";

export default {
  props: {
    notifications: {
      type: Array,
      default: () => [],
    },
    dot: {
      type: Boolean,
      default: false,
    },
  },
  components: {
    NotificationTitle,
  },
  data() {
    return {};
  },
  mounted() {},
  methods: {
    formatTime(time) {
      return date.dateShow(time);
    },
    getNotificationTypeClass(type) {
      const typeMap = {
        评论: "type-comment",
        回复: "type-reply",
        点赞: "type-like",
        "@": "type-mention",
        私信: "type-message",
        新文章: "type-post",
      };
      return typeMap[type] || "type-default";
    },
    getNotificationTypeIcon(type) {
      const iconMap = {
        评论: "💬",
        回复: "↩️",
        点赞: "❤️",
        "@": "@",
        私信: "✉️",
        新文章: "📝",
      };
      return iconMap[type] || "🔔";
    },
  },
};
</script>

<template>
  <el-scrollbar class="notification-scrollbar" v-if="notifications.length > 0">
    <ul class="notifications-list">
      <template v-for="item in notifications" :key="item.title">
        <li
          class="notification-item"
          :class="{ unread: !item.isRead }"
          @click="$emit('read', item)"
        >
          <div class="notification-content">
            <span v-if="!item.isRead" class="unread-indicator"></span>

            <div class="avatar-wrapper">
              <img
                :src="item.image"
                class="avatar-image"
                :alt="`${item.triggerNickName || '用户'}的头像`"
              />
              <div
                class="notification-type-badge"
                :class="getNotificationTypeClass(item.type)"
              >
                {{ getNotificationTypeIcon(item.type) }}
              </div>
            </div>

            <div class="message-content">
              <NotificationTitle :nItem="item" class="notification-title" />
              <div class="message-footer">
                <p class="notification-date">{{ formatTime(item.time) }}</p>
                <button
                  class="action-button"
                  v-if="item.type === '私信'"
                  @click.stop="$emit('viewChat', item)"
                >
                  <span class="action-icon">💬</span>
                  查看对话
                </button>
                <button
                  class="action-button"
                  v-else
                  @click.stop="$emit('viewPost', item)"
                >
                  <span class="action-icon">📄</span>
                  查看原文
                </button>
              </div>
            </div>
          </div>
        </li>
      </template>
    </ul>
  </el-scrollbar>

  <template v-else>
    <div class="empty-state">
      <div class="empty-icon">📭</div>
      <p class="empty-text">暂无通知</p>
    </div>
  </template>
</template>

<style scoped>
:root {
  --primary-color: #3a7bd5;
  --secondary-color: #00d2ff;
  --accent-color: #4a90e2;
  --danger-color: #f56c6c;
  --success-color: #67c23a;
  --warning-color: #e6a23c;
  --info-color: #909399;
  --text-color: #2c3e50;
  --light-text: #6c757d;
  --border-color: #e9ecef;
  --hover-color: #f8f9fa;
  --shadow-color: rgba(0, 0, 0, 0.08);
}

.notification-scrollbar {
  max-height: 360px;
  width: 100%;
}

.notifications-list {
  display: flex;
  width: 100%;
  flex-direction: column;
  list-style: none;
  padding: 0;
  margin: 0;
}

.notification-item {
  position: relative;
  width: 100%;
  cursor: pointer;
  border-bottom: 1px solid var(--border-color);
  padding: 12px 16px;
  background: transparent;
  transition: all 0.3s ease;
  box-sizing: border-box;
}

.notification-item:hover {
  background-color: rgba(74, 144, 226, 0.05);
}

.notification-item.unread {
  background-color: rgba(74, 144, 226, 0.15);
  border-left: 3px solid var(--primary-color);
}

.notification-content {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  width: 100%;
  overflow: hidden;
}

.unread-indicator {
  position: absolute;
  left: 4px;
  top: 50%;
  transform: translateY(-50%);
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(58, 123, 213, 0.2);
  animation: pulse-dot 1.5s cubic-bezier(0.455, 0.03, 0.515, 0.955) infinite;
}

@keyframes pulse-dot {
  0% {
    transform: translateY(-50%) scale(0.8);
  }
  50% {
    transform: translateY(-50%) scale(1.2);
  }
  100% {
    transform: translateY(-50%) scale(0.8);
  }
}

.avatar-wrapper {
  position: relative;
  width: 40px;
  height: 40px;
  flex-shrink: 0;
}

.avatar-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 50%;
  box-shadow: 0 2px 6px var(--shadow-color);
  border: 2px solid white;
}

.notification-type-badge {
  position: absolute;
  bottom: -2px;
  right: -2px;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background-color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border: 1px solid var(--border-color);
}

.type-comment {
  background-color: #e6f7ff;
  color: #1890ff;
}

.type-reply {
  background-color: #f6ffed;
  color: #52c41a;
}

.type-like {
  background-color: #fff1f0;
  color: #ff4d4f;
}

.type-mention {
  background-color: #fff7e6;
  color: #fa8c16;
}

.type-message {
  background-color: #f9f0ff;
  color: #722ed1;
}

.type-post {
  background-color: #f0f5ff;
  color: #2f54eb;
}

.message-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6px;
  width: calc(100% - 52px);
  overflow: hidden;
}

.notification-title {
  font-weight: 500;
  font-size: 14px;
  line-height: 1.4;
  color: var(--text-color);
  white-space: normal;
  word-break: break-word;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  max-width: 100%;
}

.message-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 4px;
  width: 100%;
}

.notification-date {
  color: var(--light-text);
  font-size: 12px;
  margin: 0;
  flex-shrink: 0;
}

.action-button {
  display: flex;
  align-items: center;
  gap: 4px;
  background: none;
  border: none;
  color: var(--primary-color);
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.action-button:hover {
  background-color: rgba(74, 144, 226, 0.1);
  transform: translateY(-1px);
}

.action-icon {
  font-size: 12px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--light-text);
  min-height: 200px;
  width: 100%;
  padding: 20px;
}

.empty-icon {
  font-size: 36px;
  margin-bottom: 12px;
  opacity: 0.6;
}

.empty-text {
  font-size: 14px;
  color: var(--light-text);
}
</style>
