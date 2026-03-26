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
  setPassword(params) {
    return $http.post(`${url_prefix}/setPassword`, params);
  },
  checkTokenFreshness() {
    return $http.get(`${url_prefix}/checkFreshness`);
  },
  oauthProviders() {
    // return $http.get(`${url_prefix}/oauth/providers`);
    return new Promise((resolve) => {
      resolve({
        code: 200,
        data: {
          providers: [
            {
              authorize_endpoint: "/auth/oauth/authorize/qq",
              name: "qq",
              provider: "qq",
            },
            {
              authorize_endpoint: "/auth/oauth/authorize/github",
              name: "github",
              provider: "github",
            },
          ],
        },
      });
    });
  },
  oauthAuthorize(provider, params = {}) {
    return $http.get(`${url_prefix}/oauth/authorize/${provider}`, { params });
  },
  oauthBind(provider) {
    return $http.post(`${url_prefix}/oauth/bind/${provider}`);
  },
  oauthUnbind(provider) {
    return $http.post(`${url_prefix}/oauth/unbind/${provider}`);
  },
};
