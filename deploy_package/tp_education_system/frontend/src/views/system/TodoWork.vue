<template>
  <div class="todo-work-container">
    <el-card class="page-header">
      <template #header>
        <div class="header-content">
          <div class="title-section">
            <el-icon class="title-icon"><Bell /></el-icon>
            <span class="title">待办工作</span>
            <el-badge :value="pendingCount" v-if="pendingCount > 0" class="pending-badge" />
          </div>
          <div class="header-actions">
            <el-button @click="refreshData">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </div>
      </template>

      <!-- 使用统一的TodoList组件 -->
      <TodoList 
        ref="todoListRef"
        :showTabs="true" 
        :showCompleted="true"
        defaultTab="pending"
        @action="handleTodoAction"
        @countChange="handleCountChange"
      />
    </el-card>

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
      <el-form ref="returnFormRef" label-width="100px">
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
      v-model="drawerVisible"
      :todo-data="currentTodo"
      :template-code="currentTemplateCode"
      @complete="handleChecklistComplete"
      @close="drawerVisible = false"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Bell, Refresh } from '@element-plus/icons-vue'
import TodoList from '@/components/TodoList.vue'
import ChecklistDrawer from '@/components/ChecklistDrawer.vue'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

// 抽屉相关
const drawerVisible = ref(false)
const currentTodo = ref<any>(null)
const currentTemplateCode = ref('')

// 统计数据
const pendingCount = ref(0)

// 退回对话框
const returnDialogVisible = ref(false)
const returnReason = ref('')
const currentReturnTodo = ref<any>(null)

// TodoList组件引用
const todoListRef = ref<any>(null)

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
    drawerVisible.value = true
  }
}

// 处理数量变化
const handleCountChange = (count: number) => {
  pendingCount.value = count
}

// 处理清单完成
const handleChecklistComplete = () => {
  drawerVisible.value = false
  refreshData()
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
      // 刷新TodoList组件
      refreshData()
    } else {
      ElMessage.error('退回失败')
    }
  } catch (error) {
    console.error('退回失败:', error)
    ElMessage.error('退回失败')
  }
}

// 刷新数据
const refreshData = () => {
  todoListRef.value?.refresh()
}
</script>

<style scoped>
.todo-work-container {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title-section {
  display: flex;
  align-items: center;
  gap: 10px;
}

.title-icon {
  font-size: 24px;
  color: #409EFF;
}

.title {
  font-size: 20px;
  font-weight: bold;
}

.pending-badge :deep(.el-badge__content) {
  background-color: #F56C6C;
}

.header-actions {
  display: flex;
  gap: 10px;
}
</style>
