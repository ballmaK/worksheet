<template>
  <div class="nav-menu" :class="{ 'is-collapsed': isCollapsed }">
    <div class="menu-header">
      <el-icon class="logo-icon"><Monitor /></el-icon>
      <span v-show="!isCollapsed" class="title">WorkLog Pro</span>
    </div>

    <el-menu
      :default-active="activeMenu"
      class="el-menu-vertical"
      :collapse="isCollapsed"
      :collapse-transition="false"
      router
    >
      <el-menu-item index="/">
        <el-icon><HomeFilled /></el-icon>
        <template #title>首页</template>
      </el-menu-item>

      <el-menu-item index="/calendar">
        <el-icon><Calendar /></el-icon>
        <template #title>日历视图</template>
      </el-menu-item>

      <el-menu-item index="/teams">
        <el-icon><UserFilled /></el-icon>
        <template #title>团队管理</template>
      </el-menu-item>

      <el-menu-item index="/worklogs">
        <el-icon><Document /></el-icon>
        <template #title>工作日志</template>
      </el-menu-item>

      <el-menu-item index="/electron-task-bar-demo">
        <el-icon><Monitor /></el-icon>
        <template #title>悬浮任务栏</template>
      </el-menu-item>

      <el-menu-item index="/settings">
        <el-icon><Setting /></el-icon>
        <template #title>系统设置</template>
      </el-menu-item>

      <el-menu-item index="/download">
        <el-icon><Download /></el-icon>
        <template #title>下载客户端</template>
      </el-menu-item>
    </el-menu>

    <div class="menu-footer">
      <el-button
        type="text"
        class="collapse-btn"
        @click="toggleCollapse"
      >
        <el-icon>
          <component :is="isCollapsed ? 'Expand' : 'Fold'" />
        </el-icon>
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import {
  HomeFilled,
  Calendar,
  UserFilled,
  Document,
  Setting,
  Expand,
  Fold,
  Monitor,
  Download
} from '@element-plus/icons-vue'

const route = useRoute()
const isCollapsed = ref(window.innerWidth <= 768)

// 监听窗口大小变化
const handleResize = () => {
  isCollapsed.value = window.innerWidth <= 768
}

onMounted(() => {
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})

const activeMenu = computed(() => route.path)

const toggleCollapse = () => {
  isCollapsed.value = !isCollapsed.value
}
</script>

<style scoped>
.nav-menu {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #304156;
  transition: width 0.3s;
  width: 240px;
}

.nav-menu.is-collapsed {
  width: 64px;
}

.menu-header {
  height: 60px;
  display: flex;
  align-items: center;
  padding: 0 20px;
  color: #fff;
  background-color: #263445;
}

.logo-icon {
  font-size: 24px;
  margin-right: 12px;
}

.title {
  font-size: 18px;
  font-weight: 600;
  white-space: nowrap;
}

.el-menu-vertical {
  flex: 1;
  border-right: none;
  background-color: transparent;
}

.el-menu-vertical:not(.el-menu--collapse) {
  width: 240px;
}

:deep(.el-menu-item) {
  height: 50px;
  line-height: 50px;
  color: #bfcbd9;
}

:deep(.el-menu-item.is-active) {
  color: #409EFF;
  background-color: #263445;
}

:deep(.el-menu-item:hover) {
  background-color: #263445;
}

:deep(.el-menu-item .el-icon) {
  color: inherit;
}

.menu-footer {
  padding: 12px;
  border-top: 1px solid #1f2d3d;
  display: flex;
  justify-content: center;
}

.collapse-btn {
  color: #bfcbd9;
  padding: 8px;
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}

.collapse-btn:hover {
  color: #409EFF;
  background-color: #263445;
  border-radius: 4px;
}

@media (max-width: 768px) {
  .nav-menu {
    position: fixed;
    z-index: 1000;
    box-shadow: 2px 0 8px rgba(0, 0, 0, 0.15);
  }

  .nav-menu.is-collapsed {
    transform: translateX(-100%);
  }

  .nav-menu:not(.is-collapsed) {
    transform: translateX(0);
  }
}
</style> 