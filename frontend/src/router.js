import { createRouter, createWebHistory } from 'vue-router'
import AdminLogin from './pages/AdminLogin.vue'
import AdminHome from './pages/AdminHome.vue'
import SurveyFill from './pages/SurveyFill.vue'
import { getAdminToken } from './utils/api'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/admin/login', component: AdminLogin },
    { path: '/admin', component: AdminHome },
    { path: '/s/:token', component: SurveyFill },
    { path: '/', redirect: '/admin/login' }
  ]
})

router.beforeEach((to) => {
  if (to.path.startsWith('/admin') && to.path !== '/admin/login') {
    if (!getAdminToken()) {
      return '/admin/login'
    }
  }
  return true
})

export default router
