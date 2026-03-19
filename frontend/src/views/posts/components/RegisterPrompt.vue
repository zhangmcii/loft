<template>
  <div class="register-prompt" @click="handleExplore">
    <div class="prompt-meta">
      <span>访客入口</span>
      <span>{{ currentUsers.toLocaleString() }} 位读者正在浏览</span>
      <span>本周新增 {{ weeklyPosts }} 条内容</span>
    </div>

    <div class="prompt-main">
      <div class="prompt-copy">
        <h3>登录后可继续阅读、关注作者并参与互动</h3>
        <p>如果你只是先看看，这里依然保留清晰、连续的阅读路径。</p>
      </div>

      <div class="prompt-actions">
        <el-button class="prompt-button" @click.stop="$router.push('/login')">
          登录
        </el-button>
        <el-button
          class="prompt-button is-secondary"
          @click.stop="$router.push('/register')"
        >
          注册
        </el-button>
      </div>
    </div>
  </div>
</template>

<script>
const STATS_CONFIG = {
  BASE_USERS: 127, // 初始用户基数
  USERS_PER_HOUR: 1, // 每小时新增用户数（可根据实际情况调整）
  BASE_WEEKLY_POSTS: 36, // 基础周新增随想数
  WEEKLY_VARIATION: 15, // 每周波动范围
  CACHE_KEY: "loft_stats_cache", // localStorage key
  UPDATE_INTERVAL: 5 * 60 * 1000, // 5分钟更新一次
};

export default {
  name: "RegisterPrompt",
  data() {
    return {
      currentUsers: 127,
      weeklyPosts: 36,
      updateTimer: null,
    };
  },
  created() {
    this.initStats();
    // 每5分钟更新一次数据
    this.updateTimer = setInterval(() => {
      this.updateStats();
    }, STATS_CONFIG.UPDATE_INTERVAL);
  },
  beforeUnmount() {
    // 清理定时器
    if (this.updateTimer) {
      clearInterval(this.updateTimer);
      this.updateTimer = null;
    }
  },
  methods: {
    // 初始化统计数据
    initStats() {
      const cache = this.getCache();
      const now = new Date();
      const today = now.toDateString();

      // 检查是否是新的一天
      if (cache.lastCalcDate !== today) {
        // 重新计算今日数据
        const startOfDay = new Date(now).setHours(0, 0, 0, 0);
        const hoursPassed = Math.min((now - startOfDay) / (1000 * 60 * 60), 24);
        const todayGrowth = Math.floor(
          hoursPassed * STATS_CONFIG.USERS_PER_HOUR
        );

        cache.lastCalcDate = today;
        cache.todayUsers = STATS_CONFIG.BASE_USERS + todayGrowth;
        cache.weeklyPosts = this.calculateWeeklyPosts();
        this.setCache(cache);
      }

      this.currentUsers = cache.todayUsers;
      this.weeklyPosts = cache.weeklyPosts;
    },

    // 更新统计数据
    updateStats() {
      const now = new Date();
      const today = now.toDateString();
      const cache = this.getCache();

      // 如果是新的一天，重新计算
      if (cache.lastCalcDate !== today) {
        // 每周一重置基数（模拟每周统计重置）
        const dayOfWeek = now.getDay(); // 0=周日
        if (dayOfWeek === 1) {
          // 周一
          // 根据上周表现微调本周基数
          const variation = Math.floor((Math.random() - 0.5) * 20);
          STATS_CONFIG.BASE_USERS = STATS_CONFIG.BASE_USERS + variation;
        }

        this.initStats();
      } else {
        // 同一天内，更新用户数和随想数
        const startOfDay = new Date(now).setHours(0, 0, 0, 0);
        const hoursPassed = Math.min((now - startOfDay) / (1000 * 60 * 60), 24);
        const todayGrowth = Math.floor(
          hoursPassed * STATS_CONFIG.USERS_PER_HOUR
        );

        this.currentUsers = STATS_CONFIG.BASE_USERS + todayGrowth;
        this.weeklyPosts = this.calculateWeeklyPosts();

        // 更新缓存
        cache.todayUsers = this.currentUsers;
        cache.weeklyPosts = this.weeklyPosts;
        this.setCache(cache);
      }
    },

    // 计算本周新增随想数
    calculateWeeklyPosts() {
      const now = new Date();
      const dayOfWeek = now.getDay(); // 0=周日
      const weekProgress = Math.max(dayOfWeek, 1) / 7; // 至少按周一计算

      // 基础值 + 本周进度 + 随机波动
      // 周一：86 * 0.7 + 波动
      // 周日：86 * 1.0 + 波动
      const baseAmount =
        STATS_CONFIG.BASE_WEEKLY_POSTS * (0.7 + weekProgress * 0.3);
      const randomFactor =
        (Math.random() - 0.5) * STATS_CONFIG.WEEKLY_VARIATION;

      return Math.max(1, Math.floor(baseAmount + randomFactor));
    },

    // 获取缓存
    getCache() {
      try {
        const cached = localStorage.getItem(STATS_CONFIG.CACHE_KEY);
        if (cached) {
          return JSON.parse(cached);
        }
      } catch (e) {
        console.warn("读取统计数据缓存失败:", e);
      }

      // 初始化缓存
      return {
        baseUsers: STATS_CONFIG.BASE_USERS,
        todayUsers: STATS_CONFIG.BASE_USERS,
        weeklyPosts: STATS_CONFIG.BASE_WEEKLY_POSTS,
        lastCalcDate: new Date().toDateString(),
      };
    },

    // 设置缓存
    setCache(data) {
      try {
        localStorage.setItem(STATS_CONFIG.CACHE_KEY, JSON.stringify(data));
      } catch (e) {
        console.warn("保存统计数据缓存失败:", e);
      }
    },

    // 点击探索
    handleExplore() {
      ElMessage({
        message: "登录后继续探索更多精彩内容",
        type: "info",
        duration: 2000,
      });
    },

    // 格式化数字（可选：大于1000时显示为K）
    formatNumber(num) {
      if (num >= 1000) {
        return (num / 1000).toFixed(1) + "K";
      }
      return num.toString();
    },
  },
};
</script>

