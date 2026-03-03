<template>
  <div class="desktop-widget" :class="{ dragging: isDragging }">
    <!-- 标题栏：拖拽区域 + 钉住/关闭 -->
    <header
      class="widget-header"
      @mousedown="startDrag"
    >
      <span class="widget-title">当日待办</span>
      <div class="header-actions">
        <button
          type="button"
          class="pin-btn"
          :class="{ pinned: isPinned }"
          :title="isPinned ? '取消置顶' : '钉在桌面'"
          @mousedown.stop
          @click="togglePin"
        >
          <el-icon><Pointer /></el-icon>
        </button>
        <button
          type="button"
          class="close-btn"
          title="收起"
          @mousedown.stop
          @click="hideWindow"
        >
          <el-icon><Minus /></el-icon>
        </button>
      </div>
    </header>

    <main class="widget-body">
      <div v-if="loading" class="loading-wrap">
        <el-icon class="is-loading"><Loading /></el-icon>
        <span>加载中...</span>
      </div>
      <template v-else>
        <div v-if="todayTasks.length === 0" class="empty-tip">
          暂无当日待办，或今日任务已完成
        </div>
        <template v-else>
          <div class="widget-toolbar">
            <button
              type="button"
              class="split-windows-btn"
              @click="openEachTaskAsWindow"
            >
              每个任务独立小窗
            </button>
          </div>
          <div class="card-list">
          <article
            v-for="task in todayTasks"
            :key="task.id"
            class="task-card"
            :class="{ 'remind-now': remindingTaskIds.has(task.id) }"
          >
            <div class="card-main">
              <h3 class="card-title">{{ task.title }}</h3>
              <p v-if="task.description" class="card-desc">{{ task.description }}</p>
              <div class="card-meta">
                <span class="priority" :class="task.priority">{{ task.priority }}</span>
                <span v-if="task.due_date" class="due">{{ task.due_date }}</span>
              </div>
            </div>
            <div class="card-remind">
              <label class="remind-label">提醒</label>
              <select
                :value="getReminderTime(task.id)"
                @change="(e) => setReminderTime(task.id, (e.target as HTMLSelectElement).value)"
                @mousedown.stop
              >
                <option value="">不提醒</option>
                <option value="08:00">08:00</option>
                <option value="09:00">09:00</option>
                <option value="10:00">10:00</option>
                <option value="11:00">11:00</option>
                <option value="12:00">12:00</option>
                <option value="14:00">14:00</option>
                <option value="15:00">15:00</option>
                <option value="16:00">16:00</option>
                <option value="17:00">17:00</option>
                <option value="18:00">18:00</option>
              </select>
            </div>
          </article>
          </div>
        </template>
      </template>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ElIcon } from 'element-plus'
import { Pointer, Minus, Loading } from '@element-plus/icons-vue'
import { taskApi } from '@/api/task'
import type { Task } from '@/api/task'
import { useUserStore } from '@/stores/user'
import { wsService } from '@/utils/websocket'

const REMINDERS_KEY = 'desktopWidgetReminders'
const REMINDED_TODAY_KEY = 'desktopWidgetRemindedToday'

const loading = ref(true)
const tasks = ref<Task[]>([])
const isPinned = ref(false)
const isDragging = ref(false)
const dragStart = ref<{ x: number; y: number } | null>(null)
const windowStart = ref<{ x: number; y: number } | null>(null)
const remindingTaskIds = ref<Set<number>>(new Set())
/** 已存在当日任务 ID，用于检测新任务并自动弹窗 */
const previousTodayTaskIds = ref<Set<number>>(new Set())
let reminderTimer: ReturnType<typeof setInterval> | null = null
let newTaskPollTimer: ReturnType<typeof setInterval> | null = null

const today = computed(() => {
  const d = new Date()
  return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0')
})

const todayTasks = computed(() => {
  return tasks.value.filter((t) => {
    if (t.status === 'completed' || t.status === 'cancelled') return false
    if (!t.due_date) return true
    const due = (t.due_date as string).slice(0, 10)
    return due === today.value || due <= today.value
  })
})

function loadReminders(): Record<string, string> {
  try {
    const raw = localStorage.getItem(REMINDERS_KEY)
    return raw ? JSON.parse(raw) : {}
  } catch {
    return {}
  }
}

function saveReminders(obj: Record<string, string>) {
  localStorage.setItem(REMINDERS_KEY, JSON.stringify(obj))
}

function getReminderTime(taskId: number): string {
  const map = loadReminders()
  return map[String(taskId)] || ''
}

function setReminderTime(taskId: number, value: string) {
  const map = loadReminders()
  if (value) map[String(taskId)] = value
  else delete map[String(taskId)]
  saveReminders(map)
}

