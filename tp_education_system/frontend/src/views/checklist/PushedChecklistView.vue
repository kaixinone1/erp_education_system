<template>
  <div class="pushed-checklist-container">
    <h2 class="page-title">推送清单</h2>

    <el-card class="checklist-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span class="card-title">
            <el-icon><Bell /></el-icon>
            待处理清单
          </span>
          <el-tag v-if="pendingTodos.length > 0" type="danger">{{ pendingTodos.length }} 项待办</el-tag>
        </div>
      </template>

      <div v-if="loading" class="loading-wrapper">
        <el-skeleton :rows="3" animated />
      </div>

      <div v-else-if="pendingTodos.length === 0" class="empty-wrapper">
        <el-empty description="暂无推送清单" :image-size="80" />
      </div>

      <el-table v-else :data="pendingTodos" style="width: 100%" border>
        <el-table-column prop="title" label="任务名称" min-width="300">
          <template #default="{ row }">
            <span>新增{{ row.teacher_name }}退休业务清单（共{{ row.total_tasks }}项，已完成{{ row.completed_tasks }}项）</span>
          </template>
        </el-table-column>
        <el-table-column prop="type" label="类型" width="150">
          <template #default="{ row }">
            <el-tag type="warning">{{ row.teacher_name }}退休呈报</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="time" label="创建时间" width="150" />
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleTodo(row)">处理</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 清单详情抽屉 -->
    <ChecklistDrawer
      v-model="drawerVisible"
      :todo-data="selectedTodo"
      @status-changed="loadTodoList"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Bell } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import ChecklistDrawer from '../../components/ChecklistDrawer.vue'

// 状态
const loading = ref(false)
const drawerVisible = ref(false)
const selectedTodo = ref<any>(null)
const rawTodoList = ref<any[]>([])

// 计算属性：待办工作列表（只显示未完成的）
const pendingTodos = computed(() => {
  return rawTodoList.value
    .filter(todo => todo.status === 'pending')
    .map(todo => ({
      id: todo.id,
      teacher_name: todo.teacher_name,
      total_tasks: todo.total_tasks,
      completed_tasks: todo.completed_tasks,
      title: `新增${todo.teacher_name}退休业务清单（共${todo.total_tasks}项，已完成${todo.completed_tasks}项）`,
      type: `${todo.teacher_name}退休呈报`,
      time: formatDate(todo.created_at)
    }))
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

// 加载待办列表
const loadTodoList = async () => {
  loading.value = true
  try {
    const response = await fetch('/api/todo-work/list')
    if (response.ok) {
      const result = await response.json()
      rawTodoList.value = result.data || []
    }
  } catch (error) {
    console.error('加载推送清单失败:', error)
    ElMessage.error('加载推送清单失败')
  } finally {
    loading.value = false
  }
}

// 处理待办工作 - 打开清单抽屉
const handleTodo = (row: any) => {
  const originalTodo = rawTodoList.value.find(todo => todo.id === row.id)
  if (originalTodo) {
    selectedTodo.value = originalTodo
    drawerVisible.value = true
  }
}

// 页面加载时获取数据
onMounted(() => {
  loadTodoList()
})
</script>

<style scoped>
.pushed-checklist-container {
  padding: 20px;
}

.page-title {
  margin: 0 0 20px 0;
  font-size: 20px;
  color: #1E40AF;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: bold;
}

.loading-wrapper {
  padding: 20px;
}

.empty-wrapper {
  padding: 40px 0;
}
</style>
