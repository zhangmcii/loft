<script>
import authApi from "@/api/auth/authApi.js";
import { useCurrentUserStore } from "@/stores/user";
export default {
  data() {
    var validateUser = (rule, value, callback) => {
      if (value === "") {
        callback(new Error("请输入账户"));
      } else {
        callback();
      }
    };
    var validatePass = (rule, value, callback) => {
      if (value === "") {
        callback(new Error("请输入密码"));
      } else {
        callback();
      }
    };
    return {
      ruleForm: {
        user: "",
        pass: "",
      },
      rules: {
        user: [{ validator: validateUser, trigger: "blur" }],
        pass: [{ validator: validatePass, trigger: "blur" }],
      },
      // 是否记住账号密码
      isRemember: false,
      loading: false,
      // OAuth 相关
      oauthProviders: [],
      loadingProviders: false,
    };
  },
  setup() {
    const currentUser = useCurrentUserStore();
    return { currentUser };
  },
  // beforeRouteEnter(to, from, next) {
  //   next((vm) => {
  //     if (to.query?.username) {
  //       vm.ruleForm.user = to.query.username;
  //     } else {
  //       vm.getAccount();
  //     }
  //   });
  // },

  mounted() {
    this.getAccount();
    this.loadOAuthProviders();
  },
  computed: {
    formHasValue() {
      return this.ruleForm.user !== "" && this.ruleForm.pass !== "";
    },
  },
  methods: {
    login() {
      this.$refs.ruleForm.validate((valid) => {
        if (valid) {
          this.loading = true;
          authApi
            .login(this.ruleForm.user, this.ruleForm.pass)
            .then((res) => {
              this.loading = false;
              // 适配新的统一接口返回格式
              if (res.code === 200) {
                // 判断是否勾选记住密码
                this.hasRemember();
                const u = res.data;
                this.currentUser.setUserInfo(u);
                this.currentUser.access_token = res.access_token;
                this.currentUser.refresh_token = res.refresh_token;
                ElMessage.success("登录成功");
                this.$router.push({ path: "/posts" });
              } else {
                ElMessage.error(res.message || "账号或密码错误");
              }
            })
            .catch((error) => {
              this.loading = false;
            });
        } else {
          ElMessage.error("请修正表单中的错误");
        }
      });
    },
    //  检查本地存储是否有记住的账号密码，如果有则填充到输入框中
    getAccount() {
      const savedUsername = localStorage.getItem("loginUsername");
      const savedPassword = localStorage.getItem("loginPassword");
      if (savedUsername && savedPassword) {
        this.ruleForm.user = savedUsername;
        this.ruleForm.pass = savedPassword;
        this.isRemember = true;
      }
    },
    // 判断是否勾选记住密码
    hasRemember() {
      if (this.isRemember) {
        // 保存账号密码到本地存储
        localStorage.setItem("loginUsername", this.ruleForm.user);
        localStorage.setItem("loginPassword", this.ruleForm.pass);
      } else {
        // 清除本地存储的账号密码
        localStorage.removeItem("loginUsername");
        localStorage.removeItem("loginPassword");
      }
    },
    // 加载 OAuth 提供商列表
    loadOAuthProviders() {
      this.loadingProviders = true;
      authApi
        .getOAuthProviders()
        .then((res) => {
          if (res.code === 200) {
            this.oauthProviders = res.data || [];
          }
        })
        .catch((err) => {
          console.error("加载 OAuth 提供商失败:", err);
        })
        .finally(() => {
          this.loadingProviders = false;
        });
    },
    // OAuth 登录
    handleOAuthLogin(provider) {
      ElMessage.info(`正在跳转到 ${provider} 授权页面...`);
      // 直接跳转到后端 OAuth 接口
      window.location.href = `/auth/oauth/${provider}/login`;
    },
    // 获取 OAuth 图标
    getOAuthIcon(provider) {
      // 这里可以根据 provider 返回对应的图标
      // 暂时返回 null，使用 Element Plus 默认图标
      return null;
    },
  },
};
</script>

