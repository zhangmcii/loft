<script>
import PageScroll from "@/utils/components/PageScroll.vue";
import MarkdownEditor from "@/utils/components/MarkdownEditor.vue";
import CreativeAssist from "@/views/posts/components/CreativeAssist.vue";
import postApi from "@/api/posts/postApi.js";
import uploadApi from "@/api/upload/uploadApi.js";
import emitter from "@/utils/emitter.js";
import { useCurrentUserStore } from "@/stores/user";
import {
  compressImages,
  uploadFiles,
  beforePicUpload,
} from "@/utils/common.js";

export default {
  components: {
    PageScroll,
    MarkdownEditor,
    CreativeAssist,
  },
  data() {
    return {
      postId: null,
      isEdit: false,
      loading: false,
      submitting: false,
      mode: "text",
      originalSnapshot: "",
      textContent: "",
      imageContent: "",
      imageFiles: [],
      compressedImages: [],
      existingImageUrls: [],
      markdownContent: {
        content: "",
        images: [],
        type: "markdown",
      },
      previewVisible: false,
      previewUrl: "",
      assistExpanded: false,
    };
  },
  setup() {
    const currentUser = useCurrentUserStore();
    return { currentUser };
  },
  computed: {
    submitLabel() {
      return this.isEdit ? "保存" : "发布";
    },
    submitHint() {
      if (this.loading || this.submitting) return "";
      if (this.isEdit && !this.isDirty) return "尚未修改";
      if (
        this.mode === "image" &&
        !this.isEdit &&
        this.imageFiles.length === 0
      ) {
        return "至少添加一张图片";
      }
      if (!this.canSubmit) return "正文还没有完成";
      return "";
    },
    isMarkdown() {
      return this.mode === "markdown";
    },
    canSubmit() {
      if (this.isMarkdown) {
        return this.markdownContent.content.trim() !== "";
      }
      if (this.mode === "image") {
        if (this.isEdit) {
          return this.imageContent.trim() !== "";
        }
        return this.imageContent.trim() !== "" && this.imageFiles.length > 0;
      }
      return this.textContent.trim() !== "";
    },
    textCount() {
      if (this.mode === "image") return this.imageContent.length;
      return this.textContent.length;
    },
    assistContent() {
      return this.mode === "image" ? this.imageContent : this.textContent;
    },
    isDirty() {
      return this.currentSnapshot() !== this.originalSnapshot;
    },
    modeTabs() {
      if (this.isEdit) {
        const current = {
          text: "文字",
          image: "图文",
          markdown: "Markdown",
        }[this.mode];
        return [{ key: this.mode, label: current || "正文" }];
      }
      return [
        { key: "text", label: "文字" },
        { key: "image", label: "图文" },
        { key: "markdown", label: "Markdown" },
      ];
    },
  },
  beforeRouteEnter(to, from, next) {
    next((vm) => {
      vm.initializePage(to);
    });
  },
  watch: {
    $route(to) {
      this.initializePage(to);
    },
  },
  methods: {
    initializePage(route) {
      this.postId = route.params.id ? Number(route.params.id) : null;
      this.isEdit = Boolean(this.postId);
      this.mode = route.query.mode || "text";
      this.resetDraft();
      if (this.isEdit) {
        this.fetchPost();
      } else {
        this.originalSnapshot = this.currentSnapshot();
      }
    },
    async fetchPost() {
      this.loading = true;
      try {
        const res = await postApi.getPost(this.postId);
        if (res.code === 200) {
          const post = res.data || {};
          this.mode = post.post_type || "text";
          if (this.mode === "markdown") {
            this.markdownContent = {
              content: post.content || "",
              images: [],
              type: "markdown",
            };
          } else if (this.mode === "image") {
            this.imageContent = (post.content || "").replace(
              /<br\s*\/?>/g,
              "\n"
            );
            this.existingImageUrls = [...(post.post_images || [])];
          } else {
            this.textContent = (post.content || "").replace(
              /<br\s*\/?>/g,
              "\n"
            );
          }
          this.originalSnapshot = this.currentSnapshot();
        } else {
          ElMessage.error(res.message || "获取内容失败");
        }
      } finally {
        this.loading = false;
      }
    },
    goBack() {
      if (window.history.length > 1) {
        this.$router.back();
      } else {
        this.$router.push("/posts");
      }
    },
    changeMode(nextMode) {
      if (this.isEdit) return;
      this.mode = nextMode;
    },
    handlePictureCardPreview(file) {
      this.previewUrl = file.url;
      this.previewVisible = true;
    },
    handleContentGenerated(content) {
      if (this.mode === "image") {
        this.imageContent = content;
      } else {
        this.textContent = content;
      }
    },
    async submit() {
      if (!this.canSubmit) return;
      this.submitting = true;
      try {
        const payload = await this.buildPayload();
        const res = this.isEdit
          ? await postApi.editPost(this.postId, payload)
          : await postApi.publish_post(payload);
        if (res.code === 200) {
          ElMessage.success(this.isEdit ? "保存成功" : "发布成功");
          if (this.isEdit) {
            this.$router.push(`/postDetail/${this.postId}`);
          } else {
            emitter.emit("newPostList", {
              list: Array.isArray(res.data) ? res.data : [],
              total: typeof res.total === "number" ? res.total : undefined,
            });
            this.$router.push("/posts");
          }
        } else {
          ElMessage.error(
            res.message || (this.isEdit ? "保存失败" : "发布失败")
          );
        }
      } catch (error) {
        if (error === "请求频率超限") {
          ElMessage.warning(
            this.isEdit ? "保存过快，稍后再试" : "发布次数超限"
          );
        } else {
          ElMessage.error(
            this.isEdit ? "保存失败，请稍后重试" : "发布失败，请稍后重试"
          );
        }
      } finally {
        this.submitting = false;
      }
    },
    async buildPayload() {
      if (this.mode === "markdown") {
        const images = await this.$refs.md?.uploadPhotos?.();
        return {
          content: this.markdownContent.content,
          images: images || [],
          type: "markdown",
        };
      }

      if (this.mode === "image") {
        if (this.isEdit) {
          return {
            content: this.imageContent.replace(/\n/g, "<br>"),
            type: "image",
          };
        }

        if (!beforePicUpload(this.imageFiles)) {
          throw new Error("图片格式或大小不符合要求");
        }
        this.compressedImages = await compressImages(this.imageFiles, []);
        const uploadToken = await this.getUploadToken();
        const { imageKey } = await uploadFiles(
          this.compressedImages,
          this.currentUser.uploadArticlesBaseUrl,
          uploadToken
        );
        return {
          content: this.imageContent.replace(/\n/g, "<br>"),
          images: imageKey,
          type: "image",
        };
      }

      return {
        content: this.textContent.replace(/\n/g, "<br>"),
        images: [],
        type: "text",
      };
    },
    async getUploadToken() {
      const response = await uploadApi.get_upload_token();
      return response.data.upload_token;
    },
    currentSnapshot() {
      if (this.mode === "markdown") {
        return JSON.stringify({
          mode: this.mode,
          content: this.markdownContent.content,
        });
      }
      if (this.mode === "image") {
        return JSON.stringify({
          mode: this.mode,
          content: this.imageContent,
          images: this.existingImageUrls,
        });
      }
      return JSON.stringify({
        mode: this.mode,
        content: this.textContent,
      });
    },
    resetDraft() {
      this.textContent = "";
      this.imageContent = "";
      this.imageFiles = [];
      this.compressedImages = [];
      this.existingImageUrls = [];
      this.markdownContent = {
        content: "",
        images: [],
        type: "markdown",
      };
      this.assistExpanded = false;
    },
  },
};
</script>

