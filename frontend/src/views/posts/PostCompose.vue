<script>
import PageScroll from "@/utils/components/PageScroll.vue";
import MarkdownEditor from "@/utils/components/MarkdownEditor.vue";
import CreativeAssist from "@/views/posts/components/CreativeAssist.vue";
import postApi from "@/api/posts/postApi.js";
import uploadApi from "@/api/upload/uploadApi.js";
import emitter from "@/utils/emitter.js";
import { useCurrentUserStore } from "@/stores/user";
import { useComposeDraftStore } from "@/stores/composeDraft";
import {
  compressImages,
  uploadFiles,
  beforePicUpload,
} from "@/utils/common.js";

export default {
  name: "PostCompose",
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
      restoredDraftMessage: "",
      restoredDraftMode: "",
      previewVisible: false,
      previewUrl: "",
      assistExpanded: false,
      draftSaveTimer: null,
      draftHydrating: false,
      draftPersistLocked: false,
    };
  },
  setup() {
    const currentUser = useCurrentUserStore();
    const composeDraftStore = useComposeDraftStore();
    return { currentUser, composeDraftStore };
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
    visibleRestoredDraftMessage() {
      if (!this.restoredDraftMessage) return "";
      if (this.isEdit) return this.restoredDraftMessage;
      return this.restoredDraftMode === this.mode
        ? this.restoredDraftMessage
        : "";
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
    mode() {
      this.scheduleDraftPersist();
    },
    textContent() {
      this.scheduleDraftPersist();
    },
    imageContent() {
      this.scheduleDraftPersist();
    },
    "markdownContent.content"() {
      this.scheduleDraftPersist();
    },
  },
  beforeUnmount() {
    if (!this.draftPersistLocked) {
      this.flushDraftPersist();
    } else {
      this.clearDraftPersistTimer();
    }
  },
  methods: {
    initializePage(route) {
      this.postId = route.params.id ? Number(route.params.id) : null;
      this.isEdit = Boolean(this.postId);
      this.mode = route.query.mode || "text";
      this.restoredDraftMessage = "";
      this.restoredDraftMode = "";
      this.resetDraft();
      if (this.isEdit) {
        this.fetchPost();
      } else {
        this.originalSnapshot = this.currentSnapshot();
        this.restoreDraftIfAvailable();
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
          this.restoreDraftIfAvailable();
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
      this.clearDraftPersistTimer();
      try {
        const payload = await this.buildPayload();
        const res = this.isEdit
          ? await postApi.editPost(this.postId, payload)
          : await postApi.publish_post(payload);
        if (res.code === 200) {
          this.clearDraftStorage();
          // 避免路由跳转后 beforeUnmount 再次把当前内容写回草稿
          this.draftPersistLocked = true;
          ElMessage.success(this.isEdit ? "保存成功" : "发布成功");
          if (this.isEdit) {
            void this.$router
              .push(`/postDetail/${this.postId}`)
              .catch(() => (this.draftPersistLocked = false));
          } else {
            emitter.emit("newPostList", {
              list: Array.isArray(res.data) ? res.data : [],
              total: typeof res.total === "number" ? res.total : undefined,
            });
            void this.$router
              .push("/posts")
              .catch(() => (this.draftPersistLocked = false));
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
    draftUserId() {
      return this.currentUser?.userInfo?.id || "guest";
    },
    newDraftStorageKeys() {
      const userId = this.draftUserId();
      return ["text", "image", "markdown"].map((mode) =>
        this.composeDraftStore.getNewDraftKey(userId, mode)
      );
    },
    draftStorageKey() {
      const userId = this.draftUserId();
      if (this.isEdit && this.postId) {
        return this.composeDraftStore.getEditDraftKey(userId, this.postId);
      }
      return this.composeDraftStore.getNewDraftKey(userId, this.mode);
    },
    currentDraftPayload() {
      return {
        mode: this.mode,
        textContent: this.textContent,
        imageContent: this.imageContent,
        markdownContent: this.markdownContent.content,
        updatedAt: Date.now(),
      };
    },
    hasDraftContent(payload) {
      if (!payload) return false;
      return Boolean(
        payload.textContent?.trim() ||
          payload.imageContent?.trim() ||
          payload.markdownContent?.trim()
      );
    },
    scheduleDraftPersist() {
      if (this.loading || this.submitting || this.draftHydrating) {
        return;
      }
      this.clearDraftPersistTimer();
      this.draftSaveTimer = window.setTimeout(() => {
        this.persistDraft();
      }, 280);
    },
    clearDraftPersistTimer() {
      if (this.draftSaveTimer) {
        window.clearTimeout(this.draftSaveTimer);
        this.draftSaveTimer = null;
      }
    },
    flushDraftPersist() {
      this.clearDraftPersistTimer();
      this.persistDraft();
    },
    persistDraft() {
      if (this.loading || this.submitting || this.draftHydrating) {
        return;
      }
      const payload = this.currentDraftPayload();
      const key = this.draftStorageKey();
      if (!this.hasDraftContent(payload)) {
        this.composeDraftStore.removeDraft(key);
        return;
      }
      if (!this.isEdit) {
        this.newDraftStorageKeys()
          .filter((draftKey) => draftKey !== key)
          .forEach((draftKey) => this.composeDraftStore.removeDraft(draftKey));
      }
      this.composeDraftStore.saveDraft(key, payload);
    },
    restoreNewestNewDraft() {
      let newestDraft = null;
      let newestKey = "";

      this.newDraftStorageKeys().forEach((draftKey) => {
        const draft = this.composeDraftStore.getDraft(draftKey);
        if (!draft) return;
        if (!this.hasDraftContent(draft)) {
          this.composeDraftStore.removeDraft(draftKey);
          return;
        }
        if (
          !newestDraft ||
          (draft.updatedAt || 0) > (newestDraft.updatedAt || 0)
        ) {
          newestDraft = draft;
          newestKey = draftKey;
        }
      });

      return { newestDraft, newestKey };
    },
    restoreDraftIfAvailable() {
      let draft = null;
      let draftKey = this.draftStorageKey();

      if (this.isEdit) {
        draft = this.composeDraftStore.getDraft(draftKey);
        if (!draft) {
          return;
        }
      } else {
        const restored = this.restoreNewestNewDraft();
        draft = restored.newestDraft;
        draftKey = restored.newestKey;
      }

      if (!draft) {
        return;
      }

      try {
        if (!this.hasDraftContent(draft)) {
          this.composeDraftStore.removeDraft(draftKey);
          return;
        }
        this.draftHydrating = true;
        if (!this.isEdit && draft.mode) {
          this.mode = draft.mode;
        }
        this.textContent = draft.textContent || "";
        this.imageContent = draft.imageContent || "";
        this.markdownContent = {
          ...this.markdownContent,
          content: draft.markdownContent || "",
        };
        this.restoredDraftMode = draft.mode || this.mode;
        this.restoredDraftMessage = this.isEdit
          ? "已恢复未保存修改"
          : "已恢复上次草稿";
      } catch {
        this.composeDraftStore.removeDraft(draftKey);
      } finally {
        this.$nextTick(() => {
          this.draftHydrating = false;
        });
      }
    },
    clearDraftStorage() {
      if (this.isEdit) {
        this.composeDraftStore.removeDraft(this.draftStorageKey());
      } else {
        this.newDraftStorageKeys().forEach((draftKey) =>
          this.composeDraftStore.removeDraft(draftKey)
        );
      }
      this.restoredDraftMessage = "";
      this.restoredDraftMode = "";
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
      this.restoredDraftMessage = "";
      this.restoredDraftMode = "";
      this.assistExpanded = false;
    },
  },
};
</script>

<template>
  <PageScroll max-height="calc(100vh - var(--app-header-height))">
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

      <p v-if="visibleRestoredDraftMessage" class="compose-draft-note">
        {{ visibleRestoredDraftMessage }}
      </p>

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
          <div
            class="compose-sheet"
            :class="{
              'compose-sheet-text': mode === 'text',
              'compose-sheet-image': mode === 'image',
              'compose-sheet-markdown': mode === 'markdown',
            }"
          >
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
                :min-height="660"
                :body-init="markdownContent.content"
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
@use "./components/PostReadingTokens.scss" as tokens;

.compose-page {
  box-sizing: border-box;
  width: min(100%, 960px);
  margin: 0 auto;
  padding: 24px 24px 56px;
  color: tokens.$reading-text-primary;
  background: #fff;
  overflow-x: clip;
}

.compose-topbar {
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
  padding-bottom: 12px;
  border-bottom: 1px solid tokens.$reading-border;
}

.compose-back {
  padding: 0;
  border: none;
  background: transparent;
  color: tokens.$reading-text-quaternary;
  font-size: 15px;
  line-height: 1;
  cursor: pointer;
  justify-self: start;
  transition: color 0.2s ease;

  &:hover {
    color: tokens.$reading-text-primary;
  }
}

.compose-status {
  margin: 0;
  font-size: 12px;
  color: tokens.$reading-text-quaternary;
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
  color: tokens.$reading-text-quaternary;
  white-space: nowrap;
}

.compose-submit {
  min-height: 32px;
  padding: 0 14px;
  border-color: tokens.$reading-text-primary;
  border-radius: 999px;
  background: tokens.$reading-text-primary;
  color: #fff;
  font-size: 13px;
  line-height: 1;

  &:hover,
  &:focus,
  &:focus-visible {
    border-color: tokens.$reading-text-primary;
    background: tokens.$reading-text-primary;
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
    border-color: tokens.$reading-border;
    background: transparent;
    color: tokens.$reading-text-quaternary;
  }

  :deep(.el-icon) {
    font-size: 13px;
  }
}

.compose-draft-note {
  margin: -8px 0 20px;
  font-size: 12px;
  color: tokens.$reading-text-tertiary;
  letter-spacing: 0.02em;
}

.compose-shell {
  max-width: 700px;
  margin: 0 auto;
  min-width: 0;
}

.compose-modes {
  display: flex;
  gap: 20px;
  margin-bottom: 26px;
  padding-bottom: 10px;
  border-bottom: 1px solid tokens.$reading-border;
}

.compose-mode {
  padding: 0;
  border: none;
  background: transparent;
  color: tokens.$reading-text-quaternary;
  font-size: 14px;
  letter-spacing: 0.02em;
  cursor: pointer;
  transition: color 0.2s ease;

  &.active {
    color: tokens.$reading-text-primary;
    font-weight: 500;
    text-decoration: underline;
    text-decoration-thickness: 1px;
    text-underline-offset: 10px;
    text-decoration-color: tokens.$reading-text-primary;
  }

  &:hover {
    color: tokens.$reading-text-secondary;
  }
}

.compose-editor {
  margin-bottom: 26px;
  min-height: 620px;
}

.compose-sheet {
  padding: 0 0 10px;
  min-height: 620px;
}

.compose-sheet-text,
.compose-sheet-markdown {
  display: flex;
  flex-direction: column;
}

.compose-sheet-markdown {
  min-height: 660px;
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
  color: tokens.$reading-text-quaternary;
  letter-spacing: 0.04em;
}

.compose-textarea {
  flex: 1 1 auto;

  :deep(.el-textarea__inner) {
    min-height: 460px !important;
    padding: 0;
    border: none;
    border-radius: 0;
    box-shadow: none;
    font-size: tokens.$reading-font-size-body;
    line-height: tokens.$reading-line-height-body;
    color: tokens.$reading-text-primary;
    resize: none;
    background: transparent;
    font-family: tokens.$reading-font-family;
  }

  :deep(.el-textarea .el-input__count) {
    color: tokens.$reading-text-quaternary;
    background: transparent;
  }
}

.compose-insert {
  min-width: 0;
  margin-top: 30px;
  padding-top: 18px;
  border-top: 1px solid tokens.$reading-border-soft;
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
  color: tokens.$reading-text-tertiary;
  letter-spacing: 0.08em;
}

.insert-meta {
  margin: 0;
  font-size: 12px;
  color: tokens.$reading-text-quaternary;
}

.insert-note {
  margin: 0 0 12px;
  font-size: 12px;
  color: tokens.$reading-text-quaternary;
  line-height: 1.6;
}

.upload-trigger {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  color: tokens.$reading-text-secondary;
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
  border: 1px solid tokens.$reading-border;
}

.compose-assist {
  padding-top: 16px;
  border-top: 1px solid tokens.$reading-border-soft;
}

.assist-toggle {
  padding: 0;
  border: none;
  background: transparent;
  color: tokens.$reading-text-secondary;
  font-size: 13px;
  cursor: pointer;
  text-decoration: underline;
  text-decoration-color: transparent;
  text-underline-offset: 4px;
  transition: color 0.2s ease, text-decoration-color 0.2s ease;

  &:hover {
    color: tokens.$reading-text-primary;
    text-decoration-color: tokens.$reading-border;
  }
}

.compose-preview-image {
  width: 100%;
}

:deep(.el-upload--picture-card),
:deep(.el-upload-list--picture-card .el-upload-list__item) {
  box-sizing: border-box;
  border-radius: 0;
  border-color: tokens.$reading-border;
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
  border-color: tokens.$reading-text-primary;
}

@media (max-width: 768px) {
  .compose-page {
    padding: 14px 16px 36px;
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

  .compose-editor,
  .compose-sheet {
    min-height: 500px;
  }

  .compose-sheet-markdown {
    min-height: 560px;
  }

  .compose-textarea {
    :deep(.el-textarea__inner) {
      min-height: 360px !important;
      font-size: 15px;
    }
  }

  :deep(.el-upload-list--picture-card) {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}
</style>
