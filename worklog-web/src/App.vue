<template>
  <div class="app-container" :class="{ 'floating-task-bar-page': isFloatingTaskBarPage }">
    <!-- 独立任务栏窗口 - 不显示任何导航和装饰 -->
    <template v-if="isFloatingTaskBarPage">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </template>
    
    <!-- 登录页面 - 不显示导航 -->
    <template v-else-if="isLoginPage">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </template>
    
    <!-- 注册页面 - 不显示导航 -->
    <template v-else-if="isRegisterPage">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </template>

    <!-- 正常页面 - 显示完整布局 -->
    <template v-else-if="userStore.isLoggedIn">
      <!-- 操作提示横幅 -->
      <OperationTips />
      
             <el-header class="app-header" height="60px">
         <div class="header-left">
           <Logo size="medium" :show-text="true" :clickable="true" @click="$router.push('/')" />
         </div>
        <div class="header-right">
          <!-- WebSocket状态指示器 - 只在用户登录时显示 -->
          <WebSocketStatus
            v-if="userStore.isLoggedIn"
            :is-connected="isConnected"
            :connection-state="connectionState"
            :unread-count="unreadCount"
          />

          <el-button v-if="userStore.isLoggedIn" type="primary" link @click="$router.push('/')">
            <el-icon><Monitor /></el-icon>
            工作看板
          </el-button>
          <el-button v-if="userStore.isLoggedIn" type="primary" link @click="$router.push('/calendar')">
            <el-icon><Calendar /></el-icon>
            日历视图
          </el-button>
          <el-button v-if="userStore.isLoggedIn" type="primary" link @click="$router.push('/messages')">
            <el-icon><Message /></el-icon>
            消息中心
            <span v-if="unreadCount > 0" class="message-badge">{{ unreadCount > 99 ? '99+' : unreadCount }}</span>
          </el-button>
          <!-- 隐藏测试按钮
          <el-button v-if="userStore.isLoggedIn" type="primary" link @click="$router.push('/websocket-test')">
            <el-icon><Connection /></el-icon>
            WebSocket测试
          </el-button>
          <el-button v-if="userStore.isLoggedIn" type="primary" link @click="$router.push('/notification-test')">
            <el-icon><Bell /></el-icon>
            通知测试
          </el-button>
          -->
          <el-button
            v-if="userStore.isLoggedIn"
            type="primary"
            link 
            @click="toggleTaskBar"
            :class="{ 'task-bar-active': showTaskBar }"
          >
            <el-icon><Timer /></el-icon>
            {{ showTaskBar ? '隐藏任务栏' : '显示任务栏' }}
          </el-button>
          <el-dropdown v-if="userStore.isLoggedIn" trigger="click">
            <el-avatar :size="32" :src="userAvatar">
              <el-icon><User /></el-icon>
            </el-avatar>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="$router.push('/profile')">
                  <el-icon><User /></el-icon>个人信息
                </el-dropdown-item>
                <el-dropdown-item @click="$router.push('/settings')">
                  <el-icon><Setting /></el-icon>系统设置
                </el-dropdown-item>
                <el-dropdown-item @click="$router.push('/download')">
                  <el-icon><Download /></el-icon>下载客户端
                </el-dropdown-item>
                <el-dropdown-item divided @click="handleLogout">
                  <el-icon><SwitchButton /></el-icon>退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
          <!-- 移除头部的工作模式切换按钮，改为在主页面显示 -->
        </div>
      </el-header>
      
      <div class="main-content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </div>
      
      <FloatingTaskBar 
        v-if="showTaskBar && userStore.isLoggedIn && !isLoginPage && !isRegisterPage"
        class="desktop-task-bar"
        @task-switched="handleTaskSwitched"
        @work-started="handleWorkStarted"
        @work-paused="handleWorkPaused"
      />

      <!-- 通知Toast组件 -->
      <NotificationToast ref="notificationToastRef" />
    </template>

    <!-- 用户未登录 - 重定向到登录页面 -->
    <template v-else>
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Monitor, Plus, Document, UserFilled, Folder, User, Setting, SwitchButton, Calendar, HomeFilled, Timer, Message, Connection, Bell, Download } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import { userApi } from '@/api/user'
import FloatingTaskBar from '@/components/FloatingTaskBar.vue'
import WebSocketStatus from '@/components/WebSocketStatus.vue'
import NotificationToast from '@/components/NotificationToast.vue'
import OperationTips from '@/components/OperationTips.vue'
import Logo from '@/components/Logo.vue'
// 移除头部的工作模式切换组件导入
import { useWebSocket } from '@/composables/useWebSocket'
import { useNotification } from '@/composables/useNotification'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const userAvatar = ref('')
const showTaskBar = ref(true) // 默认显示任务栏

// WebSocket相关
const { isConnected, connectionState, unreadCount } = useWebSocket()

// 通知系统
const { setToastRef, showTaskNotification, showTeamNotification, showSystemNotification } = useNotification()
const notificationToastRef = ref()

const isLoginPage = computed(() => {
  console.log('isLoginPage - 当前路由名称:', route.name)
  console.log('isLoginPage - 当前路由路径:', route.path)
  const isLogin = route.name === 'login'
  console.log('isLoginPage - 是否为登录页面:', isLogin)
  return isLogin
})

