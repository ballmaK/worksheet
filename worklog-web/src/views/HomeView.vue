<template>
  <div class="home-view">
    <nav-menu class="nav-menu" />
    <div class="main-content" :class="{ 'is-collapsed': isCollapsed }">
      <router-view />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import NavMenu from '@/components/NavMenu.vue'

const isCollapsed = ref(window.innerWidth <= 768)

const handleResize = () => {
  isCollapsed.value = window.innerWidth <= 768
}

onMounted(() => {
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.home-view {
  display: flex;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
}

.nav-menu {
  flex-shrink: 0;
}

.main-content {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  transition: margin-left 0.3s;
  margin-left: 240px;
  background-color: #f5f7fa;
}

.main-content.is-collapsed {
  margin-left: 64px;
}

@media (max-width: 768px) {
  .main-content {
    margin-left: 0;
  }
  
  .main-content.is-collapsed {
    margin-left: 0;
  }
}
</style> 