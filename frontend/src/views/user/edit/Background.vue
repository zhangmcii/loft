<script setup>
import PageHeadBack from '@/utils/components/PageHeadBack.vue'
import { ref, reactive, onMounted, nextTick } from 'vue'
import imageApi from '@/api/user/imageApi.js'
import editApi from '@/api/user/editApi.js'
import { useRouter } from 'vue-router'
import { ElMessage, ElLoading } from 'element-plus'
import { useCurrentUserStore } from '@/stores/user'
import { useChange } from '@/utils/composedFunc/change.js'

const currentUser = useCurrentUserStore()
const router = useRouter()

let images = ref([])
const active = ref('图片壁纸')
const radio = ref(currentUser.userInfo.bg_image)

const { isChange } = useChange(radio)
// 分页
const query = reactive({
  currentPage: 1, // 当前页数
  size: 6, // 页大小
  total: 10 // 评论总数
})
onMounted(() => {
  getBackgroundImage()
})

function getBackgroundImage() {
  imageApi.getBackgroundImage(query.currentPage, query.size).then((res) => {
    if (res.code == 200) {
      images.value = [...res.data]
      query.total = res.total
    }
  })
}

function handleCurrentChange() {
  getBackgroundImage()
}

function redefault() {
  const loading = ElLoading.service({
    lock: true,
    text: '正在保存',
    background: 'rgba(0, 0, 0, 0.7)'
  })
  setTimeout(() => {
    loading.close()
    // 恢复默认
  }, 800)
}
async function submitdata() {
  if (!radio.value) {
    ElMessage.warning('请选择壁纸')
    return
  }
  const loading = ElLoading.service({
    lock: true,
    text: '正在保存',
    background: 'rgba(0, 0, 0, 0.7)'
  })
  // 至少加载1s
  const startTime = Date.now()
  // 保存url
  await editApi.editUser({ bg_image: radio.value })
  currentUser.userInfo = { ...currentUser.userInfo, bg_image: radio.value }
  const elapsedTime = Date.now() - startTime
  const delayTime = Math.max(0, 1000 - elapsedTime)
  setTimeout(() => {
    loading.close()
    // 回到用户资料页
    router.push(`/user/${currentUser.userInfo.username}`)
  }, delayTime)
}
</script>

<template>
  <PageHeadBack>
    <van-tabs v-model:active="active" animated>
      <van-tab title="图片壁纸" class="tab">
        <!-- 图片 -->
        <el-text class="title">请选择壁纸</el-text>
        <el-radio-group v-model="radio">
          <div class="scroll-container">
            <el-row>
              <el-col :span="12" v-for="item in images" :key="item">
                <el-image
                  :src="item"
                  fit="cover"
                  :class="{ 'selected-item': radio === item }"
                  loading="lazy"
                  @click="radio = item"
                >
                  <template #placeholder>
                    <div class="img-loading">
                      <el-icon><i-ep-Loading /></el-icon>
                    </div>
                  </template>
                </el-image>
              </el-col>
            </el-row>
          </div>
        </el-radio-group>
        <!-- 分页 -->
        <el-pagination
          v-model:current-page="query.currentPage"
          layout="prev, pager, next"
          :page-size="query.size"
          :total="query.total"
          @current-change="handleCurrentChange"
        />
      </van-tab>
      <!-- <van-tab title="动态壁纸">
        <el-text>请选择壁纸</el-text>
        <div class="scroll-container">
          <el-row>
            <el-col>
              <el-text>尽请期待</el-text>
            </el-col>
          </el-row>
        </div>
      </van-tab> -->
    </van-tabs>
    <!-- 按钮区 -->
    <div class="btn-bar">
      <el-button type="info" @click="redefault">恢复</el-button>
      <el-button type="primary" :disabled="!radio || !isChange" @click="submitdata">确认</el-button>
    </div>
  </PageHeadBack>
</template>
<style lang="scss" scoped>
:deep(.van-tab__panel) {
  padding: 10px;
}
.title {
  margin-left: 10%;
}
.scroll-container {
  max-height: 300px;
  overflow-y: auto;
}

/* 覆盖全局的滚动条样式 */
.scroll-container::-webkit-scrollbar {
  width: 5px; /* 设置滚动条宽度 */
}

.scroll-container::-webkit-scrollbar-thumb {
  background-color: #888; /* 设置滚动条颜色 */
  border-radius: 4px; /* 设置滚动条圆角 */
}
.el-image {
  max-width: 100px;
  max-height: 170px;
  border-radius: 5%;
}
.img-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100px;
}
.el-col {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 12px;
}
.el-pagination {
  // 水平居中
  display: flex;
  justify-content: center;
}
.selected-item {
  /* 选中时的边框颜色 */
  border-color: rgb(206, 160, 160);
  /* 选中时的阴影 */
  box-shadow: 0 0 10px #e11111;
}

.btn-bar {
  display: flex;
  justify-content: center;
  margin-top: 24px;
  gap: 16px;
}
.snackbar {
  position: fixed;
  top: 24px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 9999;
  min-width: 180px;
}
</style>
