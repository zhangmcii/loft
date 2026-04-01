import { $http } from "@/utils/request.js";
const url_prefix = "/api/v1";

export default {
  // 获取所有文章
  getPosts(page, tabName) {
    let params = {};
    params["page"] = page;
    params["tabName"] = tabName;
    return $http.get(`${url_prefix}/posts`, { params: params });
  },

  searchPosts(page, keyword) {
    let params = {};
    params["page"] = page;
    params["q"] = keyword;
    return $http.get(`${url_prefix}/posts/search`, { params: params });
  },

  // 发布文章
  publish_post(post) {
    return $http.post(`${url_prefix}/posts`, post);
  },

  // 获取单篇文章
  getPost(id) {
    return $http.get(`${url_prefix}/posts/${id}`);
  },

  // 编辑文章
  editPost(id, post) {
    return $http.patch(`${url_prefix}/posts/${id}`, post);
  },

  // 删除文章
  deletePost(id) {
    return $http.delete(`${url_prefix}/posts/${id}`);
  },
};