<template>
  <PageScroll max-height="calc(100vh - 45px - 47px)">
    <div class="compose-page">
      <header class="compose-topbar">
        <button
          type="button"
          class="compose-back"
          @click="goBack"
          aria-label="返回"
        >
          ←
        </button>
        <p class="compose-status">{{ isEdit ? "编辑中" : "写作中" }}</p>
        <div class="compose-submit-area">
          <span v-if="submitHint" class="compose-submit-note">{{
            submitHint
          }}</span>
          <el-button
            class="compose-submit"
            type="primary"
            :loading="submitting"
            :disabled="!canSubmit || loading || (isEdit && !isDirty)"
            @click="submit"
          >
            {{ submitLabel }}
          </el-button>
        </div>
      </header>

      <div class="compose-shell">
        <nav class="compose-modes">
          <button
            v-for="tab in modeTabs"
            :key="tab.key"
            type="button"
            class="compose-mode"
            :class="{ active: mode === tab.key }"
            @click="changeMode(tab.key)"
          >
            {{ tab.label }}
          </button>
        </nav>

        <div class="compose-editor">
          <div class="compose-sheet">
            <div class="compose-sheet-head">
              <span class="sheet-label">
                {{ mode === "markdown" ? "正文（Markdown）" : "正文" }}
              </span>
              <span v-if="mode !== 'markdown'" class="sheet-count"
                >{{ textCount }} 字</span
              >
            </div>
            <template v-if="mode === 'text'">
              <el-input
                v-model="textContent"
                type="textarea"
                :autosize="{ minRows: 10, maxRows: 18 }"
                maxlength="310"
                show-word-limit
                placeholder="开始写作。"
                class="compose-textarea"
              />
            </template>

            <template v-else-if="mode === 'image'">
              <el-input
                v-model="imageContent"
                type="textarea"
                :autosize="{ minRows: 8, maxRows: 14 }"
                maxlength="150"
                show-word-limit
                placeholder="写下这一组图片的说明。"
                class="compose-textarea"
              />

              <section class="compose-insert">
                <div class="insert-head">
                  <p class="insert-title">插图</p>
                  <p v-if="!isEdit" class="insert-meta">最多 9 张</p>
                </div>
                <div
                  v-if="isEdit && existingImageUrls.length"
                  class="existing-images"
                >
                  <el-image
                    v-for="url in existingImageUrls"
                    :key="url"
                    :src="url"
                    fit="cover"
                    class="existing-image"
                    :preview-src-list="existingImageUrls"
                  />
                </div>
                <p v-if="isEdit" class="insert-note">
                  编辑时先只调整配文，图片保持不变。
                </p>
                <el-upload
                  v-else
                  v-model:file-list="imageFiles"
                  list-type="picture-card"
                  :auto-upload="false"
                  :before-upload="() => false"
                  accept="image/jpeg,image/png,image/jpg,image/webp"
                  :limit="9"
                  multiple
                  :on-preview="handlePictureCardPreview"
                  :on-exceed="() => ElMessage.info('最多只能上传9张图片')"
                >
                  <div class="upload-trigger">
                    <el-icon><i-ep-Plus /></el-icon>
                    <span>添加图片</span>
                  </div>
                </el-upload>
              </section>
            </template>

            <template v-else>
              <MarkdownEditor
                ref="md"
                :body-init="markdownContent.content"
                :initially-active="false"
                inactive-label="点击进入 Markdown 写作"
                @contentChange="
                  (payload) =>
                    (markdownContent = { ...markdownContent, ...payload })
                "
              />
            </template>
          </div>
        </div>

        <section v-if="mode !== 'markdown'" class="compose-assist">
          <button
            type="button"
            class="assist-toggle"
            @click="assistExpanded = !assistExpanded"
          >
            {{ assistExpanded ? "收起辅助" : "需要一点写作帮助" }}
          </button>
          <CreativeAssist
            v-if="assistExpanded"
            @contentGenerated="handleContentGenerated"
          />
        </section>
      </div>
    </div>

    <el-dialog v-model="previewVisible">
      <img
        class="compose-preview-image"
        :src="previewUrl"
        alt="Preview Image"
      />
    </el-dialog>
  </PageScroll>
