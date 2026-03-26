<script>
import postApi from "@/api/posts/postApi.js";
import PageScroll from "@/utils/components/PageScroll.vue";
import SkeletonUtil from "@/utils/components/SkeletonUtil.vue";
import PostPreview from "@/views/posts/components/PostPreview.vue";
import PostImage from "@/views/posts/components/PostImage.vue";
import { useCurrentUserStore } from "@/stores/user";
import { useSearchHistoryStore } from "@/stores/searchHistory";
import { Search } from "@element-plus/icons-vue";

export default {
  name: "PostSearchPage",
  components: {
    PageScroll,
    SkeletonUtil,
    PostPreview,
    PostImage,
    Search,
  },
  data() {
    return {
      keyword: "",
      searchKeyword: "",
      results: [],
      total: -1,
      currentPage: 1,
      loading: {
        card: false,
        more: false,
      },
      throttle: {
        leading: 0,
        trailing: 0,
        initVal: false,
      },
    };
  },
  setup() {
    const currentUser = useCurrentUserStore();
    const searchHistoryStore = useSearchHistoryStore();
    return { currentUser, searchHistoryStore };
  },
  computed: {
    userHistory() {
      return this.searchHistoryStore.getHistory(
        this.currentUser?.userInfo?.id || "guest"
      );
    },
    canSearch() {
      return this.keyword.trim() !== "";
    },
    showHistory() {
      return (
        !this.hasKeyword && !this.keyword.trim() && this.userHistory.length > 0
      );
    },
    hasKeyword() {
      return this.searchKeyword.trim() !== "";
    },
    noMore() {
      if (this.total < 0) return false;
      return this.results.length >= this.total;
    },
    infiniteDisabled() {
      return (
        !this.hasKeyword ||
        this.loading.card ||
        this.loading.more ||
        this.noMore
      );
    },
    resultSummary() {
      if (!this.hasKeyword) return "";
      if (this.loading.card && this.results.length === 0) {
        return `正在查找 “${this.searchKeyword}”`;
      }
      return `“${this.searchKeyword}” 的搜索结果`;
    },
  },
  mounted() {
    const initialKeyword = String(this.$route.query.q || "").trim();
    if (initialKeyword) {
      this.keyword = initialKeyword;
      this.submitSearch();
    }
  },
  methods: {
    goBack() {
      if (window.history.length > 1) {
        this.$router.back();
      } else {
        this.$router.push("/posts");
      }
    },
    syncRouteQuery() {
      const nextQuery = this.searchKeyword ? { q: this.searchKeyword } : {};
      this.$router.replace({ query: nextQuery });
    },
    async submitSearch() {
      const nextKeyword = this.keyword.trim();
      this.searchKeyword = nextKeyword;
      this.results = [];
      this.total = -1;
      this.currentPage = 1;
      this.syncRouteQuery();

      if (!nextKeyword) {
        return;
      }

      this.searchHistoryStore.addHistory(
        this.currentUser?.userInfo?.id || "guest",
        nextKeyword
      );
      await this.fetchResults(1, { append: false });
    },
    async fetchResults(page, { append = false } = {}) {
      if (!this.searchKeyword) {
        return false;
      }
      const loadingKey = append ? "more" : "card";
      this.loading[loadingKey] = true;
      try {
        const res = await postApi.searchPosts(page, this.searchKeyword);
        if (res.code === 200) {
          const list = Array.isArray(res.data) ? res.data : [];
          this.results = append ? [...this.results, ...list] : list;
          if (typeof res.total === "number") {
            this.total = res.total;
          } else if (!append) {
            this.total = list.length;
          } else {
            this.total = Math.max(this.total, this.results.length);
          }
          return true;
        }
      } finally {
        this.loading[loadingKey] = false;
      }
      return false;
    },
    async loadMore() {
      if (this.infiniteDisabled) return;
      const nextPage = this.currentPage + 1;
      const ok = await this.fetchResults(nextPage, { append: true });
      if (ok) {
        this.currentPage = nextPage;
      }
    },
    clearSearch() {
      this.keyword = "";
      this.searchKeyword = "";
      this.results = [];
      this.total = -1;
      this.currentPage = 1;
      this.syncRouteQuery();
    },
    applyHistory(keyword) {
      this.keyword = keyword;
      this.submitSearch();
    },
    clearHistory() {
      this.searchHistoryStore.clearHistory(
        this.currentUser?.userInfo?.id || "guest"
      );
    },
  },
};
</script>

