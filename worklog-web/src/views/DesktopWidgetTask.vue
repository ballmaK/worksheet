<template>
  <div
    class="sticky-note"
    :class="[`note-color-${noteColorIndex}`, { dragging: isDragging, 'remind-now': isReminding, 'is-detail': isDetailMode }]"
  >
    <!-- 便签顶部胶条拖拽区 -->
    <header class="note-tape" @mousedown="startDrag">
      <span class="note-title">{{ task?.title || '加载中...' }}</span>
      <div class="tape-actions">
        <button
          v-if="isDetailMode"
          type="button"
          class="note-btn back-btn"
          title="返回简洁"
          @mousedown.stop
          @click="exitDetailMode"
        >
          <el-icon><ArrowLeft /></el-icon>
        </button>
        <button
          type="button"
          class="note-btn"
          :class="{ pinned: isPinned }"
          :title="isPinned ? '取消置顶' : '钉在桌面'"
          @mousedown.stop
          @click="togglePin"
        >
          <el-icon><Pointer /></el-icon>
        </button>
        <button type="button" class="note-btn close" title="关闭" @mousedown.stop @click="closeWindow">
          <el-icon><Close /></el-icon>
        </button>
      </div>
    </header>
    <main
      class="note-body"
      :class="{ 'is-concise': !isDetailMode }"
      @click="onBodyClick"
    >
      <template v-if="loading">
        <div class="note-loading"><el-icon class="is-loading"><Loading /></el-icon></div>
      </template>
      <template v-else-if="task">
        <Transition name="note-mode" mode="out-in">
          <!-- 简洁模式：点击任意处进入详情 -->
          <div v-if="!isDetailMode" key="concise" class="note-concise-wrap">
            <div class="note-concise-line">
              <span class="note-priority" :class="task.priority">{{ priorityLabel(task.priority) }}</span>
              <span v-if="task.due_date" class="note-due">{{ String(task.due_date).slice(0, 10) }}</span>
              <span v-if="task.description" class="note-desc-one">{{ truncateDesc(task.description, 28) }}</span>
            </div>
            <div class="note-remind" @click.stop>
              <label>提醒</label>
              <select
                :value="reminderTime"
                @change="onReminderChange"
                @mousedown.stop
              >
                <option value="">不提醒</option>
                <option value="08:00">08:00</option>
                <option value="09:00">09:00</option>
                <option value="10:00">10:00</option>
                <option value="12:00">12:00</option>
                <option value="14:00">14:00</option>
                <option value="15:00">15:00</option>
                <option value="17:00">17:00</option>
                <option value="18:00">18:00</option>
              </select>
              <button type="button" class="note-btn note-btn-test-remind" title="模拟一次提醒效果" @click="triggerTestReminder">测提醒</button>
            </div>
            <div class="note-click-hint">点击查看详情</div>
          </div>
          <!-- 详细模式：参考任务详情展示 -->
          <div v-else key="detail" class="note-detail-wrap">
            <section class="note-detail-section">
              <div class="note-section-title">
                <el-icon><Document /></el-icon>
                <span>任务描述</span>
              </div>
              <p class="note-detail-desc">{{ task.description || '无描述' }}</p>
            </section>
            <section class="note-detail-section">
              <div class="note-section-title">
                <el-icon><InfoFilled /></el-icon>
                <span>基本信息</span>
              </div>
              <div class="note-detail-grid">
                <div class="note-detail-row">
                  <span class="note-detail-label">状态</span>
                  <span class="note-detail-value" :class="'status-' + task.status">{{ statusLabel(task.status) }}</span>
                </div>
                <div class="note-detail-row">
                  <span class="note-detail-label">优先级</span>
                  <span class="note-detail-value"><span class="note-priority" :class="task.priority">{{ priorityLabel(task.priority) }}</span></span>
                </div>
                <div class="note-detail-row">
                  <span class="note-detail-label">类型</span>
                  <span class="note-detail-value">{{ taskTypeLabel(task.task_type) }}</span>
                </div>
                <div class="note-detail-row" v-if="task.due_date">
                  <span class="note-detail-label">截止日期</span>
                  <span class="note-detail-value">{{ String(task.due_date).slice(0, 10) }}</span>
                </div>
                <div class="note-detail-row" v-if="task.assignee">
                  <span class="note-detail-label">负责人</span>
                  <span class="note-detail-value">{{ task.assignee.username }}</span>
                </div>
                <div class="note-detail-row" v-if="task.project">
                  <span class="note-detail-label">所属项目</span>
                  <span class="note-detail-value">{{ task.project.name }}</span>
                </div>
              </div>
            </section>
            <div class="note-remind" @click.stop>
              <label>提醒</label>
              <select
                :value="reminderTime"
                @change="onReminderChange"
                @mousedown.stop
              >
                <option value="">不提醒</option>
                <option value="08:00">08:00</option>
                <option value="09:00">09:00</option>
                <option value="10:00">10:00</option>
                <option value="12:00">12:00</option>
                <option value="14:00">14:00</option>
                <option value="15:00">15:00</option>
                <option value="17:00">17:00</option>
                <option value="18:00">18:00</option>
              </select>
              <button type="button" class="note-btn note-btn-test-remind" title="模拟一次提醒效果" @click="triggerTestReminder">测提醒</button>
            </div>
          </div>
        </Transition>
        <!-- 提醒中：方案一 + 知道了 -->
        <div v-if="isReminding" class="note-remind-bar" @click.stop>
          <span class="note-remind-bar-text">收到提醒</span>
          <button type="button" class="note-btn note-btn-ack" @click="dismissReminder">知道了</button>
        </div>
      </template>
      <div v-else class="note-error">任务不存在或已删除</div>
    </main>
    <!-- 便签右下角折角 -->
    <div class="note-fold" aria-hidden="true"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { ElIcon } from 'element-plus'
