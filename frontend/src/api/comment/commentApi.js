import { $http } from '@/utils/request.js'
const url_prefix = '/api/v1'
export default {
  // 提交评论
  submitComment(postId, comment) {
    return $http.post(`${url_prefix}/posts/${postId}/comments`, comment)
  },
  // 获取文章的评论
  getComment(postId, page) {
    let params = {}
    params['page'] = page
    return $http.get(`${url_prefix}/posts/${postId}/comments/`, { params: params })
  },
  
  // 获取评论的回复
  getReplyComment(parentCommentId, page) {
    let params = {}
    params['page'] = page
    return $http.get(`${url_prefix}/comments/${parentCommentId}/replies`, { params: params })
  },
  
  // 管理员审核评论页面
  getAllComments(page) {
    let params = {}
    params['page'] = page
    return $http.get(`${url_prefix}/comments`, { params: params })
  },
  // 禁用/恢复评论
  enableOrDisable(commentId, action) {
    let params = {}
    params['action'] = action
    return $http.patch(`${url_prefix}/comments/${commentId}`, params)
  },
}
