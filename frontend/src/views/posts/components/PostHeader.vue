<script>
import date from '@/utils/date.js'
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
  mounted() {},
  computed: {
    from_now() {
      return date.dateShow(this.post.timestamp)
    }
  },
  methods: {}
}
</script>

<template>
  <el-row class="head" justify="space-between" align="middle">
    <div class="head-name">
      <el-avatar alt="用户图像" :src="post.image" @click.stop="$router.push(`/user/${post.author}`)" />
      <el-text @click.stop="$router.push(`/user/${post.author}`)">{{
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