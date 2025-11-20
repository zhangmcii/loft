import { $http } from "@/utils/request.js";
const url_prefix = "/api/v1";

export default {
  // 获取系统日志
  getLogs(page) {
    let params = {};
    params["page"] = page;
    return $http.get(`${url_prefix}/logs`, { params: params });
  },
  // 删除系统日志
  deleteLog(ids) {
    return $http.delete(`${url_prefix}/logs`, { data: ids });
  },
};
