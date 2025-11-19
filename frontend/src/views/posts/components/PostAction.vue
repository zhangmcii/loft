<script>
import { useCurrentUserStore } from "@/stores/user";
import { loginReminder } from "@/utils/common.js";
import { showConfirmDialog } from "vant";
import { copy } from "@/utils/common.js";
import praise from "@/api/praise/praiseApi.js";
import postApi from "@/api/posts/postApi.js";

export default {
  props: {
    post: {
      type: Object,
      default() {
        return {
          id: 1,
          body: "文章",
          body_html: null,
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
    showShare: {
      type: Boolean,
      default: false,
    },
    showEdit: {
      type: Boolean,
      default: false,
    },
    showDelete: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      iconSize: 15,
      praiseNum: 0,
      hasPraised: false,
      show: false,
      shareOptions: [
        { name: "微信", icon: "wechat" },
        { name: "朋友圈", icon: "wechat-moments" },
        { name: "微博", icon: "weibo" },
        { name: "QQ", icon: "qq" },
        { name: "复制链接", icon: "link" },
      ],
    };
  },
  setup() {
    const currentUser = useCurrentUserStore();
    return { currentUser };
  },
  mounted() {},
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
    isUserRoute() {
      return this.$route.path.startsWith("/user");
    },
  },
  methods: {
    comment() {
      this.$router.push(`/postDetail/${this.post.id}`);
    },
    praise() {
      if (!this.currentUser.isLogin) {
        loginReminder("快去登录再点赞吧");
        return;
      }
      praise.submitPraise(this.post.id).then((res) => {
        if (res.code == 200) {
          this.praiseNum = res.data.praise_total;
          this.hasPraised = res.data.has_praised;
        } else {
          this.$message.error(res.data.detail);
        }
      });
    },
    edit() {
      this.$router.push(`/editPost/${this.post.id}`);
    },
    shareSelect(option) {
      if (option.name === "复制链接") {
        copy(`${import.meta.env.VITE_DOMIN}/postDetail/${this.post.id}`);
      } else {
        this.$message.info(option.name);
      }
      this.show = false;
    },

    deletePost() {
      showConfirmDialog({
        title: "确定删除这篇文章吗？",
        width: 230,
        beforeClose: this.beforeDelete,
      });
    },

    beforeDelete(action) {
      if (action !== "confirm") {
        return Promise.resolve(true);
      } else {
        return postApi.deletePost(this.post.id).then((res) => {
          if (res.code === 200) {
            this.$message.success("文章删除成功");
            // 跳转到首页或文章列表页
            this.$router.push("/");
          } else {
            this.$message.error(res.message || "删除文章失败");
          }
          return res;
        });
      }
    },
  },
};
</script>

<template>
  {{ post.id }}
  <div class="post-action-container">
    <div class="action-left">
      <div
        class="action-item"
        v-if="
          showEdit &&
          (post.author == currentUser.userInfo.username || currentUser.isAdmin)
        "
      >
        <van-icon
          name="edit"
          @click.stop="edit"
          :size="iconSize"
          class="action-icon"
        />
      </div>

      <div class="action-item" v-if="showDelete && currentUser.isAdmin">
        <van-icon
          name="delete-o"
          @click.stop="deletePost"
          :size="iconSize"
          color="#f56c6c"
          class="action-icon delete-icon"
          title="删除文章"
        />
      </div>
      <div class="action-item" v-if="showShare && !isUserRoute">
        <van-icon
          name="share-o"
          @click.stop="show = !show"
          :size="iconSize"
          class="action-icon"
        />
      </div>
    </div>

    <div class="action-right">
      <div class="action-item comment">
        <van-icon
          name="notes-o"
          @click.stop="comment"
          :size="iconSize"
          class="action-icon"
        />
        <span class="action-count">{{ post.comment_count }}</span>
      </div>

      <div class="action-item like">
        <transition :name="hasPraised ? 'praise' : ''" mode="out-in">
          <van-icon
            name="good-job"
            @click.stop=""
            :size="iconSize"
            v-if="hasPraised"
            key="praised"
            class="action-icon praised"
          />
          <van-icon
            name="good-job-o"
            @click.stop="praise"
            :size="iconSize"
            v-else
            key="unPraise"
            class="action-icon"
          />
        </transition>
        <span class="action-count">{{ praiseNum }}</span>
      </div>
    </div>
  </div>

  <van-share-sheet
    v-model:show="show"
    title="立即分享给好友"
    :options="shareOptions"
    @select="shareSelect"
  />
</template>

<style scoped lang="scss">
.post-action-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  width: 100%;
}

.action-left,
.action-right {
  display: flex;
  align-items: center;
}

.action-item {
  display: flex;
  align-items: center;
  margin-right: 16px;
  cursor: pointer;

  &:last-child {
    margin-right: 0;
  }
}

.action-icon {
  margin-right: 4px;
  transition: all 0.2s ease;

  &:hover {
    transform: scale(1.1);
  }

  &.delete-icon:hover {
    transform: scale(1.2);
    filter: brightness(1.1);
  }

  // &.praised {
  //   color: #ff6b6b;
  // }
}

.action-count {
  font-size: 14px;
  color: #666;
}

.praise-enter-active,
.praise-leave-active {
  transition: all 0.3s ease;
}

.praise-enter-from,
.praise-leave-to {
  opacity: 0;
  transform: scale(0.5);
}

@media (max-width: 768px) {
  .post-action-container {
    padding: 6px 0;
  }

  .action-item {
    margin-right: 12px;
  }
}
</style>
