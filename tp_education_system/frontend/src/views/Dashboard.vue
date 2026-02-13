<template>
  <div class="dashboard-container">
    <h2 class="page-title">工作台</h2>

    <div class="dashboard-grid">
      <!-- 待办工作区域 -->
      <el-card class="todo-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span class="card-title">
              <el-icon><Bell /></el-icon>
              待办工作
            </span>
            <el-tag v-if="pendingTodos.length > 0" type="danger">{{ pendingTodos.length }} 项待办</el-tag>
          </div>
        </template>

        <div v-if="loading" class="loading-wrapper">
          <el-skeleton :rows="3" animated />
        </div>

        <div v-else-if="pendingTodos.length === 0" class="empty-wrapper">
          <el-empty description="暂无待办工作" :image-size="80" />
        </div>

        <el-table v-else :data="pendingTodos" style="width: 100%" border>
          <el-table-column prop="taskName" label="任务名称" min-width="300">
            <template #default="{ row }">
              <span>新增退休教师{{ row.teacher_name }}业务清单（共{{ row.total_tasks }}项，已完成{{ row.completed_tasks }}项）</span>
            </template>
          </el-table-column>
          <el-table-column prop="checklist_type" label="类型" width="150">
            <template #default="{ row }">
              <el-tag type="warning">{{ row.teacher_name }}退休呈报</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="截止时间" width="150">
            <template #default="{ row }">
              <span>{{ formatDate(row.created_at) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" size="small" @click="openChecklist(row)">
                处理
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>

      <!-- 快捷入口区域 -->
      <el-card class="quick-access-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span class="card-title">
              <el-icon><Grid /></el-icon>
              快捷入口
            </span>
          </div>
        </template>

        <div class="quick-access-grid">
          <div class="quick-item" @click="navigateTo('/data/teacher_basic_info')">
            <el-icon><User /></el-icon>
            <span>教师信息</span>
          </div>
          <div class="quick-item" @click="navigateTo('/data/table-structure')">
            <el-icon><Setting /></el-icon>
            <span>表结构管理</span>
          </div>
          <div class="quick-item" @click="navigateTo('/import')">
            <el-icon><Upload /></el-icon>
            <span>数据导入</span>
          </div>
          <div class="quick-item" @click="navigateTo('/admin/table-management')">
            <el-icon><Management /></el-icon>
            <span>表管理</span>
          </div>
        </div>
      </el-card>

      <!-- 统计概览区域 -->
      <el-card class="stats-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span class="card-title">
              <el-icon><DataLine /></el-icon>
              统计概览
            </span>
          </div>
        </template>

        <div class="stats-grid">
          <div class="stat-item">
            <div class="stat-value">{{ stats.teacherCount }}</div>
            <div class="stat-label">教师总数</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ stats.retiredCount }}</div>
            <div class="stat-label">退休教师</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ stats.pendingTodoCount }}</div>
            <div class="stat-label">待办事项</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ stats.tableCount }}</div>
            <div class="stat-label">数据表数</div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 清单详情抽屉 -->
    <ChecklistDrawer
      v-model="drawerVisible"
      :todo-data="selectedTodo"
      @status-changed="loadTodoList"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Bell,
  Document,
  ArrowRight,
  Grid,
  User,
  Setting,
  Upload,
  Management,
  DataLine
} from '@element-plus/icons-vue'
import ChecklistDrawer from '../components/ChecklistDrawer.vue'

const router = useRouter()

// 状态
const loading = ref(false)
const todoList = ref<any[]>([])
const drawerVisible = ref(false)
const selectedTodo = ref<any>(null)
const stats = ref({
  teacherCount: 0,
  retiredCount: 0,
  pendingTodoCount: 0,
  tableCount: 0
})

// 待办工作列表（只显示未完成的）
const pendingTodos = computed(() => {
  return todoList.value.filter(todo => todo.status === 'pending')
})

// 加载待办列表
const loadTodoList = async () => {
  loading.value = true
  try {
    console.log('开始加载待办列表...')
    const response = await fetch('/api/todo-work/list')
    console.log('待办列表API响应:', response.status)
    if (response.ok) {
      const result = await response.json()
      console.log('待办列表数据:', result)
      todoList.value = result.data || []
      console.log('todoList赋值后:', todoList.value)
      console.log('pendingTodos:', pendingTodos.value)
      stats.value.pendingTodoCount = pendingTodos.value.length
    }
  } catch (error) {
    console.error('加载待办列表失败:', error)
    ElMessage.error('加载待办列表失败')
  } finally {
    loading.value = false
  }
}

// 加载统计数据
const loadStats = async () => {
  try {
    // 获取教师数量
    const teacherResponse = await fetch('/api/data/teacher_basic_info/count')
    if (teacherResponse.ok) {
      const result = await teacherResponse.json()
      stats.value.teacherCount = result.count || 0
    }

    // 获取退休教师数量
    const retiredResponse = await fetch('/api/data/teacher_basic_info/count?filter=' + encodeURIComponent(JSON.stringify({ 任职状态: '退休' })))
    if (retiredResponse.ok) {
      const result = await retiredResponse.json()
      stats.value.retiredCount = result.count || 0
    }

    // 获取表数量
    const tablesResponse = await fetch('/api/table-structure/tables')
    if (tablesResponse.ok) {
      const result = await tablesResponse.json()
      stats.value.tableCount = result.tables?.length || 0
    }
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

// 打开清单抽屉
const openChecklist = (todo: any) => {
  selectedTodo.value = todo
  drawerVisible.value = true
}

// 导航到指定页面
const navigateTo = (path: string) => {
  router.push(path)
}

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

// 页面加载时获取数据
onMounted(() => {
  loadTodoList()
  loadStats()
})
</script>

<style scoped>
.dashboard-container {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 20px;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
}

.todo-card {
  grid-column: span 2;
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
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.loading-wrapper {
  padding: 20px;
}

.empty-wrapper {
  padding: 40px 0;
}

.quick-access-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.quick-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background-color: #f5f7fa;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  gap: 8px;
}

.quick-item:hover {
  background-color: #e4e7ed;
  transform: translateY(-2px);
}

.quick-item .el-icon {
  font-size: 28px;
  color: #409eff;
}

.quick-item span {
  font-size: 14px;
  color: #606266;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.stat-item {
  text-align: center;
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 8px;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #409eff;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #606266;
}

@media (max-width: 768px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }

  .todo-card {
    grid-column: span 1;
  }
}
</style>
