<template>
  <div class="quick-create-task-wrapper" @keydown="handleKeyDown" :tabindex="0">
    <!-- 快速创建任务弹窗 -->
    <el-dialog
        v-model="quickCreateVisible"
        title="快速创建任务"
        width="380px"
        :close-on-click-modal="false"
        :close-on-press-escape="false"
        :show-close="true"
        class="quick-create-dialog"
    >
      <div class="quick-create-form">
        <div class="form-section">
          <div class="input-group">
            <el-input
                ref="quickTaskInputRef"
                v-model="quickTaskTitle"
                placeholder="输入任务标题..."
                size="large"
                @keyup.enter="handleQuickCreateTask"
                @keyup.esc="cancelQuickCreate"
                clearable
                autofocus
            >
              <template #prefix>
                <el-icon><Edit /></el-icon>
              </template>
            </el-input>
          </div>
          
          <div class="options-group">
            <el-select
                v-model="quickTaskTeam"
                placeholder="选择团队"
                size="default"
                class="team-select"
            >
              <el-option
                  v-for="team in teams"
                  :key="team.id"
                  :label="team.name"
                  :value="team.id"
              />
            </el-select>
            
            <el-select
                v-model="quickTaskPriority"
                placeholder="优先级"
                size="default"
                class="priority-select"
            >
              <el-option label="低" value="low" />
              <el-option label="中" value="medium" />
              <el-option label="高" value="high" />
              <el-option label="紧急" value="urgent" />
            </el-select>
          </div>
        </div>
      </div>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="cancelQuickCreate" class="cancel-btn">取消</el-button>
          <el-button
              type="primary"
              @click="handleQuickCreateTask"
              :disabled="!quickTaskTitle.trim()"
              :loading="quickCreating"
              class="create-btn"
          >
            创建任务
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 插槽内容 -->
    <slot></slot>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Edit } from '@element-plus/icons-vue'
import { teamApi } from '@/api/team'
import { taskApi } from '@/api/task'
import type { Team } from '@/api/team'

// Props
interface Props {
  autoFocus?: boolean // 是否自动聚焦到输入框
}

const props = withDefaults(defineProps<Props>(), {
  autoFocus: true
})

// Emits
const emit = defineEmits<{
  taskCreated: [task: any]
  taskCreateError: [error: any]
}>()

// 响应式数据
const quickCreateVisible = ref(false)
const quickTaskInputRef = ref()
const quickTaskTitle = ref('')
const quickTaskTeam = ref<number>()
const quickTaskPriority = ref('medium')
const quickCreating = ref(false)
const teams = ref<Team[]>([])

// 双击空格键相关
const lastSpaceTime = ref(0)
const spaceKeyCount = ref(0)

// 处理键盘事件 - 双击空格键快速创建任务
const handleKeyDown = (event: KeyboardEvent) => {
  // 如果当前在输入框中，不处理空格键
  const target = event.target as HTMLElement
  if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.contentEditable === 'true') {
    return
  }
  
  // 检测双击空格键
  if (event.code === 'Space') {
    event.preventDefault() // 阻止默认的空格行为
    
    const currentTime = Date.now()
    if (currentTime - lastSpaceTime.value < 300) { // 300ms内的双击
      spaceKeyCount.value++
      if (spaceKeyCount.value >= 2) {
        showQuickCreateDialog()
        spaceKeyCount.value = 0
        lastSpaceTime.value = 0 // 重置时间，避免连续触发
      }
    } else {
      spaceKeyCount.value = 1
    }
    lastSpaceTime.value = currentTime
  }
}

// 显示快速创建任务弹窗
const showQuickCreateDialog = () => {
  quickCreateVisible.value = true
  quickTaskTitle.value = ''
  quickTaskTeam.value = teams.value.length > 0 ? teams.value[0].id : undefined
  quickTaskPriority.value = 'medium'
  
  // 下一个tick后聚焦输入框
  if (props.autoFocus) {
    setTimeout(() => {
      if (quickTaskInputRef.value) {
        quickTaskInputRef.value.focus()
      }
    }, 100)
  }
}

// 取消快速创建
const cancelQuickCreate = () => {
  quickCreateVisible.value = false
  quickTaskTitle.value = ''
  spaceKeyCount.value = 0
}

// 处理快速创建任务
const handleQuickCreateTask = async () => {
  if (!quickTaskTitle.value.trim()) {
    ElMessage.warning('请输入任务标题')
    return
  }
  
  if (!quickTaskTeam.value) {
    ElMessage.warning('请选择团队')
    return
  }
  
  try {
    quickCreating.value = true
    
    const taskData = {
      title: quickTaskTitle.value.trim(),
      team_id: quickTaskTeam.value,
      priority: quickTaskPriority.value as 'low' | 'medium' | 'high' | 'urgent',
      status: 'pending' as const,
      task_type: 'other' as const
    }
    
    const result = await taskApi.createTask(taskData)
    
    ElMessage.success('任务创建成功')
    quickCreateVisible.value = false
    quickTaskTitle.value = ''
    spaceKeyCount.value = 0
    
    // 触发事件
    emit('taskCreated', result)
  } catch (error: any) {
    console.error('快速创建任务失败:', error)
    const errorMessage = error.response?.data?.message || '创建任务失败'
    ElMessage.error(errorMessage)
    emit('taskCreateError', error)
  } finally {
    quickCreating.value = false
  }
}

