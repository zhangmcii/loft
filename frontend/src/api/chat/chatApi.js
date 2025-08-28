import { $http } from "@/utils/request.js";
const url_prefix = "/api/v1";

export default {
  // 获取聊天历史记录
  getMessageHistory(userId, currentPage) {
    let params = {};
    params["page"] = currentPage;
    return $http.get(`${url_prefix}/conversations/${userId}/messages`, {
      params: params,
    });
  },
  // markMessagesRead(ids) {
  //   let params = {}
  //   params[ids] = ids
  //   return $http.post(`${url_prefix}/conversations/${userId}/messages`, params)
  // }
};