<template>
  <PageScroll max-height="calc(100vh - var(--app-header-height))">
    <div
      class="search-page"
      v-infinite-scroll="loadMore"
      :infinite-scroll-delay="200"
      :infinite-scroll-distance="160"
      :infinite-scroll-disabled="infiniteDisabled"
      :infinite-scroll-immediate="false"
    >
      <section class="search-shell">
        <header class="search-topbar">
          <button
            type="button"
            class="search-back"
            @click="goBack"
            aria-label="返回"
          >
            ←
          </button>
          <div class="search-bar">
            <el-input
              v-model="keyword"
              class="search-input"
              placeholder="搜索文章标题、正文"
              clearable
              @keyup.enter="submitSearch"
            >
              <template #prefix>
                <el-icon class="search-input-icon">
                  <Search />
                </el-icon>
              </template>
            </el-input>
            <el-button
              class="search-submit"
              type="text"
              :disabled="!canSearch"
              :loading="loading.card"
              @click="submitSearch"
            >
              搜索
            </el-button>
          </div>
        </header>

        <div v-if="showHistory" class="search-history">
          <div class="search-history-head">
            <p class="search-history-title">最近搜索</p>
            <el-button
              type="text"
              class="search-history-clear"
              @click="clearHistory"
            >
              清空
            </el-button>
          </div>
          <div class="search-history-list">
            <el-tag
              v-for="item in userHistory"
              :key="item"
              class="search-history-tag"
              type="info"
              effect="plain"
              @click="applyHistory(item)"
            >
              {{ item }}
            </el-tag>
          </div>
        </div>

        <div v-if="hasKeyword" class="search-meta">
          <div class="search-meta-copy">
            <p class="search-meta-title">
              <span v-if="loading.card && results.length === 0">正在查找</span>
              <span class="search-meta-keyword">“{{ searchKeyword }}”</span>
              <span v-if="total >= 0" class="search-meta-sep">·</span>
              <span v-if="total >= 0" class="search-meta-count-inline"
                >{{ total }} 篇</span
              >
            </p>
          </div>
          <el-button type="text" class="search-clear" @click="clearSearch">
            清空
          </el-button>
        </div>

        <!-- <div v-else class="search-empty search-empty-idle" :class="{ 'search-empty-borderless': showHistory }">
          <p class="search-empty-title">搜索一篇想继续读的内容</p>
          <p class="search-empty-note">支持标题、正文关键词。</p>
        </div> -->

        <SkeletonUtil
          :loading="loading.card"
          :row="5"
          :throttle="throttle"
          :useNew="true"
        >
          <transition-group
            v-if="results.length"
            name="slide-in"
            tag="div"
            class="search-results"
          >
            <PostPreview
              v-for="item in results"
              :key="item.id"
              :post="item"
              @click="$router.push(`/postDetail/${item.id}`)"
            >
              <template #image>
                <PostImage :postImages="item.post_images" @click.stop="" />
              </template>
            </PostPreview>
          </transition-group>
        </SkeletonUtil>

        <!-- <div
          v-if="hasKeyword && !loading.card && !results.length"
          class="search-empty"
        >
          <p class="search-empty-title">没有找到相关内容</p>
          <p class="search-empty-note">换一个词，或者试试更短的关键词。</p>
        </div> -->

        <div v-if="results.length" class="search-infinite-footer">
          <div v-if="loading.more" class="search-loading">加载中...</div>
          <div v-else-if="noMore" class="search-end">已经到底了～</div>
        </div>
      </section>
    </div>
  </PageScroll>
</template>

<style lang="scss" scoped>
@use "./components/PostCard.scss" as *;
@use "./components/PostReadingTokens.scss" as tokens;

.search-shell {
  width: min(100%, tokens.$reading-shell-width);
  margin: 0 auto;
  padding: 24px 24px 56px;
  box-sizing: border-box;
}

.search-topbar {
  display: flex;
  align-items: center;
  gap: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid tokens.$reading-border;
}

.search-back {
  padding: 0;
  border: none;
  background: transparent;
  color: tokens.$reading-text-quaternary;
  font-size: 15px;
  line-height: 1;
  cursor: pointer;
  transition: color 0.2s ease;

  &:hover {
    color: tokens.$reading-text-primary;
  }
}

.search-input-wrap {
  min-width: 0;
}

.search-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1 1 auto;
  min-width: 0;
}

