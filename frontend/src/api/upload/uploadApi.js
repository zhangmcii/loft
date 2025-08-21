import { $http } from '@/utils/request.js'

export default {
  get_upload_token() {
    return $http.get('/get_upload_token')
  },
  del_image(key) {
    const bucket = import.meta.env.VITE_QINIU_BUCKET
    return $http.delete('/del_image', { data: { bucket, key } })
  }
}
