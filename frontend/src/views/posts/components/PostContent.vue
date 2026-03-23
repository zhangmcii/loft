<script>
import { mavonEditor } from "mavon-editor";
import "mavon-editor/dist/css/index.css";

const TRUNCATION_MAX_HEIGHT = 300;
const TRUNCATION_MASK_HEIGHT = 40;
const COPY_FEEDBACK_RESET_DELAY = 3000;

const SVG_ICONS = {
  copy: `
    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="copy-icon">
      <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
      <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
    </svg>
  `,
  success: `
    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="copy-icon">
      <polyline points="20 6 9 17 4 12"></polyline>
    </svg>
  `,
  error: `
    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="copy-icon">
      <line x1="18" y1="6" x2="6" y2="18"></line>
      <line x1="6" y1="6" x2="18" y2="18"></line>
    </svg>
  `,
};

export default {
  emits: ["toc-ready"],
  props: {
    postContent: {
      type: String,
      default: "",
    },
    preview: {
      type: Boolean,
      default: false,
    },
    previewType: {
      type: String,
      default: "",
    },
    compact: {
      type: Boolean,
      default: false,
    },
    fontSize: {
      type: Number,
      default: 16,
    },
  },
  components: {
    mavonEditor,
  },
  data() {
    return {
      pContent: "",
      isTruncated: false,
      // 图片预览相关状态
      imageViewerVisible: false,
      imageViewerUrls: [],
      imageViewerIndex: 0,
      // 观察内容渲染与代码块处理
      contentObserver: null,
      lastContentEl: null,
      codeBlockProcessRaf: null,
      isProcessingCodeBlocks: false,
      needsFullRebuild: false,
      // 截断高度观察器
      truncationObserver: null,
      truncationObservedEl: null,
      truncationRaf: null,
      tocRaf: null,
    };
  },
  watch: {
    postContent: {
      handler(newVal) {
        this.pContent = newVal;
        this.refreshContent(true);
      },
      immediate: true,
    },
    fontSize: {
      handler(newVal) {
        this.updateFontSize(newVal);
      },
    },
  },
  beforeUnmount() {
    if (this.contentObserver) {
      this.contentObserver.disconnect();
      this.contentObserver = null;
    }
    if (this.codeBlockProcessRaf) {
      cancelAnimationFrame(this.codeBlockProcessRaf);
      this.codeBlockProcessRaf = null;
    }
    if (this.tocRaf) {
      cancelAnimationFrame(this.tocRaf);
      this.tocRaf = null;
    }
    const contentDom = this.getContentDom();
    if (contentDom) {
      this.unbindTruncationImageListeners(contentDom);
    }
    this.teardownTruncationObserver();
  },

  methods: {
    getContentDom() {
      return this.$refs.md?.$el?.querySelector(".v-show-content") || null;
    },

    refreshContent(forceRebuild = false) {
      this.needsFullRebuild = this.needsFullRebuild || forceRebuild;
      this.$nextTick(() => {
        this.updateFontSize(this.fontSize);
        this.updateTruncation();
        this.setupContentObserver();
        this.scheduleProcessCodeBlocks(forceRebuild);
      });
    },

    setupContentObserver() {
      const contentDom = this.getContentDom();
      if (!contentDom) return;

      if (this.lastContentEl === contentDom && this.contentObserver) {
        return;
      }

      if (this.contentObserver) {
        this.contentObserver.disconnect();
      }

      this.lastContentEl = contentDom;
      this.contentObserver = new MutationObserver((mutations) => {
        if (this.isProcessingCodeBlocks) return;

        const hasRelevantChange = mutations.some((m) => m.type === "childList");
        if (!hasRelevantChange) return;

        if (this.preview) {
          this.scheduleTruncationApply();
        }
        this.scheduleProcessCodeBlocks(false);
      });

      this.contentObserver.observe(contentDom, {
        childList: true,
        subtree: true,
      });
    },

    scheduleProcessCodeBlocks(fullRebuild = false) {
      if (fullRebuild) {
        this.needsFullRebuild = true;
      }

      if (this.codeBlockProcessRaf) {
        cancelAnimationFrame(this.codeBlockProcessRaf);
      }

      this.codeBlockProcessRaf = requestAnimationFrame(() => {
        this.codeBlockProcessRaf = null;
        const doFullRebuild = this.needsFullRebuild;
        this.needsFullRebuild = false;
        this.processCodeBlocks(doFullRebuild);
        if (this.preview) {
          this.updateTruncation();
        }
        this.scheduleTocEmit();
      });
    },
    updateFontSize(size) {
      const contentDom = this.getContentDom();
      if (contentDom) {
        contentDom.style.fontSize = `${size}px`;

        // 根据字体大小调整其他元素
        const h1Elements = contentDom.querySelectorAll("h1");
        const h2Elements = contentDom.querySelectorAll("h2");

        h1Elements.forEach((el) => {
          el.style.fontSize = `${(size * 1.4) / 16}em`;
        });

        h2Elements.forEach((el) => {
          el.style.fontSize = `${(size * 1.2) / 16}em`;
        });
      }
    },

    updateTruncation() {
      const contentDom = this.getContentDom();
      if (!this.preview) {
        if (contentDom) {
          this.clearTruncationStyles(contentDom);
          this.unbindTruncationImageListeners(contentDom);
        }
        this.teardownTruncationObserver();
        return;
      }
      if (!contentDom) return;

      if (this.canUseResizeObserver()) {
        this.setupTruncationObserver(contentDom);
      } else {
        this.bindTruncationImageListeners(contentDom);
      }

      this.applyTruncationStyles(contentDom);
    },

    canUseResizeObserver() {
      return typeof ResizeObserver !== "undefined";
    },

    setupTruncationObserver(contentDom) {
      if (this.truncationObservedEl === contentDom && this.truncationObserver) {
        return;
      }

      this.teardownTruncationObserver();
      this.truncationObservedEl = contentDom;

      this.truncationObserver = new ResizeObserver(() => {
        this.scheduleTruncationApply();
      });

      this.truncationObserver.observe(contentDom);
    },

    teardownTruncationObserver() {
      if (this.truncationObserver) {
        this.truncationObserver.disconnect();
        this.truncationObserver = null;
      }
      this.truncationObservedEl = null;
      if (this.truncationRaf) {
        cancelAnimationFrame(this.truncationRaf);
        this.truncationRaf = null;
      }
    },

    scheduleTruncationApply() {
      if (this.truncationRaf) {
        cancelAnimationFrame(this.truncationRaf);
      }

      this.truncationRaf = requestAnimationFrame(() => {
        this.truncationRaf = null;
        const dom = this.getContentDom();
        if (dom && this.preview) {
          this.applyTruncationStyles(dom);
        }
      });
    },

    bindTruncationImageListeners(contentDom) {
      const imgs = contentDom.querySelectorAll("img");
      if (imgs.length === 0) return;

      const schedule = () => this.scheduleTruncationApply();

      imgs.forEach((img) => {
        if (img._truncationHandler) return;
        img._truncationHandler = schedule;
        img.addEventListener("load", img._truncationHandler);
        img.addEventListener("error", img._truncationHandler);
        if (img.complete) {
          schedule();
        }
      });
    },

    unbindTruncationImageListeners(contentDom) {
      const imgs = contentDom.querySelectorAll("img");
      if (imgs.length === 0) return;
      imgs.forEach((img) => {
        if (img._truncationHandler) {
          img.removeEventListener("load", img._truncationHandler);
          img.removeEventListener("error", img._truncationHandler);
          delete img._truncationHandler;
        }
      });
    },

    clearTruncationStyles(contentDom) {
      const oldMask = contentDom.querySelector(".truncation-mask");
      if (oldMask) oldMask.remove();
      contentDom.style.maxHeight = "none";
      contentDom.style.overflow = "auto";
      contentDom.style.position = "static";
      this.isTruncated = false;
    },

    applyTruncationStyles(contentDom) {
      const oldMask = contentDom.querySelector(".truncation-mask");
      if (oldMask) oldMask.remove();

      if (contentDom.scrollHeight > TRUNCATION_MAX_HEIGHT) {
        this.isTruncated = true;
        contentDom.style.maxHeight = `${TRUNCATION_MAX_HEIGHT}px`;
        contentDom.style.overflow = "hidden";
        contentDom.style.position = "relative";

        const mask = document.createElement("div");
        mask.className = "truncation-mask";
        mask.style.position = "absolute";
        mask.style.left = 0;
        mask.style.right = 0;
        mask.style.bottom = "10px";
        mask.style.height = `${TRUNCATION_MASK_HEIGHT + 6}px`;
        mask.style.background =
          "linear-gradient(rgba(255,255,255,0), #fff 72%)";
        contentDom.appendChild(mask);
      } else {
        this.isTruncated = false;
        contentDom.style.maxHeight = "none";
        contentDom.style.overflow = "auto";
        contentDom.style.position = "static";
      }
    },

    // 创建复制按钮HTML
    createCopyButtonHtml(icon, text) {
      return `${SVG_ICONS[icon]}<span>${text}</span>`;
    },

    // 处理代码块，添加复制按钮
    processCodeBlocks(forceRebuild = false) {
      this.isProcessingCodeBlocks = true;
      try {
        const contentDom = this.getContentDom();
        if (!contentDom) {
          return;
        }

        if (forceRebuild) {
          // 移除已存在的代码块包装器
          const existingWrappers = contentDom.querySelectorAll(
            ".code-block-wrapper"
          );
          existingWrappers.forEach((wrapper) => {
            const pre = wrapper.querySelector("pre");
            if (pre) {
              wrapper.parentNode?.insertBefore(pre, wrapper);
              wrapper.remove();
            }
          });
        }

        // 处理所有代码块
        const preElements = contentDom.querySelectorAll("pre");
        preElements.forEach((pre) => {
          // 检查是否已经处理过
          if (pre.parentNode?.classList?.contains("code-block-wrapper")) {
            return;
          }

          // 创建包装器
          const wrapper = document.createElement("div");
          wrapper.className = "code-block-wrapper";

          // 创建复制按钮
          const copyBtn = document.createElement("button");
          copyBtn.className = "copy-btn";
          copyBtn.type = "button";
          copyBtn.innerHTML = this.createCopyButtonHtml("copy", "复制");

          // 获取代码内容
          const codeElement = pre.querySelector("code");
          const codeText = codeElement ? codeElement.innerText : pre.innerText;

          // 检查Clipboard API是否可用
          const isClipboardApiAvailable = !!(
            navigator.clipboard && navigator.clipboard.writeText
          );

          // 添加复制功能
          const handleCopyClick = async () => {
            // 如果已经是已复制状态，则阻止点击事件
            if (copyBtn.classList.contains("copied")) {
              return;
            }

            if (isClipboardApiAvailable) {
              try {
                await navigator.clipboard.writeText(codeText);
                this.handleCopySuccess(copyBtn);
              } catch (err) {
                this.fallbackCopyText(codeText, copyBtn);
              }
            } else {
              // 直接使用降级方案
              this.fallbackCopyText(codeText, copyBtn);
            }
          };

          copyBtn.addEventListener("click", handleCopyClick);

          // 包装结构
          wrapper.appendChild(copyBtn);

          // 将 pre 元素移动到包装器中
          pre.parentNode?.insertBefore(wrapper, pre);
          wrapper.appendChild(pre);
        });

        // 处理图片点击事件
        this.processImages();
      } finally {
        this.isProcessingCodeBlocks = false;
      }
    },

    scheduleTocEmit() {
      if (this.tocRaf) {
        cancelAnimationFrame(this.tocRaf);
      }
      this.tocRaf = requestAnimationFrame(() => {
        this.tocRaf = null;
        this.emitToc();
      });
    },

    emitToc() {
      const contentDom = this.getContentDom();
      if (!contentDom) return;

      const headings = contentDom.querySelectorAll("h1, h2, h3, h4, h5, h6");
      if (!headings.length) {
        this.$emit("toc-ready", []);
        return;
      }

      const toc = [];
      const seenSlugCounts = new Map();
      headings.forEach((heading) => {
        const text = heading.textContent.trim();
        if (!text) return;

        const baseId = text.toLowerCase().replace(/\s+/g, "-");
        const count = (seenSlugCounts.get(baseId) || 0) + 1;
        seenSlugCounts.set(baseId, count);
        const id = count === 1 ? baseId : `${baseId}-${count}`;
        heading.id = id;

        toc.push({
          level: parseInt(heading.tagName.substring(1)),
          text,
          id,
        });
      });

      this.$emit("toc-ready", toc);
    },

    // 处理图片点击事件，使用 Element Plus 的图片查看器
    processImages() {
      const contentDom = this.$refs.md?.$el?.querySelector(".v-show-content");
      if (!contentDom) return;

      const imgs = contentDom.querySelectorAll("img");

      // 收集所有图片URL
      const imageUrls = [];
      imgs.forEach((img) => {
        const src = img.src || img.getAttribute("data-src");
        if (src) {
          imageUrls.push(src);
        }
      });

      this.imageViewerUrls = imageUrls;

      // 为每个图片添加点击事件
      imgs.forEach((img, index) => {
        img._imageClickHandler &&
          img.removeEventListener("click", img._imageClickHandler);

        const handler = (e) => {
          e.preventDefault();
          e.stopPropagation();

          // 禁用 mavon-editor 默认的图片预览
          const parentLink = img.closest("a");
          if (parentLink && parentLink.getAttribute("href") === img.src) {
            parentLink.style.pointerEvents = "none";
          }

          // 显示 Element Plus 图片查看器
          this.openImageViewer(index);
        };

        img._imageClickHandler = handler;
        img.addEventListener("click", handler);

        // 添加鼠标样式提示
        img.style.cursor = "pointer";
        img.title = "点击查看大图";
      });
    },

    // 打开图片查看器
    openImageViewer(index) {
      if (this.imageViewerUrls.length === 0) return;

      this.imageViewerIndex = index;
      this.imageViewerVisible = true;
    },

    // 关闭图片查看器
    closeImageViewer() {
      this.imageViewerVisible = false;
    },

    // 处理复制成功
    handleCopySuccess(copyBtn) {
      copyBtn.innerHTML = this.createCopyButtonHtml("success", "已复制");
      copyBtn.classList.add("copied");

      setTimeout(() => {
        copyBtn.innerHTML = this.createCopyButtonHtml("copy", "复制");
        copyBtn.classList.remove("copied");
      }, COPY_FEEDBACK_RESET_DELAY);
    },

    // 处理复制失败
    handleCopyError(copyBtn) {
      copyBtn.innerHTML = this.createCopyButtonHtml("error", "复制失败");
      copyBtn.classList.add("copied");

      setTimeout(() => {
        copyBtn.innerHTML = this.createCopyButtonHtml("copy", "复制");
        copyBtn.classList.remove("copied");
      }, COPY_FEEDBACK_RESET_DELAY);
    },

    // 降级复制方案
    fallbackCopyText(codeText, copyBtn) {
      const textArea = document.createElement("textarea");
      textArea.value = codeText;
      textArea.style.position = "fixed";
      textArea.style.opacity = "0";
      document.body.appendChild(textArea);
      textArea.select();

      try {
        const successful = document.execCommand("copy");
        if (successful) {
          this.handleCopySuccess(copyBtn);
        } else {
          this.handleCopyError(copyBtn);
        }
      } catch (err) {
        console.error("降级复制方案失败：", err);
        this.handleCopyError(copyBtn);
      } finally {
        document.body.removeChild(textArea);
      }
    },
  },
};
</script>

