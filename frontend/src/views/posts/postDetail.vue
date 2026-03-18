<script>
import PageHeadBack from "@/utils/components/PageHeadBack.vue";
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
    PageHeadBack,
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
      fontSize: 14,
      // 是否显示搜索框
      showSearch: false,
      toolboxVisible: false,
      toolboxFontSize: 14,
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
          this.getPostById(this.postId);
        }
      }
    );
  },
  mounted() {
    this.bindScrollListener();
  },
  computed: {},

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
    handleTocReady(toc) {
      this.toc = Array.isArray(toc) ? toc : [];
      this.setupScrollObserver();
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
          this.lastScrollTop = currentTop;
          return;
        }
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
  <PageHeadBack>
    <PageScroll ref="pageScrollRef" max-height="calc(100vh - 45px - 47px)">
      <!-- 回到顶部 -->
      <el-backtop
        target=".page-scroll .el-scrollbar__wrap"
        :right="20"
        :bottom="30"
      />
      <!-- 阅读进度条 -->
      <ReadProgress target=".page-scroll .el-scrollbar__wrap" />
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
                style="width: 40px; height: 40px"
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
            <div class="post-detail-layout">
              <div class="post-main-column">
                <div class="post-main-content">
                  <PostHeader :post="post" class="post-header" />

                  <PostContent
                    :postContent="post.content"
                    class="post-content"
                    :fontSize="fontSize"
                    ref="postContent"
                    @toc-ready="handleTocReady"
                  />
                  <PostImage
                    :postImages="post.post_images"
                    class="post-images"
                  />
                </div>

                <div class="post-actions">
                  <PostAction
                    :post="post"
                    :showShare="true"
                    :showEdit="true"
                    :showDelete="true"
                  />
                </div>
              </div>

              <aside
                v-if="showSkeletonComponents && toc.length > 0"
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
        <div class="post-comments">
          <CommentCard :post-id="postId" :post-author="post.author" />
        </div>
        <PostToc
          v-if="showSkeletonComponents"
          :toc="toc"
          :activeId="activeHeadingId"
          class="post-toc-drawer"
          :class="{ 'float-hidden': !showFloatingButtons }"
          mode="drawer"
          @navigate="scrollToHeading"
        />

        <!-- 工具箱按钮 -->
        <div
          v-if="showSkeletonComponents"
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
    </PageScroll>
  </PageHeadBack>
</template>

<style scoped lang="scss">
@use "./components/PostDetail.scss" as *;

// 文章容器
.post-detail-container {
  margin: 0 auto;
  padding: $spacing-md;
  background-color: #fff;
  border-radius: $border-radius-md;
  box-shadow: 0 1px 3px $shadow-color;
  @extend .fade-in;

  @include mobile {
    padding: $spacing-sm;
    border-radius: 0;
    box-shadow: none;
  }
}

.post-detail-layout {
  display: flex;
  gap: 32px;
  align-items: flex-start;
}

.post-main-column {
  flex: 1 1 auto;
  min-width: 0;
}

.post-aside {
  flex: 0 0 300px;
  position: sticky;
  top: 20px;
  align-self: flex-start;
  max-height: calc(100vh - 100px);
  overflow: auto;
}

.post-toc-drawer {
  display: none;
}

.toolbox-button {
  position: fixed;
  right: 20px;
  bottom: 80px;
  z-index: 999;
  transition: all 0.3s ease;

  .el-button {
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
    transition: all 0.3s ease;
  }
}

.float-hidden {
  opacity: 0;
  transform: translateY(12px);
  pointer-events: none;
}

.post-main-content {
  margin-bottom: $spacing-lg;
  @extend .slide-up;
}

.post-header {
  margin-bottom: $spacing-md;
}

.post-content {
  margin-bottom: $spacing-md;
}

.post-images {
  margin-bottom: $spacing-lg;
}

.post-actions {
  padding: $spacing-sm 0;
  margin-bottom: $spacing-md;
  border-top: 1px solid $border-color;
  border-bottom: 1px solid $border-color;
}

.post-comments {
  margin-top: $spacing-md;
}

@include mobile {
  .post-detail-layout {
    display: block;
  }

  .post-aside {
    display: none;
  }

  .post-toc-drawer {
    display: block;
  }
}

// 骨架屏样式
.skeleton-wrapper {
  // min-height: calc(100vh - 200px);
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
  gap: 100px;
  padding: 0 16px;
}

.toolbox-section {
  padding-bottom: 8px;
}

.toolbox-title {
  margin-bottom: 12px;
  font-weight: 600;
  color: #303133;
}

.toolbox-preview {
  max-height: 180px;
  padding: 16px;
  margin-bottom: 16px;
  overflow: auto;
  background-color: #f5f7fa;
  border-radius: 8px;

  .preview-title {
    margin-bottom: 10px;
    font-size: 14px;
    font-weight: 500;
    color: #606266;
  }

  .preview-text {
    line-height: 1.8;
    color: #303133;
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
      color: #606266;
    }
  }

  .control-buttons {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
    margin-top: 20px;
  }
}

.toolbox-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.toolbox-hint {
  color: #909399;
}

// 其他样式
.el-button {
  margin-top: $spacing-sm;
}

.Scrollbar {
  height: calc(100vh - var(--el-main-padding) * 2 - 50px);
}
</style>
