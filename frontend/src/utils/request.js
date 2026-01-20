import { useCurrentUserStore } from "@/stores/user";
import errorManager from "@/utils/message";
import router from "../router/index.js";
import axios from "axios";

const $http = axios.create({
  baseURL: import.meta.env.VITE_APP_BASE_API ?? "/",
  timeout: 10000,
});

const REFRESH_URL = "/auth/refresh";
const FRESH_REQUIRED_MESSAGE = "该操作需要重新登录以验证身份";
const EXPIRED_MESSAGE = "身份已过期";
const TOKEN_KEY = "blog";

// 刷新状态管理
let isRefreshing = false;
let pendingQueue = [];

// 获取token的安全方法
function getToken(type = "access_token") {
  try {
    const blogData = JSON.parse(localStorage.getItem(TOKEN_KEY) || "{}");
    return blogData[type] || "";
  } catch {
    return "";
  }
}

// 处理登出
export function handleUnauthorized() {
  const store = useCurrentUserStore();
  if (store.access_token) {
    store.logOut();
    router.push("/login");
  }
}

// 处理队列中的请求
function processQueue(error, newToken = null) {
  pendingQueue.forEach(({ resolve, reject }) => {
    if (error) {
      reject(error);
    } else {
      resolve(newToken);
    }
  });
  pendingQueue = [];
}

// 刷新token
async function refreshToken() {
  const store = useCurrentUserStore();
  const refreshToken = getToken("refresh_token");

  // 使用独立的axios实例，避免循环调用拦截器
  const res = await axios.post(REFRESH_URL, null, {
    headers: { Authorization: refreshToken },
    baseURL: import.meta.env.VITE_APP_BASE_API ?? "/",
    timeout: 10000,
  });

  // 后端返回格式: { code: 200, data: { access_token: "Bearer xxx" } }
  if (res.data.code !== 200) {
    throw new Error(res.data.message || "刷新token失败");
  }

  const accessToken = res.data.data.access_token;
  store.access_token = accessToken;
  return accessToken;
}

// 重试请求
function retryRequest(config, token) {
  config.headers.Authorization = token;
  return $http(config);
}

// 处理401 token过期
function handleTokenExpired(config) {
  // 刷新接口自己报错，直接登出
  if (config.url.includes(REFRESH_URL)) {
    errorManager.warning("您的身份已过期, 请重新登录");
    handleUnauthorized();
    return Promise.reject();
  }

  // 已经在刷新，排队等待
  if (isRefreshing) {
    return new Promise((resolve, reject) => {
      pendingQueue.push({
        resolve: (token) => resolve(retryRequest(config, token)),
        reject,
      });
    });
  }

  // 开始刷新
  isRefreshing = true;
  console.log("刷新token开始...");
  return refreshToken()
    .then((newToken) => {
      console.log("刷新token结束...");
      processQueue(null, newToken);
      console.log("请求开始重试...");
      return retryRequest(config, newToken);
    })
    .catch((refreshError) => {
      // 如果是401错误，说明refresh_token也过期了
      if (refreshError.response?.status === 401) {
        errorManager.warning("您的身份已过期, 请重新登录");
      }
      processQueue(refreshError, null);
      handleUnauthorized();
      return Promise.reject(refreshError);
    })
    .finally(() => {
      isRefreshing = false;
    });
}

// 处理标准响应（有code字段）
function handleStandardResponse(response) {
  const { code, message } = response.data;

  if (code === 200) {
    return response.data;
  }

  if (code === 401 && message === FRESH_REQUIRED_MESSAGE) {
    // 提示用户需要重新登录
    errorManager.warning("为了您的账户安全，请重新登录");
    handleUnauthorized();
    return Promise.reject(new Error(FRESH_REQUIRED_MESSAGE));
  }

  if (code === 401 && message === EXPIRED_MESSAGE) {
    return handleTokenExpired(response.config);
  }

  errorManager.error(message || "请求失败");
  return Promise.reject(message);
}

// 处理HTTP错误
function handleHttpError(error) {
  const { status, data } = error.response || {};

  // 网络错误
  if (!error.response) {
    errorManager.error("服务器响应超时");
    return Promise.reject(error);
  }

  // 状态码路由处理
  const statusHandlers = {
    401: () => {
      errorManager.error("您的身份未认证, 请重新登录");
      router.push("/login");
    },
    403: () => router.push("/403"),
    404: () => router.push("/404"),
    500: () => router.push("/500"),
    400: () => errorManager.error("接口报错"),
    429: () => {},
  };

  const handler = statusHandlers[status];
  if (handler) {
    handler();
  } else if (data?.code && typeof data.code === "number" && data.code !== 200) {
    errorManager.error(data.message || "请求失败，请稍后重试！");
  } else if (!data) {
    errorManager.error("请求失败，请稍后重试！");
  }

  return Promise.reject(error);
}

// 日志辅助函数
function logRequest(config) {
  console.log("==>请求开始");
  console.log(`${config.baseURL}${config.url}`);
  if (config.data) {
    console.log("==>请求数据", config.data);
  }
}

function logResponse(response) {
  console.log(response);
  console.log("==>请求结束");
}

function logError(error) {
  console.log(error);
  console.log("==>请求结束");
}

/**
 * 设置网络请求监听
 */
function setInterceptors(...instance) {
  instance.forEach((i) => {
    // 请求拦截器
    i.interceptors.request.use(
      (config) => {
        // 统一根据 useRefreshToken 配置获取 token
        const tokenType = config.useRefreshToken
          ? "refresh_token"
          : "access_token";
        const token = getToken(tokenType);
        if (token) {
          config.headers.Authorization = token;
        }

        logRequest(config);
        return config;
      },
      (error) => {
        logError(error);
        errorManager.error(error);
        return Promise.reject(error);
      }
    );

    // 响应拦截器
    i.interceptors.response.use((response) => {
      logResponse(response);

      if (response.status !== 200) {
        return Promise.reject(response);
      }

      // 标准响应格式（有code字段）
      if (response.data.code !== undefined) {
        return handleStandardResponse(response);
      }

      // 其他格式直接返回
      return response;
    }, handleHttpError);
  });
}

setInterceptors($http);

export { $http };
