<script>
import dragVerifyImgRotate from "./components/dragVerifyImgRotate.vue";
import authApi from "@/api/auth/authApi.js";
import { useCurrentUserStore } from "@/stores/user";
import imageCfg from "@/config/image.js";
export default {
  components: {
    dragVerifyImgRotate,
  },
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
        isPassing2: false,
      },
      rules: {
        user: [{ validator: validateUser, trigger: "blur" }],
        pass: [{ validator: validatePass, trigger: "blur" }],
      },
      // 是否记住账号密码
      isRemember: false,
      loading: false,
      imgPic: imageCfg.login,
      githubLoading: false,
    };
  },
  setup() {
    const currentUser = useCurrentUserStore();
    return { currentUser };
  },
  computed: {
    formHasValue() {
      return this.ruleForm.user !== "" && this.ruleForm.pass !== "";
    },
  },
  mounted() {
    this.getAccount();
  },
  methods: {
    login() {
      this.$refs.ruleForm.validate((valid) => {
        if (valid) {
          if (this.ruleForm.isPassing2) {
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
                  ElMessage({
                    message: "登录成功",
                    type: "success",
                    duration: 1700,
                  });
                  this.$router.push({ path: "/posts" });
                } else {
                  ElMessage({
                    message: res.message || "账号或密码错误",
                    type: "error",
                    duration: 1700,
                  });
                }
              })
              .catch(() => {
                this.loading = false;
              });
          } else {
            ElMessage("请先完成验证");
          }
        } else {
          ElMessage.error("请修正表单中的错误");
        }
      });
    },
    //  GitHub 登录
    loginWithGitHub() {
      this.githubLoading = true;
      authApi
        .getGitHubAuthUrl()
        .then((res) => {
          if (res.code === 200 && res.data && res.data.auth_url) {
            // 保存当前页面路径，登录后返回
            localStorage.setItem("loginRedirectPath", "/posts");
            // 跳转到 GitHub 授权页面
            window.location.href = res.data.auth_url;
          } else {
            ElMessage.error("获取授权地址失败");
            this.githubLoading = false;
          }
        })
        .catch(() => {
          ElMessage.error("获取授权地址失败");
          this.githubLoading = false;
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
    handleImageError() {
      this.imgPic = imageCfg.loginFail;
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
    <el-form-item class="pic">
      <drag-verify-img-rotate
        ref="dragVerify"
        :imgsrc="imgPic"
        v-model:isPassing="ruleForm.isPassing2"
        text="请按住滑块拖动"
        successText="验证通过"
        @img-error="handleImageError"
      >
      </drag-verify-img-rotate>
    </el-form-item>
  </el-form>
  <el-row justify="space-between">
    <el-col :span="4"
      ><el-checkbox label="记住密码" v-model="isRemember"></el-checkbox
    ></el-col>
    <el-col :span="6"
      ><div class="text">
        <el-link class="forget-pass" @click="$router.push('/resetPassword')"
          >忘记密码？</el-link
        >
      </div></el-col
    >
  </el-row>

  <el-button
    type="primary"
    round
    :disabled="!formHasValue"
    @click="login"
    :loading="loading"
    >登录</el-button
  >

  <!-- GitHub 登录按钮 -->
  <el-button
    round
    :loading="githubLoading"
    @click="loginWithGitHub"
    class="github-login-btn"
  >
    <span style="margin-right: 8px">
      <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
        <path
          d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.012 8.012 0 0016 8c0-4.42-3.58-8-8-8z"
        />
      </svg>
    </span>
    GitHub 登录
  </el-button>

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

.github-login-btn {
  background-color: #ffffff;
  border: 1px solid #dcdfe6;
  color: #24292f;
  margin-top: 0.8rem;
}

.github-login-btn:hover {
  background-color: #f6f8fa;
  border-color: #24292f;
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
.pic {
  display: grid;
  justify-content: center;
}
.visit {
  display: flex;
  justify-content: center;
  margin-top: 10px;
}
</style>