<template>
  <div
    class="post-content-wrapper"
    :class="{
      'post-content-wrapper-compact': compact,
      'post-content-wrapper-preview': preview,
      'post-content-wrapper-detail': !preview,
    }"
  >
    <mavon-editor
      ref="md"
      v-model="pContent"
      class="detail"
      :subfield="false"
      :editable="false"
      box-shadow-style="#ffffff"
      default-open="preview"
      :toolbars-flag="false"
      :markdown-options="{
        breaks: true,
        linkify: true,
        typographer: true,
        highlight: false,
        bulletListMarker: '-',
      }"
    />
    <div
      v-if="preview && isTruncated"
      class="truncation-indicator"
      :class="{ 'truncation-indicator-markdown': previewType === 'markdown' }"
    >
      <span class="truncation-line"></span>
      <span class="truncation-text">下文已折叠</span>
      <span class="truncation-cta">点击卡片继续阅读</span>
    </div>
    <!-- Element Plus 图片查看器 -->
    <el-image-viewer
      v-if="imageViewerVisible"
      :url-list="imageViewerUrls"
      :initial-index="imageViewerIndex"
      @close="closeImageViewer"
      teleported
    />
  </div>
</template>

<style lang="scss" scoped>
@use "./PostReadingTokens.scss" as tokens;

