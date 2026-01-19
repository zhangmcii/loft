import { useCurrentUserStore } from "@/stores/user";
import errorManager from "@/utils/message";
import router from "../router/index.js";
import axios from "axios";

const $http = axios.create({
  // 后端api的base_url
  baseURL: import.meta.env.VITE_APP_BASE_API ?? "/",
  timeout: 10000,
});

export function handleUnauthorized() {
  const store = useCurrentUserStore();
  if (store.access_token) {
    store.logOut();
    router.push("/login");
  }
}

/**
 * 设置网路请求监听
 */
function setInterceptors(...instance) {
  instance.forEach((i) => {
    i.interceptors.request.use(
      function (config) {
        let token = "";
        if (config.url == "/auth/refresh") {
          // 从localStorage中获取token。注意，不可以从pinia中读取，因为刷新页面，此时组件可能还未初始化完
          token = JSON.parse(localStorage.getItem("blog"))?.refresh_token;
        } else {
          token = JSON.parse(localStorage.getItem("blog"))?.access_token;
        }
        if (token) {
          config.headers["Authorization"] = token;
        }

        console.log("==>请求开始");
        console.log(`${config.baseURL}${config.url}`);
        if (config.data) {
          console.log("==>请求数据", config.data);
        }
        return config;
      },
      function (error) {
        // 对请求错误做些什么
        console.log("==>请求开始");
        console.log(error);

        errorManager.error(error);
        return Promise.reject(error);
      }
    );

    i.interceptors.response.use(
      function (response) {
        // 2xx 范围内的状态码都会触发该函数。
        console.log(response);
        console.log("==>请求结束");

        if (response.status == 200) {
          // 处理新的统一接口返回格式
          if (response.data.code !== undefined) {
            if (response.data.code === 200) {
              // 成功响应，返回完整响应数据（包括code、message、data和其他字段如total）
              return response.data;
            } else {
              // 业务错误，显示错误消息
              if (
                response.data.code === 401 &&
                response.data.message == "身份已过期"
              ) {
                errorManager.warning("您的身份已过期, 请重新登录");
                handleUnauthorized();
                return Promise.reject();
              }
              errorManager.error(response.data.message || "请求失败");
              return Promise.reject(response.data.message);
            }
          } else {
            // 其他情况，直接返回响应
            return response;
          }
        } else {
          return Promise.reject(response);
        }
      },
      function (error) {
        // 超出 2xx 范围的状态码都会触发该函数。
        console.log(error);
        console.log("==>请求结束");

        if (error.response === undefined) {
          errorManager.error("服务器响应超时");
          return Promise.reject(error);
        }
        if (error.response.status >= 500) {
          router.push("/500");
          return Promise.reject(error);
        }
        if (error.response.status === 404) {
          router.push("/404");
          return Promise.reject(error);
        }
        if (error.response.status === 400) {
          errorManager.error("接口报错");
          return Promise.reject(error);
        }
        if (error.response.status === 401) {
          errorManager.error("您的身份未认证, 请重新登录");
          router.push("/login");
          return Promise.reject(error);
        }
        if (error.response.status === 429) {
          return Promise.reject(error);
        }

        if (error.response.status === 403) {
          router.push("/403");
          return Promise.reject(error);
        } else {
          const data = error.response.data;
          if (data === null || data === undefined) {
            errorManager.error("请求失败，请稍后重试！");
            return Promise.reject(error);
          } else {
            // 处理新的统一接口返回格式的错误
            const resCode = data.code;
            if (resCode && typeof resCode == "number" && resCode !== 200) {
              errorManager.error(data.message || "请求失败，请稍后重试！");
            }
            return Promise.reject(error);
          }
        }
      }
    );
  });
}

//添加拦截器
setInterceptors($http);

export { $http };
