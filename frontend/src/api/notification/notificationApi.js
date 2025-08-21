import { $http } from '@/utils/request.js'
export default {
  getUnRead() {
    return $http.get('/notification/unread')
  },
  markRead(params) {
    return $http.post('/notification/read', params)
  },
  getOnline(){
    return $http.get('/socketData') 
  }
}
