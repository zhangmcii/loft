import { defineStore } from "pinia";

export const useOtherUserStore = defineStore("otherUser", {
  state: () => ({
    userInfo: {
      id: 1,
      username: "",
      nickname: "",
      social_account: {
        github: "",
        email: "",
        qq: "",
        wechat: "",
        bilibili: "",
        twitter: "",
      },
      music: {
        title: "",
        author: "",
        url: "",
        pic: "",
        lrc: "",
      },
    },
    defaultBackground: `${
      import.meta.env.VITE_QINIU_DOMAIN
    }/userBackground/static/image-pre3.webp-slim`,
  }),
  getters: {
    isCommentManage: (state) => state.userInfo.roleId >= 2,
    isConfirmed: (state) => state.userInfo.confirmed == true,
    isAdmin: (state) => state.userInfo.isAdmin == true,
    priorityName: (state) =>
      state.userInfo.nickname
        ? state.userInfo.nickname
        : state.userInfo.username,
    backGroundUrl: (state) =>
      state.userInfo.bg_image
        ? state.userInfo.bg_image
        : state.defaultBackground,
  },
  actions: {
    setUserInfo(val) {
      this.userInfo = val;
    },
  },
  persist: {
    key: "blogOtherUser",
    storage: localStorage,
  },
});
