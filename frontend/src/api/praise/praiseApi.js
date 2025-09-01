import { $http } from "@/utils/request.js";
const url_prefix = "/api/v1";

export default {
  // 文章点赞
  submitPraise(postId) {
    return $http.post(`${url_prefix}/posts/${postId}/likes`);
  },

  // 获取文章点赞总数
  getPraise(postId) {
    return $http.get(`${url_prefix}/posts/${postId}/likes`);
  },

  // 评论点赞
  submitPraiseComment(commentId) {
    return $http.post(`${url_prefix}/comments/${commentId}/likes`);
  },

  // 查找某文章下当前用户已点赞的评论id
  has_praised_comment_ids(postId) {
    let params = {}
    params['liked'] = "true"
    return $http.get(`${url_prefix}/posts/${postId}/comments/praised`, { params: params });
  }
};