<template>
  <div class="header">
    <h2>欢迎回来 👋🏻</h2>
    <p>云端阁楼，随想悠悠，静候时光</p>
  </div>

  <el-form
    :model="ruleForm"
    label-position="left"
    status-icon
    :rules="rules"
    ref="ruleForm"
    style="max-width: 600px"
  >
    <el-form-item prop="user">
      <el-input
        v-model="ruleForm.user"
        size="large"
        placeholder="请输入用户名"
      />
    </el-form-item>
    <el-form-item prop="pass">
      <el-input
        v-model="ruleForm.pass"
        show-password
        size="large"
        placeholder="密码"
      />
    </el-form-item>
  </el-form>
  <el-row justify="space-between">
    <el-col :span="4"
      ><el-checkbox label="记住密码" v-model="isRemember"></el-checkbox
    ></el-col>
    <el-col :span="6">
      <div class="text">
        <el-link class="forget-pass" @click="$router.push('/resetPassword')"
          >忘记密码？</el-link
        >
      </div>
    </el-col>
  </el-row>

  <el-button
    type="primary"
    round
    :disabled="!formHasValue"
    @click="login"
    :loading="loading"
    >登录</el-button
  >
  <!-- 第三方登录 -->
  <div v-if="oauthProviders.length > 0" class="oauth-section">
    <el-divider>其他登录方式</el-divider>
    <div class="oauth-buttons">
      <el-button
        v-for="provider in oauthProviders"
        :key="provider.provider"
        :icon="getOAuthIcon(provider.provider)"
        class="oauth-button"
        @click="handleOAuthLogin(provider.provider)"
      >
        {{ provider.name }}
      </el-button>
    </div>
  </div>

  <!-- <el-divider> 其他登录方式 </el-divider> -->
  <div class="register-container">
    <el-text class="register-account">还没有账号?</el-text>
    <el-link class="register" @click="$router.push('/register')"
      >创建账号
    </el-link>
  </div>
  <div class="visit">
    <el-text class="register" @click="$router.push('/posts')">游客访问</el-text>
  </div>
</template>

<style scoped>
* {
  font-family: -apple-system, blinkmacsystemfont, "Segoe UI", roboto,
    "Helvetica Neue", arial, "Noto Sans", sans-serif, "Apple Color Emoji",
    "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji";
  /* color: #323639; */
  font-size: 14px;
  /* 移动端点击可点击元素时，出现蓝色默认背景色 */
  -webkit-tap-highlight-color: transparent;
  padding-left: 3px;
}

a,
button,
input,
textarea {
  outline: None;
}

.el-button {
  width: 95%;
  letter-spacing: 2px;
  margin-left: 9px;
}

:deep(.el-checkbox__input.is-checked + .el-checkbox__label) {
  color: #323639;
}

.text {
  height: 90%;
  height: 32px;
  display: grid;
  align-content: center;
}

.forget-pass,
.register {
  color: #006be6;
}

.el-checkbox,
.register-account {
  color: #323639;
}

h2 {
  font-size: 30px;
  color: #323639;
  margin: 0px 0px 12px 0px;
}

p {
  color: #71717a;
}

.el-form-item {
  padding-bottom: 0.8rem;
}

.el-input {
  height: 38px;
}

:deep(.el-input__wrapper) {
  border-radius: 7px;
}

.register-container {
  width: 95%;
  display: flex;
  justify-content: center;
  margin-top: 3vh;
}

.el-form {
  width: 95%;
}

.header {
  margin-top: 5vh;
}

.header,
.el-form,
.el-row,
.el-button {
  margin-bottom: 0.8rem;
}

.visit {
  display: flex;
  justify-content: center;
  margin-top: 10px;
}
.oauth-section {
  margin-top: 1.5rem;
  width: 95%;
}
.oauth-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: center;
  margin-top: 1rem;
}
.oauth-button {
  flex: 1;
  min-width: 120px;
  max-width: 200px;
}
</style>
