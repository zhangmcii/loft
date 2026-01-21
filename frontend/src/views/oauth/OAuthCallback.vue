<script>
import { onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import authApi from "@/api/auth/authApi.js";
import { useCurrentUserStore } from "@/stores/user";
import { ElMessage } from "element-plus";

export default {
  name: "OAuthCallback",
  setup() {
    const route = useRoute();
    const router = useRouter();
    const currentUser = useCurrentUserStore();

    const loading = ref(true);
    const error = ref(null);
    const provider = ref("");

    onMounted(async () => {
      // 获取 URL 参数
      const providerParam = route.params.provider;
      const queryParams = route.query;

      if (!providerParam) {
        error.value = "缺少平台参数";
        loading.value = false;
        return;
      }

      provider.value = providerParam;

      try {
        // 将所有查询参数传递给后端
        const params = {};
        Object.keys(queryParams).forEach((key) => {
          params[key] = queryParams[key];
        });

        // 调用后端接口处理回调
        const res = await authApi.oauthCallback(providerParam, params);

        if (res.code === 200 && res.data) {
          // 登录成功
          const { user, access_token, refresh_token } = res.data;

          currentUser.setUserInfo(user);
          currentUser.access_token = access_token;
          currentUser.refresh_token = refresh_token;

          ElMessage.success("登录成功");

          // 延迟跳转，让用户看到成功状态
          setTimeout(() => {
            router.push("/posts");
          }, 500);
        } else {
          // 登录失败
          error.value = res.message || "登录失败，请重试";
          loading.value = false;
        }
      } catch (err) {
        console.error("OAuth 回调处理失败:", err);
        error.value = err.message || "网络错误，请稍后重试";
        loading.value = false;
      }
    });

    const goToLogin = () => {
      router.push("/login");
    };

    return {
      loading,
      error,
      provider,
      goToLogin,
    };
  },
};
</script>

<template>
  <div class="oauth-callback-container">
    <div class="callback-card">
      <!-- 加载状态 -->
      <div v-if="loading" class="loading-state">
        <el-icon class="is-loading" :size="40" color="#409eff">
          <Loading />
        </el-icon>
        <h2>正在登录...</h2>
        <p>请稍候，我们正在完成 {{ provider }} 授权登录</p>
      </div>

      <!-- 成功状态 -->
      <div v-else-if="!error" class="success-state">
        <el-icon :size="60" color="#67c23a">
          <CircleCheck />
        </el-icon>
        <h2>登录成功</h2>
        <p>即将跳转到首页...</p>
      </div>

      <!-- 错误状态 -->
      <div v-else class="error-state">
        <el-icon :size="60" color="#f56c6c">
          <CircleClose />
        </el-icon>
        <h2>登录失败</h2>
        <p>{{ error }}</p>
        <el-button type="primary" @click="goToLogin" round>
          返回登录
        </el-button>
      </div>
    </div>
  </div>
</template>

<style scoped>
* {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}

.oauth-callback-container {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.callback-card {
  background: white;
  border-radius: 16px;
  padding: 60px 40px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
  text-align: center;
  max-width: 480px;
  width: 100%;
}

.loading-state,
.success-state,
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

h2 {
  font-size: 28px;
  font-weight: 600;
  margin: 0;
  color: #1f2937;
}

p {
  font-size: 16px;
  color: #6b7280;
  margin: 0;
  line-height: 1.6;
}

.el-button {
  margin-top: 20px;
  width: 200px;
}
</style>
