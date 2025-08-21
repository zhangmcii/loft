import { $http } from '@/utils/request.js'
export default {
  saveImageUrl(image) {
    return $http.post('/image', image)
  },
  saveInterestImage(userId, data) {
    return $http.post(`/user/${userId}/interest_images`, data)
  },
  getBackgroundImage(currentPage, pageSize, prefix = 'userBackground/static', complete_url = 1) {
    const params = {
      prefix: prefix,
      pageSize: pageSize,
      currentPage: currentPage,
      completeUrl: complete_url
    }
    return $http.get('/dir_name', { params: params })
  }
}