import { Pointer, Close, Loading, Document, ArrowLeft, InfoFilled } from '@element-plus/icons-vue'
import { taskApi } from '@/api/task'
import type { Task } from '@/api/task'

const REMINDERS_KEY = 'desktopWidgetReminders'
const REMINDED_TODAY_KEY = 'desktopWidgetRemindedToday'

const CONCISE_SIZE = [280, 200] as const
const DETAIL_SIZE = [320, 420] as const

const route = useRoute()
const taskId = computed(() => {
  const id = route.query.taskId
  return id ? Number(id) : 0
})

/** 便签颜色主题数量，按 taskId 取模保证同一任务同色 */
const NOTE_COLOR_COUNT = 6
const noteColorIndex = computed(() => {
  const id = taskId.value
  return id ? Math.abs(id % NOTE_COLOR_COUNT) : 0
})

const task = ref<Task | null>(null)
const loading = ref(true)
const isPinned = ref(false)
const isDragging = ref(false)
const dragStart = ref<{ x: number; y: number } | null>(null)
const windowStart = ref<{ x: number; y: number } | null>(null)
const isReminding = ref(false)
/** true=详细内容，false=简洁内容（默认） */
const isDetailMode = ref(false)
let reminderTimer: ReturnType<typeof setInterval> | null = null

function truncateDesc(text: string, maxLen: number): string {
  if (!text || text.length <= maxLen) return text
  return text.slice(0, maxLen) + '…'
}

/** 与 TaskDetail 一致的状态/优先级/类型文案 */
function statusLabel(s: string): string {
  const map: Record<string, string> = {
    pending: '待处理',
    assigned: '已分配',
    in_progress: '进行中',
    review: '审核中',
    completed: '已完成',
    cancelled: '已取消'
  }
  return map[s] || s
}

