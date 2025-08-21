import { $http } from '@/utils/request.js'
export default {
    getLogs(page) {
        let params = {}
        params['page'] = page
        return $http.get('/logs', { params: params })
      },
      deleteLog(ids){
        return $http.post('/deleteLog', ids)
      }
  }
