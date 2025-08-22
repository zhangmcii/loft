<script>
import commentApi from '@/api/comment/commentApi.js'
import PostCard from '../posts/PostCard.vue'
import { useCurrentUserStore } from '@/stores/user'
import PageHeadBack from '@/utils/components/PageHeadBack.vue'
import SkeletonUtil from '@/utils/components/SkeletonUtil.vue'
export default {
  components: {
    PostCard,
    PageHeadBack,
    SkeletonUtil
  },
  data() {
    return {
      comments: [],
      currentPage: 1,
      comments_count: 0,
      loading: {
        comment: false
      }
    }
  },
  setup() {
    const currentUser = useCurrentUserStore()
    return { currentUser }
  },
  computed: {
    isCommentManage() {
      return this.currentUser.userInfo.roleId >= 2
    }
  },
  mounted() {
    this.getAllComments()
  },
  methods: {
    getAllComments(page = 1) {
      this.loading.comment = true
      commentApi.getAllComments(page).then((res) => {
        if (res.code === 200) {
          this.comments = res.data
          if (res.total !== undefined) {
            this.comments_count = res.total
          }
          this.loading.comment = false
        }
      })
    },
    handleCurrentChange() {
      this.getAllComments(this.currentPage)
    },
    disabled(item) {
      commentApi.disable(item.id).then((res) => {
        if (res.code == 200) {
          this.comments = res.data
          this.$message.warning('已禁用')
        }
      })
    },
    enable(item) {
      commentApi.enable(item.id).then((res) => {
        if (res.code == 200) {
          this.comments = res.data
          this.$message.success('已开启')
        }
      })
    }
  }
}
</script>

<template>
  <PageHeadBack>
    <SkeletonUtil :loading="loading.comment" :row="7" :count="4" :cardStyle="{ marginBottom: '10px' }">
      <PostCard v-for="item in comments" :key="item" :post="item" :cardStyle="{ marginBottom: '10px' }"
        :showEdit="false" :showShare="false" :showComment="false" :showPraise="false">
        <el-row v-if="isCommentManage">
          <el-button @click="enable(item)" v-if="item.disabled">开启</el-button>
          <el-button type="danger" @click="disabled(item)" v-else>禁用</el-button>
        </el-row>
      </PostCard>
    </SkeletonUtil>
    <el-pagination v-model:current-page="currentPage" :page-size="10" layout="total, prev, pager, next"
      :total="comments_count" @current-change="handleCurrentChange" :hide-on-single-page="true" :pager-count="5" />
  </PageHeadBack>
</template>
<style scoped></style>
