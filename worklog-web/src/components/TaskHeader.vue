<template>
  <div class="page-header">
    <h2>任务管理</h2>
    <div class="header-actions">
      <el-input
          v-model="searchKeyword"
          placeholder="搜索任务"
          class="search-input"
          clearable
          @input="handleSearch"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
      <el-button type="primary" @click="showCreateDialog">
        <el-icon><Plus /></el-icon>
        创建任务
      </el-button>
      <el-button 
        :type="hasActiveFilters ? 'success' : 'primary'" 
        @click="showFilterDrawer"
        class="filter-btn"
      >
        <el-icon><Filter /></el-icon>
        筛选
        <el-badge 
          v-if="activeFilterCount > 0" 
          :value="activeFilterCount" 
          class="filter-badge"
          type="danger"
        />
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { Search, Plus, Filter } from '@element-plus/icons-vue'

// Props
interface Props {
  searchKeyword?: string
  viewMode?: string
  selectedTeamId?: number
  selectedProjectId?: number
  selectedAssigneeIds?: number[]
  filterPriority?: string
  filterTaskType?: string
  filterStatus?: string
}

const props = withDefaults(defineProps<Props>(), {
  searchKeyword: '',
  viewMode: 'all',
  selectedTeamId: undefined,
  selectedProjectId: undefined,
  selectedAssigneeIds: () => [],
  filterPriority: '',
  filterTaskType: '',
  filterStatus: ''
})

// Emits
const emit = defineEmits<{
  'update:searchKeyword': [value: string]
  'search': []
  'create': []
  'showFilter': []
}>()

// 本地状态
const searchKeyword = ref(props.searchKeyword)

// 计算属性
const hasActiveFilters = computed(() => {
  return props.viewMode !== 'all' || 
         props.selectedTeamId || 
         props.selectedProjectId || 
         props.selectedAssigneeIds.length > 0 ||
         props.filterPriority ||
         props.filterTaskType ||
         props.filterStatus
})

const activeFilterCount = computed(() => {
  let count = 0
  if (props.viewMode !== 'all') count++
  if (props.selectedTeamId) count++
  if (props.selectedProjectId) count++
  if (props.selectedAssigneeIds.length > 0) count++
  if (props.filterPriority) count++
  if (props.filterTaskType) count++
  if (props.filterStatus) count++
  return count
})

// 监听本地状态变化，同步到父组件
watch(searchKeyword, (newValue) => {
  emit('update:searchKeyword', newValue)
})

// 监听props变化，同步到本地状态
watch(() => props.searchKeyword, (newValue) => {
  searchKeyword.value = newValue
})

// 方法
const handleSearch = () => {
  emit('search')
}

const showCreateDialog = () => {
  emit('create')
}

const showFilterDrawer = () => {
  emit('showFilter')
}
</script>

<style scoped>
.page-header {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 24px;
}

.page-header h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.search-input {
  width: 300px;
}

.header-actions .el-select {
  width: 150px;
}

.filter-btn {
  position: relative;
}

.filter-badge {
  position: absolute;
  top: -8px;
  right: -8px;
}

@media (max-width: 768px) {
  .page-header {
    gap: 12px;
  }
  .header-actions {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }
  .search-input {
    width: 100%;
  }
  .header-actions .el-select {
    width: 100%;
  }
}
</style> 