<template>
  <div class="todo-list-container">
    <!-- 标签页（可选） -->
    <el-tabs v-if="showTabs" v-model="activeTab" @tab-change="handleTabChange">
      <el-tab-pane label="我的待办" name="pending">
        <template #label>
          <span>
            <el-icon><Document /></el-icon>
            我的待办
            <el-badge :value="pendingCount" v-if="pendingCount > 0" />
          </span>
        </template>
      </el-tab-pane>
      <el-tab-pane label="已完成" name="completed">
        <template #label>
          <span>
            <el-icon><CircleCheck /></el-icon>
            已完成
          </span>
        </template>
      </el-tab-pane>
    </el-tabs>

    <!-- 待办表格 -->
    <el-table 
      :data="displayTodos" 
      v-loading="loading" 
      stripe 
      border 
      :row-class-name="rowClassName"
      style="width: 100%"
    >
      <el-table-column prop="title" label="任务名称" min-width="350">
        <template #default="{ row }">
          <span :class="{ 'gray-text': row.isCompleted }">{{ row.displayTitle }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="type" label="类型" width="150">
        <template #default="{ row }">
          <el-tag :type="row.isCompleted ? 'info' : 'warning'">{{ row.type }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.isCompleted ? 'info' : (row.status === 'pending' ? 'danger' : 'success')">
            {{ row.isCompleted ? '已完成' : (row.status === 'pending' ? '待处理' : '处理中') }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="time" label="时间" width="120">
        <template #default="{ row }">
          <span :class="{ 'gray-text': row.isCompleted }">{{ row.time }}</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="100" fixed="right">
        <template #default="{ row }">
          <el-button 
            :type="row.isCompleted ? 'warning' : 'primary'" 
            size="small" 
            @click="handleAction(row)"
          >
            {{ row.isCompleted ? '退回' : '处理' }}
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-empty v-if="!loading && displayTodos.length === 0" description="暂无待办工作" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { Document, CircleCheck } from '@element-plus/icons-vue'

// 定义接口
interface Todo {
  id: number
  teacher_id: number
  teacher_name: string
  template_code: string
  business_type: string
  title: string
  status: string
  total_tasks: number
  completed_tasks: number
  progress: number
  created_at: string
  completed_at: string
  updated_at: string
  business_type_display: string
  template_name: string
}

// Props定义
const props = defineProps<{
  // 是否显示标签页
  showTabs?: boolean
  // 默认激活的标签
  defaultTab?: string
  // 是否显示已完成
  showCompleted?: boolean
  // 外部传入的数据（可选）
  externalData?: Todo[]
}>()

// Emits定义
const emit = defineEmits<{
  action: [todo: any]
  countChange: [count: number]
}>()

// 状态
const loading = ref(false)
const activeTab = ref(props.defaultTab || 'pending')
const rawTodoList = ref<Todo[]>([])

// 计算属性：待办数量
const pendingCount = computed(() => {
  return rawTodoList.value.filter(t => t.status !== 'completed').length
})

// 计算属性：显示的待办列表
const displayTodos = computed(() => {
  let filtered = rawTodoList.value
  
  // 根据标签页筛选
  if (props.showTabs) {
    if (activeTab.value === 'pending') {
      // 我的待办：显示所有未完成的（包括pending和in_progress）
      filtered = rawTodoList.value.filter(todo => todo.status !== 'completed')
    } else if (activeTab.value === 'completed') {
      filtered = rawTodoList.value.filter(todo => todo.status === 'completed')
    }
  } else if (!props.showCompleted) {
    // 不显示已完成时，只显示未完成的
    filtered = rawTodoList.value.filter(todo => todo.status !== 'completed')
  }
  
  // 映射显示格式
  return filtered.map(todo => {
    const isCompleted = todo.status === 'completed'
    const templateName = todo.business_type_display || todo.template_name || '待办任务'
    const teacherName = todo.teacher_name || '未知'
    const baseTitle = todo.title || `${teacherName} - ${templateName}`
    const progress = todo.total_tasks > 0 ? Math.round((todo.completed_tasks / todo.total_tasks) * 100) : 0
    
    return {
      id: todo.id,
      teacher_id: todo.teacher_id,
      teacher_name: teacherName,
      template_code: todo.template_code,
      business_type: todo.business_type,
      displayTitle: isCompleted 
        ? `✓ ${baseTitle}（共${todo.total_tasks}项，已完成${todo.completed_tasks}项，100%）`
        : `${baseTitle}（共${todo.total_tasks}项，已完成${todo.completed_tasks}项，${progress}%）`,
      type: isCompleted ? `${templateName} - 已完成` : templateName,
      time: formatDate(isCompleted ? (todo.completed_at || todo.updated_at) : todo.created_at),
      status: todo.status,
      isCompleted: isCompleted,
      progress: progress,
      rawData: todo
    }
  })
})

// 格式化日期
const formatDate = (dateStr: string): string => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  })
}

// 表格行样式
const rowClassName = ({ row }: { row: any }) => {
  return row.isCompleted ? 'completed-row' : ''
}

// 加载待办列表
const loadTodoList = async () => {
  // 如果传入了外部数据，直接使用
  if (props.externalData) {
    rawTodoList.value = props.externalData
    emit('countChange', pendingCount.value)
    return
  }
  
  loading.value = true
  try {
    const response = await fetch('/api/todo-system/todo-list')
    if (response.ok) {
      const result = await response.json()
      rawTodoList.value = result.data || []
      emit('countChange', pendingCount.value)
    }
  } catch (error) {
    console.error('加载待办列表失败:', error)
  } finally {
    loading.value = false
  }
}

// 处理操作
const handleAction = (row: any) => {
  emit('action', row)
}

// 处理标签页切换
const handleTabChange = () => {
  // 切换标签页时不需要重新加载
}

// 监听外部数据变化
watch(() => props.externalData, (newData) => {
  if (newData) {
    rawTodoList.value = newData
    emit('countChange', pendingCount.value)
  }
}, { deep: true })

// 暴露刷新方法
defineExpose({
  refresh: loadTodoList
})

onMounted(() => {
  loadTodoList()
})
</script>

<style scoped>
.todo-list-container {
  width: 100%;
}

.gray-text {
  color: #909399 !important;
}

:deep(.completed-row) {
  background-color: #f5f7fa !important;
}

:deep(.completed-row:hover) {
  background-color: #e4e7ed !important;
}
</style>
