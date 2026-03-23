<template>
  <header class="header-container">
    <!-- 左侧区域 -->
    <div class="header-left">
      <div class="home-icon" @click="goHomePage">
        <homeIcon />
      </div>
      <div class="site-title" @click="goHomePage">LOFT</div>
    </div>

    <!-- 中间空白区域 -->
    <div class="header-center"></div>

    <!-- 右侧区域 -->
    <div class="header-right">
      <BellCom class="notification-icon" />
      <div class="user-avatar">
        <van-popover
          v-model:show="showPopover"
          :show-arrow="false"
          placement="bottom-end"
          :offset="[12, 8]"
          :actions="actions"
          @select="onSelect"
        >
          <template #reference>
            <el-avatar
              alt="用户图像"
              :size="32"
              :src="currentUser.avatarsUrl"
              @error="errorImage"
            />
          </template>
          <template #default v-if="currentUser.isLogin">
            <van-cell
              :title="currentUser.priorityName"
              :label="currentUser.userInfo.username"
              title-style="margin-left:10px"
            >
              <template #icon>
                <el-avatar
                  alt="用户图像"
                  :src="currentUser.avatarsUrl"
                  :size="47"
                />
              </template>
            </van-cell>
            <van-cell
              title="个人资料"
              icon="manager-o"
              clickable
              @click="handleCellClick(`/user/${currentUser.userInfo.username}`)"
            />
            <van-cell
              title="设置"
              icon="setting-o"
              clickable
              @click="handleCellClick('/settings')"
            />
          </template>
        </van-popover>
      </div>
    </div>
  </header>
</template>

<script>
import { useCurrentUserStore } from "@/stores/user";
import emitter from "@/utils/emitter.js";
import imageCfg from "@/config/image.js";
import homeIcon from "@/asset/svg/homeIcon.svg?component";
import BellCom from "./BellCom.vue";
import authApi from "@/api/auth/authApi.js";

export default {
  name: "BurgerMenu",
  components: {
    homeIcon,
    BellCom,
  },
  data() {
    return {
      windowWidth: window.innerWidth,
      menuItems: [
        { label: "About", href: "#" },
        { label: "Services", href: "#" },
        { label: "Contact", href: "#" },
      ],
      isContactDropdownActive: false,
      accountLabel: "账户",
      daySentence: "",
      photo: {
        Avatar: "",
        default:
          "https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png",
      },
      showPopover: false,
      actions: [
        { text: "登录", icon: "user-o" },
        { text: "注册", icon: "add-o" },
      ],
    };
  },
  setup() {
    const currentUser = useCurrentUserStore();
    return { currentUser };
  },
  computed: {
    isHomePage() {
      return this.$route.path === "/posts";
    },
  },
  mounted() {
    this.initImage();
    emitter.on("image", (url) => {
      this.photo.Avatar = url;
    });
  },
  created() {
    window.addEventListener("resize", this.updateWindowWidth);
  },
  beforeUnmount() {
    window.removeEventListener("resize", this.updateWindowWidth);
  },
  methods: {
    handleCellClick(route) {
      this.closeToggleMenu();
      this.$router.push(route);
    },
    closeToggleMenu() {
      if (this.showPopover) {
        this.showPopover = false;
      }
    },
    updateWindowWidth() {
      this.windowWidth = window.innerWidth;
    },
    toggleContactDropdown() {
      this.isContactDropdownActive = !this.isContactDropdownActive;
      this.accountLabel = this.isContactDropdownActive ? "关闭" : "账户";
    },
    log_out() {
      showConfirmDialog({
        title: "提示",
        message: "是否退出登陆？",
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
            this.closeToggleMenu();
            this.currentUser.logOut();
            this.initImage();
            return res;
          })
          .catch((err) => {
            console.error("撤销令牌失败:", err);
            this.closeToggleMenu();
            this.currentUser.logOut();
            this.initImage();
            return err;
          });
      }
    },

    goHomePage() {
      if (this.isHomePage) {
        return;
      }
      this.$router.push("/posts");
    },
    errorImage() {
      this.photo.Avatar = imageCfg.logOut;
    },
    initImage() {
      if (!this.currentUser.userInfo.image) {
        this.photo.Avatar = imageCfg.logOut;
        return;
      }
      this.photo.Avatar = this.currentUser.userInfo.image;
    },
    onSelect(action) {
      if (action.text === "登录") {
        this.$router.push("/login");
      } else if (action.text === "注册") {
        this.$router.push("/register");
      }
    },
  },
};
</script>

<style lang="scss" scoped>
@use "@/views/posts/components/PostReadingTokens.scss" as tokens;

.header-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  height: 56px;
  padding: 0 28px;
  box-sizing: border-box;
  background: #fff;
  border-bottom: 1px solid tokens.$reading-border;
}

.header-left {
  display: flex;
  flex-shrink: 0;
  align-items: center;
  gap: 10px;
}

.home-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  border-radius: 999px;
  cursor: pointer;
  color: tokens.$reading-text-primary;
  transition: color 0.2s ease, background-color 0.2s ease;

  &:hover {
    background: tokens.$reading-fill-softer;
  }
}

.site-title {
  font-size: 15px;
  font-weight: 600;
  letter-spacing: 0.06em;
  color: tokens.$reading-text-primary;
  cursor: pointer;
}

.header-center {
  flex: 1;
  min-width: 0;
}

.header-right {
  display: flex;
  flex-shrink: 0;
  align-items: center;
  gap: 10px;
}

.notification-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 999px;
  cursor: pointer;
  transition: background-color 0.2s ease;

  &:hover {
    background: tokens.$reading-fill-softer;
  }
}

.user-avatar {
  display: flex;
  align-items: center;
  height: 32px;
  padding: 0;

  .el-avatar {
    cursor: pointer;
    transition: opacity 0.2s ease, border-color 0.2s ease;
    border: 1px solid tokens.$reading-border;

    &:hover {
      opacity: 0.92;
      border-color: tokens.$reading-border-strong;
    }
  }
}

.van-cell {
  width: 200px;
}

.van-divider {
  margin: 10px 0 0;
}

@media (max-width: 768px) {
  .header-container {
    height: 56px;
    padding: 0 16px;
  }

  .site-title {
    font-size: 13px;
  }

  .home-icon,
  .notification-icon {
    width: 32px;
    height: 32px;
  }

  .user-avatar {
    height: 32px;
  }
}
</style>
