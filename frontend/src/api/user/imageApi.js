import { $http } from "@/utils/request.js";
const url_prefix = "/api/v1";

export default {
  // 存储用户图像地址
  saveImageUrl(userId, image) {
    return $http.post(`${url_prefix}/users/${userId}/image`, image);
  },

  // 保存用户兴趣的图片
  saveInterestImage(userId, data) {
    return $http.post(`${url_prefix}/user/${userId}/interest_images`, data);
  },

  // 获取资料背景图片列表
  getBackgroundImage(
    currentPage,
    pageSize,
    prefix = "userBackground/static",
    complete_url = 1
  ) {
    const params = {
      prefix: prefix,
      pageSize: pageSize,
      currentPage: currentPage,
      completeUrl: complete_url,
    };
    return $http.get(`${url_prefix}/dir_name`, { params: params });
  },

  // 获取用户公共图像列表
  getPublicImages(
    currentPage,
    pageSize,
    prefix = "userAvatars/",
    complete_url = 1
  ) {
    const params = {
      prefix: prefix,
      pageSize: pageSize,
      currentPage: currentPage,
      completeUrl: complete_url,
    };
    return $http.get(`${url_prefix}/dir_name`, { params: params });
  },
};
