<template>
  <el-dialog
    v-model="visible"
    title="完成任务"
    width="500px"
    :before-close="handleClose"
    :close-on-click-modal="false"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="100px"
      label-position="left"
    >
      <el-form-item label="任务标题">
        <el-input
          :value="task?.title"
          readonly
          disabled
        />
      </el-form-item>
      
      <el-form-item label="实际工时" prop="actualHours" required>
        <el-input-number
          v-model="form.actualHours"
          :min="0"
          :max="999"
          :precision="1"
          :step="0.5"
          placeholder="请输入实际工时（小时）"
          style="width: 100%"
        />
        <div class="form-tip">
          <el-icon><InfoFilled /></el-icon>
          <span>请输入完成任务实际花费的时间</span>
        </div>
      </el-form-item>
      
      <el-form-item label="工作内容" prop="workContent">
        <el-input
          v-model="form.workContent"
          type="textarea"
          :rows="4"
          placeholder="请描述完成的工作内容（可选）"
          maxlength="500"
          show-word-limit
        />
        <div class="form-tip">
          <el-icon><InfoFilled /></el-icon>
          <span>简要描述完成的工作内容，将作为工作日志记录</span>
        </div>
      </el-form-item>
    </el-form>
    
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button
          type="primary"
          :loading="submitting"
          @click="handleSubmit"
        >
          完成任务
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { InfoFilled } from '@element-plus/icons-vue'
import type { Task } from '@/api/task'
import { taskApi } from '@/api/task'

interface Props {
  modelValue: boolean
  task: Task | null
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void
  (e: 'success'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const visible = ref(false)
const submitting = ref(false)
const formRef = ref<FormInstance>()

const form = reactive({
  actualHours: 0,
  workContent: ''
})

const rules: FormRules = {
  actualHours: [
    { required: true, message: '请输入实际工时', trigger: 'blur' },
    { type: 'number', min: 0.1, message: '工时必须大于0', trigger: 'blur' }
  ]
}

// 监听对话框显示状态
watch(() => props.modelValue, (newVal) => {
  visible.value = newVal
  if (newVal && props.task) {
    // 重置表单
    form.actualHours = props.task.estimated_hours || 0
    form.workContent = ''
  }
})

// 监听内部状态变化
watch(visible, (newVal) => {
  emit('update:modelValue', newVal)
})

const handleClose = () => {
  visible.value = false
}

const handleSubmit = async () => {
  if (!formRef.value || !props.task) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        submitting.value = true
        
        await taskApi.completeTask(
          props.task!.id,
          form.actualHours,
          form.workContent || undefined
        )
        
        ElMessage.success('任务完成成功')
        emit('success')
        handleClose()
        
      } catch (error: any) {
        ElMessage.error('完成任务失败：' + (error.response?.data?.detail || '未知错误'))
      } finally {
        submitting.value = false
      }
    }
  })
}
</script>

<style scoped>
.form-tip {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: 4px;
  font-size: 12px;
  color: #909399;
}

.form-tip .el-icon {
  font-size: 12px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

:deep(.el-form-item__label) {
  font-weight: 500;
}

:deep(.el-input-number) {
  width: 100%;
}

:deep(.el-textarea__inner) {
  resize: vertical;
}
</style>
