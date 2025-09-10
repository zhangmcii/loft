<script>
import PageHeadBack from "@/utils/components/PageHeadBack.vue";
import PostImage from "@/views/posts/components/PostImage.vue";
import PostAction from "@/views/posts/components/PostAction.vue";
import CommentCard from "@/views/comment/ComCard.vue";
import PostHeader from "@/views/posts/components/PostHeader.vue";
import PostContent from "@/views/posts/components/PostContent.vue";
import ReadProgress from "@/utils/components/ReadProgress.vue";
import FontSizeAdjuster from "@/views/posts/components/FontSizeAdjuster.vue";
import PostSearch from "@/views/posts/components/PostSearch.vue";
import PostToc from "@/views/posts/components/PostToc.vue";
import postApi from "@/api/posts/postApi.js";
import message from "@/utils/message";

export default {
  components: {
    PageHeadBack,
    CommentCard,
    PostImage,
    PostAction,
    PostHeader,
    PostContent,
    ReadProgress,
    FontSizeAdjuster,
    PostSearch,
    PostToc,
  },
  data() {
    return {
      post: {
        id: 1,
        body: "",
        body_html: null,
        timestamp: "",
        author: "--",
        nick_name: "",
        commentCount: 20,
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
      // 文章目录
      toc: [],
      // 当前激活的标题ID
      activeHeadingId: "",
      // 滚动监听器
      scrollObserver: null,
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
  computed: {},

  mounted() {
    // 移除这里的调用，只在post.body变化时生成目录
  },

  watch: {
    "post.body": {
      handler(newVal) {
        if (newVal) {
          this.$nextTick(() => {
            this.generateToc();
          });
        }
      },
      deep: true,
    },
  },

  beforeUnmount() {
    if (this.scrollObserver) {
      this.scrollObserver.disconnect();
    }
  },

  methods: {
    // 生成目录
    generateToc() {
      const contentEl = this.$refs.postContent?.$el;
      if (!contentEl) {
        this.toc = [];
        return;
      }

      const headings = contentEl.querySelectorAll("h1, h2, h3, h4, h5, h6");
      const toc = [];
      // 用于去重
      const seenTexts = new Set();

      headings.forEach((heading) => {
        const text = heading.textContent.trim();

        // 跳过空标题和重复标题
        if (!text || seenTexts.has(text)) {
          return;
        }

        seenTexts.add(text);
        const id = text.toLowerCase().replace(/\s+/g, "-");
        heading.id = id;

        toc.push({
          level: parseInt(heading.tagName.substring(1)),
          text: text,
          id: id,
        });
      });

      this.toc = toc;

      // 初始化滚动监听
      this.setupScrollObserver();
    },

    setupScrollObserver() {
      if (this.scrollObserver) {
        this.scrollObserver.disconnect();
      }

      const contentEl = this.$refs.postContent?.$el;
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
        const elementPosition =
          el.getBoundingClientRect().top + window.pageYOffset;
        window.scrollTo({
          top: elementPosition - offset,
          behavior: "smooth",
        });

        // 手动设置当前激活的标题
        this.activeHeadingId = id;
      }
    },

    getPostById(postId) {
      postApi
        .getPost(postId)
        .then((res) => {
          // 适配新的统一接口返回格式
          if (res.code === 200) {
            this.post = res.data;
          }
        })
        .catch((error) => {
          console.error("获取文章详情失败", error);
          // this.$message.error('获取文章详情失败，请稍后重试')
          message.error("获取文章详情失败，请稍后重试");
        });
    },
    updateFontSize(size) {
      // 这里不再实时更新字体大小，只在预览中显示
      // 不做任何操作，因为我们只想在保存时更新字体大小
    },
    saveFontSizeSettings(size) {
      // 只有在保存时才更新实际的字体大小
      this.fontSize = size;
      localStorage.setItem("article-font-size", size.toString());
    },
  },
};
</script>

<template>
  <PageHeadBack>
    <!-- 回到顶部 -->
    <el-backtop target=".el-scrollbar__wrap" :right="20" :bottom="30" />
    <!-- 阅读进度条 -->
    <ReadProgress target=".el-scrollbar__wrap" />
    <div class="post-detail-container">
      <div class="post-main-content">
        <PostHeader :post="post" class="post-header" />

        <PostContent
          :postContent="post.body"
          class="post-content"
          :fontSize="fontSize"
          ref="postContent"
        />
        <PostImage :postImages="post.post_images" class="post-images" />
      </div>

      <div class="post-actions">
        <PostAction :post="post" :showShare="true" :showEdit="true" />
      </div>

      <div class="post-comments">
        <CommentCard :post-id="postId" />
      </div>
      <PostToc
        :toc="toc"
        :activeId="activeHeadingId"
        @navigate="scrollToHeading"
      />
      <!-- 字体大小调整悬浮按钮 -->
      <FontSizeAdjuster
        :defaultFontSize="fontSize"
        @update:fontSize="updateFontSize"
        @save="saveFontSizeSettings"
      />

      <!-- 搜索按钮 -->
      <div class="search-button" @click="showSearch = !showSearch">
        <el-button
          type="primary"
          circle
          size="large"
          :class="{ active: showSearch }"
        >
          <el-icon><i-ep-Search /></el-icon>
        </el-button>
      </div>

      <!-- 搜索组件 -->
      <PostSearch
        v-if="showSearch"
        :contentRef="$refs.postContent"
        @close="showSearch = false"
      />
    </div>
  </PageHeadBack>
</template>

<style scoped lang="scss">
@use "./components/PostDetail.scss" as *;

.toc-container {
  position: sticky;
  top: 20px;
  max-height: calc(100vh - 100px);
  overflow-y: auto;
  padding: 16px;
  margin-bottom: 20px;
  background: #f8f9fa;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);

  .toc-title {
    font-weight: bold;
    margin-bottom: 12px;
    padding-bottom: 8px;
    border-bottom: 1px solid #eaeaea;
  }

  .toc-item {
    margin-bottom: 8px;
    cursor: pointer;
    transition: all 0.2s;
    color: #555;

    &:hover {
      color: #409eff;
      transform: translateX(4px);
    }
  }
}

.search-button {
  position: fixed;
  bottom: 80px;
  right: 20px;
  z-index: 999;
  transition: all 0.3s ease;

  .el-button {
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
    transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);

    &.active {
      background-color: #409eff;
      transform: rotate(90deg);
    }

    &:hover {
      transform: scale(1.1);

      &.active {
        transform: rotate(90deg) scale(1.1);
      }
    }
  }
}

.post-detail-container {
  // max-width: 800px;
  margin: 0 auto;
  padding: $spacing-md;
  background-color: #fff;
  border-radius: $border-radius-md;
  box-shadow: 0 1px 3px $shadow-color;
  @extend .fade-in;
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
  border-top: 1px solid $border-color;
  border-bottom: 1px solid $border-color;
  margin-bottom: $spacing-md;
}

.post-comments {
  margin-top: $spacing-md;
}

.el-button {
  margin-top: $spacing-sm;
}

.Scrollbar {
  height: calc(100vh - var(--el-main-padding) * 2 - 50px);
}

@include mobile {
  .post-detail-container {
    padding: $spacing-sm;
    border-radius: 0;
    box-shadow: none;
  }
}
</style>