<style lang="scss" scoped>
.register-prompt {
  margin: 18px 0 22px;
  cursor: pointer;
  background: #fff;
  border-top: 1px solid #ececec;
  border-bottom: 1px solid #ececec;
  transition: border-color 0.2s ease;
  padding: 16px 0 18px;

  &:hover {
    border-color: #dcdcdc;
  }
}

.prompt-meta {
  display: flex;
  gap: 18px;
  flex-wrap: wrap;
  margin-bottom: 12px;
  font-size: 12px;
  line-height: 1.7;
  color: #777;
  letter-spacing: 0.03em;
}

.prompt-main {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 18px;
}

.prompt-copy {
  flex: 1;

  h3 {
    margin: 0 0 8px;
    font-size: 17px;
    font-weight: 500;
    color: #111;
    line-height: 1.45;
  }

  p {
    margin: 0;
    font-size: 13px;
    color: #666;
    line-height: 1.8;
  }
}

.prompt-actions {
  display: flex;
  gap: 10px;
  flex-shrink: 0;
}

.prompt-button {
  min-width: 72px;
  height: 34px;
  padding: 0 14px;
  color: #111;
  background: #111;
  border: 1px solid #111;
  border-radius: 999px;
  font-size: 13px;
}

.prompt-button.is-secondary {
  color: #444;
  background: #fff;
  border-color: #d8d8d8;
}

@media (max-width: 768px) {
  .register-prompt {
    margin: 16px 0 20px;
    padding: 14px 0 16px;
  }

  .prompt-main {
    flex-direction: column;
    align-items: flex-start;
  }

  .prompt-actions {
    width: 100%;
  }

  .prompt-button {
    flex: 1;
  }
}
</style>