.post-content-wrapper {
  width: 100%;
  margin: 0;
  padding: 0;
}

.post-content-wrapper-detail {
  --content-font-family: #{tokens.$reading-font-family};
  --content-code-font-family: #{tokens.$reading-code-font-family};
  --content-text-color: #{tokens.$reading-text-primary};
  --content-muted-color: #{tokens.$reading-text-secondary};
  --content-line-height: #{tokens.$reading-line-height-body};
  --content-heading-color: #{tokens.$reading-text-primary};
  --content-block-spacing: 1.3em;
  --content-heading-spacing-top: 2.1em;
  --content-heading-spacing-bottom: 0.72em;
}

.post-content-wrapper-preview {
  --content-font-family: #{tokens.$reading-font-family};
  --content-code-font-family: #{tokens.$reading-code-font-family};
  --content-text-color: #{tokens.$reading-text-primary};
  --content-muted-color: #{tokens.$reading-text-secondary};
  --content-line-height: #{tokens.$reading-line-height-summary};
  --content-heading-color: #{tokens.$reading-text-primary};
  --content-block-spacing: 0.92em;
  --content-heading-spacing-top: 1.35em;
  --content-heading-spacing-bottom: 0.68em;
}

.post-content-wrapper-compact {
  :deep(.v-note-wrapper) {
    min-height: auto;
  }

  :deep(.v-show-content) {
    p {
      margin: 0.1em 0 0.24em;
      line-height: 1.7;
    }

    h1,
    h2,
    h3,
    h4,
    h5,
    h6,
    ul,
    ol,
    blockquote,
    pre,
    table,
    hr {
      margin-top: 0.4em;
      margin-bottom: 0.5em;
    }
  }

  .truncation-indicator {
    margin-top: 6px;
    padding-top: 8px;
  }
}

