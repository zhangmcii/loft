<template>
  <PageHeadBack>
    <div class="container">
      <el-text>选择公共背景库图片</el-text>
      <el-text>文件名即为图片名</el-text>
      <el-text>支持webp格式图片</el-text>
      <el-upload
        ref="uploadRef"
        v-model:file-list="originalFiles"
        list-type="picture-card"
        :auto-upload="false"
        :before-upload="() => false"
        accept="image/jpeg,image/png,image/jpg,image/webp"
        :on-change="handleFileChange"
        :on-preview="handlePictureCardPreview"
        :on-remove="handleFileRemove"
        :on-exceed="handleExceed"
        :limit="9"
        multiple
      >
        <el-icon><i-ep-Plus /></el-icon>
      </el-upload>

      <el-dialog v-model="dialogVisible">
        <img w-full :src="dialogImageUrl" alt="Preview Image" />
      </el-dialog>
      <!-- <div class="note">
        <el-text size="small">(图文 每日发布次数限定2次)</el-text>
      </div> -->
    </div>
    <template #action>
      <ButtonClick content="发布" size="small" :disabled="ban_pub" @do-search="submitBlog">
        <el-icon><i-ep-Pointer /></el-icon>
      </ButtonClick>
    </template>
  </PageHeadBack>
</template>

<script>
import PageHeadBack from '@/utils/components/PageHeadBack.vue'
import ButtonClick from '@/utils/components/ButtonClick.vue'
import { useCurrentUserStore } from '@/stores/user'
import uploadApi from '@/api/upload/uploadApi.js'
import * as qiniu from 'qiniu-js'
import lrz from 'lrz'

export default {
  name: 'BlogPost',
  props: {},
  components: {
    PageHeadBack,
    ButtonClick
  },
  data() {
    return {
      uploadToken: '',
      imageUrls: [],
      uploading: false,
      imageKey: [],

      inputStyle: {
        width: '100%',
        marginBottom: '10px',
        borderColor: '#ffffff',
        boxShadow: '0 0 0 0 #ffffff'
      },
      dialogVisible: false,
      dialogImageUrl: '',
      // 原始文件
      originalFiles: [],
      // 压缩后的文件
      compressedImages: [],
      // 默认压缩比率为80%
      compressedRatio: 80
    }
  },
  setup() {
    const currentUser = useCurrentUserStore()
    return { currentUser }
  },
  computed: {
    ban_pub() {
      return this.originalFiles.length === 0
    }
  },
  created() {
    this.debounceCompress = this.debounce(this.compressImages, 100)
  },
  mounted() {
    this.getUploadToken()
  },
  methods: {
    async getUploadToken() {
      const response = await uploadApi.get_upload_token()
      this.uploadToken = response.data.upload_token
    },
    debounce(func, wait) {
      let timeout
      return function (...args) {
        const context = this
        clearTimeout(timeout)
        timeout = setTimeout(() => {
          func.apply(context, args)
        }, wait)
      }
    },
    handleFileChange(file, fileList) {
      if (!this.beforePicUpload([file])) {
        return
      }
      // 确保只添加新的文件
      const newFiles = fileList.filter((f) => !this.originalFiles.some((of) => of.uid === f.uid))
      this.originalFiles = [...this.originalFiles, ...newFiles]
      // console.log('文件列表:', this.originalFiles)
      this.debounceCompress()
    },

    async compressImages() {
      const compressionRatio = this.compressedRatio / 100

      // 找出未压缩的文件
      const uncompressedFiles = this.originalFiles.filter(
        (file) => !this.compressedImages.some((img) => img.uid === file.uid)
      )

      for (const file of uncompressedFiles) {
        const rawFile = file.raw
        const compressedFile = await lrz(rawFile, { quality: compressionRatio })

        console.log('压缩后的文件:', compressedFile)
        console.log(`压缩后大小: ${(compressedFile.file.size / 1024).toFixed(2)} KB`)

        // 将 base64 转换为 Blob
        const byteString = atob(compressedFile.base64.split(',')[1])
        const mimeString = compressedFile.base64.split(',')[0].split(':')[1].split(';')[0]
        const arrayBuffer = new ArrayBuffer(byteString.length)
        const uintArray = new Uint8Array(arrayBuffer)
        for (let i = 0; i < byteString.length; i++) {
          uintArray[i] = byteString.charCodeAt(i)
        }
        const blob = new Blob([arrayBuffer], { type: mimeString })

        this.compressedImages.push({
          src: compressedFile.base64,
          blob, // 保存 Blob 对象
          name: rawFile.name,
          uid: rawFile.uid,
          sizeInfo: `压缩后大小: ${(compressedFile.file.size / 1024).toFixed(2)} KB`
        })
      }
    },
    handleFileRemove(file, fileList) {
      // 删除原始文件
      this.originalFiles = this.originalFiles.filter((f) => f.uid !== file.uid)
      // 删除压缩文件
      this.compressedImages = this.compressedImages.filter((img) => img.uid !== file.uid)

      // console.log('文件已删除:', file.name)
      // console.log('当前原始文件列表:', this.originalFiles)
      // console.log('当前压缩文件列表:', this.compressedImages)
    },
    beforePicUpload(fileList) {
      for (const file of fileList) {
        const isImage = file.raw.type.startsWith('image/')
        if (!isImage) {
          this.$message.error('只能上传图片格式文件！')
          return false
        }
        const limitPic =
          file.raw.type === 'image/png' ||
          file.raw.type === 'image/jpg' ||
          file.raw.type === 'image/jpeg' ||
          file.raw.type === 'image/webp'
        if (!limitPic) {
          this.$message.warning('请上传格式为png/jpg/jpeg/webp的图片')
          return false
        }
      }
      return true
    },
    async uploadFiles() {
      const domin = import.meta.env.VITE_QINIU_DOMAIN
      this.uploading = true
      try {
        const putExtra = {}
        const config = {
          // 存储区域
          region: qiniu.region.z0
        }
        for (const file of this.compressedImages) {
          const folder = this.currentUser.uploadBackgroundStatic
          console.log('uniqueFileName', file.name)
          const key = folder + file.name
          console.log('key', key)
          //   const observable = qiniu.upload(file.blob, key, this.uploadToken, putExtra, config)
          //   await new Promise((resolve, reject) => {
          //     // 保存 this 上下文
          //     const self = this
          //     observable.subscribe({
          //       next() {},
          //       error(err) {
          //         reject(err)
          //       },
          //       complete(res) {
          //         self.imageKey.push(res.key)
          //         const imageUrl = `http://${domin}/${res.key}`
          //         self.imageUrls.push(imageUrl)
          //         resolve()
          //       }
          //     })
          //   })
        }
      } catch (error) {
        console.error('Upload failed:', error)
      } finally {
        this.uploading = false
      }
    },
    async submitBlog() {
      if (this.originalFiles.length === 0) {
        this.$message.error('图片不能为空')
        return
      }
      if (!this.beforePicUpload(this.originalFiles)) {
        return
      }
      const loadingInstance = this.$loading({
        lock: true,
        text: 'Loading',
        background: 'rgba(0, 0, 0, 0.7)'
      })
      try {
        await this.uploadFiles()
      } catch (error) {
        loadingInstance.close()
      }
    },
    handlePictureCardPreview(uploadFile) {
      this.dialogImageUrl = uploadFile.url
      this.dialogVisible = true
    },
    handleExceed() {
      this.$message.info('最多只能上传9张图片')
    }
  }
}
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
