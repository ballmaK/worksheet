<template>
  <div class="mobile-worklog-form">
    <div class="form-header">
      <h3>记录工作日志</h3>
      <el-button type="primary" link @click="$emit('close')">
        <el-icon><Close /></el-icon>
      </el-button>
    </div>
    
    <el-form 
      ref="formRef" 
      :model="formData" 
      :rules="rules" 
      label-position="top"
      class="worklog-form"
    >
      <!-- 快速模板选择 -->
      <div class="template-section">
        <h4>快速模板</h4>
        <div class="template-buttons">
          <el-button 
            v-for="template in templates" 
            :key="template.id"
            size="small"
            @click="applyTemplate(template)"
            :type="selectedTemplate === template.id ? 'primary' : 'default'"
          >
            {{ template.name }}
          </el-button>
        </div>
      </div>
      
      <!-- 工作内容 -->
      <el-form-item label="工作内容" prop="content">
        <el-input
          v-model="formData.content"
          type="textarea"
          :rows="6"
          placeholder="请详细描述今天的工作内容..."
          maxlength="1000"
          show-word-limit
        />
      </el-form-item>
      
      <!-- 工作时间 -->
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="开始时间" prop="start_time">
            <el-time-picker
              v-model="formData.start_time"
              placeholder="选择时间"
              format="HH:mm"
              value-format="HH:mm"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="结束时间" prop="end_time">
            <el-time-picker
              v-model="formData.end_time"
              placeholder="选择时间"
              format="HH:mm"
              value-format="HH:mm"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
      </el-row>
      
      <!-- 工作类型 -->
      <el-form-item label="工作类型" prop="work_type">
        <el-select v-model="formData.work_type" placeholder="选择工作类型" style="width: 100%">
          <el-option label="功能开发" value="feature" />
          <el-option label="Bug修复" value="bug" />
          <el-option label="改进优化" value="improvement" />
          <el-option label="文档工作" value="documentation" />
          <el-option label="会议" value="meeting" />
          <el-option label="调研" value="research" />
          <el-option label="其他" value="other" />
        </el-select>
      </el-form-item>
      
      <!-- 关联任务 -->
      <el-form-item label="关联任务" prop="task_id">
        <el-select 
          v-model="formData.task_id" 
          placeholder="选择关联任务（可选）" 
          clearable
          filterable
          style="width: 100%"
        >
          <el-option
            v-for="task in myTasks"
            :key="task.id"
            :label="task.title"
            :value="task.id"
          />
        </el-select>
      </el-form-item>
      
      <!-- 工作成果 -->
      <el-form-item label="工作成果" prop="achievements">
        <el-input
          v-model="formData.achievements"
          type="textarea"
          :rows="3"
          placeholder="描述今天的工作成果和进展..."
          maxlength="500"
          show-word-limit
        />
      </el-form-item>
      
      <!-- 遇到的问题 -->
      <el-form-item label="遇到的问题" prop="issues">
        <el-input
          v-model="formData.issues"
          type="textarea"
          :rows="3"
          placeholder="描述遇到的问题和解决方案..."
          maxlength="500"
          show-word-limit
        />
      </el-form-item>
      
      <!-- 明日计划 -->
      <el-form-item label="明日计划" prop="next_plan">
        <el-input
          v-model="formData.next_plan"
          type="textarea"
          :rows="3"
          placeholder="描述明天的工作计划..."
          maxlength="500"
          show-word-limit
        />
      </el-form-item>
    </el-form>
    
    <!-- 操作按钮 -->
    <div class="form-actions">
      <el-button @click="$emit('close')" size="large">取消</el-button>
      <el-button type="primary" @click="submitForm" size="large" :loading="loading">
        提交日志
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElForm } from 'element-plus'
import { Close } from '@element-plus/icons-vue'
import { workLogApi } from '@/api/workLog'
import { taskApi } from '@/api/task'

const emit = defineEmits<{
  close: []
  submitted: [workLog: any]
}>()

const formRef = ref<InstanceType<typeof ElForm>>()
const loading = ref(false)
const selectedTemplate = ref<number | null>(null)
const myTasks = ref([])

// 快速模板
const templates = ref([
  { id: 1, name: '日常开发', content: '今日主要进行功能开发和代码优化工作。' },
  { id: 2, name: '问题修复', content: '今日主要处理bug修复和问题排查工作。' },
  { id: 3, name: '会议讨论', content: '今日参加项目会议，讨论项目进展和下一步计划。' },
  { id: 4, name: '文档编写', content: '今日主要进行技术文档编写和整理工作。' }
])

const formData = reactive({
  content: '',
  start_time: '',
  end_time: '',
  work_type: '',
  task_id: null,
  achievements: '',
  issues: '',
  next_plan: ''
})

const rules = {
  content: [
    { required: true, message: '请输入工作内容', trigger: 'blur' }
  ],
  work_type: [
    { required: true, message: '请选择工作类型', trigger: 'change' }
  ]
}

const applyTemplate = (template: any) => {
  selectedTemplate.value = template.id
  formData.content = template.content
}

const fetchMyTasks = async () => {
  try {
    const response = await taskApi.getTasks({ assignee_id: 'me' })
    myTasks.value = response.items || []
  } catch (error) {
    console.error('获取任务失败:', error)
  }
}

const submitForm = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    loading.value = true
    
    const workLogData = {
      ...formData,
      date: new Date().toISOString().split('T')[0]
    }
    
    const result = await workLogApi.createWorkLog(workLogData)
    ElMessage.success('工作日志提交成功')
    emit('submitted', result)
  } catch (error) {
    console.error('提交失败:', error)
    ElMessage.error('提交失败，请重试')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchMyTasks()
})
</script>

<style scoped>
.mobile-worklog-form {
  background: white;
  border-radius: 16px 16px 0 0;
  padding: 20px;
  max-height: 90vh;
  overflow-y: auto;
}

.form-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e4e7ed;
}

.form-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.template-section {
  margin-bottom: 20px;
}

.template-section h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #606266;
}

.template-buttons {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.worklog-form {
  margin-bottom: 20px;
}

.form-actions {
  display: flex;
  gap: 12px;
  padding-top: 20px;
  border-top: 1px solid #e4e7ed;
}

.form-actions .el-button {
  flex: 1;
  min-height: 44px;
}

/* 移动端优化 */
@media (max-width: 768px) {
  .mobile-worklog-form {
    padding: 16px;
    border-radius: 12px 12px 0 0;
  }
  
  .form-header {
    margin-bottom: 16px;
    padding-bottom: 12px;
  }
  
  .form-header h3 {
    font-size: 16px;
  }
  
  .template-buttons {
    gap: 6px;
  }
  
  .template-buttons .el-button {
    font-size: 12px;
    padding: 6px 12px;
  }
  
  .form-actions {
    padding-top: 16px;
  }
}

@media (max-width: 480px) {
  .mobile-worklog-form {
    padding: 12px;
  }
  
  .form-header {
    margin-bottom: 12px;
    padding-bottom: 8px;
  }
  
  .template-buttons {
    flex-direction: column;
  }
  
  .template-buttons .el-button {
    width: 100%;
    justify-content: center;
  }
  
  .form-actions {
    flex-direction: column;
    gap: 8px;
  }
}

/* 触摸优化 */
@media (hover: none) and (pointer: coarse) {
  .el-button {
    min-height: 44px;
  }
  
  .el-input,
  .el-select,
  .el-time-picker {
    min-height: 44px;
  }
}
</style> 