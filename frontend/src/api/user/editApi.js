import { $http } from '@/utils/request.js'
const url_prefix = '/api/v1'
export default {
  // editProfile(formUserData) {
  //   return $http.post('/edit-profile', formUserData)
  // },
  editProfileAdmin(formUserData) {
    return $http.post(`/edit-profile/${formUserData.id}`, formUserData)
  },
  editUserTag(data) {
    return $http.post('/update_user_tag', data)
  },
  editUser(data){
    return $http.post(`${url_prefix}/update_user`, data)
  },
  updateTag(data){
    return $http.post('/update_tag', data)
  }
}
