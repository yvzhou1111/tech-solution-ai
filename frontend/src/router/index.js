import { createRouter, createWebHistory } from 'vue-router'

// 导入视图组件
const HomeView = () => import('../views/HomeView.vue')
const ProjectView = () => import('../views/ProjectView.vue')
const HistoryView = () => import('../views/HistoryView.vue')
const NotFoundView = () => import('../views/NotFoundView.vue')

// 创建路由配置
const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView,
    meta: {
      title: '首页 - 技术方案生成AI'
    }
  },
  {
    path: '/project/:id',
    name: 'project',
    component: ProjectView,
    meta: {
      title: '项目详情 - 技术方案生成AI'
    }
  },
  {
    path: '/history',
    name: 'history',
    component: HistoryView,
    meta: {
      title: '历史记录 - 技术方案生成AI'
    }
  },
  {
    // 404页面
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: NotFoundView,
    meta: {
      title: '页面未找到 - 技术方案生成AI'
    }
  }
]

// 创建路由实例
const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

// 路由前置守卫 - 设置页面标题
router.beforeEach((to, from, next) => {
  // 设置文档标题
  if (to.meta.title) {
    document.title = to.meta.title
  }
  next()
})

export default router 