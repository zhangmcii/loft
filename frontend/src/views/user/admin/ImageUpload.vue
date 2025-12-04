<template>
  <PageHeadBack>
    <div class="container">
      <el-text>选择{{ title }}库图片</el-text>
      <el-text>文件名即为图片名</el-text>
      <el-text>支持webp格式图片</el-text>
      <el-upload ref="uploadRef" v-model:file-list="originalFiles" list-type="picture-card" :auto-upload="false"
        :before-upload="() => false" accept="image/jpeg,image/png,image/jpg,image/webp" :on-change="handleFileChange"
        :on-preview="handlePictureCardPreview" :on-remove="handleFileRemove" :on-exceed="handleExceed" :limit="9"
        multiple>
        <el-icon><i-ep-Plus /></el-icon>
      </el-upload>

      <el-dialog v-model="dialogVisible">
        <img w-full :src="dialogImageUrl" alt="Preview Image" />
      </el-dialog>
    </div>
    <template #action>
      <ButtonClick content="上传" size="small" :disabled="ban_pub" @do-search="submitBlog">
        <el-icon><i-ep-Pointer /></el-icon>
      </ButtonClick>
    </template>
  </PageHeadBack>
</template>

<script>
import PageHeadBack from "@/utils/components/PageHeadBack.vue";
import ButtonClick from "@/utils/components/ButtonClick.vue";
import uploadApi from "@/api/upload/uploadApi.js";

import {
  compressImages,
  uploadFiles,
  beforePicUpload,
} from "@/utils/common.js";

export default {
  name: "BlogPost",
  props: {
    title: {
      type: String,
      default: "背景",
    },
    uploadPath: {
      type: String,
      default: "",
    }
  },
  components: {
    PageHeadBack,
    ButtonClick,
  },
  data() {
    return {
      imageUrls: [],
      uploading: false,
      imageKey: [],

      inputStyle: {
        width: "100%",
        marginBottom: "10px",
        borderColor: "#ffffff",
        boxShadow: "0 0 0 0 #ffffff",
      },
      dialogVisible: false,
      dialogImageUrl: "",
      // 原始文件
      originalFiles: [],
      // 压缩后的文件
      compressedImages: [],
      // 默认压缩比率为80%
      compressedRatio: 80,
    };
  },
  computed: {
    ban_pub() {
      return this.originalFiles.length === 0;
    },
  },

  methods: {
    async getUploadToken() {
      const response = await uploadApi.get_upload_token();
      return response.data.upload_token;
    },
    debounce(func, wait) {
      let timeout;
      return function (...args) {
        const context = this;
        clearTimeout(timeout);
        timeout = setTimeout(() => {
          func.apply(context, args);
        }, wait);
      };
    },
    async handleFileChange(file, fileList) {
      if (!beforePicUpload([file])) {
        return;
      }
      // 确保只添加新的文件
      const newFiles = fileList.filter(
        (f) => !this.originalFiles.some((of) => of.uid === f.uid)
      );
      this.originalFiles = [...this.originalFiles, ...newFiles];
      // console.log('文件列表:', this.originalFiles)
      // 压缩图像
      this.compressedImages = await compressImages(
        this.originalFiles,
        this.compressedImages
      );
    },

    handleFileRemove(file, fileList) {
      // 删除原始文件
      this.originalFiles = this.originalFiles.filter((f) => f.uid !== file.uid);
      // 删除压缩文件
      this.compressedImages = this.compressedImages.filter(
        (img) => img.uid !== file.uid
      );
    },
    async submitBlog() {
      if (this.originalFiles.length === 0) {
        this.$message.error("图片不能为空");
        return;
      }
      if (!beforePicUpload(this.originalFiles)) {
        return;
      }
      const loadingInstance = this.$loading({
        lock: true,
        text: "Loading",
        background: "rgba(0, 0, 0, 0.7)",
      });
      try {
        // 获取上传凭证
        const uploadToken = await this.getUploadToken();
        // 上传图片
        await uploadFiles(
          this.compressedImages,
          this.uploadPath,
          uploadToken
        );
        this.originalFiles = [];
        loadingInstance.close();
        this.$message.success("上传成功");
      } catch (error) {
        loadingInstance.close();
      }
    },
    handlePictureCardPreview(uploadFile) {
      this.dialogImageUrl = uploadFile.url;
      this.dialogVisible = true;
    },
    handleExceed() {
      this.$message.info("最多只能上传9张图片");
    },
  },
};
</script>

<style scoped>
.container {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

:deep(.el-textarea__inner) {
  /* 去掉去除右下角默认小图标 */
  resize: none;
  /* 隐藏滚动条 */
  /* overflow: hidden; */
}

.note {
  padding: 5px;
}

img {
  width: 100%;
}
</style>
