import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'
import Teams from '@/views/Teams.vue'
import Projects from '@/views/Projects.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/Home.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/Login.vue')
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('@/views/Register.vue')
    },
    {
      path: '/verify-invitation',
      name: 'verify-invitation',
      component: () => import('@/views/VerifyInvitation.vue')
    },
    {
      path: '/teams',
      name: 'Teams',
      component: Teams
    },
    {
      path: '/projects',
      name: 'Projects',
      component: Projects
    },
    {
      path: '/projects/:projectId',
      name: 'project-management',
      component: () => import('@/views/ProjectManagement.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/teams/:teamId/members',
      name: 'team-members',
      component: () => import('@/views/TeamMembers.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/teams/:teamId/projects',
      name: 'team-projects',
      component: () => import('@/views/TeamProjects.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/teams/:teamId/work-logs',
      name: 'team-work-logs',
      component: () => import('@/views/work-log/TeamWorkLogs.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/teams/:teamId/tasks',
      name: 'team-tasks',
      component: () => import('@/views/TaskManagement.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/tasks',
      name: 'tasks',
      component: () => import('@/views/TaskManagement.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/calendar',
      name: 'calendar',
      component: () => import('@/views/Calendar.vue'),
      meta: { requiresAuth: true }
    },
    // 隐藏demo路由
    /*
    {
      path: '/calendar-demo',
      name: 'CalendarDemo',
      component: CalendarDemo
    },
    */
    {
      path: '/my-teams',
      name: 'MyTeams',
      component: () => import('@/views/MyTeams.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/teams/:teamId/manage',
      name: 'team-manage',
      component: () => import('@/views/TeamManagement.vue'),
      meta: { requiresAuth: true }
    },
    // 隐藏其他demo路由
    /*
    {
      path: '/floating-task-bar-demo',
      name: 'floating-task-bar-demo',
      component: () => import('@/views/FloatingTaskBarDemo.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/electron-task-bar-demo',
      name: 'electron-task-bar-demo',
      component: () => import('@/views/ElectronTaskBarDemo.vue'),
      meta: { requiresAuth: true }
    },
    */
    {
      path: '/messages',
      name: 'messages',
      component: () => import('@/views/MessageCenter.vue'),
      meta: { requiresAuth: true }
    }
    // 隐藏测试路由
    /*
    {
      path: '/websocket-test',
      name: 'websocket-test',
      component: () => import('@/views/WebSocketTest.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/notification-test',
      name: 'notification-test',
      component: () => import('@/views/NotificationTest.vue'),
      meta: { requiresAuth: true }
    }
    */
  ]
})

// 路由守卫
router.beforeEach((to, from, next) => {
  console.log('=== 路由守卫开始 ===')
  console.log('路由守卫 - 目标路由名称:', to.name)
  console.log('路由守卫 - 目标路由路径:', to.path)
  console.log('路由守卫 - 目标路由meta:', to.meta)
  console.log('路由守卫 - 来源路由名称:', from.name)
  console.log('路由守卫 - 来源路由路径:', from.path)
  
  const userStore = useUserStore()
  console.log('路由守卫 - 用户登录状态:', userStore.isLoggedIn)
  console.log('路由守卫 - 用户token:', userStore.token ? '存在' : '不存在')
  
  // 检查是否需要认证
  const requiresAuth = to.meta.requiresAuth === true
  console.log('路由守卫 - 是否需要认证:', requiresAuth)
  
  if (requiresAuth && !userStore.isLoggedIn) {
    console.log('路由守卫 - 需要认证但未登录，重定向到登录页面')
    next({ name: 'login' })
  } else {
    console.log('路由守卫 - 允许访问目标路由')
    next()
  }
  console.log('=== 路由守卫结束 ===')
})

export default router 