.truncation-indicator {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: -2px;
  padding-top: 12px;
  color: #777;
  font-size: tokens.$reading-font-size-meta;
  line-height: 1.55;

  .truncation-line {
    width: 24px;
    height: 1px;
    background: tokens.$reading-border;
    flex-shrink: 0;
  }

  .truncation-text {
    color: tokens.$reading-text-secondary;
  }

  .truncation-cta {
    color: tokens.$reading-text-primary;
    text-decoration: underline;
    text-decoration-color: tokens.$reading-border;
    text-underline-offset: 2px;
  }
}

.truncation-indicator-markdown {
  margin-top: 8px;
  padding-top: 14px;

  .truncation-line {
    width: 32px;
    background: tokens.$reading-border;
  }

  .truncation-text {
    color: tokens.$reading-text-secondary;
    font-weight: 400;
  }
}

.base {
  font-size: tokens.$reading-font-size-body;
  line-height: var(--content-line-height);
  letter-spacing: 0;
  color: var(--content-text-color);
  font-family: var(--content-font-family);
}

.v-note-wrapper {
  min-height: 25px;
  border: none !important;
  @extend .base;
}

// 优化 markdown 内容样式
:deep(.v-show-content) {
  padding: 0 !important;
  background-color: transparent !important;
  color: var(--content-text-color);
  font-family: var(--content-font-family);
  line-height: var(--content-line-height);
  text-rendering: optimizeLegibility;
  -webkit-font-smoothing: antialiased;
  overflow-wrap: anywhere;
  word-break: break-word;

  // 标题样式优化
  h1,
  h2,
  h3,
  h4,
  h5,
  h6 {
    margin-top: var(--content-heading-spacing-top);
    margin-bottom: var(--content-heading-spacing-bottom);
    font-weight: 600;
    line-height: 1.42;
    letter-spacing: 0;
    color: var(--content-heading-color);
  }

  h1 {
    font-size: 1.74em;
    font-weight: 600;
    margin-top: 0;
    margin-bottom: 0.95em;
    border-bottom: none;
    padding-bottom: 0;
  }

  h2 {
    font-size: 1.34em;
    border-bottom: none;
    padding-bottom: 0;
  }

  h3 {
    font-size: 1.14em;
  }

  h4,
  h5,
  h6 {
    font-size: 1.02em;
  }

  // 段落样式
  p {
    margin: 0 0 var(--content-block-spacing);
    line-height: var(--content-line-height);
  }

  // 列表样式
  ul,
  ol {
    padding-left: 1.5em;
    margin: 0 0 var(--content-block-spacing);
  }

  // 无序列表
  ul {
    list-style-type: disc;
    padding-left: 2em;
  }

  // 有序列表
  ol {
    list-style-type: decimal;
    padding-left: 2em;
  }

  li {
    margin: 0.42em 0;
    line-height: 1.84;
  }

  // 引用样式
  blockquote {
    padding: 0.2em 0 0.2em 1.15em;
    color: var(--content-muted-color);
    border-left: 2px solid tokens.$reading-border;
    margin: 0 0 calc(var(--content-block-spacing) + 0.15em);
    background-color: transparent;
    border-radius: 0;
  }

  // 代码样式
  pre {
    margin: 0 0 calc(var(--content-block-spacing) + 0.12em);
    border-radius: 0;
    background-color: tokens.$reading-fill-soft !important;
    padding: 1.05em;
    overflow: auto;
    border: 1px solid tokens.$reading-border-code;
  }

  // 代码块内的 code 元素样式
  pre code {
    display: block;
    padding: 0 !important;
    font-family: var(--content-code-font-family);
    font-size: 0.92em;
    line-height: 1.68;
    color: inherit;
    background-color: transparent !important;
    border-radius: 0 !important;
  }

  // 行内代码样式
  :not(pre) > code {
    font-family: var(--content-code-font-family);
    background-color: tokens.$reading-fill-soft;
    padding: 0.2em 0.4em;
    border-radius: 0;
    font-size: 0.9em;
    color: tokens.$reading-text-primary;
  }

  // 图片样式
  img {
    max-width: 100%;
    border-radius: 0;
    margin: 0.35em auto calc(var(--content-block-spacing) + 0.2em);
    display: block;
  }

  // 表格样式
  table {
    border-collapse: collapse;
    width: 100%;
    margin: 0 0 calc(var(--content-block-spacing) + 0.1em);
    overflow-x: auto;
    display: block;
  }

  th,
  td {
    border: 1px solid tokens.$reading-border;
    padding: 10px 12px;
  }

  th {
    background-color: tokens.$reading-fill-softer;
    font-weight: 600;
  }

  // 水平线
  hr {
    height: 1px;
    background-color: tokens.$reading-border;
    border: none;
    margin: calc(var(--content-block-spacing) + 0.35em) 0;
  }

  // 链接样式
  a {
    color: tokens.$reading-text-primary;
    text-decoration: underline;
    text-decoration-color: tokens.$reading-border;

    &:hover {
      text-decoration-color: tokens.$reading-text-primary;
    }
  }
}