function loadRemindedToday(): Record<string, boolean> {
  try {
    const raw = localStorage.getItem(REMINDED_TODAY_KEY)
    const data = raw ? JSON.parse(raw) : {}
    const dateKey = today.value
    if (data.date !== dateKey) return {}
    return data.tasks || {}
  } catch {
    return {}
  }
}

function markRemindedToday(taskId: number) {
  try {
    const raw = localStorage.getItem(REMINDED_TODAY_KEY)
    const data = raw ? JSON.parse(raw) : { date: '', tasks: {} }
    if (data.date !== today.value) {
      data.date = today.value
      data.tasks = {}
    }
    data.tasks[String(taskId)] = true
    localStorage.setItem(REMINDED_TODAY_KEY, JSON.stringify(data))
  } catch {}
}

async function fetchTasks() {
  loading.value = true
  try {
    const res = await taskApi.getTasks({ page: 1, page_size: 100 })
    tasks.value = res?.items ?? []
  } catch {
    tasks.value = []
  } finally {
    loading.value = false
  }
}

function startDrag(e: MouseEvent) {
  const api = (window as any).electronAPI
  if (!api?.widgetGetPosition || !api?.widgetMoveTo) return
  if ((e.target as HTMLElement).closest('button')) return
  isDragging.value = true
  dragStart.value = { x: e.clientX, y: e.clientY }
  api.widgetGetPosition().then((pos: [number, number]) => {
    windowStart.value = { x: pos[0], y: pos[1] }
  })
  document.addEventListener('mousemove', onDragMove)
  document.addEventListener('mouseup', stopDrag)
  e.preventDefault()
}

function onDragMove(e: MouseEvent) {
  if (!isDragging.value || !dragStart.value || !windowStart.value) return
  const api = (window as any).electronAPI
  if (!api?.widgetMoveTo) return
  const dx = e.clientX - dragStart.value.x
  const dy = e.clientY - dragStart.value.y
  api.widgetMoveTo(windowStart.value.x + dx, windowStart.value.y + dy)
}

function stopDrag() {
  isDragging.value = false
  dragStart.value = null
  windowStart.value = null
  document.removeEventListener('mousemove', onDragMove)
  document.removeEventListener('mouseup', stopDrag)
}

async function togglePin() {
  const api = (window as any).electronAPI
  if (!api?.widgetSetAlwaysOnTop) return
  const next = !isPinned.value
  const result = await api.widgetSetAlwaysOnTop(next)
  isPinned.value = result
}

function hideWindow() {
  const api = (window as any).electronAPI
  if (api?.widgetHide) {
    api.widgetHide()
  }
}

/** 每个任务拆成独立小窗 */
function openEachTaskAsWindow() {
  const api = (window as any).electronAPI
  if (!api?.createTaskCardWindow) return
  todayTasks.value.forEach((task, index) => {
    api.createTaskCardWindow(task.id, index)
  })
  hideWindow()
}

/** 检测新当日任务并自动弹出任务卡片小窗（仅新出现的任务，轮询用） */
function checkAndOpenNewTaskWindows() {
  const api = (window as any).electronAPI
  if (!api?.createTaskCardWindow) return
  const currentIds = new Set(todayTasks.value.map((t) => t.id))
  const newTasks = todayTasks.value.filter((t) => !previousTodayTaskIds.value.has(t.id))
  newTasks.forEach((task, i) => {
    api.createTaskCardWindow(task.id, previousTodayTaskIds.value.size + i)
  })
  previousTodayTaskIds.value = currentIds
}

/** WebSocket 收到任务创建通知时，自动弹出该任务便签（实时，无需轮询） */
function onTaskNotification(event: Event) {
  const detail = (event as CustomEvent).detail
  const data = detail?.data
  if (data?.notification_type !== 'task_created' || !data?.task_id) return
  const api = (window as any).electronAPI
  if (!api?.createTaskCardWindow) return
  const taskId = Number(data.task_id)
  api.createTaskCardWindow(taskId, previousTodayTaskIds.value.size)
  previousTodayTaskIds.value = new Set([...previousTodayTaskIds.value, taskId])
}

function checkReminders() {
  const now = new Date()
  const nowMinutes = now.getHours() * 60 + now.getMinutes()
  const remindedToday = loadRemindedToday()
  const reminders = loadReminders()
  const toRemind = new Set<number>()
  Object.entries(reminders).forEach(([taskIdStr, timeStr]) => {
    if (remindedToday[taskIdStr]) return
    const [h, m] = timeStr.split(':').map(Number)
    const remindMinutes = h * 60 + m
    if (nowMinutes >= remindMinutes && nowMinutes < remindMinutes + 2) {
      toRemind.add(Number(taskIdStr))
    }
  })
  if (toRemind.size > 0) {
    remindingTaskIds.value = new Set([...remindingTaskIds.value, ...toRemind])
    toRemind.forEach((id) => markRemindedToday(id))
    const api = (window as any).electronAPI
    if (api?.showNotification) {
      api.showNotification({ title: '待办提醒', body: '有任务到达提醒时间' })
    }
    // 约 60 秒后取消高亮动画
    setTimeout(() => {
      remindingTaskIds.value = new Set([...remindingTaskIds.value].filter((id) => !toRemind.has(id)))
    }, 60000)
  }
}

