<script>
import date from '@/utils/date.js'
import { useOtherUserStore } from '@/stores/otherUser'
export default {
  props: {
    post: {
      type: Object,
      default() {
        return {
          id: 1,
          body: '',
          body_html: null,
          timestamp: '',
          author: '--',
          nick_name: '',
          user_id: 1,
          commentCount: 20,
          disabled: false,
          image: '',
          comment_count: 0,
          praise_num: 0,
          has_praised: false,
          post_images: []
        }
      }
    }
  },
  data() {
    return {}
  },
   setup() {
      const otherUser = useOtherUserStore()
      return { otherUser }
    },
  mounted() {},
  computed: {
    from_now() {
      return date.dateShow(this.post.timestamp)
    }
  },
  methods: {
    toUser() {
      // 接口都已改为根据用户id获取用户数据
      this.otherUser.userInfo.id = this.post.user_id
      this.$router.push(`/user/${this.post.author}`)
    }
  }
}
</script>

<template>
  <el-row class="head" justify="space-between" align="middle">
    <div class="head-name">
      <el-avatar alt="用户图像" :src="post.image" @click.stop="toUser" />
      <el-text @click.stop="toUser">{{
        post.nick_name ? post.nick_name : post.author
      }}</el-text>
    </div>
    <div>
      <el-text size="small" class="head-time">{{ from_now }}</el-text>
    </div>
  </el-row>
</template>
<style lang="scss" scoped>
.head {
  height: 40px;
  margin: 0px 0px 10px 0px;
}
.head-name {
  display: flex;
  align-items: center;
  .el-text {
    margin-left: 5px;
    font-size: 13px;
  }
}
.head-time {
  margin-right: 1px;
}
</style>