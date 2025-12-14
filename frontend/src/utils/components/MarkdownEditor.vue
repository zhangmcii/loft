<template>
  <div class="markdown-editor">
    <mavon-editor
      ref="mavonEditor"
      v-model="markdown"
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
import { mavonEditor } from 'mavon-editor';
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
  },
  components:{
    mavonEditor
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
      if (!beforePicUpload(this.originalFiles)) {
        return;
      }
      // 上传至七牛云
      // await this.uploadFiles()

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
        body: value,
        bodyHtml: value,
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

<style scoped></style>