.post-content-wrapper-detail {
  :deep(.v-note-wrapper) {
    min-height: auto;
  }

  :deep(.v-show-content) {
    font-size: tokens.$reading-font-size-body;

    h1 {
      font-size: 1.78em;
      line-height: 1.34;
      margin-bottom: 1em;
    }

    h2 {
      font-size: 1.36em;
      margin-top: 2.15em;
    }

    h3 {
      font-size: 1.16em;
      margin-top: 1.9em;
    }

    blockquote {
      padding-left: 1.2em;
    }
  }

  :deep(.code-block-wrapper) {
    margin: 0 0 calc(var(--content-block-spacing) + 0.15em);
  }
}

.detail {
  height: 100% !important;
}

// 代码块包装器样式
:deep(.code-block-wrapper) {
  position: relative;
  margin: 1.5em 0;
}

:deep(.copy-btn) {
  position: absolute;
  top: 4px;
  right: 8px;
  z-index: 10;
  padding: 0px 8px;
  font-size: 12px;
  background: #fff;
  border: 1px solid tokens.$reading-border;
  border-radius: 0;
  color: tokens.$reading-text-primary;
  cursor: pointer;
  transition: all 0.2s ease;
  font-family: var(--content-font-family);
  display: flex;
  align-items: center;
  gap: 4px;

  &.copied {
    color: tokens.$reading-text-secondary;
    cursor: default !important;
    pointer-events: none !important;
  }

  .copy-icon {
    flex-shrink: 0;
  }
}

