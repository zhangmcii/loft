import typewriter from "@/utils/components/Typewriter.vue";
import interest from "@/views/user/components/Interest.vue";
import socialLinks from "@/utils/components/SocialLinks.vue";
import ButtonAnimate from "@/utils/components/ButtonAnimate.vue";
import cityUtil from "@/utils/cityUtil.js";
import { areaList } from "@vant/area-data";
import { useCurrentUserStore } from "@/stores/user";
import { useOtherUserStore } from "@/stores/otherUser";
import SkeletonUtil from "@/utils/components/SkeletonUtil.vue";
import PostImage from "@/views/posts/components/PostImage.vue";
import PostPreview from "@/views/posts/components/PostPreview.vue";
import PageScroll from "@/utils/components/PageScroll.vue";
import userApi from "@/api/user/userApi.js";
import date from "@/utils/date.js";
import dayjs from "@/config/dayjsCfg";
import { loginReminder, waitImage } from "@/utils/common.js";
import musicPlayer from "./music.vue";
import { useMusicStore } from "@/stores/music";

export default {
  components: {
    typewriter,
    interest,
    socialLinks,
    ButtonAnimate,
    SkeletonUtil,
    PostImage,
    PostPreview,
    musicPlayer,
    PageScroll,
  },
  data() {
    return {
      isUserPage: true,
      activeInterest: "movie",
      user: null,
      posts: [],
      currentPage: 1,
      posts_count: -1,
      loading: {
        userData: true,
        follow: false,
        switch: false,
        more: false,
      },
      dialogShow: false,
      contentLoaded: false,
      isMobileDevice: false,
      noPadding: true,
    };
  },
  setup() {
    const currentUser = useCurrentUserStore();
    const otherUser = useOtherUserStore();
    const musicStore = useMusicStore();
    return { currentUser, otherUser, areaList, musicStore };
  },
  computed: {
    location() {
      if (!this.user || !this.user.location) return "";
      if (!isNaN(this.user.location)) {
        return cityUtil.getCodeToName(this.user.location, this.areaList);
      }
      return "";
    },
    member_since() {
      return this.user
        ? dayjs(this.user.member_since).format("YYYY-MM-DD")
        : "";
    },
    from_now() {
      return date.dateShow(this.user.last_seen);
    },
    isCurrentUser() {
      return this.$route.params.userName == this.currentUser.userInfo.username;
    },
    isFollowCurrentUser() {
      return (
        this.user &&
        this.currentUser.userInfo.username &&
        !this.isCurrentUser &&
        this.user.is_following_current_user
      );
    },
    isFollowEachOther() {
      return (
        this.user &&
        this.currentUser.userInfo.username &&
        !this.isCurrentUser &&
        this.user.is_following_current_user &&
        this.user.is_followed_by_current_user
      );
    },
    isFollowOtherUser() {
      return (
        this.user &&
        this.currentUser.userInfo.username &&
        !this.isCurrentUser &&
        this.user.is_followed_by_current_user
      );
    },
    bgImage() {
      const isMobile = this.isMobileDevice;
      if (this.isCurrentUser) {
        return isMobile
          ? this.currentUser.backGroundUrl
          : this.currentUser.pcBackGroundUrl;
      }
      return isMobile
        ? this.otherUser.backGroundUrl
        : this.otherUser.pcBackGroundUrl;
    },
    backColor() {
      return this.isUserPage ? "#ffffff" : "#000000";
    },
    socialCount() {
      if (!this.user || !this.user.social_account) return true;
      return Object.values(this.user.social_account).every(
        (value) => value === "" || value === null || value === undefined
      );
    },
    noMore() {
      if (this.posts_count < 0) return false;
      return this.posts.length >= this.posts_count;
    },
    infiniteDisabled() {
      return this.loading.userData || this.loading.switch || this.loading.more;
    },
  },
  // 当从A资料跳转B资料时，更新资料页面
  created() {
    this.isMobileDevice = this.checkIsMobile();
    // 首次加载时获取用户数据
    this.getUser();
    console.log("111", this.$route.params.userName);
    // 从A用户主页跳转到B用户主页触发
    this.$watch(
      () => this.$route.params.userName,
      (newUserName, oldUserName) => {
        if (this.$route.name === "user" && newUserName !== oldUserName) {
          this.isUserPage = true;
          // 重置加载状态
          this.user = null;
          this.posts = [];
          this.currentPage = 1;
          this.posts_count = -1;
          this.loading.more = false;
          this.loading.userData = true;
          this.contentLoaded = false;
          this.getUser();
        }
      }
    );
  },
  methods: {
    checkIsMobile() {
      if (typeof window === "undefined") return false;
      const ua = navigator.userAgent || "";
      return (
        /Mobi|Android|iPhone|iPad|iPod/i.test(ua) || window.innerWidth <= 768
      );
    },
    setMainProperty() {
      if (!this.isUserPage) {
        return;
      }

      const bgImageUrl = this.bgImage;
      const root = document.documentElement;
      root.style.setProperty(
        "--leleo-background-image-url",
        bgImageUrl ? `url('${bgImageUrl}')` : "none"
      );
    },
    // 每次点击tag触发动画
    playTagAnimation(e) {
      const el = e.currentTarget;
      el.classList.remove("animate");
      // 强制重绘
      void el.offsetWidth;
      el.classList.add("animate");
    },
    setActive(type) {
      this.activeInterest = type;
    },
    handleSwitchChange() {
      const root = document.documentElement;
      if (this.isUserPage) {
        this.setMainProperty();
        this.noPadding = true;
      } else {
        root.style.setProperty("--leleo-background-image-url", `none`);
        root.style.setProperty("background-color", "#fff");
        this.noPadding = false;
      }
    },
    async beforeSwitch() {
      // 从文章列表切换到用户资料页时，不会发请求
      if (!this.isUserPage) {
        return true;
      }
      this.loading.switch = true;
      this.posts = [];
      this.currentPage = 1;
      this.posts_count = -1;
      await this.fetchUserPosts(this.$route.params.userName, 1, {
        append: false,
      });
      this.loading.switch = false;
      return true;
    },
    getUser() {
      this.loading.userData = true;
      this.contentLoaded = false;

      // 检查是否是查看当前登录用户的资料
      const isViewingSelf =
        this.currentUser.isLogin &&
        this.$route.params.userName === this.currentUser.userInfo.username;

      let param = isViewingSelf
        ? this.currentUser.userInfo.username
        : this.$route.params.userName;

      userApi
        .getUserByUsername(param)
        .then(async (res) => {
          // 适配新的统一接口返回格式
          let userData;
          if (res.code === 200) {
            userData = res.data;
          } else {
            throw new Error("获取用户数据失败");
          }

          // 一次性赋值，避免多次局部更新
          this.user = userData;

          // 更新对应的存储
          if (isViewingSelf) {
            this.currentUser.setUserInfo(userData);
            if (userData.bg_image) {
              this.currentUser.userInfo.bg_image = userData.bg_image;
            }
            if (userData.pc_bg_image) {
              this.currentUser.userInfo.pc_bg_image = userData.pc_bg_image;
            }
          } else {
            this.otherUser.userInfo = userData;
            if (userData.bg_image) {
              this.otherUser.userInfo.bg_image = userData.bg_image;
            }
            if (userData.pc_bg_image) {
              this.otherUser.userInfo.pc_bg_image = userData.pc_bg_image;
            }
          }

          // 只有从文章预览卡片的音乐部分点击进入时才自动播放音乐
          const shouldPlayMusic = this.$route.query.playMusic === "true";
          if (shouldPlayMusic && this.user?.music && this.user.music.url) {
            this.$nextTick(() => {
              this.musicStore.playMusic(this.user.music);
            });
          }

          // 背景图片加载（不阻塞内容显示）
          if (this.bgImage) {
            waitImage([this.bgImage]);
          }

          // 关闭加载状态
          this.loading.userData = false;
          this.setMainProperty();

          // 标记内容已加载，触发清晰度过渡
          this.$nextTick(() => {
            this.contentLoaded = true;
          });
        })
        .catch((err) => {
          this.loading.userData = false;
          ElMessage.error(err);
          console.error(err);
        });
    },
    async fetchUserPosts(userName, page, { append = false } = {}) {
      const loadingKey = append ? "more" : "userData";
      this.loading[loadingKey] = true;
      try {
        const ok = await userApi
          .getPosts(userName, page)
          .then((res) => {
            // 适配新的统一接口返回格式
            if (res.code === 200) {
              // 新格式
              const list = res.data.posts || res.data || [];
              this.posts = append ? [...this.posts, ...list] : list;
              this.posts_count = res.total || 0;
              return true;
            } else if (res.data) {
              // 兼容旧格式
              const list = res.data.posts || [];
              this.posts = append ? [...this.posts, ...list] : list;
              this.posts_count = res.data.total;
              return true;
            }
            return false;
          })
          .catch((error) => {
            console.error("获取用户文章失败", error);
            ElMessage.error("获取用户文章失败，请稍后重试");
            return false;
          });
        return ok;
      } finally {
        this.loading[loadingKey] = false;
      }
    },
    async loadMoreUserPosts() {
      if (this.isUserPage || this.infiniteDisabled || this.noMore) {
        return;
      }
      const nextPage = this.currentPage + 1;
      const ok = await this.fetchUserPosts(
        this.$route.params.userName,
        nextPage,
        {
          append: true,
        }
      );
      if (ok) {
        this.currentPage = nextPage;
      }
    },
    editProfile() {
      this.$router.push(`/editProfile`);
    },
    editProfileAdmin() {
      this.$router.push(`/editProfileAdmin/${this.user.id}`);
    },
    followUser() {
      if (!this.currentUser.isLogin) {
        loginReminder("快去登录再私信吧");
        return;
      }
      this.loading.follow = true;
      userApi.follow(this.user.username).then((res) => {
        // 适配新的统一接口返回格式
        if (res.code === 200) {
          // 新格式
          this.loading.follow = false;
          this.user = res.data;
          this.currentUser.addItemFollowed({
            id: this.user.id,
            name: this.user.name ? this.user.name : this.user.username,
            uName: this.user.username,
            avatar: this.user.image,
          });
          ElMessage.success("关注成功");
        } else {
          this.loading.follow = false;
          ElMessage.error(res.message || res.data?.msg || "关注失败");
        }
      });
    },
    unFollowUser() {
      this.dialogShow = true;
    },

    beforeClose(action) {
      if (action !== "confirm") {
        return Promise.resolve(true);
      } else {
        return userApi.unFollow(this.user.username).then((res) => {
          // 适配新的统一接口返回格式
          if (res.code === 200) {
            // 新格式
            this.user = res.data;
            this.currentUser.delItemFollowed(this.user.username);
            ElMessage.success("已取消关注");
          } else {
            ElMessage.error(res.message || res.data?.msg || "取消关注失败");
          }
          return res;
        });
      }
    },
    followerDetail() {
      const f = "follower";
      this.$router.push(`/follow/${f}/${this.user.username}`);
    },
    followedDetail() {
      const f = "followed";
      this.$router.push(`/follow/${f}/${this.user.username}`);
    },
    openChat() {
      if (!this.currentUser.isLogin) {
        loginReminder("快去登录再私信吧");
        return;
      }
      this.$router.push("/chat");
    },
  },
};