onMounted(async () => {
  const api = (window as any).electronAPI
  if (api?.widgetGetPinned) {
    isPinned.value = await api.widgetGetPinned()
  }
  await fetchTasks()
  // 首次加载只记录当前当日任务，不自动弹窗
  previousTodayTaskIds.value = new Set(todayTasks.value.map((t) => t.id))
  reminderTimer = setInterval(checkReminders, 30000)
  checkReminders()

  // WebSocket：任务创建时实时弹出便签（后端已有 task_notification + task_created）
  const userStore = useUserStore()
  userStore.initFromStorage()
  if (userStore.token) {
    window.addEventListener('task-notification', onTaskNotification)
    wsService.connect()
  }

  // 轮询作为兜底：WebSocket 未连上或漏消息时，每 60 秒检查一次新当日任务
  if (api?.createTaskCardWindow) {
    newTaskPollTimer = setInterval(() => {
      fetchTasks().then(() => checkAndOpenNewTaskWindows())
    }, 60000)
  }
})

onUnmounted(() => {
  window.removeEventListener('task-notification', onTaskNotification)
  wsService.disconnect()
  if (reminderTimer) clearInterval(reminderTimer)
  if (newTaskPollTimer) clearInterval(newTaskPollTimer)
})
</script>

<style scoped>
.desktop-widget {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
  user-select: none;
  -webkit-app-region: no-drag;
}

.desktop-widget.dragging {
  cursor: move;
}

.widget-header {
  -webkit-app-region: drag;
  app-region: drag;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  flex-shrink: 0;
}

.widget-title {
  font-size: 14px;
  font-weight: 600;
}

.header-actions {
  display: flex;
  gap: 4px;
  -webkit-app-region: no-drag;
  app-region: no-drag;
}

.pin-btn,
.close-btn {
  padding: 4px;
  border: none;
  background: rgba(255, 255, 255, 0.2);
  color: #fff;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.pin-btn:hover,
.close-btn:hover {
  background: rgba(255, 255, 255, 0.35);
}

.pin-btn.pinned {
  background: rgba(255, 255, 255, 0.5);
}

.widget-body {
  flex: 1;
  overflow: auto;
  padding: 10px;
}

.widget-toolbar {
  margin-bottom: 10px;
}

.split-windows-btn {
  width: 100%;
  padding: 8px 12px;
  font-size: 13px;
  color: #667eea;
  background: rgba(102, 126, 234, 0.1);
  border: 1px solid rgba(102, 126, 234, 0.3);
  border-radius: 6px;
  cursor: pointer;
}

.split-windows-btn:hover {
  background: rgba(102, 126, 234, 0.2);
}

.loading-wrap {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: #909399;
  padding: 24px;
}

.empty-tip {
  text-align: center;
  color: #909399;
  padding: 24px;
  font-size: 13px;
}

.card-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.task-card {
  background: #fff;
  border-radius: 8px;
  padding: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  border: 2px solid transparent;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.task-card.remind-now {
  border-color: #f56c6c;
  box-shadow: 0 0 0 2px rgba(245, 108, 108, 0.3);
  animation: remind-pulse 0.8s ease-in-out infinite;
}

@keyframes remind-pulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.85;
  }
}

.card-title {
  margin: 0 0 6px 0;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.card-desc {
  margin: 0 0 8px 0;
  font-size: 12px;
  color: #606266;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.card-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 11px;
  color: #909399;
}

.priority {
  padding: 2px 6px;
  border-radius: 4px;
  text-transform: capitalize;
}

.priority.low {
  background: #e8f5e9;
  color: #2e7d32;
}

.priority.medium {
  background: #fff3e0;
  color: #e65100;
}

.priority.high {
  background: #ffe0b2;
  color: #bf360c;
}

.priority.urgent {
  background: #ffcdd2;
  color: #b71c1c;
}

.card-remind {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid #ebeef5;
  display: flex;
  align-items: center;
  gap: 6px;
}

.remind-label {
  font-size: 11px;
  color: #909399;
}

.card-remind select {
  font-size: 12px;
  padding: 2px 6px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  background: #fff;
  cursor: pointer;
}
</style>
