<template>
  <div class="calendar-demo">
    <h2>Qalendar Demo</h2>
    <Qalendar
      :events="events"
      :config="config"
      @event-click="onEventClick"
      @day-click="onDayClick"
      @interval-was-clicked="onIntervalClick"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Qalendar } from 'qalendar'
import 'qalendar/dist/style.css'

// 示例事件数据
const events = ref([
  {
    id: '1',
    title: '测试事件1',
    time: {
      start: '2024-03-20 09:00',
      end: '2024-03-20 10:00'
    },
    color: 'blue'
  },
  {
    id: '2',
    title: '测试事件2',
    time: {
      start: '2024-03-20 14:00',
      end: '2024-03-20 15:30'
    },
    color: 'green'
  }
])

// Qalendar 配置
const config = {
  locale: 'zh-CN',
  defaultMode: 'week',
  week: {
    nDays: 7,
    startsToday: true,
    scrollToHour: 8
  },
  dayIntervals: {
    length: 30,
    height: 50,
    displayClickableInterval: true,
    intervalStyles: {
      backgroundColor: '#f5f7fa',
      color: '#606266'
    }
  }
}

// 事件点击处理
const onEventClick = (event: any) => {
  console.log('Event clicked:', event)
  alert(`点击了事件：${event.title}`)
}

// 日期点击处理
const onDayClick = (date: Date) => {
  console.log('Day clicked:', date)
  alert(`点击了日期：${date.toLocaleDateString()}`)
}

// 时间段点击处理
const onIntervalClick = (payload: { start: string; end: string }) => {
  console.log('Interval clicked:', payload)
  alert(`点击了时间段：${payload.start} 到 ${payload.end}`)
}
</script>

<style scoped>
.calendar-demo {
  padding: 20px;
  height: 800px;
}

h2 {
  margin-bottom: 20px;
}
</style> 