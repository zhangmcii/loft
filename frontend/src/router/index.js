import { createRouter, createWebHistory } from "vue-router";
import routes from "./routes";

const router = createRouter({
  history: createWebHistory(import.meta.env.VITE_BASE),
  routes,
});

router.beforeEach((to, _from, next) => {
  try {
    const blogData = JSON.parse(localStorage.getItem("blog") || "{}");
    const { token = "", userInfo = {} } = blogData;
    const { roleId = 0 } = userInfo;

    const role = roleId === 3 ? "admin" : roleId;

    if (to.meta?.roles && !to.meta.roles.includes(role)) {
      next("/403");
    } else if (to.meta?.requireAuth && !token) {
      next("/login");
    } else {
      next();
    }
  } catch (error) {
    console.error("路由守卫解析用户数据失败:", error);
    if (to.meta?.requireAuth) {
      next("/login");
    } else {
      next();
    }
  }
});
export default router;