</template>

<style lang="scss" scoped>
.compose-page {
  box-sizing: border-box;
  width: min(100%, 980px);
  margin: 0 auto;
  padding: 24px 24px 48px;
  color: #111;
  background: #fff;
  overflow-x: clip;
}

.compose-topbar {
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}

.compose-back {
  padding: 0;
  border: none;
  background: transparent;
  color: #7a7a7a;
  font-size: 18px;
  line-height: 1;
  cursor: pointer;
  justify-self: start;
}

.compose-status {
  margin: 0;
  font-size: 12px;
  color: #8a8a8a;
  letter-spacing: 0.08em;
}

.compose-submit-area {
  display: flex;
  align-items: center;
  justify-self: end;
  gap: 12px;
}

.compose-submit-note {
  font-size: 12px;
  color: #8a8a8a;
  white-space: nowrap;
}

.compose-submit {
  border-color: #111;
  background: #111;
  color: #fff;

  &:hover,
  &:focus,
  &:focus-visible {
    border-color: #111;
    background: #111;
    color: #fff;
  }

  &:active {
    border-color: #000;
    background: #000;
    color: #fff;
  }

  &.is-disabled,
  &.is-disabled:hover,
  &.is-disabled:focus {
    border-color: #d7d7d7;
    background: #d7d7d7;
    color: #8a8a8a;
  }
}

