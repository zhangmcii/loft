<!-- 这个组件只用作首页文章预览 。可以不用加上PostCard中复杂的逻辑
 prop只接受文章的json
-->
<script>
import PostAction from "@/views/posts/components/PostAction.vue";
import PostHeader from "@/views/posts/components/PostHeader.vue";
import PostContent from "@/views/posts/components/PostContent.vue";

export default {
  props: {
    post: {
      type: Object,
      default() {
        return {
          id: 1,
          content: "文章",
          post_type: "text",
          timestamp: "",
          author: "张三",
          nick_name: "",
          commentCount: 20,
          disabled: false,
          image: "",
          comment_count: 0,
          praise_num: 0,
          has_praised: false,
          post_images: [],
        };
      },
    },
    // 整个容器样式
    containerStyle: {
      type: Object,
      default() {
        return {};
      },
    },
  },
  components: {
    PostAction,
    PostHeader,
    PostContent,
  },
  data() {
    return {
      iconSize: 15,
      praiseNum: 0,
      hasPraised: false,
    };
  },
  watch: {
    "post.praise_num": {
      handler(newValue) {
        this.praiseNum = newValue;
      },
      immediate: true,
    },
    "post.has_praised": {
      handler(newValue) {
        this.hasPraised = newValue;
      },
      immediate: true,
    },
  },
  computed: {
    plainSummaryLength() {
      const summary = this.post?.summary || "";
      const plainText = summary
        .replace(/<br\s*\/?>/gi, "\n")
        .replace(/<[^>]+>/g, "")
        .replace(/\s+/g, " ")
        .trim();
      return plainText.length;
    },
    isShortPost() {
      return this.plainSummaryLength > 0 && this.plainSummaryLength <= 28;
    },
  },
};
</script>

<template>
  <div
    class="post-card"
    :class="{ 'post-card-short': isShortPost }"
    :style="containerStyle"
  >
    <PostHeader :post="post" :compact="isShortPost" />
    <PostContent
      :postContent="post.summary"
      :preview="true"
      :preview-type="post.post_type"
      :fontSize="isShortPost ? 18 : 16"
      :compact="isShortPost"
      :force-truncation-indicator="Boolean(post.has_more)"
    />
    <slot name="image"></slot>

    <PostAction :post="post" :compact="isShortPost" />

    <div class="block"></div>
  </div>
</template>
<style lang="scss" scoped>
@use "./PostCard.scss" as *;
</style>
