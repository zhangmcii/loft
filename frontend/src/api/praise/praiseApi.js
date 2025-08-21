import { $http } from '@/utils/request.js'
export default {
  submitPraise(postId) {
    return $http.post(`/praise/${postId}`)
  },
  getPraise(postId){
    return $http.get(`/praise/${postId}`)
  },
  
  submitPraiseComment(commentId) {
    return $http.post(`/praise/comment/${commentId}`)
  },
  // 查找某文章下当前用户已点赞的评论id
  get_has_praised_comment_id(postId){
    return $http.get(`/has_praised/${postId}`)
  },
}
