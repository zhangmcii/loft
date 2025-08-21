import { createRouter, createWebHistory } from 'vue-router'
import routes from './routes'


const router = createRouter({
  history: createWebHistory(import.meta.env.VITE_BASE),
  routes
})

router.beforeEach((to, _from, next) => {
  let j = JSON.parse(localStorage.getItem('blog'))
  if (!j) {
    j = {
      token: '',
      userInfo: {
        roleId: '',
      }
    }
  }
  const r = j.userInfo.roleId

  const role = r === 3 ? 'admin' : r

  // 无权限跳转403页面
  if (to.meta?.roles && !to.meta?.roles.includes(role)) {
    next({ path: '/403' })
  } else if (to.meta?.requireAuth && !j.token) {
    // 判断是否需要登录
    next({ path: '/login' })
  } else {
    next()
  }
})
export default router
