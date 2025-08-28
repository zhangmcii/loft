import { $http } from '@/utils/request.js'
const url_prefix = '/api/v1'

export default {
  // 获取用户的粉丝列表
  getFan(userName, page) {
    let params = {}
    params['page'] = page
    return $http.get(`${url_prefix}/users/${userName}/followers`, { params: params })
  },

  // 获取用户关注的人列表
  getFollowing(userName,page) {
    let params = {}
    params['page'] = page
    return $http.get(`${url_prefix}/users/${userName}/followings`, { params: params })
  },

  searchFollowed(name){
    let params = {}
    params['name'] = name
    return $http.get(`${url_prefix}/search_followed`, { params: params })
  },
  
  searchFan(name){
    let params = {}
    params['name'] = name
    return $http.get(`${url_prefix}/search_fan`, { params: params })
  }

}
