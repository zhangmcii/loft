<script>
import PageScroll from "@/utils/components/PageScroll.vue";
import PostImage from "@/views/posts/components/PostImage.vue";
import PostAction from "@/views/posts/components/PostAction.vue";
import CommentCard from "@/views/comment/ComCard.vue";
import PostHeader from "@/views/posts/components/PostHeader.vue";
import PostContent from "@/views/posts/components/PostContent.vue";
import ReadProgress from "@/utils/components/ReadProgress.vue";
import PostSearch from "@/views/posts/components/PostSearch.vue";
import PostToc from "@/views/posts/components/PostToc.vue";
import postApi from "@/api/posts/postApi.js";
import message from "@/utils/message";
import { useCurrentUserStore } from "@/stores/user";

export default {
  components: {
    PageScroll,
    CommentCard,
    PostImage,
    PostAction,
    PostHeader,
    PostContent,
    ReadProgress,
    PostSearch,
    PostToc,
  },
  setup() {
    const currentUser = useCurrentUserStore();
    return {
      currentUser,
    };
  },
  data() {
    return {
      post: {
        id: 1,
        content: "",
        post_type: "text",
        timestamp: "",
        author: "--",
        nick_name: "",
        comment_count: 20,
        disabled: false,
        image: "",
        praise_num: 0,
        has_praised: false,
        post_images: [],
      },
      postId: -1,
      // 默认字体大小
      fontSize: 16,
      // 是否显示搜索框
      showSearch: false,
      toolboxVisible: false,
      toolboxFontSize: 16,
      showFloatingButtons: true,
      lastScrollTop: 0,
      scrollRaf: null,
      scrollEl: null,
      // 文章目录
      toc: [],
      // 当前激活的标题ID
      activeHeadingId: "",
      // 滚动监听器
      scrollObserver: null,
      loading: false,
      // 控制骨架屏相关组件的显示状态
      showSkeletonComponents: false,
      // 骨架屏延时配置（毫秒）
      skeletonDelay: 500,
      skeletonTimer: null,
      commentsExpanded: false,
      hasEnteredReadingMode: false,
    };
  },
  beforeRouteEnter(to, from, next) {
    next((vm) => {
      vm.postId = Number(to.params.id);
      vm.getPostById(vm.postId);

      // 从本地存储加载字体大小设置
      const savedFontSize = localStorage.getItem("article-font-size");
      if (savedFontSize) {
        vm.fontSize = parseInt(savedFontSize);
      }
      vm.toolboxFontSize = vm.fontSize;
    });
  },
  // 通知栏上可能会频繁切换跳转的文章
  created() {
    this.$watch(
      () => this.$route.params.id,
      (newVal) => {
        if (this.$route.name === "postDetail") {
          this.postId = Number(newVal);
          this.commentsExpanded = false;
          this.getPostById(this.postId);
        }
      }
    );
  },
  mounted() {
    this.bindScrollListener();
  },
  computed: {
    plainContent() {
      const raw = this.post?.content || "";
      return raw
        .replace(/```[\s\S]*?```/g, " ")
        .replace(/`[^`]*`/g, " ")
        .replace(/!\[[^\]]*\]\([^)]+\)/g, " ")
        .replace(/\[[^\]]*\]\([^)]+\)/g, " ")
        .replace(/[#>*_\-\[\]\(\)!]/g, " ")
        .replace(/\s+/g, " ")
        .trim();
    },
    plainContentLength() {
      return this.plainContent.length;
    },
    isShortArticle() {
      return (
        this.plainContentLength > 0 &&
        this.plainContentLength <= 120 &&
        this.toc.length === 0 &&
        (this.post?.post_images?.length || 0) === 0
      );
    },
    isLongArticle() {
      return (
        this.plainContentLength >= 420 ||
        this.toc.length >= 3 ||
        (this.post?.post_images?.length || 0) >= 2
      );
    },
    shouldShowReadingAids() {
      return (
        this.isLongArticle &&
        this.showSkeletonComponents &&
        this.hasEnteredReadingMode
      );
    },
    commentToggleLabel() {
      return this.commentsExpanded ? "收起评论" : "展开评论";
    },
  },

  watch: {
    loading: {
      handler(newVal) {
        if (newVal) {
          if (this.skeletonTimer) {
            clearTimeout(this.skeletonTimer);
            this.skeletonTimer = null;
          }
          this.showSkeletonComponents = false;
          return;
        }
        if (!newVal) {
          // loading 变为 false 时，延时显示组件（与 skeleton 的 throttle trailing 对应）
          this.skeletonTimer = setTimeout(() => {
            this.showSkeletonComponents = true;
          }, this.skeletonDelay);
        }
      },
    },
  },

  beforeUnmount() {
    if (this.scrollObserver) {
      this.scrollObserver.disconnect();
    }
    this.teardownScrollListener();
    if (this.skeletonTimer) {
      clearTimeout(this.skeletonTimer);
      this.skeletonTimer = null;
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
    handleTocReady(toc) {
      this.toc = Array.isArray(toc) ? toc : [];
      this.setupScrollObserver();
    },
    toggleComments() {
      this.commentsExpanded = !this.commentsExpanded;
      if (this.commentsExpanded) {
        this.$nextTick(() => {
          this.$refs.commentsAnchor?.scrollIntoView({
            behavior: "smooth",
            block: "start",
          });
        });
      }
    },
    handleCommentCountChange(count) {
      this.post = {
        ...this.post,
        comment_count: Number(count) || 0,
      };
    },

    setupScrollObserver() {
      if (this.scrollObserver) {
        this.scrollObserver.disconnect();
      }

      const contentEl =
        this.$refs.postContent?.$el?.querySelector(".v-show-content") ||
        this.$refs.postContent?.$el ||
        null;
      if (!contentEl) return;

      const headings = contentEl.querySelectorAll("h1, h2, h3, h4, h5, h6");
      if (headings.length === 0) return;

      const options = {
        root: null,
        rootMargin: "0px 0px -50% 0px",
        threshold: 0.5,
      };

      this.scrollObserver = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            this.activeHeadingId = entry.target.id;
          }
        });
      }, options);

      headings.forEach((heading) => {
        this.scrollObserver.observe(heading);
      });
    },

    // 跳转到标题位置
    scrollToHeading(id) {
      const el = document.getElementById(id);
      if (el) {
        // 添加偏移量避免被顶部导航栏遮挡
        const offset = 80;
        const elementPosition = el.offsetTop;
        const pageScroll = this.$refs.pageScrollRef;
        if (pageScroll) {
          pageScroll.setScrollTop(elementPosition - offset);
        }

        // 手动设置当前激活的标题
        this.activeHeadingId = id;
      }
    },

    getPostById(postId) {
      this.loading = true;
      postApi
        .getPost(postId)
        .then((res) => {
          if (res.code === 200) {
            const nextPost = res.data || {};
            this.post = {
              ...nextPost,
              comment_count:
                nextPost.comment_count ?? nextPost.commentCount ?? 0,
            };
            this.commentsExpanded = false;
          }
        })
        .catch((error) => {
          console.error("获取文章详情失败", error);
          message.error("获取文章详情失败，请稍后重试");
        })
        .finally(() => {
          this.loading = false;
        });
    },
    updateFontSize(size) {
      // 不做任何操作，只在预览中显示
    },
    saveFontSizeSettings(size) {
      this.fontSize = size;
      localStorage.setItem("article-font-size", size.toString());
    },
    search() {
      this.toolboxVisible = !this.toolboxVisible;
      this.showSearch = !this.showSearch;
    },
    toggleToolbox() {
      this.toolboxVisible = !this.toolboxVisible;
      if (this.toolboxVisible) {
        this.toolboxFontSize = this.fontSize;
      }
    },
    saveToolboxFontSize() {
      this.saveFontSizeSettings(this.toolboxFontSize);
      this.toolboxVisible = false;
    },
    resetToolboxFontSize() {
      this.toolboxFontSize = 16;
    },
    bindScrollListener() {
      this.$nextTick(() => {
        const wrap =
          this.$refs.pageScrollRef?.$el?.querySelector(".el-scrollbar__wrap") ||
          null;
        if (!wrap) return;
        this.scrollEl = wrap;
        this.lastScrollTop = wrap.scrollTop || 0;
        wrap.addEventListener("scroll", this.handleScroll, { passive: true });
      });
    },
    teardownScrollListener() {
      if (this.scrollRaf) {
        cancelAnimationFrame(this.scrollRaf);
        this.scrollRaf = null;
      }
      if (this.scrollEl) {
        this.scrollEl.removeEventListener("scroll", this.handleScroll);
        this.scrollEl = null;
      }
    },
    handleScroll(event) {
      if (this.toolboxVisible) {
        this.showFloatingButtons = true;
        return;
      }
      const target = event.target;
      const currentTop = target.scrollTop || 0;
      if (this.scrollRaf) {
        cancelAnimationFrame(this.scrollRaf);
      }
      this.scrollRaf = requestAnimationFrame(() => {
        this.scrollRaf = null;
        const delta = currentTop - this.lastScrollTop;
        const threshold = 10;
        if (Math.abs(delta) < threshold) {
          this.hasEnteredReadingMode = currentTop > 220;
          this.lastScrollTop = currentTop;
          return;
        }
        this.hasEnteredReadingMode = currentTop > 220;
        if (currentTop < 10) {
          this.showFloatingButtons = true;
        } else {
          this.showFloatingButtons = delta < 0;
        }
        this.lastScrollTop = currentTop;
      });
    },
  },
};
</script>

<template>
  <PageScroll ref="pageScrollRef" max-height="calc(100vh - 45px - 47px)">
    <div class="post-detail-shell">
      <button
        type="button"
        class="detail-back"
        aria-label="返回"
        title="返回"
        @click="goBack"
      >
        ←
      </button>
      <!-- 回到顶部 -->
      <el-backtop
        target=".page-scroll .el-scrollbar__wrap"
        :right="20"
        :bottom="30"
      />
      <!-- 阅读进度条 -->
      <ReadProgress
        v-if="shouldShowReadingAids"
        target=".page-scroll .el-scrollbar__wrap"
      />
      <div class="post-detail-container">
        <!-- 骨架屏：当文章内容为空时显示 -->
        <el-skeleton
          :loading="loading"
          animated
          :throttle="{
            leading: skeletonDelay,
            trailing: skeletonDelay,
            initVal: true,
          }"
          class="skeleton-wrapper"
        >
          <template #template>
            <div class="skeleton-header">
              <el-skeleton-item
                variant="circle"
                style="width: 30px; height: 30px"
              />
              <el-skeleton-item variant="text" style="width: 120px" />
            </div>
            <!-- 文章标题骨架 -->
            <div class="skeleton-title-section">
              <el-skeleton-item
                variant="text"
                style="width: 75%; height: 22px; margin-bottom: 20px"
              />
            </div>
            <!-- 文章内容骨架 -->
            <div class="skeleton-content-section">
              <el-skeleton-item
                variant="text"
                style="width: 100%; margin-bottom: 16px"
              />
              <el-skeleton-item
                variant="text"
                style="width: 95%; margin-bottom: 16px"
              />
              <el-skeleton-item
                variant="text"
                style="width: 88%; margin-bottom: 16px"
              />
              <div class="skeleton-spacer"></div>
              <el-skeleton-item
                variant="text"
                style="width: 100%; margin-bottom: 16px"
              />
              <el-skeleton-item
                variant="text"
                style="width: 92%; margin-bottom: 16px"
              />
              <el-skeleton-item
                variant="text"
                style="width: 78%; margin-bottom: 16px"
              />
            </div>
          </template>

          <!-- 实际内容 -->
          <template #default>
            <div
              class="post-detail-layout"
              :class="{
                'post-detail-layout-short': isShortArticle,
                'post-detail-layout-long': !isShortArticle,
              }"
            >
              <div class="post-main-column">
                <div class="post-main-content">
                  <div class="post-meta-intro">
                    <PostHeader
                      :post="post"
                      mode="byline"
                      class="post-header"
                    />
                  </div>

                  <PostContent
                    :postContent="post.content"
                    class="post-content"
                    :fontSize="fontSize"
                    ref="postContent"
                    @toc-ready="handleTocReady"
                  />
                  <PostImage
                    :postImages="post.post_images"
                    mode="article"
                    class="post-images"
                  />
                </div>

                <div class="post-tail">
                  <p class="post-tail-note">
                    {{ isShortArticle ? "文后信息" : "读完这一篇，再继续往下" }}
                  </p>
                </div>

                <div class="post-actions">
                  <PostAction
                    :post="post"
                    :showEdit="true"
                    :showDelete="true"
                    :showComment="false"
                  />
                </div>

                <div class="post-comment-entry">
                  <button
                    type="button"
                    class="comment-toggle"
                    @click="toggleComments"
                  >
                    <span>{{ commentToggleLabel }}</span>
                    <span class="comment-toggle-count"
                      >{{ post.comment_count || 0 }} 条</span
                    >
                  </button>
                </div>
              </div>

              <aside
                v-if="shouldShowReadingAids && toc.length > 0"
                class="post-aside"
              >
                <PostToc
                  :toc="toc"
                  :activeId="activeHeadingId"
                  mode="inline"
                  @navigate="scrollToHeading"
                />
              </aside>
            </div>
          </template>
        </el-skeleton>
        <div
          v-show="commentsExpanded"
          ref="commentsAnchor"
          class="post-comments"
          :class="{ 'post-comments-short': isShortArticle }"
        >
          <CommentCard
            :post-id="postId"
            :post-author="post.author"
            @count-change="handleCommentCountChange"
          />
        </div>
        <PostToc
          v-if="shouldShowReadingAids"
          :toc="toc"
          :activeId="activeHeadingId"
          class="post-toc-drawer"
          :class="{ 'float-hidden': !showFloatingButtons }"
          mode="drawer"
          @navigate="scrollToHeading"
        />

        <!-- 工具箱按钮 -->
        <div
          v-if="shouldShowReadingAids"
          class="toolbox-button"
          :class="{ 'float-hidden': !showFloatingButtons }"
          @click="toggleToolbox"
        >
          <el-button type="primary" circle size="large">
            <el-icon><i-ep-Tools /></el-icon>
          </el-button>
        </div>

        <el-drawer
          v-model="toolboxVisible"
          title="工具箱"
          direction="rtl"
          size="300px"
          :destroy-on-close="false"
          :modal="true"
        >
          <div class="toolbox-content">
            <div class="toolbox-section">
              <div class="toolbox-title">字体调整</div>
              <div class="toolbox-preview">
                <div class="preview-title">预览效果</div>
                <div
                  class="preview-text"
                  :style="{ fontSize: toolboxFontSize + 'px' }"
                >
                  这是预览文本，调整滑块可以改变字体大小，使阅读更加舒适。
                </div>
              </div>
              <div class="toolbox-control">
                <div class="control-label">
                  <span>字体大小: {{ toolboxFontSize }}px</span>
                  <el-button link @click="resetToolboxFontSize">重置</el-button>
                </div>
                <el-slider
                  v-model="toolboxFontSize"
                  :min="12"
                  :max="24"
                  :step="1"
                  show-stops
                />
                <div class="control-buttons">
                  <el-button @click="toolboxVisible = false">取消</el-button>
                  <el-button type="primary" @click="saveToolboxFontSize"
                    >保存设置</el-button
                  >
                </div>
              </div>
            </div>

            <div class="toolbox-section">
              <div class="toolbox-title">文本搜索</div>
              <el-button type="primary" @click="search">搜索</el-button>
            </div>
          </div>
        </el-drawer>

        <!-- 搜索组件 -->
        <PostSearch
          v-if="showSearch"
          :contentRef="$refs.postContent"
          @close="showSearch = false"
        />
      </div>
    </div>
  </PageScroll>
</template>

<style scoped lang="scss">
@use "./components/PostDetail.scss" as *;
@use "./components/PostReadingTokens.scss" as tokens;

.post-detail-shell {
  width: min(100%, 1040px);
  margin: 0 auto;
}

.detail-back {
  margin: 14px 0 0 28px;
  padding: 0;
  border: none;
  background: transparent;
  color: tokens.$reading-text-quaternary;
  font-size: 15px;
  line-height: 1;
  cursor: pointer;
  transition: color 0.2s ease, opacity 0.2s ease;

  &:hover {
    color: tokens.$reading-text-primary;
    opacity: 1;
  }

  @include mobile {
    margin: 12px 0 0 16px;
    font-size: 15px;
  }
}

// 文章容器
.post-detail-container {
  width: min(100%, 1040px);
  margin: 0 auto;
  padding: 26px 28px 56px;
  box-sizing: border-box;
  background-color: #fff;
  @extend .fade-in;

  @include mobile {
    padding: 18px 16px 40px;
  }
}

.post-detail-layout {
  display: flex;
  gap: 56px;
  align-items: flex-start;
  width: 100%;
  min-width: 0;
}

.post-detail-layout-short {
  .post-main-column {
    max-width: 620px;
  }
}

.post-main-column {
  flex: 1 1 auto;
  min-width: 0;
  width: 100%;
  max-width: 680px;
}

.post-aside {
  flex: 0 0 208px;
  position: sticky;
  top: 24px;
  align-self: flex-start;
  max-height: calc(100vh - 72px);
  overflow: auto;
}

.post-toc-drawer {
  display: none;
}

.toolbox-button {
  position: fixed;
  right: 18px;
  bottom: 76px;
  z-index: 999;
  transition: all 0.2s ease;

  .el-button {
    box-shadow: none;
  }
}

.float-hidden {
  opacity: 0;
  transform: translateY(12px);
  pointer-events: none;
}

.post-main-content {
  margin-bottom: 36px;
  @extend .slide-up;
}

.post-meta-intro {
  margin-bottom: 22px;
  padding-bottom: 0;
  border-bottom: none;
}

.post-header {
  margin-bottom: 0;
}

.post-content {
  margin-bottom: 0;
}

.post-images {
  margin-top: 24px;
  margin-bottom: 0;
}

.post-tail {
  margin-top: 56px;
  padding-top: 14px;
  border-top: 1px solid tokens.$reading-border-soft;
}

.post-tail-note {
  margin: 0;
  font-size: tokens.$reading-font-size-meta;
  letter-spacing: 0.05em;
  color: tokens.$reading-text-quaternary;
}

.post-actions {
  margin-top: 10px;
  padding: 14px 0 0;
  margin-bottom: 0;
  border-top: 1px solid tokens.$reading-border-soft;
  border-bottom: none;
}

.post-comment-entry {
  padding-top: 20px;
}

.comment-toggle {
  display: inline-flex;
  align-items: baseline;
  gap: 8px;
  padding: 0;
  border: none;
  background: transparent;
  color: tokens.$reading-text-secondary;
  font-size: 13px;
  font-weight: 500;
  line-height: 1.6;
  cursor: pointer;
  transition: color 0.2s ease;

  &:hover {
    color: tokens.$reading-text-primary;
  }
}

.comment-toggle-count {
  color: tokens.$reading-text-tertiary;
  font-size: tokens.$reading-font-size-meta;
  font-weight: 400;
}

.post-comments {
  margin-top: 56px;
  padding-top: 24px;
  border-top: 1px solid tokens.$reading-border;
}

.post-comments-short {
  margin-top: 72px;
}

@include mobile {
  .post-detail-layout {
    display: block;
  }

  .post-main-column {
    max-width: 100%;
  }

  .post-meta-intro {
    margin-bottom: 16px;
    padding-bottom: 0;
  }

  .post-content {
    margin-bottom: 0;
  }

  .post-aside {
    display: none;
  }

  .post-toc-drawer {
    display: block;
  }

  .post-tail {
    margin-top: 40px;
    padding-top: 14px;
  }

  .post-comment-entry {
    padding-top: 18px;
  }

  .post-comments,
  .post-comments-short {
    margin-top: 44px;
    padding-top: 20px;
  }
}

.skeleton-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
}

.skeleton-title-section {
  margin-bottom: 32px;
}

.skeleton-content-section {
  margin-bottom: 40px;
}

.skeleton-spacer {
  height: 24px;
}

.toolbox-content {
  display: flex;
  flex-direction: column;
  gap: 32px;
  padding: 2px 16px 0;
}

.toolbox-section {
  padding-bottom: 8px;
}

.toolbox-title {
  margin-bottom: 10px;
  font-size: 14px;
  font-weight: 500;
  color: #111;
  font-family: tokens.$reading-font-family;
}

.toolbox-preview {
  max-height: 180px;
  padding: 16px;
  margin-bottom: 16px;
  overflow: auto;
  background-color: #fafafa;
  border: 1px solid tokens.$reading-border;
  border-radius: 0;

  .preview-title {
    margin-bottom: 10px;
    font-size: 13px;
    font-weight: 500;
    color: tokens.$reading-text-secondary;
  }

  .preview-text {
    line-height: 1.9;
    color: tokens.$reading-text-primary;
    font-family: tokens.$reading-font-family;
  }
}

.toolbox-control {
  .control-label {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 12px;

    span {
      font-size: 14px;
      color: tokens.$reading-text-secondary;
    }
  }

  .control-buttons {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
    margin-top: 20px;
  }
}

:deep(.el-backtop) {
  background: #fff;
  border: 1px solid tokens.$reading-border;
  box-shadow: none;
  color: tokens.$reading-text-primary;
}

:deep(.skeleton-wrapper .el-skeleton__item) {
  --el-skeleton-color: #f4f4f4;
  --el-skeleton-to-color: #fafafa;
}

:deep(.skeleton-wrapper .el-skeleton__circle) {
  border: 1px solid tokens.$reading-border;
}

:deep(.toolbox-button .el-button) {
  width: 38px;
  height: 38px;
  color: tokens.$reading-text-primary;
  background: #fff;
  border: 1px solid tokens.$reading-border;
}

:deep(.toolbox-button .el-button:hover) {
  border-color: tokens.$reading-text-primary;
  background: tokens.$reading-fill-softer;
}

:deep(.el-drawer__header) {
  margin-bottom: 0;
  padding: 18px 20px 12px;
  border-bottom: 1px solid tokens.$reading-border;
}

:deep(.el-drawer__title) {
  color: tokens.$reading-text-primary;
  font-weight: 500;
}

:deep(.toolbox-content .el-button) {
  border-radius: 0;
}

:deep(.toolbox-content .el-button--primary) {
  color: #fff;
  background: tokens.$reading-text-primary;
  border-color: tokens.$reading-text-primary;
}

:deep(.toolbox-content .el-button:not(.el-button--primary)) {
  color: tokens.$reading-text-secondary;
  background: #fff;
  border-color: tokens.$reading-border;
}

:deep(.toolbox-content .el-slider__runway) {
  background: tokens.$reading-border;
}

:deep(.toolbox-content .el-slider__bar) {
  background: tokens.$reading-text-primary;
}

:deep(.toolbox-content .el-slider__button) {
  border-color: tokens.$reading-text-primary;
}

:deep(.post-comments .comment-section) {
  padding-top: 0;
}

.Scrollbar {
  height: calc(100vh - var(--el-main-padding) * 2 - 50px);
}
</style>