.compose-shell {
  max-width: 720px;
  margin: 0 auto;
  min-width: 0;
}

.compose-modes {
  display: flex;
  gap: 20px;
  margin-bottom: 22px;
  padding-bottom: 10px;
  border-bottom: 1px solid #ececec;
}

.compose-mode {
  padding: 0;
  border: none;
  background: transparent;
  color: #8a8a8a;
  font-size: 14px;
  letter-spacing: 0.02em;
  cursor: pointer;

  &.active {
    color: #111;
    font-weight: 500;
  }
}

.compose-editor {
  margin-bottom: 22px;
}

.compose-sheet {
  padding: 0 0 12px;
}

.compose-sheet-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
}

.sheet-label,
.sheet-count {
  font-size: 12px;
  color: #7d7d7d;
  letter-spacing: 0.04em;
}

.compose-textarea {
  :deep(.el-textarea__inner) {
    min-height: 320px !important;
    padding: 0;
    border: none;
    border-radius: 0;
    box-shadow: none;
    font-size: 16px;
    line-height: 1.9;
    color: #1f1f1f;
    resize: none;
    background: transparent;
  }

  :deep(.el-textarea .el-input__count) {
    color: #9a9a9a;
    background: transparent;
  }
}

.compose-insert {
  min-width: 0;
  margin-top: 28px;
  padding-top: 18px;
  border-top: 1px solid #efefef;
}

.insert-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
}

.insert-title {
  margin: 0;
  font-size: 12px;
  color: #7d7d7d;
  letter-spacing: 0.08em;
}

.insert-meta {
  margin: 0;
  font-size: 12px;
  color: #9a9a9a;
}

.insert-note {
  margin: 0 0 12px;
  font-size: 12px;
  color: #888;
  line-height: 1.6;
}

.upload-trigger {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  color: #666;
  font-size: 12px;

  :deep(svg) {
    font-size: 16px;
  }
}

.existing-images {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 10px;
  min-width: 0;
}

.existing-image {
  width: 100%;
  aspect-ratio: 1;
  border: 1px solid #ececec;
}

.compose-assist {
  padding-top: 16px;
  border-top: 1px solid #efefef;
}

.assist-toggle {
  padding: 0;
  border: none;
  background: transparent;
  color: #666;
  font-size: 13px;
  cursor: pointer;
}

.compose-preview-image {
  width: 100%;
}

:deep(.el-upload--picture-card),
:deep(.el-upload-list--picture-card .el-upload-list__item) {
  box-sizing: border-box;
  border-radius: 0;
  border-color: #e6e6e6;
  background: #fff;
}

:deep(.el-upload-list) {
  max-width: 100%;
}

:deep(.el-upload-list--picture-card) {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(92px, 1fr));
  gap: 10px;
}

:deep(.el-upload-list--picture-card .el-upload-list__item),
:deep(.el-upload--picture-card) {
  width: 100%;
  margin: 0;
}

:deep(.el-upload--picture-card:hover) {
  border-color: #111;
}

@media (max-width: 768px) {
  .compose-page {
    padding: 14px 16px 32px;
  }

  .compose-topbar {
    gap: 8px;
    margin-bottom: 14px;
  }

  .compose-submit-area {
    gap: 6px;
  }

  .compose-submit-note {
    display: none;
  }

  .compose-submit {
    justify-self: end;
  }

  .compose-status {
    font-size: 11px;
    letter-spacing: 0.04em;
  }

  .compose-modes {
    margin-bottom: 16px;
    gap: 16px;
    overflow-x: auto;
    overflow-y: hidden;
  }

  .compose-sheet-head {
    margin-bottom: 12px;
  }

  .compose-textarea {
    :deep(.el-textarea__inner) {
      min-height: 260px !important;
      font-size: 15px;
    }
  }

  :deep(.el-upload-list--picture-card) {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}
</style>
