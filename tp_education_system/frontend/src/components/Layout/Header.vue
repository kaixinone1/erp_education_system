<template>
  <el-header height="60px" class="header-container">
    <div class="header-left-full">
      <div class="header-left">
        <el-button circle class="logo-button">
          <el-icon class="logo-icon"><School /></el-icon>
        </el-button>
        <h1 class="system-title">太平教育人事管理系统</h1>
      </div>
      <div class="header-right">
        <el-badge :value="todoCount" :hidden="todoCount === 0" class="notification-badge">
          <el-button circle class="notification-button" @click="showTodoDrawer">
            <el-icon><Bell /></el-icon>
          </el-button>
        </el-badge>
        <span class="welcome-text">欢迎您</span>
        <el-dropdown trigger="click">
          <span class="user-info">
            <span class="user-name">admin</span>
            <el-icon class="arrow-icon"><ArrowDown /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item>个人中心</el-dropdown-item>
              <el-dropdown-item>设置</el-dropdown-item>
              <el-dropdown-item divided @click="logout">退出系统</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>
  </el-header>

  <!-- 待办工作抽屉 -->
  <el-drawer
    v-model="drawerVisible"
    title="待办工作"
    size="60%"
    :with-header="true"
    destroy-on-close
  >
    <TodoList 
      ref="todoListRef"
      :showTabs="true" 
      :showCompleted="true"
      defaultTab="pending"
      @action="handleTodoAction"
      @countChange="handleCountChange"
    />
  </el-drawer>

  <!-- 退回原因对话框 -->
  <el-dialog
    v-model="returnDialogVisible"
    title="退回原因（必填）"
    width="500px"
    :close-on-click-modal="false"
  >
    <el-alert
      title="该待办已完成，退回后需要重新办理"
      type="warning"
      :closable="false"
      style="margin-bottom: 20px"
    />
    <el-form label-width="100px">
      <el-form-item label="退回原因" required>
        <el-input
          v-model="returnReason"
          type="textarea"
          :rows="4"
          placeholder="请详细说明退回原因，以便后续处理"
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="returnDialogVisible = false">取消</el-button>
      <el-button type="primary" @click="submitReturn">确认退回</el-button>
    </template>
  </el-dialog>

  <!-- 清单抽屉 -->
  <ChecklistDrawer
    v-model="checklistDrawerVisible"
    :todo-data="currentTodo"
    :template-code="currentTemplateCode"
    @complete="handleChecklistComplete"
    @close="checklistDrawerVisible = false"
  />
</template>

<script setup lang="ts">
import { School, Bell, ArrowDown } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import TodoList from '../TodoList.vue'
import ChecklistDrawer from '../ChecklistDrawer.vue'

const router = useRouter()
const todoCount = ref(0)
let timer: number | null = null

// 抽屉相关
const drawerVisible = ref(false)
const checklistDrawerVisible = ref(false)
const currentTodo = ref<any>(null)
const currentTemplateCode = ref('')
const todoListRef = ref<any>(null)

// 退回对话框
const returnDialogVisible = ref(false)
const returnReason = ref('')
const currentReturnTodo = ref<any>(null)

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

// 获取待办工作数量 - 使用新的todo-system API
const fetchTodoCount = async () => {
  try {
    const response = await fetch('/api/todo-system/todo-list')
    if (response.ok) {
      const result = await response.json()
      // 统计未完成的待办数量（排除已完成的）
      const todos = result.data || []
      const pendingCount = todos.filter((todo: any) => todo.status !== 'completed').length
      todoCount.value = pendingCount
    }
  } catch (error) {
    console.error('Header: 获取待办数量失败:', error)
  }
}

// 显示待办工作抽屉
const showTodoDrawer = () => {
  drawerVisible.value = true
}

// 处理待办（来自TodoList组件的action事件）
const handleTodoAction = (row: any) => {
  if (row.isCompleted) {
    // 已完成，显示退回对话框
    currentReturnTodo.value = row
    returnReason.value = ''
    returnDialogVisible.value = true
  } else {
    // 未完成，打开处理抽屉
    currentTodo.value = row.rawData
    currentTemplateCode.value = row.template_code || row.business_type || ''
    checklistDrawerVisible.value = true
  }
}

// 处理数量变化
const handleCountChange = (count: number) => {
  todoCount.value = count
}

// 处理清单完成
const handleChecklistComplete = () => {
  checklistDrawerVisible.value = false
  // 刷新待办列表和数量
  todoListRef.value?.refresh()
  fetchTodoCount()
}

// 提交退回
const submitReturn = async () => {
  if (!returnReason.value.trim()) {
    ElMessage.warning('请输入退回原因')
    return
  }
  
  try {
    const response = await fetch(`${API_BASE_URL}/api/todo-system/todo/${currentReturnTodo.value.id}/return`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        reason: returnReason.value
      })
    })
    
    if (response.ok) {
      ElMessage.success('已退回')
      returnDialogVisible.value = false
      // 刷新TodoList组件和数量
      todoListRef.value?.refresh()
      fetchTodoCount()
    } else {
      ElMessage.error('退回失败')
    }
  } catch (error) {
    console.error('退回失败:', error)
    ElMessage.error('退回失败')
  }
}

// 定期刷新待办数量
onMounted(() => {
  fetchTodoCount()
  timer = window.setInterval(fetchTodoCount, 30000) // 每30秒刷新一次
})

onUnmounted(() => {
  if (timer) {
    clearInterval(timer)
  }
})

const logout = () => {
  // 清除localStorage中的用户信息
  localStorage.removeItem('userInfo')
  localStorage.removeItem('token')
  
  // 刷新首页
  router.go(0)
}
</script>

<style scoped>
.header-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #1890FF;
  color: #ffffff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  border-bottom: 1px solid rgba(255, 255, 255, 0.3);
}

.header-left-full {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding: 0 20px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-button {
  background-color: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.3);
}

.logo-icon {
  color: #ffffff;
  font-size: 20px;
}

.system-title {
  font-size: 18px;
  font-weight: bold;
  color: #ffffff;
  margin: 0;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 15px;
}

.notification-button {
  background-color: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.3);
  color: #ffffff;
}

.notification-badge {
  margin-right: 5px;
}

.notification-badge :deep(.el-badge__content) {
  background-color: #ff4d4f;
  border: none;
  font-size: 12px;
  font-weight: bold;
}

.welcome-text {
  font-size: 14px;
  color: #ffffff;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 5px;
  cursor: pointer;
  color: #ffffff;
}

.user-name {
  font-size: 14px;
  color: #ffffff;
}

.arrow-icon {
  font-size: 12px;
  color: #ffffff;
}
</style>
