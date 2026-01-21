<script>
import axios from "axios";
import { useCurrentUserStore } from "@/stores/user";

export default {
  setup() {
    const currentUser = useCurrentUserStore();
    return { currentUser };
  },
  mounted() {
    this.handleGitHubCallback();
  },
  methods: {
    async handleGitHubCallback() {
      try {
        // 从 URL 查询参数获取 code
        const urlParams = new URLSearchParams(window.location.search);
        const code = urlParams.get("code");
        const state = urlParams.get("state");

        if (!code) {
          ElMessage.error("授权失败: 缺少授权码");
          this.$router.push("/login");
          return;
        }

        // 调用后端回调接口处理登录
        const callbackUrl = `/auth/bp/github/callback?code=${code}&state=${
          state || "github_auth"
        }`;

        // 使用 axios 发送请求
        const response = await axios.get(callbackUrl, {
          baseURL: import.meta.env.VITE_APP_BASE_API ?? "/",
          timeout: 10000,
        });

        if (
          response.data.code === 200 &&
          response.data.data &&
          response.data.access_token
        ) {
          // 登录成功
          const u = response.data.data;
          this.currentUser.setUserInfo(u);
          this.currentUser.access_token = response.data.access_token;
          this.currentUser.refresh_token = response.data.refresh_token;

          ElMessage({
            message: "GitHub 登录成功",
            type: "success",
            duration: 1700,
          });

          // 跳转到保存的页面或默认到 /posts
          const redirectPath =
            localStorage.getItem("loginRedirectPath") || "/posts";
          localStorage.removeItem("loginRedirectPath");
          this.$router.push(redirectPath);
        } else {
          ElMessage.error(response.data.message || "GitHub 登录失败");
          setTimeout(() => {
            this.$router.push("/login");
          }, 1500);
        }
      } catch (error) {
        console.error("GitHub 回调处理失败:", error);
        ElMessage.error("登录失败，请稍后重试");
        setTimeout(() => {
          this.$router.push("/login");
        }, 1500);
      }
    },
  },
};
</script>

<template>
  <div class="callback-container">
    <el-icon class="is-loading" :size="50">
      <Loading />
    </el-icon>
    <p>正在登录中...</p>
  </div>
</template>

<style scoped>
.callback-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
  color: #606266;
}

.callback-container p {
  margin-top: 20px;
  font-size: 16px;
}
</style>
