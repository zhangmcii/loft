import { $http } from "@/utils/request.js";
const url_prefix = "/auth";
export default {
  login(username, password) {
    const param = {};
    param.uiAccountName = username;
    param.uiPassword = password;
    return $http.post(`${url_prefix}/login`, param);
  },
  revokeToken(tokenType = "access_token") {
    return $http.delete(`${url_prefix}/revokeToken`, {
      useRefreshToken: tokenType === "refresh_token",
    });
  },
  register(params) {
    return $http.post(`${url_prefix}/register`, params);
  },
  bindEmail(params) {
    return $http.post(`${url_prefix}/bindEmail`, params);
  },
  applyCode(params) {
    return $http.post(`${url_prefix}/applyCode`, params);
  },
  checkCode(params) {
    return $http.post(`${url_prefix}/confirm`, params);
  },
  changeEmail(params) {
    return $http.post(`${url_prefix}/changeEmail`, params);
  },
  changePassword(params) {
    return $http.post(`${url_prefix}/changePassword`, params);
  },
  resetPassword(params) {
    return $http.post(`${url_prefix}/resetPassword`, params);
  },
  helpChangePassword(params) {
    return $http.post(`${url_prefix}/helpChangePassword`, params);
  },
  checkTokenFreshness() {
    return $http.get(`${url_prefix}/checkFreshness`);
  },
  // OAuth 第三方登录
  getOAuthProviders() {
    return $http.get(`${url_prefix}/oauth/providers`);
  },
  oauthLogin(provider) {
    return $http.get(`${url_prefix}/oauth/${provider}/login`);
  },
  oauthCallback(provider, params) {
    // 将 params 作为查询参数传递
    return $http.get(`${url_prefix}/oauth/${provider}/callback-api`, {
      params,
    });
  },
};
