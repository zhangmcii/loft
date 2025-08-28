import { $http } from "@/utils/request.js";
const url_prefix = "/api/v1";

export default {
  // 获取七牛云上传凭证
  get_upload_token() {
    return $http.get(`${url_prefix}/files/token`);
  },

  del_image(key) {
    const bucket = import.meta.env.VITE_QINIU_BUCKET;
    return $http.delete(`${url_prefix}/del_image`, { data: { bucket, key } });
  },
};
