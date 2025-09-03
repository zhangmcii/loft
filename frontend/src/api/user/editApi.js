import { $http } from "@/utils/request.js";
const url_prefix = "/api/v1";

export default {
  // 编辑用户资料
  editUser(userId, data) {
    return $http.patch(`${url_prefix}/users/${userId}`, data);
  },

  // 管理员编辑用户资料
  editProfileAdmin(formUserData) {
    return $http.post(
      `${url_prefix}/edit-profile/${formUserData.id}`,
      formUserData
    );
  },

  // 更新当前用户标签
  editUserTag(userId, data) {
    return $http.post(`${url_prefix}/users/${userId}/tags`, data);
  },

  // 更新公共标签库
  updateTag(data) {
    return $http.post(`${url_prefix}/tags`, data);
  },
};
