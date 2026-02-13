<template>
  <div class="todo-list">
    <el-table v-if="todos.length > 0" :data="todos" style="width: 100%" border>
      <el-table-column prop="title" label="任务名称" min-width="300">
        <template #default="{ row }">
          <span>{{ row.title }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="type" label="类型" width="150">
        <template #default="{ row }">
          <el-tag type="warning">{{ row.type }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column v-if="showStatus" prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.status === 'completed' ? 'success' : 'warning'">
            {{ row.status === 'completed' ? '已完成' : '待处理' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="time" label="创建时间" width="150">
        <template #default="{ row }">
          <span>{{ row.time }}</span>
        </template>
      </el-table-column>
      <el-table-column v-if="showAction" label="操作" width="100" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" size="small" @click="handleAction(row)">
            处理
          </el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-empty v-else description="暂无待办任务" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'

interface Todo {
  id: number
  teacher_id: number
  teacher_name: string
  title: string
  type: string
  time: string
  status: string
  total_tasks: number
  completed_tasks: number
}

const props = defineProps<{
  showStatus?: boolean
  showAction?: boolean
  filterStatus?: string
}>()

const emit = defineEmits<{
  action: [todo: Todo]
}>()

const rawTodoList = ref<any[]>([])

// 加载待办列表
const loadTodoList = async () => {
  try {
    const response = await fetch('/api/todo-work/list')
    if (response.ok) {
      const data = await response.json()
      rawTodoList.value = data
    }
  } catch (error) {
    console.error('加载待办列表失败:', error)
  }
}

// 格式化日期
const formatDate = (dateStr: string): string => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN')
}

// 过滤后的待办列表
const todos = computed(() => {
  return rawTodoList.value
    .filter(todo => !props.filterStatus || todo.status === props.filterStatus)
    .map(todo => ({
      id: todo.id,
      teacher_id: todo.teacher_id,
      teacher_name: todo.teacher_name,
      title: `新增${todo.teacher_name}退休业务清单（共${todo.total_tasks}项，已完成${todo.completed_tasks}项）`,
      type: `${todo.teacher_name}退休呈报`,
      time: formatDate(todo.created_at),
      status: todo.status,
      total_tasks: todo.total_tasks,
      completed_tasks: todo.completed_tasks
    }))
})

const handleAction = (todo: Todo) => {
  emit('action', todo)
}

onMounted(() => {
  loadTodoList()
})
</script>
