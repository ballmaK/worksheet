<template>
  <el-dialog
      v-model="visible"
      title="分配任务"
      width="500px"
      :close-on-click-modal="false"
  >
    <div class="assign-dialog-content">
      <p class="assign-description">
        请选择负责人来分配任务「{{ task?.title }}」
      </p>

      <el-form :model="assignForm" :rules="assignRules" ref="assignFormRef" label-width="80px">
        <el-form-item label="负责人" prop="assignee_id">
          <el-select v-model="assignForm.assignee_id" placeholder="选择负责人" class="w-full">
            <el-option
                v-for="member in availableMembers"
                :key="member.id"
                :label="member.username"
                :value="member.user_id"
            >
              <div class="member-option">
                <el-avatar :size="24" :src="member.avatar">
                  {{ member.username[0].toUpperCase() }}
                </el-avatar>
                <span>{{ member.username }}</span>
              </div>
            </el-option>
          </el-select>
        </el-form-item>
      </el-form>
    </div>

    <template #footer>
      <el-button @click="close">取消</el-button>
      <el-button
          type="primary"
          @click="handleAssign"
          :loading="assigning"
          :disabled="!assignForm.assignee_id"
      >
        确认分配
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import type { Task } from '@/api/task'

// Props
interface Props {
  visible?: boolean
  task?: Task | null
  availableMembers?: any[]
}

const props = withDefaults(defineProps<Props>(), {
  visible: false,
  task: null,
  availableMembers: () => []
})

// Emits
const emit = defineEmits<{
  'update:visible': [value: boolean]
  'assign': [assigneeId: number]
}>()

// 本地状态
const visible = ref(props.visible)
const assigning = ref(false)
const assignFormRef = ref()
const assignForm = ref({
  assignee_id: null as number | null
})

// 分配任务验证规则
const assignRules = {
  assignee_id: [{ required: true, message: '请选择负责人', trigger: 'change' }]
}

// 监听visible变化
watch(visible, (newValue) => {
  emit('update:visible', newValue)
})

watch(() => props.visible, (newValue) => {
  visible.value = newValue
})

// 方法
const close = () => {
  visible.value = false
  assignForm.value.assignee_id = null
}

const handleAssign = async () => {
  try {
    await assignFormRef.value.validate()
    assigning.value = true
    
    if (assignForm.value.assignee_id) {
      emit('assign', assignForm.value.assignee_id)
    }
  } catch (error) {
    console.error('表单验证失败:', error)
  } finally {
    assigning.value = false
  }
}
</script>

<style scoped>
.assign-dialog-content {
  padding: 20px;
}

.assign-description {
  margin-bottom: 20px;
  font-size: 16px;
  font-weight: 500;
}

.member-option {
  display: flex;
  align-items: center;
  gap: 8px;
}

.w-full {
  width: 100%;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .assign-dialog-content {
    padding: 16px;
  }
}
</style> 