import { $http } from '@/utils/request.js'
export default {
  sendMsg(params) {
    return $http.post('/msg', params)
  },
  getMessageHistory(userId ,currentPage) {
    let params = {}
    params['userId'] = userId
    params['page'] = currentPage
    return $http.get('/msg', { params: params })
  },
  markMessagesRead(ids) {
    let params = {}
    params[ids] = ids
    return $http.post('/msg/read', params)
  }
}
