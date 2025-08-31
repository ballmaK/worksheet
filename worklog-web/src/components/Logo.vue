<template>
  <div class="logo-container" :class="[`logo-${size}`, { 'logo-clickable': clickable }]" @click="handleClick">
    <img 
      src="@/assets/worklog-logo.jpg" 
      alt="WorkLog Pro" 
      class="logo-image"
    />
    <span v-if="showText" class="logo-text">WorkLog Pro</span>
  </div>
</template>

<script setup lang="ts">
interface Props {
  size?: 'small' | 'medium' | 'large'
  showText?: boolean
  clickable?: boolean
}

interface Emits {
  (e: 'click'): void
}

const props = withDefaults(defineProps<Props>(), {
  size: 'medium',
  showText: true,
  clickable: false
})

const emit = defineEmits<Emits>()

const handleClick = () => {
  if (props.clickable) {
    emit('click')
  }
}
</script>

<style scoped>
.logo-container {
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
}

.logo-image {
  display: block;
  flex-shrink: 0;
  object-fit: contain;
  border-radius: 4px;
}

.logo-text {
  font-weight: 600;
  color: #303133;
  white-space: nowrap;
}

/* 尺寸变体 */
.logo-small .logo-image {
  width: 24px;
  height: 24px;
}

.logo-small .logo-text {
  font-size: 14px;
}

.logo-medium .logo-image {
  width: 32px;
  height: 32px;
}

.logo-medium .logo-text {
  font-size: 18px;
}

.logo-large .logo-image {
  width: 120px;
  height: 120px;
}

.logo-large .logo-text {
  font-size: 32px;
  font-weight: 700;
}

/* 可点击样式 */
.logo-clickable {
  cursor: pointer;
}

.logo-clickable:hover {
  transform: scale(1.05);
}

.logo-clickable:active {
  transform: scale(0.95);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .logo-large .logo-image {
    width: 80px;
    height: 80px;
  }
  
  .logo-large .logo-text {
    font-size: 24px;
  }
  
  .logo-medium .logo-image {
    width: 28px;
    height: 28px;
  }
  
  .logo-medium .logo-text {
    font-size: 16px;
  }
}
</style>
