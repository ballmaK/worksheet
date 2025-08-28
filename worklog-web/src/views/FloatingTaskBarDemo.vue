<template>
  <div class="floating-task-bar-demo">
    <ElectronFloatingTaskBar />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import ElectronFloatingTaskBar from '@/components/ElectronFloatingTaskBar.vue'

const route = useRoute()

const isTaskBarPage = computed(() => {
  return route.name === 'floating-task-bar-demo' || route.name === 'electron-task-bar-demo'
})
</script>

<style scoped>
/* 独立任务栏窗口样式 - 隐藏所有导航和装饰 */
.floating-task-bar-demo {
  width: 100%;
  height: 100%;
  margin: 0;
  padding: 0;
  overflow: hidden;
  background: transparent;
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
}

/* 确保任务栏组件完全占满窗口 */
.floating-task-bar-demo :deep(.floating-task-bar) {
  width: 100% !important;
  height: 100% !important;
  border-radius: 0 !important;
  margin: 0 !important;
  padding: 0 !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  overflow: hidden !important;
}

/* 隐藏任何可能的滚动条 */
.floating-task-bar-demo :deep(*) {
  box-sizing: border-box;
}
</style>

<style>
/* 全局样式覆盖 - 在独立任务栏页面中隐藏所有header和导航 */
.floating-task-bar-demo ~ .app-header,
.floating-task-bar-demo ~ .el-header,
.floating-task-bar-demo ~ header,
.floating-task-bar-demo ~ .header,
.floating-task-bar-demo ~ .nav,
.floating-task-bar-demo ~ .navigation {
  display: none !important;
}

/* 确保body和html在任务栏页面中没有额外的margin和padding */
body.floating-task-bar-page,
html.floating-task-bar-page {
  margin: 0 !important;
  padding: 0 !important;
  overflow: hidden !important;
  width: 100% !important;
  height: 100% !important;
}

/* 隐藏Element Plus可能添加的全局元素 */
.floating-task-bar-demo ~ .el-message,
.floating-task-bar-demo ~ .el-notification {
  display: none !important;
}
</style> 