.search-input {
  flex: 1 1 auto;
  min-width: 0;

  :deep(.el-input__wrapper) {
    min-height: 32px;
    padding: 0 2px 0 0;
    border-radius: 0;
    box-shadow: none;
    background: transparent;
    border-bottom: 1px solid tokens.$reading-border;
    transition: border-color 0.2s ease, border-bottom-width 0.2s ease;
  }

  :deep(.el-input__wrapper.is-focus) {
    border-bottom-color: tokens.$reading-border-strong;
    border-bottom-width: 1.5px;
  }

  :deep(.el-input__inner) {
    font-size: 13px;
    color: tokens.$reading-text-primary;
  }

  :deep(.el-input__inner::placeholder) {
    color: tokens.$reading-text-quaternary;
  }
}

.search-input-icon {
  font-size: 13px;
  color: tokens.$reading-text-quaternary;
}

.search-submit {
  padding: 0;
  font-size: 13px;
  font-weight: 500;
  line-height: 1;
  color: tokens.$reading-text-secondary;
  text-decoration: underline;
  text-decoration-color: transparent;
  text-underline-offset: 3px;
  transition: color 0.2s ease, text-decoration-color 0.2s ease;

  &:hover,
  &:focus {
    color: tokens.$reading-text-primary;
    text-decoration-color: tokens.$reading-border;
  }

  &.is-disabled,
  &.is-disabled:hover,
  &.is-disabled:focus {
    color: tokens.$reading-text-quaternary;
    text-decoration-color: transparent;
  }
}

.search-history {
  padding: 16px 0 12px;
  border-bottom: 1px solid tokens.$reading-border-soft;
}

.search-history-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 8px;
}

.search-history-title {
  margin: 0;
  font-size: 12px;
  color: tokens.$reading-text-quaternary;
  letter-spacing: 0.04em;
}

.search-history-clear,
.search-clear {
  padding: 0;
  color: tokens.$reading-text-quaternary;

  &:hover,
  &:focus {
    color: tokens.$reading-text-primary;
  }
}

.search-history-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.search-history-tag {
  cursor: pointer;
  height: 30px;
  padding: 0 10px;
  border-color: tokens.$reading-border;
  border-radius: 6px;
  background: #fff;
  color: tokens.$reading-text-secondary;
  transition: border-color 0.2s ease, background-color 0.2s ease,
    color 0.2s ease;

  &:hover {
    border-color: tokens.$reading-border-strong;
    color: tokens.$reading-text-primary;
    background: tokens.$reading-fill-softer;
  }

  :deep(.el-tag__content) {
    max-width: 220px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    font-size: 12px;
    line-height: 1.4;
  }
}

.search-meta {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
  padding: 16px 0 8px;
}

.search-meta-copy {
  min-width: 0;
}

.search-meta-title {
  margin: 0;
  font-size: 12px;
  line-height: 1.7;
  color: tokens.$reading-text-secondary;
}

.search-meta-keyword {
  color: tokens.$reading-text-primary;
}

.search-meta-sep {
  margin: 0 6px;
  color: tokens.$reading-text-quaternary;
}

.search-meta-count-inline {
  color: tokens.$reading-text-quaternary;
}

.search-results {
  min-height: 20px;
}

.search-empty {
  padding: 24px 0 32px;
  border-bottom: 1px solid tokens.$reading-border;
}

.search-empty-idle {
  margin-top: 0;
}

.search-empty-borderless {
  border-bottom: none;
  padding-top: 10px;
}

.search-empty-title {
  margin: 0;
  font-size: 16px;
  line-height: 1.45;
  font-weight: 500;
  color: tokens.$reading-text-primary;
}

.search-empty-note {
  margin: 6px 0 0;
  font-size: 12px;
  line-height: 1.7;
  color: tokens.$reading-text-tertiary;
}

.search-infinite-footer {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 32px;
  padding: 4px 0 20px;
  color: tokens.$reading-text-tertiary;
  font-size: 12px;
  letter-spacing: 0.04em;
}

.search-loading {
  display: inline-flex;
  align-items: center;

  &::before {
    content: "·";
    margin-right: 6px;
  }
}

.search-end {
  color: tokens.$reading-text-quaternary;
}

@media (max-width: 768px) {
  .search-shell {
    width: min(100%, 700px);
    padding: 22px 16px 40px;
  }

  .search-topbar {
    gap: 10px;
  }

  .search-submit {
    padding: 0 12px;
  }

  .search-meta {
    align-items: flex-start;
    flex-direction: column;
    gap: 8px;
    padding-top: 16px;
  }

  .search-empty {
    padding: 24px 0 30px;
  }

  .search-empty-title {
    font-size: 16px;
  }
}
</style>