const isRegisterPage = computed(() => {
  console.log('isRegisterPage - 当前路由名称:', route.name)
  console.log('isRegisterPage - 当前路由路径:', route.path)
  const isRegister = route.name === 'register'
  console.log('isRegisterPage - 是否为注册页面:', isRegister)
  return isRegister
})

const isFloatingTaskBarPage = computed(() => {
  console.log('当前路由名称:', route.name)
  console.log('当前路由路径:', route.path)
  const isTaskBarPage = route.name === 'floating-task-bar-demo' || route.name === 'electron-task-bar-demo'
  console.log('是否为任务栏页面:', isTaskBarPage)
  return isTaskBarPage
})

// 切换任务栏显示状态
const toggleTaskBar = () => {
  showTaskBar.value = !showTaskBar.value
  // 保存到本地存储
  localStorage.setItem('showTaskBar', showTaskBar.value.toString())
  ElMessage.success(showTaskBar.value ? '任务栏已显示' : '任务栏已隐藏')
}

// 任务栏事件处理
const handleTaskSwitched = (task: any) => {
  console.log('任务已切换:', task)
  ElMessage.success(`已切换到任务: ${task.title}`)
}

const handleWorkStarted = (task: any) => {
  console.log('开始工作:', task)
  ElMessage.success(`开始为任务"${task.title}"工作`)
}

const handleWorkPaused = (task: any, duration: number) => {
  console.log('暂停工作:', task, '持续时间:', duration)
  ElMessage.success(`已暂停任务"${task.title}"，工作时长: ${Math.round(duration / 1000 / 60)}分钟`)
}

// 初始化用户状态
onMounted(async () => {
  // 从localStorage恢复用户状态
  userStore.initFromStorage()
  
  // 恢复任务栏显示状态
  const savedTaskBarState = localStorage.getItem('showTaskBar')
  if (savedTaskBarState !== null) {
    showTaskBar.value = savedTaskBarState === 'true'
  }
  
  const token = localStorage.getItem('token')
  
  // 设置通知Toast引用
  nextTick(() => {
    if (notificationToastRef.value) {
      setToastRef(notificationToastRef.value)
    }
  })
  

  
  if (token) {
    try {
      const user = await userApi.getCurrentUser() as any
      userStore.setUser({
        userId: user.id,
        username: user.username,
        email: user.email,
        role: user.role || 'user'
      })
    } catch (error) {
      console.error('获取用户信息失败:', error)
      userStore.logout()
      router.push('/login')
    }
  }
})

const handleLogout = () => {
  userStore.logout()
  ElMessage.success('退出成功')
  router.push('/login')
}
</script>

<style>
html, body {
  margin: 0;
  padding: 0;
  height: 100%;
  width: 100%;
  overflow-x: hidden;
  overflow-y: auto;
}

#app {
  height: 100%;
  width: 100%;
  overflow-x: hidden;
  overflow-y: auto;
}

.app-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  position: relative;
}

.app-main {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.app-header {
  background-color: #fff;
  border-bottom: 1px solid #e6e6e6;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  flex-shrink: 0;
  z-index: 1000;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-icon {
  font-size: 24px;
  color: #409eff;
}

.app-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.message-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 18px;
  height: 18px;
  padding: 0 6px;
  background: #f56c6c;
  color: white;
  border-radius: 9px;
  font-size: 12px;
  font-weight: bold;
  margin-left: 4px;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(245, 108, 108, 0.7);
  }
  70% {
    box-shadow: 0 0 0 6px rgba(245, 108, 108, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(245, 108, 108, 0);
  }
}

/* 任务栏按钮样式 */
.task-bar-active {
  background-color: #e6f7ff !important;
  color: #1890ff !important;
}

.main-content {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 12px;
  background-color: #f5f7fa;
  min-height: 0;
}

/* 桌面端任务栏样式 */
.desktop-task-bar {
  position: fixed !important;
  top: 80px !important;
  right: 20px !important;
  z-index: 9999 !important;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15) !important;
  border: 1px solid rgba(255, 255, 255, 0.3) !important;
  backdrop-filter: blur(20px) !important;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

.desktop-task-bar:hover {
  transform: translateY(-2px) !important;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.2) !important;
}

/* 优化滚动条样式 */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb {
  background: #c0c4cc;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #909399;
}

/* 全局紧凑布局 */
.el-card {
  margin-bottom: 12px !important;
}

.el-form-item {
  margin-bottom: 16px !important;
}

/* 页面切换动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@media (max-width: 768px) {
  .app-header {
    padding: 0 12px;
  }
  
  .app-title {
    font-size: 16px;
  }
  
  .main-content {
    padding: 10px;
  }
}

/* 独立任务栏页面样式 */
.app-container.floating-task-bar-page {
  height: 100vh !important;
  width: 100vw !important;
  margin: 0 !important;
  padding: 0 !important;
  overflow: hidden !important;
  background: transparent !important;
}

.app-container.floating-task-bar-page .app-header,
.app-container.floating-task-bar-page .main-content,
.app-container.floating-task-bar-page .desktop-task-bar {
  display: none !important;
}

/* 确保独立任务栏页面的内容完全占满 */
.app-container.floating-task-bar-page > * {
  width: 100% !important;
  height: 100% !important;
  margin: 0 !important;
  padding: 0 !important;
}
</style> 