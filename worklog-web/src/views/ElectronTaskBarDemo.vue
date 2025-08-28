<template>
  <div class="electron-task-bar-demo">
    <ElectronFloatingTaskBar />
  </div>
</template>

<script setup lang="ts">
import ElectronFloatingTaskBar from '@/components/ElectronFloatingTaskBar.vue'
</script>

<style scoped>
.electron-task-bar-demo {
  width: 100vw;
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}
</style> 