function priorityLabel(p: string): string {
  const map: Record<string, string> = {
    low: '低',
    medium: '中',
    high: '高',
    urgent: '紧急'
  }
  return map[p] || p
}

function taskTypeLabel(t: string): string {
  const map: Record<string, string> = {
    feature: '功能',
    bug: '缺陷',
    improvement: '改进',
    documentation: '文档',
    other: '其他'
  }
  return map[t] || t
}

function onBodyClick() {
  if (loading.value || !task.value || isDetailMode.value) return
  enterDetailMode()
}

function enterDetailMode() {
  if (isDetailMode.value) return
  isDetailMode.value = true
  nextTick(() => {
    const api = (window as any).electronAPI
    if (api?.widgetResize) api.widgetResize(DETAIL_SIZE[0], DETAIL_SIZE[1])
  })
}

function exitDetailMode() {
  if (!isDetailMode.value) return
  isDetailMode.value = false
  nextTick(() => {
    const api = (window as any).electronAPI
    if (api?.widgetResize) api.widgetResize(CONCISE_SIZE[0], CONCISE_SIZE[1])
  })
}

const reminderTime = computed(() => {
  if (!task.value) return ''
  try {
    const raw = localStorage.getItem(REMINDERS_KEY)
    const map = raw ? JSON.parse(raw) : {}
    return map[String(task.value.id)] || ''
  } catch {
    return ''
  }
})

function loadRemindedToday(): Record<string, boolean> {
  try {
    const raw = localStorage.getItem(REMINDED_TODAY_KEY)
    const data = raw ? JSON.parse(raw) : {}
    const today = new Date().toISOString().slice(0, 10)
    if (data.date !== today) return {}
    return data.tasks || {}
  } catch {
    return {}
  }
}

