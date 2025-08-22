import { $http } from '@/utils/request.js'
export default {
  getCurrentUserNotification() {
    return $http.get('/notifications')
  },
  markRead(params) {
    return $http.post('/notification/read', params)
  },
  getOnline(){
    return $http.get('/socketData') 
  }
}