// 代码块样式调整
:deep(pre) {
  position: relative;
  margin: 0 !important;
  border-radius: 0;
  background-color: tokens.$reading-fill-soft !important;
  padding: 1em !important;
  overflow: auto;
  border: 1px solid tokens.$reading-border-code;

  // 避免复制按钮挡住代码
  padding-top: 2.5em !important;

  .hljs {
    background: none;
  }
  // 确保语法高亮背景色统一
  code {
    background: none !important;
    // 处理语法高亮的各类元素
    .hljs-keyword,
    .hljs-selector-tag,
    .hljs-built_in,
    .hljs-name,
    .hljs-tag {
      color: #d73a49;
    }
    .hljs-string,
    .hljs-title,
    .hljs-section,
    .hljs-attribute,
    .hljs-literal,
    .hljs-template-tag,
    .hljs-template-variable,
    .hljs-type,
    .hljs-addition {
      color: #032f62;
    }

    .hljs-comment,
    .hljs-quote,
    .hljs-deletion,
    .hljs-meta {
      color: #6a737d;
    }

    .hljs-number,
    .hljs-regexp,
    .hljs-literal,
    .hljs-built_in,
    .hljs-builtin-name {
      color: #005cc5;
    }

    .hljs-class .hljs-title {
      color: #6f42c1;
    }

    .hljs-function .hljs-title {
      color: #6f42c1;
    }
  }
}

// 适配移动端
@media (max-width: 768px) {
  .post-content-wrapper-detail {
    --content-line-height: 1.9;
    --content-block-spacing: 1.2em;
    --content-heading-spacing-top: 1.9em;

    :deep(.v-show-content) {
      font-size: 15px;

      h1 {
        font-size: 1.68em;
        margin-bottom: 0.88em;
      }

      h2 {
        font-size: 1.3em;
      }
    }
  }

  .post-content-wrapper-preview {
    :deep(.v-show-content) {
      font-size: 14px;

      h1 {
        font-size: 1.52em;
      }

      h2 {
        font-size: 1.28em;
      }
    }
  }

  :deep(.copy-btn) {
    padding: 0px 6px;
    font-size: 11px;
    top: 3px;
    right: 6px;
  }

  :deep(pre) {
    padding-top: 2em !important;
  }
}
</style>