async function fetchTask() {
  if (!taskId.value) return
  loading.value = true
  try {
    task.value = await taskApi.getTask(taskId.value)
  } catch {
    task.value = null
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
  isPinned.value = await api.widgetSetAlwaysOnTop(next)
}

function closeWindow() {
  const api = (window as any).electronAPI
  if (api?.widgetHide) api.widgetHide()
}

function onReminderChange(e: Event) {
  const value = (e.target as HTMLSelectElement).value
  if (!task.value) return
  try {
    const raw = localStorage.getItem(REMINDERS_KEY)
    const map = raw ? JSON.parse(raw) : {}
    if (value) map[String(task.value.id)] = value
    else delete map[String(task.value.id)]
    localStorage.setItem(REMINDERS_KEY, JSON.stringify(map))
  } catch {}
}

function checkReminder() {
  if (!task.value) return
  const now = new Date()
  const nowMin = now.getHours() * 60 + now.getMinutes()
  const r = reminderTime.value
  if (!r) return
  const [h, m] = r.split(':').map(Number)
  const remindMin = h * 60 + m
  const reminded = loadRemindedToday()
  if (reminded[String(task.value.id)]) return
  if (nowMin >= remindMin && nowMin < remindMin + 2) {
    isReminding.value = true
    try {
      const raw = localStorage.getItem(REMINDED_TODAY_KEY)
      const data = raw ? JSON.parse(raw) : { date: '', tasks: {} }
      const today = new Date().toISOString().slice(0, 10)
      if (data.date !== today) {
        data.date = today
        data.tasks = {}
      }
      data.tasks = data.tasks || {}
      data.tasks[String(task.value.id)] = true
      localStorage.setItem(REMINDED_TODAY_KEY, JSON.stringify(data))
    } catch {}
    const api = (window as any).electronAPI
    // 方案二：系统通知 + 任务卡置顶
    if (api?.showNotification) {
      const parts: string[] = []
      if (task.value.due_date) parts.push(`截止: ${String(task.value.due_date).slice(0, 10)}`)
      parts.push(priorityLabel(task.value.priority) + '优先级')
      api.showNotification({
        title: task.value.title,
        body: parts.length ? parts.join(' · ') : '待办提醒'
      })
    }
    if (api?.widgetSetAlwaysOnTop) api.widgetSetAlwaysOnTop(true)
    // 60 秒后自动收起提醒态并恢复置顶偏好
    setTimeout(() => {
      isReminding.value = false
      const api = (window as any).electronAPI
      if (api?.widgetSetAlwaysOnTop) api.widgetSetAlwaysOnTop(isPinned.value)
    }, 60000)
  }
}

function dismissReminder() {
  isReminding.value = false
  const api = (window as any).electronAPI
  if (api?.widgetSetAlwaysOnTop) api.widgetSetAlwaysOnTop(isPinned.value)
}

/** 仅用于测试：立即触发一次提醒效果（不发今日已提醒，可重复测） */
function triggerTestReminder() {
  if (!task.value) return
  isReminding.value = true
  const api = (window as any).electronAPI
  if (api?.showNotification) {
    const parts: string[] = []
    if (task.value.due_date) parts.push(`截止: ${String(task.value.due_date).slice(0, 10)}`)
    parts.push(priorityLabel(task.value.priority) + '优先级')
    api.showNotification({
      title: '[测试] ' + task.value.title,
      body: parts.length ? parts.join(' · ') : '待办提醒'
    })
  }
  if (api?.widgetSetAlwaysOnTop) api.widgetSetAlwaysOnTop(true)
  setTimeout(() => {
    isReminding.value = false
    const a = (window as any).electronAPI
    if (a?.widgetSetAlwaysOnTop) a.widgetSetAlwaysOnTop(isPinned.value)
  }, 60000)
}

onMounted(async () => {
  const api = (window as any).electronAPI
  if (api?.widgetGetPinned) isPinned.value = await api.widgetGetPinned()
  await fetchTask()
  reminderTimer = setInterval(checkReminder, 30000)
  checkReminder()
})

onUnmounted(() => {
  if (reminderTimer) clearInterval(reminderTimer)
})
</script>

<style scoped>
/* 便签整体 + 柔和阴影（具体颜色由 .note-color-* 提供） */
.sticky-note {
  height: 100vh;
  display: flex;
  flex-direction: column;
  box-shadow:
    inset 0 1px 0 rgba(255,255,255,0.5),
    2px 2px 6px rgba(0,0,0,0.12),
    4px 4px 12px rgba(0,0,0,0.08);
  user-select: none;
  position: relative;
  border-radius: 2px;
}

.sticky-note.dragging {
  cursor: move;
}

/* 方案一：短时边框高亮约 2s + 温和呼吸动效 */
.sticky-note.remind-now {
  box-shadow:
    inset 0 1px 0 rgba(255,255,255,0.5),
    0 0 0 2px rgba(245,158,11,0.9),
    0 0 14px rgba(245,158,11,0.35),
    2px 2px 6px rgba(0,0,0,0.12),
    4px 4px 12px rgba(0,0,0,0.08);
  animation:
    note-remind-glow 2.5s ease-out forwards,
    note-remind-breath 1.8s ease-in-out infinite;
}

@keyframes note-remind-glow {
  0%, 70% {
    box-shadow:
      inset 0 1px 0 rgba(255,255,255,0.5),
      0 0 0 2px rgba(245,158,11,0.9),
      0 0 14px rgba(245,158,11,0.35),
      2px 2px 6px rgba(0,0,0,0.12),
      4px 4px 12px rgba(0,0,0,0.08);
  }
  100% {
    box-shadow:
      inset 0 1px 0 rgba(255,255,255,0.5),
      0 0 0 2px rgba(245,158,11,0.25),
      2px 2px 6px rgba(0,0,0,0.12),
      4px 4px 12px rgba(0,0,0,0.08);
  }
}

@keyframes note-remind-breath {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.02); }
}

