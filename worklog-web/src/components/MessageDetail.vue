<template>
  <el-dialog 
    v-model="visible" 
    width="480px" 
    :title="message?.title || '消息详情'" 
    @close="onClose"
    :close-on-click-modal="false"
  >
    <div v-if="message" class="message-detail">
      <div class="msg-meta">
        <span class="msg-type">
          <el-tag :type="getTypeColor(message.message_type)" size="small">
            {{ typeLabel(message.message_type) }}
          </el-tag>
        </span>
        <span class="msg-time">{{ formatTime(message.created_at) }}</span>
      </div>
      
      <div class="msg-content" v-html="message.content"></div>
      
      <div v-if="message.message_data" class="msg-extra">
        <el-divider content-position="left">相关数据</el-divider>
        <pre class="msg-data">{{ JSON.stringify(message.message_data, null, 2) }}</pre>
      </div>
    </div>
    
    <template #footer>
      <div class="dialog-footer">
        <el-button v-if="!message?.is_read" type="primary" @click="markRead">
          <el-icon><Check /></el-icon>
          标为已读
        </el-button>
        <el-button type="danger" @click="del">
          <el-icon><Delete /></el-icon>
          删除
        </el-button>
        <el-button @click="visible = false">关闭</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, watch } from 'vue'
import { markMessageAsRead, deleteMessage } from '@/api/message'
import { ElMessageBox, ElMessage } from 'element-plus'
import { Check, Delete } from '@element-plus/icons-vue'

const props = defineProps({
  message: {
    type: Object,
    default: null
  },
  visible: {
    type: Boolean,
    default: false
  }
})

const emits = defineEmits(['update:visible', 'refresh'])

const visible = ref(props.visible)

watch(() => props.visible, (v) => {
  visible.value = v
})

watch(visible, (v) => {
  emits('update:visible', v)
})

function typeLabel(type) {
  const typeMap = {
    'task': '任务',
    'team': '团队', 
    'system': '系统',
    'worklog': '工作日志',
    'project': '项目',
    'user': '用户'
  }
  return typeMap[type] || type
}

function getTypeColor(type) {
  const colorMap = {
    'task': 'primary',
    'team': 'success',
    'system': 'warning',
    'worklog': 'info',
    'project': 'danger',
    'user': ''
  }
  return colorMap[type] || ''
}

function formatTime(time) {
  if (!time) return ''
  const date = new Date(time)
  const now = new Date()
  const diff = now - date
  
  // 如果是今天，显示时间
  if (diff < 24 * 60 * 60 * 1000 && date.toDateString() === now.toDateString()) {
    return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  }
  
  // 如果是昨天
  const yesterday = new Date(now)
  yesterday.setDate(yesterday.getDate() - 1)
  if (date.toDateString() === yesterday.toDateString()) {
    return '昨天 ' + date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  }
  
  // 其他显示完整日期时间
  return date.toLocaleString('zh-CN')
}

async function markRead() {
  try {
    await markMessageAsRead(props.message.id)
    ElMessage.success('已标为已读')
    emits('refresh')
    visible.value = false
  } catch (error) {
    ElMessage.error('操作失败')
    console.error('标记已读失败:', error)
  }
}

async function del() {
  try {
    await ElMessageBox.confirm('确定要删除该消息吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await deleteMessage(props.message.id)
    ElMessage.success('删除成功')
    emits('refresh')
    visible.value = false
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
      console.error('删除消息失败:', error)
    }
  }
}

function onClose() {
  emits('update:visible', false)
}
</script>

<style scoped>
.message-detail {
  max-height: 60vh;
  overflow-y: auto;
}

.msg-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f0f0;
}

.msg-time {
  color: #999;
  font-size: 13px;
}

.msg-content {
  min-height: 80px;
  margin-bottom: 16px;
  line-height: 1.6;
  word-break: break-word;
  white-space: pre-wrap;
}

.msg-extra {
  margin-top: 16px;
}

.msg-data {
  background: #f8f9fa;
  padding: 12px;
  border-radius: 4px;
  font-size: 12px;
  color: #666;
  max-height: 200px;
  overflow-y: auto;
  white-space: pre-wrap;
  word-break: break-all;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

:deep(.el-dialog__body) {
  padding: 20px;
}

:deep(.el-dialog__footer) {
  padding: 16px 20px;
  border-top: 1px solid #f0f0f0;
}
</style> 