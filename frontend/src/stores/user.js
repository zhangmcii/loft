import { defineStore } from "pinia";
import { io } from "socket.io-client";
import imageCfg from "@/config/image.js";
import cityUtil from "@/utils/cityUtil.js";
import { areaList } from "@vant/area-data";

export const useCurrentUserStore = defineStore("currentUser", {
  state: () => ({
    socket: null,
    activeChat: null,
    heartbeatInterval: null,
    token: "",
    userInfo: {
      id: "1",
      username: "",
      nickname: "",
      roleId: 0,
      confirmed: false,
      bg_image: "",
      image: "",
      about_me: "",
      location: "",
      // token: '',
      // 已点赞的评论id
      likeIds: [],
      // 关注的用户
      followed: [
        {
          id: -1,
          name: "",
          uName: "",
          avatar: "",
        },
      ],
      interest: {
        movies: [],
        books: [],
      },
      social_account: {
        github: "",
        email: "",
        qq: "",
        wechat: "",
        bilibili: "",
        twitter: "",
      },
      music: {
        name: "",
        aitist: "",
        url: "",
        pic: "",
        lrc: "",
      },
      tags: [],
    },
    notice: {
      Notification_data: [],
      // NOTIFICATION_KEY: `user_notifications_${userInfo.id}`,
      NOTIFICATION_KEY: `user_notifications_1`,
      MAX_ITEM: 50,
    },
    devUploadBaseUrl: "dev/",
    // 主页背景库地址
    userBackgroundUrl: "userBackground/",
    // 用户头像库地址
    userAvatars: "userAvatars/",
    defaultBackground: `${
      import.meta.env.VITE_QINIU_DOMAIN
    }/userBackground/static/image-pre3.webp-slim`,
  }),
  getters: {
    isLogin: (state) => state.token != "",
    isCommentManage: (state) => state.userInfo.roleId >= 2,
    isConfirmed: (state) => state.userInfo.confirmed == true,
    isAdmin: (state) => state.userInfo.roleId == 3,
    priorityName: (state) =>
      state.userInfo.nickname
        ? state.userInfo.nickname
        : state.userInfo.username,
    avatarsUrl: (state) =>
      state.userInfo.image ? state.userInfo.image : imageCfg.logOut,
    backGroundUrl: (state) =>
      state.userInfo.bg_image
        ? state.userInfo.bg_image
        : state.defaultBackground,
    cityName: (state) => {
      if (!state.userInfo.location) return "";
      return cityUtil.getCodeToName(state.userInfo.location, areaList);
    },
    // 图片上传目录
    uploadArticlesBaseUrl: (state) =>
      import.meta.env.DEV == true
        ? state.devUploadBaseUrl
        : `user_image/user_${state.userInfo.id}/articles/`,
    uploadAvatarsBaseUrl: (state) =>
      import.meta.env.DEV == true
        ? state.devUploadBaseUrl
        : `user_image/user_${state.userInfo.id}/avatars/`,
    uploadCommentsBaseUrl: (state) =>
      import.meta.env.DEV == true
        ? state.devUploadBaseUrl
        : `user_image/user_${state.userInfo.id}/comments/`,
    uploadInterestBaseUrl: (state) =>
      import.meta.env.DEV == true
        ? state.devUploadBaseUrl
        : `user_image/user_${state.userInfo.id}/interest/`,
    uploadMarkdownBaseUrl: (state) =>
      import.meta.env.DEV == true
        ? state.devUploadBaseUrl
        : `user_image/user_${state.userInfo.id}/markdown/`,
    uploadBackgroundStatic: (state) => `${state.userBackgroundUrl}static/`,
    uploadBackgroundDynamics: (state) => `${state.userBackgroundUrl}dynamics/`,
  },
  actions: {
    addItemLikeIds(value) {
      this.userInfo.likeIds.push(value);
    },
    addItemFollowed(value) {
      this.userInfo.followed.push(value);
    },
    delItemFollowed(username) {
      this.userInfo.followed = this.userInfo.followed.filter(
        (item) => item.uName != username
      );
    },
    // 保存通知
    saveNotifications(notifications) {
      const trimmed = notifications.slice(0, this.notice.MAX_ITEM);
      this.notice.Notification_data = trimmed;
    },
    // 读取通知
    loadNotifications() {
      return this.notice.Notification_data;
    },
    // 清空通知（可选）
    clearNotifications() {},
    logOut() {
      this.disconnectSocket();
      this.$reset();
      localStorage.removeItem("blog");
      localStorage.removeItem("blogOtherUser");
    },
    connectSocket() {
      if (this.socket) return;
      this.socket = io(import.meta.env.DEV ? "" : import.meta.env.VITE_DOMAIN, {
        path: "/socket.io",
        query: { token: this.token },
        transports: ["websocket"],
        withCredentials: true,
        reconnectionAttempts: 5,
        reconnectionDelay: 5000,
        // 与后端ping_timeout一致
        pingTimeout: 30000,
        pingInterval: 60000,
      });

      // 监听连接成功事件
      this.socket.on("connect", () => {
        console.log("已连接到WebSocket服务器", this.socket.id);
      });
      this.socket.on("connect_error", (err) => {
        console.error("❌ WebSocket连接失败：", {
          message: err.message,
          code: err.code,
          data: err.data,
        });
      });

      this.socket.on("disconnect", (reason) => {
        console.warn("⚠️ WebSocket断开连接：", reason);
      });

      this.socket.on("message_sent", (msg) => {
        console.log("📤 消息发送成功（后端确认）：", msg);
        // 前端消息发送成功后的逻辑（比如清空输入框、更新聊天记录）
      });

      this.socket.on("heartbeat", () => {
        console.log("💓 心跳响应正常");
      });

      // 初始化心跳定时器
      this.heartbeatInterval = setInterval(() => {
        if (this.socket?.connected) {
          this.socket.emit("heartbeat");
        }
      }, 30000);
    },
    disconnectSocket() {
      if (!this.socket) return;

      // 监听new_notification，new_message事件， 在具体组件中写了

      this.socket.off("connect");
      this.socket.off("connect_error");

      this.socket.off("disconnect");
      // 清理业务事件
      this.socket.off("new_message");
      this.socket.off("message_sent");
      this.socket.off("new_notification");
      this.socket.off("heartbeat");

      this.cleanup();
      this.socket = null;
      console.log("前端主动断开WebSocket连接");
    },
    cleanup() {
      // 清理定时器
      if (this.heartbeatInterval) {
        clearInterval(this.heartbeatInterval);
        this.heartbeatInterval = null;
      }

      // 断开Socket连接
      if (this.socket) {
        this.socket.disconnect();
        this.socket = null;
      }
    },
    enterChat(targetId) {
      this.activeChat = targetId;
      // 确保socket已连接再发送事件
      if (this.socket?.connected) {
        this.socket.emit("enter_chat", { targetId: targetId });
        console.log("🗨️ 进入聊天:", targetId);
      } else {
        console.error("❌ 未连接WebSocket，无法进入聊天。正在重试");
        // 重连后重试（可选）
        this.connectSocket();
        setTimeout(() => this.enterChat(targetId), 1000);
      }
    },

    sendMessage(chat, func) {
      let content = chat.content;
      if (this.activeChat && content.trim()) {
        if (this.socket?.connected) {
          this.socket.emit("send_message", {
            receiver_id: this.activeChat,
            content: content.trim(),
          });
          console.log("📤 发送消息:", content.trim());
          // 前端临时处理（最终以后端message_sent为准）
          if (func) func(chat);
        } else {
          console.error("❌ 未连接WebSocket，无法发送消息");
          // 重连后重试（可选）
          this.connectSocket();
          setTimeout(() => this.sendMessage(chat, func), 1000);
        }
      }
    },
    setUserInfo(val) {
      this.userInfo = { ...this.userInfo, ...val };
    },
  },
  persist: {
    key: "blog",
    storage: localStorage,
    pick: ["token", "userInfo", "notice"],
  },
});
