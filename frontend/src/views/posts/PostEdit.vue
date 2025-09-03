<script>
import postApi from "@/api/posts/postApi.js";
import ButtonClick from "@/utils/components/ButtonClick.vue";
import PageHeadBack from "@/utils/components/PageHeadBack.vue";
import MarkdownEditor from "@/utils/components/MarkdownEditor.vue";

export default {
  components: {
    ButtonClick,
    PageHeadBack,
    MarkdownEditor,
  },
  data() {
    return {
      post: {},
      postId: -1,
      richContent: {
        body: "",
        bodyHtml: "",
        images: [],
      },
      originalPost: "",
      isChange: false,
      loading: false,
      activeRichEditor: false,
    };
  },
  beforeRouteEnter(to, from, next) {
    next((vm) => {
      vm.postId = to.params.id;
      vm.getPostById(vm.postId);
      vm.$nextTick(() => {});
    });
  },
  watch: {
    "post.body"(newVal) {
      this.isChange = newVal !== this.originalPost;
    },
    "richContent.body"(newVal) {
      this.isChange = newVal !== this.originalPost;
    },
  },
  methods: {
    getPostById(postId) {
      postApi.getPost(postId).then((res) => {
        if (res.code == 200) {
          this.originalPost = res.data.body;
          this.post = res.data;
          if (this.post.body_html) {
            this.activeRichEditor = true;
          }
        }
      });
    },
    normalModify() {
      this.loading = true;
      postApi
        .editPost(this.post.id, { body: this.post.body, bodyHtml: null })
        .then((res) => {
          if (res.code == 200) {
            this.loading = false;
            this.$message.success("修改成功");
            this.$router.push(`/postDetail/${this.postId}`);
          } else {
            this.loading = false;
            this.$message.success("修改失败");
          }
        });
    },
    async richEditorModify() {
      this.loading = true;
      const images = await this.$refs.md.uploadPhotos();
      this.richContent.images = images;
      postApi.editPost(this.post.id, this.richContent).then((res) => {
        if (res.code == 200) {
          this.loading = false;
          this.$message.success("修改成功");
          this.post.body = this.richContent.body;
          this.post.body_html = this.richContent.bodyHtml;
          this.$router.push(`/postDetail/${this.postId}`);
        } else {
          this.loading = false;
          this.$message.success("修改失败");
        }
      });
    },
    modify() {
      if (this.activeRichEditor) {
        this.richEditorModify();
      } else {
        this.normalModify();
      }
    },
  },
};
</script>

<template>
  <PageHeadBack>
    <h1>编辑</h1>
    <h4>你在想什么？</h4>
    <MarkdownEditor
      ref="md"
      v-if="activeRichEditor"
      :bodyInit="post.body"
      @contentChange="(n) => (richContent = n)"
    />
    <el-input
      v-else
      v-model="post.body"
      :autosize="{ minRows: 2, maxRows: 4 }"
      type="textarea"
      placeholder="发你所想"
    />
    <ButtonClick
      content="修改"
      :loading="loading"
      :disabled="!isChange"
      @do-search="modify"
    />
  </PageHeadBack>
</template>
<style scoped>
.el-button {
  margin-top: 10px;
}
.el-switch {
  margin-top: 10px;
  float: right;
}
</style>
