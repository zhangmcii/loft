import { $http } from '@/utils/request.js'
const url_prefix = '/api/v1'
export default {
  getFan(userName, page) {
    let params = {}
    params['page'] = page
    return $http.get(`/followers/${userName}`, { params: params })
  },
  
  getFollowing(userName,page) {
    let params = {}
    params['page'] = page
    return $http.get(`/followed_by/${userName}`, { params: params })
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