// 获取团队列表
const fetchTeams = async () => {
  try {
    const response = await teamApi.getTeams()
    let teamsData: any[] = []
    
    if (response && typeof response === 'object') {
      const responseData = response as any
      if (responseData.data) {
        if (responseData.data.items && Array.isArray(responseData.data.items)) {
          teamsData = responseData.data.items
        } else if (Array.isArray(responseData.data)) {
          teamsData = responseData.data
        }
      } else if (responseData.items && Array.isArray(responseData.items)) {
        teamsData = responseData.items
      } else if (Array.isArray(responseData)) {
        teamsData = responseData
      }
    }
    
    teams.value = teamsData
  } catch (error) {
    console.error('获取团队列表失败:', error)
  }
}

// 暴露方法给父组件
defineExpose({
  showQuickCreateDialog,
  cancelQuickCreate
})

// 生命周期
onMounted(() => {
  fetchTeams()
})
</script>

<style scoped>
.quick-create-task-wrapper {
  outline: none; /* 移除tabindex的默认边框 */
}

/* 快速创建任务弹窗样式 - 现代化设计 */
.quick-create-dialog {
  :deep(.el-dialog) {
    border-radius: 12px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
    border: none;
    overflow: hidden;
    background: #ffffff;
  }
  
  :deep(.el-dialog__header) {
    padding: 20px 24px 16px;
    border-bottom: 1px solid #f0f0f0;
    background: #ffffff;
    margin: 0;
  }
  
  :deep(.el-dialog__title) {
    color: #1a1a1a;
    font-size: 16px;
    font-weight: 600;
    letter-spacing: 0.3px;
  }
  
  :deep(.el-dialog__headerbtn) {
    top: 18px;
    right: 20px;
  }
  
  :deep(.el-dialog__headerbtn .el-dialog__close) {
    color: #999999;
    font-size: 16px;
    transition: color 0.2s ease;
  }
  
  :deep(.el-dialog__headerbtn .el-dialog__close:hover) {
    color: #666666;
  }
  
  :deep(.el-dialog__body) {
    padding: 20px 24px;
    background: #ffffff;
  }
  
  :deep(.el-dialog__footer) {
    padding: 16px 24px 20px;
    border-top: 1px solid #f0f0f0;
    background: #ffffff;
  }
}

.quick-create-form {
  .form-section {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }
  
  .input-group {
    width: 100%;
  }
  
  .options-group {
    display: flex;
    gap: 12px;
  }
  
  .team-select {
    flex: 2;
  }
  
  .priority-select {
    flex: 1;
  }
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* 输入框样式优化 */
.quick-create-form :deep(.el-input__wrapper) {
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border: 1px solid #e0e0e0;
  transition: all 0.2s ease;
  background: #ffffff;
}

.quick-create-form :deep(.el-input__wrapper:hover) {
  border-color: #409eff;
  box-shadow: 0 2px 6px rgba(64, 158, 255, 0.15);
}

.quick-create-form :deep(.el-input__wrapper.is-focus) {
  border-color: #409eff;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.1);
}

.quick-create-form :deep(.el-input__inner) {
  font-size: 14px;
  color: #1a1a1a;
}

.quick-create-form :deep(.el-input__prefix) {
  color: #999999;
  font-size: 16px;
}

/* 选择框样式优化 */
.quick-create-form :deep(.el-select .el-input__wrapper) {
  border-radius: 6px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.08);
  border: 1px solid #e0e0e0;
  transition: all 0.2s ease;
}

.quick-create-form :deep(.el-select .el-input__wrapper:hover) {
  border-color: #409eff;
  box-shadow: 0 2px 4px rgba(64, 158, 255, 0.1);
}

.quick-create-form :deep(.el-select .el-input__wrapper.is-focus) {
  border-color: #409eff;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.1);
}

/* 按钮样式优化 */
.dialog-footer :deep(.el-button) {
  border-radius: 6px;
  font-weight: 500;
  padding: 8px 16px;
  font-size: 14px;
  transition: all 0.2s ease;
  border: 1px solid;
}

.dialog-footer :deep(.cancel-btn) {
  border-color: #e0e0e0;
  background: #ffffff;
  color: #666666;
}

.dialog-footer :deep(.cancel-btn:hover) {
  border-color: #c0c0c0;
  background: #f8f8f8;
  color: #333333;
}

.dialog-footer :deep(.create-btn) {
  background: #409eff;
  border-color: #409eff;
  color: #ffffff;
}

.dialog-footer :deep(.create-btn:hover) {
  background: #337ecc;
  border-color: #337ecc;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(64, 158, 255, 0.3);
}

.dialog-footer :deep(.create-btn:disabled) {
  background: #c0c4cc;
  border-color: #c0c4cc;
  color: #ffffff;
  transform: none;
  box-shadow: none;
}

/* 下拉菜单样式 */
.quick-create-form :deep(.el-select-dropdown) {
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  border: 1px solid #e0e0e0;
}

.quick-create-form :deep(.el-select-dropdown__item) {
  padding: 8px 12px;
  font-size: 14px;
}

.quick-create-form :deep(.el-select-dropdown__item:hover) {
  background: #f5f7fa;
}

.quick-create-form :deep(.el-select-dropdown__item.selected) {
  background: #409eff;
  color: #ffffff;
}
</style> 