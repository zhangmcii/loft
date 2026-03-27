<script>
import PostPreview from "@/views/posts/components/PostPreview.vue";
import PostImage from "@/views/posts/components/PostImage.vue";
import notificationApi from "@/api/notification/notificationApi.js";
import postApi from "@/api/posts/postApi.js";
import { useCurrentUserStore } from "@/stores/user";
import SkeletonUtil from "@/utils/components/SkeletonUtil.vue";
import PublishEntry from "@/views/posts/components/PublishEntry.vue";
import SearchEntry from "@/views/posts/components/SearchEntry.vue";
import RegisterPrompt from "@/views/posts/components/RegisterPrompt.vue";
import PageScroll from "@/utils/components/PageScroll.vue";
import emitter from "@/utils/emitter.js";

export default {
  components: {
    PostPreview,
    PostImage,
    PublishEntry,
    SearchEntry,
    SkeletonUtil,
    RegisterPrompt,
    PageScroll,
  },
  data() {
    return {
      activeName: "all",
      posts: [],
      posts_count: -1,
      currentPage: 1,
      loading: {
        publishPost: false,
        card: false,
        more: false,
      },
      showEmoji: false,
      // 延迟渲染会导致与空页面闪烁
      throttle: {
        leading: 0,
        trailing: 0,
        initVal: false,
      },
      showDot: false,
      followPost: [],
      followPostHandler: null,
      newPostListHandler: null,
      postDeletedHandler: null,
    };
  },
  computed: {
    noMore() {
      if (this.posts_count < 0) return false;
      return this.posts.length >= this.posts_count;
    },
    infiniteDisabled() {
      return this.loading.card || this.loading.more || this.noMore;
    },
  },
  setup() {
    const currentUser = useCurrentUserStore();
    return { currentUser };
  },
  mounted() {
    this.resetPosts(this.activeName);
    // 关注的用户发布了新文章
    this.followPostHandler = (newPost) => {
      this.showDot = true;
      this.followPost = [...newPost];
      console.log("newPost", this.followPost);
    };
    emitter.on("followPost", this.followPostHandler);
    this.newPostListHandler = (payload) => {
      const list = Array.isArray(payload?.list) ? payload.list : [];
      this.posts = list;
      this.posts_count =
        typeof payload?.total === "number" ? payload.total : list.length;
      this.currentPage = 1;
      this.loading.publishPost = false;
      this.loading.card = false;
      this.loading.more = false;
    };
    emitter.on("newPostList", this.newPostListHandler);
    // 监听文章删除事件，刷新页面
    this.postDeletedHandler = () => {
      this.resetPosts(this.activeName);
    };
    emitter.on("postDeleted", this.postDeletedHandler);
  },
  methods: {
    changeTab(tabName) {
      this.resetPosts(tabName);
    },
    resetPosts(tabName) {
      this.currentPage = 1;
      this.posts = [];
      this.posts_count = -1;
      this.loading.more = false;
      this.fetchPosts(1, tabName, { append: false });
    },
    async fetchPosts(page, tabName, { append = false } = {}) {
      const loadingKey = append ? "more" : "card";
      this.loading[loadingKey] = true;
      if (tabName === "showFollowed" && this.showDot && page === 1) {
        const ids = this.followPost.map((item) => item.id);
        notificationApi.markRead({ ids }).then(() => {
          this.showDot = false;
        });
      }
      try {
        const res = await postApi.getPosts(page, tabName);
        if (res.code === 200) {
          const list = Array.isArray(res.data) ? res.data : [];
          this.posts = append ? [...this.posts, ...list] : list;
          if (typeof res.total === "number") {
            this.posts_count = res.total;
          } else if (!append) {
            this.posts_count = list.length;
          } else {
            this.posts_count = Math.max(this.posts_count, this.posts.length);
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
      const ok = await this.fetchPosts(nextPage, this.activeName, {
        append: true,
      });
      if (ok) {
        this.currentPage = nextPage;
      }
    },
    getPostsResult(post) {
      const newPosts = Array.isArray(post) ? post : [post];
      this.posts.unshift(...newPosts);
      if (this.posts_count >= 0) {
        this.posts_count += newPosts.length;
      }

      // 首页设置了缓存，手动更新为第一页
      this.currentPage = 1;
      this.loading.publishPost = false;
    },
  },
  beforeUnmount() {
    // 清理事件监听
    if (this.followPostHandler) {
      emitter.off("followPost", this.followPostHandler);
      this.followPostHandler = null;
    }
    if (this.newPostListHandler) {
      emitter.off("newPostList", this.newPostListHandler);
      this.newPostListHandler = null;
    }
    if (this.postDeletedHandler) {
      emitter.off("postDeleted", this.postDeletedHandler);
      this.postDeletedHandler = null;
    }
  },
};
</script>

<template>
  <PageScroll max-height="calc(100vh - var(--app-header-height))">
    <div
      class="posts-container"
      v-infinite-scroll="loadMore"
      :infinite-scroll-delay="200"
      :infinite-scroll-distance="160"
      :infinite-scroll-disabled="infiniteDisabled"
      :infinite-scroll-immediate="true"
    >
      <section class="posts-shell">
        <RegisterPrompt
          v-if="!currentUser.isLogin"
          :key="'register-prompt'"
          v-slide-in
        />

        <SearchEntry />
        <PublishEntry v-if="currentUser.isLogin" />
        <el-tabs v-model="activeName" class="demo-tabs" @tab-change="changeTab">
          <el-tab-pane label="广场" name="all">
            <div
              v-if="activeName == 'all' && posts_count == 0 && !loading.card"
              class="posts-empty"
            >
              <p class="posts-empty-title">这里还没有内容</p>
              <p class="posts-empty-note">
                等第一篇文字出现，阅读会从这里开始。
              </p>
            </div>
            <SkeletonUtil
              :loading="loading.card"
              :row="5"
              :throttle="throttle"
              :useNew="true"
            >
              <transition-group name="slide-in" tag="div" class="posts-list">
                <PostPreview
                  v-for="item in posts"
                  :key="item.id"
                  :post="item"
                  @click="$router.push(`/postDetail/${item.id}`)"
                  v-slide-in
                >
                  <template #image>
                    <PostImage :postImages="item.post_images" @click.stop="" />
                  </template>
                </PostPreview>
              </transition-group>
            </SkeletonUtil>
            <div class="posts-infinite-footer">
              <div v-if="loading.more" class="posts-loading">加载中...</div>
              <div v-else-if="noMore && posts.length" class="posts-end">
                已经到底了～
              </div>
            </div>
          </el-tab-pane>
          <el-tab-pane label="热门" name="hot">
            <div
              v-if="activeName == 'hot' && posts_count == 0 && !loading.card"
              class="posts-empty"
            >
              <p class="posts-empty-title">热门榜暂时为空</p>
              <p class="posts-empty-note">点赞和讨论会让文章慢慢浮上来。</p>
            </div>
            <SkeletonUtil
              :loading="loading.card"
              :row="5"
              :throttle="throttle"
              :useNew="true"
            >
              <transition-group name="slide-in" tag="div" class="posts-list">
                <PostPreview
                  v-for="item in posts"
                  :key="item.id"
                  :post="item"
                  @click="$router.push(`/postDetail/${item.id}`)"
                  v-slide-in
                >
                  <template #image>
                    <PostImage :postImages="item.post_images" @click.stop="" />
                  </template>
                </PostPreview>
              </transition-group>
            </SkeletonUtil>
            <div class="posts-infinite-footer">
              <div v-if="loading.more" class="posts-loading">加载中...</div>
              <div v-else-if="noMore && posts.length" class="posts-end">
                已经到底了～
              </div>
            </div>
          </el-tab-pane>
          <el-tab-pane name="showFollowed" v-if="currentUser.isLogin">
            <template #label>
              <van-badge :dot="showDot" :offset="[1, 10]"> 关注 </van-badge>
            </template>
            <div
              v-if="
                activeName == 'showFollowed' &&
                posts_count == 0 &&
                !loading.card
              "
              class="posts-empty"
            >
              <p class="posts-empty-title">关注流暂时为空</p>
              <p class="posts-empty-note">
                先去看看广场，或关注一些你想继续阅读的人。
              </p>
            </div>
            <SkeletonUtil
              :loading="loading.card"
              :row="5"
              :throttle="throttle"
              :useNew="true"
            >
              <transition-group name="slide-in" tag="div" class="posts-list">
                <PostPreview
                  v-for="item in posts"
                  :key="item.id"
                  :post="item"
                  @click="$router.push(`/postDetail/${item.id}`)"
                  v-slide-in
                >
                  <template #image>
                    <PostImage :postImages="item.post_images" @click.stop="" />
                  </template>
                </PostPreview>
              </transition-group>
            </SkeletonUtil>
            <div class="posts-infinite-footer">
              <div v-if="loading.more" class="posts-loading">加载中...</div>
              <div v-else-if="noMore && posts.length" class="posts-end">
                已经到底了～
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>
      </section>
    </div>
  </PageScroll>
</template>
<style lang="scss" scoped>
@use "./components/PostCard.scss" as *;
@use "./components/PostReadingTokens.scss" as tokens;

.posts-shell {
  width: min(100%, tokens.$reading-shell-width);
  margin: 0 auto;
  padding: 28px 24px 56px;
  box-sizing: border-box;
}

.demo-tabs {
  margin-top: 18px;
  min-height: 47vh;

  :deep(.el-tabs__header) {
    margin-bottom: 18px;
  }

  :deep(.el-tabs__nav) {
    border: none;
    background: transparent;
  }

  :deep(.el-tabs__item) {
    height: 32px;
    line-height: 32px;
    padding: 0 4px;
    margin-right: 22px;
    font-size: 14px;
    color: #7a7a7a;
    border: none;
    border-radius: 0;
    transition: color 0.2s ease;

    &.is-active {
      color: #111;
      font-weight: 500;
    }

    &:hover:not(.is-active) {
      color: #444;
    }
  }

  :deep(.el-tabs__active-bar) {
    height: 1px;
    background: #111;
  }

  :deep(.el-tabs__nav-wrap::after) {
    height: 1px;
    background: #ececec;
  }
}

.posts-infinite-footer {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 32px;
  padding: 4px 0 20px;
  color: #777;
  font-size: 12px;
  letter-spacing: 0.04em;

  .posts-loading {
    display: inline-flex;
    align-items: center;
    gap: 0;

    &::before {
      content: "·";
      margin-right: 6px;
    }
  }

  .posts-end {
    color: #8a8a8a;
  }
}

.posts-empty {
  padding: 32px 0 40px;
  border-bottom: 1px solid #ececec;

  .posts-empty-title {
    margin: 0;
    font-size: 17px;
    line-height: 1.4;
    font-weight: 500;
    color: #111;
  }

  .posts-empty-note {
    margin: 8px 0 0;
    font-size: 13px;
    line-height: 1.75;
    color: #777;
  }
}

@media (max-width: 768px) {
  .posts-shell {
    width: min(100%, 740px);
    padding: 22px 16px 40px;
  }

  .demo-tabs {
    :deep(.el-tabs__item) {
      margin-right: 16px;
    }
  }

  .posts-empty {
    padding: 24px 0 30px;

    .posts-empty-title {
      font-size: 16px;
    }
  }
}
</style>