/* 提醒时底部「知道了」条 */
.note-remind-bar {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px 10px 8px;
  margin-top: 4px;
  border-top: 1px solid rgba(0,0,0,0.06);
  background: rgba(245,158,11,0.12);
  border-radius: 4px;
  margin-left: 4px;
  margin-right: 4px;
}

.note-remind-bar-text {
  font-size: 12px;
  opacity: 0.9;
}

.note-btn-ack {
  padding: 4px 10px;
  font-size: 12px;
  border-radius: 4px;
  font-weight: 500;
}

/* 便签颜色主题：0 黄 1 粉 2 蓝 3 薄荷 4 薰衣草 5 蜜桃 */
.sticky-note.note-color-0 {
  background: linear-gradient(160deg, #fef9c3 0%, #fef08a 50%, #fde047 100%);
}
.sticky-note.note-color-0 .note-tape { background: linear-gradient(180deg, rgba(253,224,71,0.85) 0%, rgba(254,240,138,0.5) 70%, transparent 100%); }
.sticky-note.note-color-0 .note-title,
.sticky-note.note-color-0 .note-body,
.sticky-note.note-color-0 .note-desc { color: #422006; }
.sticky-note.note-color-0 .note-meta,
.sticky-note.note-color-0 .note-loading,
.sticky-note.note-color-0 .note-error { color: #713f12; }
.sticky-note.note-color-0 .note-btn { background: rgba(113,63,18,0.12); color: #713f12; }
.sticky-note.note-color-0 .note-btn:hover,
.sticky-note.note-color-0 .note-btn.pinned { background: rgba(113,63,18,0.22); }
.sticky-note.note-color-0 .note-fold { border-color: transparent transparent rgba(0,0,0,0.06) transparent; }

.sticky-note.note-color-1 {
  background: linear-gradient(160deg, #fce7f3 0%, #fbcfe8 50%, #f9a8d4 100%);
}
.sticky-note.note-color-1 .note-tape { background: linear-gradient(180deg, rgba(249,168,212,0.85) 0%, rgba(251,207,232,0.5) 70%, transparent 100%); }
.sticky-note.note-color-1 .note-title,
.sticky-note.note-color-1 .note-body,
.sticky-note.note-color-1 .note-desc { color: #4c0519; }
.sticky-note.note-color-1 .note-meta,
.sticky-note.note-color-1 .note-loading,
.sticky-note.note-color-1 .note-error { color: #831843; }
.sticky-note.note-color-1 .note-btn { background: rgba(131,24,67,0.15); color: #831843; }
.sticky-note.note-color-1 .note-btn:hover,
.sticky-note.note-color-1 .note-btn.pinned { background: rgba(131,24,67,0.28); }
.sticky-note.note-color-1 .note-fold { border-color: transparent transparent rgba(0,0,0,0.06) transparent; }

.sticky-note.note-color-2 {
  background: linear-gradient(160deg, #dbeafe 0%, #bfdbfe 50%, #93c5fd 100%);
}
.sticky-note.note-color-2 .note-tape { background: linear-gradient(180deg, rgba(147,197,253,0.85) 0%, rgba(191,219,254,0.5) 70%, transparent 100%); }
.sticky-note.note-color-2 .note-title,
.sticky-note.note-color-2 .note-body,
.sticky-note.note-color-2 .note-desc { color: #1e3a8a; }
.sticky-note.note-color-2 .note-meta,
.sticky-note.note-color-2 .note-loading,
.sticky-note.note-color-2 .note-error { color: #1e40af; }
.sticky-note.note-color-2 .note-btn { background: rgba(30,64,175,0.15); color: #1e40af; }
.sticky-note.note-color-2 .note-btn:hover,
.sticky-note.note-color-2 .note-btn.pinned { background: rgba(30,64,175,0.28); }
.sticky-note.note-color-2 .note-fold { border-color: transparent transparent rgba(0,0,0,0.06) transparent; }

.sticky-note.note-color-3 {
  background: linear-gradient(160deg, #d1fae5 0%, #a7f3d0 50%, #6ee7b7 100%);
}
.sticky-note.note-color-3 .note-tape { background: linear-gradient(180deg, rgba(110,231,183,0.85) 0%, rgba(167,243,208,0.5) 70%, transparent 100%); }
.sticky-note.note-color-3 .note-title,
.sticky-note.note-color-3 .note-body,
.sticky-note.note-color-3 .note-desc { color: #064e3b; }
.sticky-note.note-color-3 .note-meta,
.sticky-note.note-color-3 .note-loading,
.sticky-note.note-color-3 .note-error { color: #047857; }
.sticky-note.note-color-3 .note-btn { background: rgba(4,120,87,0.15); color: #047857; }
.sticky-note.note-color-3 .note-btn:hover,
.sticky-note.note-color-3 .note-btn.pinned { background: rgba(4,120,87,0.28); }
.sticky-note.note-color-3 .note-fold { border-color: transparent transparent rgba(0,0,0,0.06) transparent; }

.sticky-note.note-color-4 {
  background: linear-gradient(160deg, #ede9fe 0%, #ddd6fe 50%, #c4b5fd 100%);
}
.sticky-note.note-color-4 .note-tape { background: linear-gradient(180deg, rgba(196,181,253,0.85) 0%, rgba(221,214,254,0.5) 70%, transparent 100%); }
.sticky-note.note-color-4 .note-title,
.sticky-note.note-color-4 .note-body,
.sticky-note.note-color-4 .note-desc { color: #3b0764; }
.sticky-note.note-color-4 .note-meta,
.sticky-note.note-color-4 .note-loading,
.sticky-note.note-color-4 .note-error { color: #5b21b6; }
.sticky-note.note-color-4 .note-btn { background: rgba(91,33,182,0.15); color: #5b21b6; }
.sticky-note.note-color-4 .note-btn:hover,
.sticky-note.note-color-4 .note-btn.pinned { background: rgba(91,33,182,0.28); }
.sticky-note.note-color-4 .note-fold { border-color: transparent transparent rgba(0,0,0,0.06) transparent; }

.sticky-note.note-color-5 {
  background: linear-gradient(160deg, #ffedd5 0%, #fed7aa 50%, #fdba74 100%);
}
.sticky-note.note-color-5 .note-tape { background: linear-gradient(180deg, rgba(253,186,116,0.85) 0%, rgba(254,215,170,0.5) 70%, transparent 100%); }
.sticky-note.note-color-5 .note-title,
.sticky-note.note-color-5 .note-body,
.sticky-note.note-color-5 .note-desc { color: #431407; }
.sticky-note.note-color-5 .note-meta,
.sticky-note.note-color-5 .note-loading,
.sticky-note.note-color-5 .note-error { color: #9a3412; }
.sticky-note.note-color-5 .note-btn { background: rgba(154,52,18,0.15); color: #9a3412; }
.sticky-note.note-color-5 .note-btn:hover,
.sticky-note.note-color-5 .note-btn.pinned { background: rgba(154,52,18,0.28); }
.sticky-note.note-color-5 .note-fold { border-color: transparent transparent rgba(0,0,0,0.06) transparent; }

/* 顶部胶条 */
.note-tape {
  -webkit-app-region: drag;
  app-region: drag;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 10px 10px;
  flex-shrink: 0;
  border-bottom: 1px solid rgba(0,0,0,0.06);
}

.note-title {
  font-size: 14px;
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 180px;
  letter-spacing: 0.02em;
}

.tape-actions {
  -webkit-app-region: no-drag;
  app-region: no-drag;
  display: flex;
  gap: 4px;
}

.note-btn {
  padding: 4px 8px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.note-btn.close:hover {
  background: rgba(185,28,28,0.2) !important;
  color: #b91c1c !important;
}

/* 便签正文区 */
.note-body {
  flex: 1;
  overflow: auto;
  padding: 10px 12px 24px 12px;
  font-size: 13px;
}

.note-body.is-concise {
  padding: 6px 12px 16px 12px;
}

/* 简洁/详情模式切换动画 */
.note-mode-enter-active,
.note-mode-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}
.note-mode-enter-from,
.note-mode-leave-to {
  opacity: 0;
  transform: translateY(8px);
}

.note-concise-wrap {
  min-height: 60px;
}

.note-click-hint {
  font-size: 11px;
  opacity: 0.75;
  margin-top: 6px;
}

/* 详情模式区块 */
.note-detail-wrap {
  padding: 4px 0;
}
.note-detail-section {
  margin-bottom: 12px;
}
.note-section-title {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  opacity: 0.8;
  margin-bottom: 6px;
}
.note-detail-desc {
  font-size: 12px;
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-word;
  max-height: 120px;
  overflow-y: auto;
}
.note-detail-grid {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.note-detail-row {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
}
.note-detail-label {
  flex-shrink: 0;
  min-width: 56px;
  opacity: 0.85;
}
.note-detail-value {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
}
.note-detail-value[class*='status-'] {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  max-width: none;
}
.status-pending { background: rgba(0,0,0,0.08); }
.status-assigned { background: rgba(59,130,246,0.2); color: #1d4ed8; }
.status-in_progress { background: rgba(234,179,8,0.25); color: #854d0e; }
.status-review { background: rgba(168,85,247,0.2); color: #6b21a8; }
.status-completed { background: rgba(34,197,94,0.2); color: #15803d; }
.status-cancelled { background: rgba(0,0,0,0.1); color: #525252; }

.back-btn {
  -webkit-app-region: no-drag;
  app-region: no-drag;
  padding: 2px 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  background: transparent;
  color: inherit;
}
.back-btn:hover {
  background: rgba(0,0,0,0.08);
}

/* 简洁模式：一行概要 */
.note-concise-line {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px 10px;
  font-size: 12px;
  margin-bottom: 8px;
}

.note-desc-one {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  opacity: 0.9;
}

.note-loading,
.note-error {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
  opacity: 0.9;
}

.note-desc {
  margin: 0 0 10px 0;
  line-height: 1.5;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
}

.note-meta {
  display: flex;
  gap: 8px;
  margin-bottom: 10px;
  font-size: 11px;
  opacity: 0.9;
}

.note-priority {
  padding: 2px 8px;
  border-radius: 3px;
  text-transform: capitalize;
}

.note-priority.low { background: rgba(34,197,94,0.25); color: #166534; }
.note-priority.medium { background: rgba(249,115,22,0.25); color: #9a3412; }
.note-priority.high { background: rgba(234,88,12,0.3); color: #9a3412; }
.note-priority.urgent { background: rgba(220,38,38,0.25); color: #991b1b; }

.note-remind {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px dashed rgba(0,0,0,0.12);
}

.note-remind label {
  opacity: 0.85;
  font-size: 12px;
}

.note-remind select {
  font-size: 12px;
  padding: 4px 8px;
  border: 1px solid rgba(0,0,0,0.12);
  border-radius: 4px;
  background: rgba(255,255,255,0.7);
  color: inherit;
  cursor: pointer;
}

.note-remind select:hover,
.note-remind select:focus {
  background: rgba(255,255,255,0.95);
  outline: none;
}

.note-btn-test-remind {
  margin-left: 6px;
  font-size: 11px;
  padding: 2px 6px;
  opacity: 0.85;
}

/* 右下角折角效果 */
.note-fold {
  position: absolute;
  right: 0;
  bottom: 0;
  width: 0;
  height: 0;
  border-style: solid;
  border-width: 0 0 20px 20px;
  border-color: transparent transparent rgba(0,0,0,0.06) transparent;
  border-bottom-right-radius: 2px;
  pointer-events: none;
}
</style>
