import { $http } from '@/utils/request.js'
const url_prefix = '/api/v1'
export default {
  // 根据用户名，返回文章数据
  getPosts(username, page) {
    let params = {}
    params['page'] = page
    return $http.get(`/user/${username}`, { params: params })
  },
  follow(username) {
    return $http.get(`/follow/${username}`)
  },
  unFollow(username) {
    return $http.get(`/unfollow/${username}`)
  },
  // 根据用户名，返回用户信息
  getUserByUsername(username) {
    return $http.get(`/users/${username}`)
  },
  // 根据用户id，返回用户信息
  getUser(userId) {
    return $http.get(`${url_prefix}/users/${userId}`)
  },
  get_tag_list() {
    return $http.get('/tags_list')
  }
}
