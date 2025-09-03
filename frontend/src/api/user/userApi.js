import { $http } from "@/utils/request.js";
const url_prefix = "/api/v1";

export default {
  // 获取用户的文章
  getPosts(username, page) {
    let params = {};
    params["page"] = page;
    return $http.get(`${url_prefix}/users/${username}/posts`, {
      params: params,
    });
  },

  // 根据用户id，返回用户信息
  getUser(userId) {
    return $http.get(`${url_prefix}/users/${userId}`);
  },

  // 获取所有标签
  get_tag_list() {
    return $http.get(`${url_prefix}/tags`);
  },

  // 关注
  follow(username) {
    return $http.post(`${url_prefix}/users/${username}/follow`);
  },

  // 取消关注
  unFollow(username) {
    return $http.delete(`${url_prefix}/users/${username}/follow`);
  },
};
