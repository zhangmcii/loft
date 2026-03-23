<template>
  <div
    class="markdown-editor"
    :style="{ '--markdown-min-height': editorMinHeight }"
  >
    <mavon-editor
      ref="mavonEditor"
      v-model="markdown"
      :autofocus="false"
      @imgAdd="handleImageUpload"
      @change="change"
    />
  </div>
</template>

<script>
import MarkdownIt from "markdown-it";
import { useCurrentUserStore } from "@/stores/user";
import {
  compressImages,
  uploadFiles,
  beforePicUpload,
} from "@/utils/common.js";
import uploadApi from "@/api/upload/uploadApi.js";
import { v4 as uuidv4 } from "uuid";
import { mavonEditor } from "mavon-editor";
import "mavon-editor/dist/css/index.css";

export default {
  name: "MarkdownEditor",
  props: {
    bodyInit: {
      type: String,
      default: () => "",
    },
    bodyHtmlInit: {
      type: String,
      default: () => "",
    },
    minHeight: {
      type: Number,
      default: 620,
    },
  },
  components: {
    mavonEditor,
  },
  data() {
    return {
      markdown: "",
      md: new MarkdownIt(),

      imageUrls: [],
      imageKey: [],

      // 原始文件
      originalFiles: [],
      // 压缩后的文件
      compressedImages: [],
    };
  },
  setup() {
    const currentUser = useCurrentUserStore();
    return { currentUser };
  },
  mounted() {
    this.markdown = this.bodyInit || "";
  },
  computed: {
    editorMinHeight() {
      return `${this.minHeight}px`;
    },
  },
  methods: {
    async handleImageUpload(pos, file) {
      // 包装成 el-upload 格式
      const uid = uuidv4();
      file.uid = uid;
      file.pos = pos;
      const uploadFile = {
        name: file.name,
        uid: uid,
        status: "ready",
        raw: file,
      };
      if (!beforePicUpload([uploadFile])) {
        return;
      }
      this.originalFiles = [...this.originalFiles, uploadFile];
      // 压缩图片
      this.compressedImages = await compressImages(
        this.originalFiles,
        this.compressedImages
      );
    },

    async uploadPhotos() {
      if (!this.compressedImages.length) {
        return [];
      }
      if (!beforePicUpload(this.originalFiles)) {
        return [];
      }

      // 获取上传凭证
      const uploadToken = await this.getUploadToken();
      // 上传图片
      const { imageKey, imageUrls } = await uploadFiles(
        this.compressedImages,
        this.currentUser.uploadMarkdownBaseUrl,
        uploadToken
      );
      this.imageKey = imageKey;
      this.imageUrls = imageUrls;
      console.log("imageKey", this.imageKey);
      // imageKey[{url:'', pos:''},{url:'', pos:''}]
      return this.imageKey;
    },
    change(value) {
      this.$emit("contentChange", {
        content: value,
      });
    },
    clean() {
      this.markdown = "";
    },
    async getUploadToken() {
      const response = await uploadApi.get_upload_token();
      return response.data.upload_token;
    },
  },
};
</script>

<style scoped lang="scss">
@use "@/views/posts/components/PostReadingTokens.scss" as tokens;

.markdown-editor {
  min-height: var(--markdown-min-height);

  :deep(.v-note-wrapper) {
    min-height: var(--markdown-min-height);
    border: 1px solid tokens.$reading-border;
    border-radius: 0;
    box-shadow: none;
  }

  :deep(.v-note-op) {
    background: tokens.$reading-fill-softer;
    border-bottom: 1px solid tokens.$reading-border;
  }

  :deep(.v-note-panel) {
    min-height: calc(var(--markdown-min-height) - 48px);
  }

  :deep(.v-note-edit.divarea-wrapper),
  :deep(.v-note-show) {
    min-height: calc(var(--markdown-min-height) - 48px);
  }

  :deep(.content-input),
  :deep(.v-show-content) {
    min-height: calc(var(--markdown-min-height) - 80px);
    font-family: tokens.$reading-font-family;
    font-size: tokens.$reading-font-size-body;
    line-height: tokens.$reading-line-height-body;
    color: tokens.$reading-text-primary;
  }

  :deep(.content-input) {
    padding: 18px 20px;
  }

  :deep(.v-show-content) {
    padding: 18px 20px;
  }
}

@media (max-width: 768px) {
  .markdown-editor {
    min-height: min(var(--markdown-min-height), 560px);

    :deep(.v-note-wrapper) {
      min-height: min(var(--markdown-min-height), 560px);
    }

    :deep(.v-note-panel),
    :deep(.v-note-edit.divarea-wrapper),
    :deep(.v-note-show) {
      min-height: 500px;
    }

    :deep(.content-input),
    :deep(.v-show-content) {
      min-height: 420px;
      font-size: 15px;
    }
  }
}
</style>
