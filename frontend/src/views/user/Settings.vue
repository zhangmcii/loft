<template>
  <PageHeadBack>
    <div class="settings-content">
      <!-- 账户设置 -->
      <div class="cell-group">
        <van-cell
          title="修改密码"
          icon="lock"
          is-link
          @click="goTo('/changePassword')"
        />
        <van-cell
          v-if="currentUser.isConfirmed"
          title="修改邮箱"
          icon="envelop-o"
          is-link
          @click="goTo('/changeEmail')"
        />
        <van-cell
          v-else
          title="绑定邮箱"
          icon="envelop-o"
          is-link
          @click="goTo('/bindEmail')"
        />
      </div>

      <!-- 管理员设置 -->
      <div v-if="currentUser.isCommentManage" class="cell-group">
        <van-cell
          title="评论管理"
          icon="chat-o"
          is-link
          @click="goTo('/commentManagement')"
        />
        <van-cell
          title="标签管理"
          icon="medal-o"
          is-link
          @click="goTo('/tag')"
        />
        <van-cell
          title="操作日志"
          icon="shield-o"
          is-link
          @click="goTo('/operateLog')"
        />
        <van-cell
          title="管理背景库"
          icon="photo-o"
          is-link
          @click="goTo('/uploadBg')"
        />
        <van-cell
          title="管理图像库"
          icon="user-o"
          is-link
          @click="goTo('/uploadAva')"
        />
        <van-cell
          title="找回其他用户密码"
          icon="warning-o"
          is-link
          @click="goTo('/PasswordChangeAdmin')"
        />
      </div>

      <!-- 通用设置 -->
      <div class="cell-group">
        <van-cell title="主题" icon="setting-o" is-link />
        <van-cell title="语言" icon="gem-o" is-link />
      </div>

      <!-- 其他设置 -->
      <div class="cell-group">
        <van-cell title="关于" icon="info-o" is-link />
        <van-cell title="意见反馈" icon="question-o" is-link />
      </div>

      <div class="logout-button">
        <el-button type="danger" @click="handleLogout">退出登录</el-button>
      </div>
    </div>
  </PageHeadBack>
</template>

<script>
import PageHeadBack from "@/utils/components/PageHeadBack.vue";
import { useCurrentUserStore } from "@/stores/user";
import { showConfirmDialog } from "vant";
import authApi from "@/api/auth/authApi.js";

export default {
  name: "Settings",
  components: {
    PageHeadBack,
  },
  setup() {
    const currentUser = useCurrentUserStore();
    return { currentUser };
  },
  methods: {
    goTo(route) {
      this.$router.push(route);
    },
    handleLogout() {
      showConfirmDialog({
        title: "提示",
        message: "是否退出登录？",
        width: "280px",
        beforeClose: this.beforeClose,
      });
    },
    beforeClose(action) {
      if (action !== "confirm") {
        return Promise.resolve(true);
      } else {
        this.currentUser.disconnectSocket();
        return Promise.all([
          authApi.revokeToken("access_token"),
          authApi.revokeToken("refresh_token"),
        ])
          .then((res) => {
            this.currentUser.logOut();
            this.$router.push("/posts");
            return res;
          })
          .catch((err) => {
            console.error("撤销令牌失败:", err);
            this.currentUser.logOut();
            this.$router.push("/posts");
            return err;
          });
      }
    },
  },
};
</script>

<style scoped>
.settings-content {
  padding: 12px;
}

.cell-group {
  margin-bottom: 16px;
}

.logout-button {
  margin-top: 24px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}
.el-button {
  width: 92%;
}
</style>
