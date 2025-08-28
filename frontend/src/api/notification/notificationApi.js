import { $http } from "@/utils/request.js";
const url_prefix = "/api/v1";

export default {
  // 获取当前用户的所有通知
  getCurrentUserNotification() {
    return $http.get(`${url_prefix}/notifications`);
  },

  // 标记通知为已读
  markRead(params) {
    return $http.patch(`${url_prefix}/notifications`, params);
  },

  // 获取在线用户信息
  getOnline() {
    return $http.get(`${url_prefix}/online-users`);
  },
};
