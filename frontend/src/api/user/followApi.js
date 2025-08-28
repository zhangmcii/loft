import { $http } from '@/utils/request.js'
const url_prefix = '/api/v1'

export default {
  // 获取用户关注的人列表
  getFollowing(userName, page, name='') {
    let params = {}
    params['page'] = page
    params['name'] = name
    return $http.get(`${url_prefix}/users/${userName}/following`, { params: params })
  },

  // 获取用户的粉丝列表
  getFan(userName, page, name='') {
    let params = {}
    params['page'] = page
    params['name'] = name
    return $http.get(`${url_prefix}/users/${userName}/followers`, { params: params })
  },

  // // 搜索关注的人
  // searchFollowed(name){
  //   let params = {}
  //   params['name'] = name
  //   return $http.get(`${url_prefix}/search_followed`, { params: params })
  // },

  // // 搜索粉丝
  // searchFan(name){
  //   let params = {}
  //   params['name'] = name
  //   return $http.get(`${url_prefix}/search_fan`, { params: params })
  // }

}
