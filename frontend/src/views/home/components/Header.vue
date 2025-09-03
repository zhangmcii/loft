<template>
  <div class="burger-menu">
    <div class="home" @click="goHomePage">
      <homeIcon />
    </div>
    <div class="marQuee">
      <MarQuee :text="daySentence" :speed="0.7" />
    </div>
    <BellCom class="notification" />
    <div class="user-image">
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
          <div v-if="currentUser.isCommentManage">
            <van-cell
              title="评论管理"
              icon="chat-o"
              clickable
              @click="handleCellClick('/commentManagement')"
            />
            <van-cell
              title="标签管理"
              icon="medal-o"
              clickable
              @click="handleCellClick('/tag')"
            />
            <van-cell
              title="操作日志"
              icon="shield-o"
              clickable
              @click="handleCellClick('/operateLog')"
            />
            <van-cell
              title="找回其他用户密码"
              icon="warning-o"
              clickable
              @click="handleCellClick('/PasswordChangeAdmin')"
            ></van-cell>
          </div>
          <van-cell
            :title="accountLabel"
            :icon="accountLabel == '账户' ? 'notes-o' : ''"
            is-link
            arrow-direction="down"
            @click.prevent="toggleContactDropdown"
          />
          <div v-if="isContactDropdownActive">
            <van-cell
              title="修改密码"
              title-style="margin-left:10px"
              clickable
              @click="handleCellClick('/changePassword')"
            ></van-cell>
            <van-cell
              title="修改邮箱"
              title-style="margin-left:10px"
              clickable
              @click="handleCellClick('/changeEmail')"
              v-if="currentUser.isConfirmed"
            ></van-cell>
            <van-cell
              title="绑定邮箱"
              title-style="margin-left:10px"
              clickable
              @click="handleCellClick('/bindEmail')"
              v-else
            ></van-cell>
          </div>
          <van-cell
            title="退出登录"
            icon="peer-pay"
            clickable
            @click="log_out"
            href="/posts"
          ></van-cell>
        </template>
      </van-popover>
    </div>
  </div>
</template>

<script>
import { useCurrentUserStore } from "@/stores/user";
import MarQuee from "@/utils/components/MarQuee.vue";
import daysApi from "@/api/days/daysApi.js";
import emitter from "@/utils/emitter.js";
import imageCfg from "@/config/image.js";
import homeIcon from "@/asset/svg/homeIcon.svg?component";
import BellCom from "./BellCom.vue";
export default {
  name: "BurgerMenu",
  components: {
    MarQuee,
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
    this.daySentence = daysApi.fetchQuote();
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
      this.closeToggleMenu(); // 关闭弹出框
      this.$router.push(route); // 路由跳转
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
      this.closeToggleMenu();
      this.currentUser.disconnectSocket();
      this.currentUser.logOut();
      this.$message({
        message: "已退出",
        type: "success",
        duration: 1700,
      });
      this.$router.push("/posts");
      this.initImage();
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
      if (action.text == "登录") {
        this.$router.push("/login");
      } else if (action.text == "注册") {
        this.$router.push("/register");
      }
    },
  },
};
</script>

<style scoped>
.burger-menu {
  width: 100%;
  height: 6vh;
  display: flex;
  flex-direction: row;
  justify-content: space-between;
}
.home {
  margin: 8px 0px 0px 17px;
}
.marQuee {
  margin: 3px 0px 0px 0px;
  width: 70%;
}
.notification {
  margin: 11px 10px 0px 0px;
}
.user-image {
  margin: 8px 20px 0px 0px;
}
.van-cell {
  width: 200px;
}
.van-divider {
  margin: 10px 0px 0px 0px;
}
</style>
