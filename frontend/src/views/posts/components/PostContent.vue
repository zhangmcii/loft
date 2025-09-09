<script>
export default {
  props: {
    postContent: {
      type: String,
      default: "",
    },
    preview: {
      type: Boolean,
      default: false,
    },
    fontSize: {
      type: Number,
      default: 16,
    },
  },
  data() {
    return {
      pContent: "",
      truncationTryCount: 0, // 新增
    };
  },
  watch: {
    postContent: {
      handler(newVal) {
        this.pContent = newVal;
        this.truncationTryCount = 0; // 重置
        this.$nextTick(() => {
          this.updateTruncation();
        });
      },
      immediate: true,
    },
    fontSize: {
      handler(newVal) {
        this.updateFontSize(newVal);
      },
    },
  },
  mounted() {
    this.$nextTick(() => {
      this.updateTruncation();
      // 从本地存储加载字体大小设置
      const savedFontSize = localStorage.getItem("article-font-size");
      if (savedFontSize) {
        this.fontSize = parseInt(savedFontSize);
        this.updateFontSize(this.fontSize);
      }
    });
  },
  computed: {},
  methods: {
    updateFontSize(size) {
      const contentDom = this.$refs.md?.$el?.querySelector(".v-show-content");
      if (contentDom) {
        contentDom.style.fontSize = `${size}px`;

        // 根据字体大小调整其他元素
        const h1Elements = contentDom.querySelectorAll("h1");
        const h2Elements = contentDom.querySelectorAll("h2");

        h1Elements.forEach((el) => {
          el.style.fontSize = `${(size * 1.8) / 16}em`;
        });

        h2Elements.forEach((el) => {
          el.style.fontSize = `${(size * 1.5) / 16}em`;
        });
      }
    },

    updateTruncation() {
      if (!this.preview) return;

      this.$nextTick(() => {
        const contentDom = this.$refs.md?.$el?.querySelector(".v-show-content");
        if (!contentDom) return;

        // 监听图片加载
        const imgs = contentDom.querySelectorAll("img");
        let loadedCount = 0;
        const totalImgs = imgs.length;

        const checkAllLoaded = () => {
          loadedCount++;
          if (loadedCount === totalImgs && this.truncationTryCount < 10) {
            this.truncationTryCount++;
            setTimeout(() => {
              this.updateTruncation();
            }, 50);
          }
        };

        if (totalImgs > 0) {
          imgs.forEach((img) => {
            if (!img._truncationLoaded) {
              img._truncationLoaded = true;
              img.addEventListener("load", checkAllLoaded);
              img.addEventListener("error", checkAllLoaded);
            }
          });
        }

        // 先移除旧的遮罩
        const oldMask = contentDom.querySelector(".truncation-mask");
        if (oldMask) oldMask.remove();

        // 判断是否超出最大高度
        const maxHeight = 300;
        if (contentDom.scrollHeight > maxHeight) {
          contentDom.style.maxHeight = maxHeight + "px";
          contentDom.style.overflow = "hidden";
          contentDom.style.position = "relative";

          // 添加遮罩和省略号
          const mask = document.createElement("div");
          mask.className = "truncation-mask";
          mask.style.position = "absolute";
          mask.style.left = 0;
          mask.style.right = 0;
          mask.style.bottom = 0;
          mask.style.height = "40px";
          mask.style.background =
            "linear-gradient(rgba(255,255,255,0), #fff 80%)";
          // mask.style.display = 'flex'
          // mask.style.alignItems = 'flex-end'
          // mask.style.justifyContent = 'flex-end'
          // mask.style.pointerEvents = 'none'
          // mask.innerHTML =
          //   '<div style="color:#888;font-size:18px;padding:20px 10px 10px 10px;">...</div>'
          contentDom.appendChild(mask);
        } else {
          contentDom.style.maxHeight = "none";
          contentDom.style.overflow = "auto";
          contentDom.style.position = "static";
        }

        // 延迟再触发一次，兜底
        if (this.truncationTryCount < 10) {
          this.truncationTryCount++;
          setTimeout(() => {
            const dom = this.$refs.md?.$el?.querySelector(".v-show-content");
            if (dom && dom.scrollHeight > maxHeight) {
              this.updateTruncation();
            }
          }, 300);
        }
      });
    },
  },
};
</script>

<template>
  <div class="post-content-wrapper">
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
  </div>
</template>

<style lang="scss" scoped>
.post-content-wrapper {
  width: 100%;
  margin: 0;
  padding: 0;
}

.base {
  font-size: 16px;
  line-height: 1.8;
  letter-spacing: 0.02em;
  color: #333;
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

  // 标题样式优化
  h1,
  h2,
  h3,
  h4,
  h5,
  h6 {
    margin-top: 1.5em;
    margin-bottom: 0.8em;
    font-weight: 600;
    line-height: 1.4;
    color: #222;
  }

  h1 {
    font-size: 1.8em;
    border-bottom: 1px solid #eee;
    padding-bottom: 0.3em;
  }

  h2 {
    font-size: 1.5em;
    border-bottom: 1px solid #f0f0f0;
    padding-bottom: 0.2em;
  }

  // 段落样式
  p {
    margin: 0.8em 0 1.2em;
    line-height: 1.8;
  }

  // 列表样式
  ul,
  ol {
    padding-left: 1.5em;
    margin: 0.8em 0;
  }

  ul {
    list-style-type: disc;
    padding-left: 2em;
  }

  li {
    margin: 0.4em 0;
  }

  // 引用样式
  blockquote {
    padding: 0.5em 1em;
    color: #666;
    border-left: 4px solid #ddd;
    margin: 1em 0;
    background-color: #f9f9f9;
    border-radius: 0 4px 4px 0;
  }

  // 代码样式
  pre {
    margin: 1em 0;
    border-radius: 6px;
    background-color: #f6f8fa !important;
    padding: 1em;
    overflow: auto;
  }

  code {
    font-family: Consolas, Monaco, "Andale Mono", monospace;
    background-color: #f6f8fa;
    padding: 0.2em 0.4em;
    border-radius: 3px;
    font-size: 0.9em;
    color: #e83e8c;
  }

  // 图片样式
  img {
    max-width: 100%;
    border-radius: 6px;
    margin: 1em auto;
    display: block;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }

  // 表格样式
  table {
    border-collapse: collapse;
    width: 100%;
    margin: 1em 0;
    overflow-x: auto;
    display: block;
  }

  th,
  td {
    border: 1px solid #ddd;
    padding: 8px 12px;
  }

  th {
    background-color: #f6f8fa;
    font-weight: 600;
  }

  // 水平线
  hr {
    height: 1px;
    background-color: #eee;
    border: none;
    margin: 1.5em 0;
  }

  // 链接样式
  a {
    color: #0366d6;
    text-decoration: none;

    &:hover {
      text-decoration: underline;
    }
  }
}

.detail {
  height: 100% !important;
}

// 适配移动端
@media (max-width: 768px) {
  :deep(.v-show-content) {
    font-size: 14px;

    h1 {
      font-size: 1.6em;
    }

    h2 {
      font-size: 1.4em;
    }
  }
}
</style>
