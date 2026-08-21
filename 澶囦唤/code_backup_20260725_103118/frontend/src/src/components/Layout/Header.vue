<template>
  <el-header height="60px" class="header-container">
    <div class="header-left-full">
      <div class="header-left">
        <el-button circle class="logo-button">
          <el-icon class="logo-icon"><School /></el-icon>
        </el-button>
        <h1 class="system-title">{{ userStore.系统名称 }}</h1>
      </div>
      <div class="header-right">
        <!-- 单位选择器 -->
        <template v-if="userStore.isLoggedIn">
          <span class="unit-label">当前单位：</span>
          <el-select
            v-if="userStore.可选单位.length > 0"
            v-model="selectedUnitId"
            placeholder="请选择工作单位"
            size="small"
            class="unit-selector"
            @change="handleUnitChange"
          >
            <el-option
              v-for="unit in userStore.可选单位"
              :key="unit.id"
              :label="unit.unit_name"
              :value="unit.id"
            >
              <span>{{ unit.unit_name }}</span>
              <span style="color: #909399; font-size: 12px; margin-left: 8px">
                <el-tag size="small" :type="unit.unit_level === '县' ? 'danger' : unit.unit_level === '镇' ? 'warning' : 'info'">
                  {{ unit.unit_level }}
                </el-tag>
              </span>
            </el-option>
          </el-select>
          <el-tag v-else-if="!userStore.已选单位名称" type="warning" size="small" class="no-unit-tag">
            未选择单位，请重新登录
          </el-tag>
          <el-tag v-else type="success" size="small" class="unit-tag">
            {{ userStore.已选单位名称 }}
          </el-tag>
        </template>
        <el-badge :value="todoCount" :hidden="todoCount === 0" class="notification-badge">
          <el-button circle class="notification-button" @click="showTodoDrawer">
            <el-icon><Bell /></el-icon>
          </el-button>
        </el-badge>
        <span class="welcome-text">欢迎您，{{ userStore.userInfo.name }}</span>
        <el-dropdown trigger="click">
          <span class="user-info">
            <span class="user-name">{{ userStore.userInfo.name }}</span>
            <el-icon class="arrow-icon"><ArrowDown /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item v-if="userStore.是县级管理员" @click="showUserMgt">用户管理</el-dropdown-item>
              <el-dropdown-item @click="showChangePasswordDialog">修改密码</el-dropdown-item>
              <el-dropdown-item divided @click="handleLogout">退出系统</el-dropdown-item>
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

  <!-- 修改密码对话框 -->
  <el-dialog
    v-model="changePasswordDialogVisible"
    title="修改密码"
    width="420px"
    :close-on-click-modal="false"
  >
    <el-form ref="changePasswordFormRef" :model="changePasswordForm" :rules="changePasswordRules" label-width="100px">
      <el-form-item label="旧密码" prop="旧密码">
        <el-input v-model="changePasswordForm.旧密码" type="password" placeholder="请输入旧密码" show-password />
      </el-form-item>
      <el-form-item label="新密码" prop="新密码">
        <el-input v-model="changePasswordForm.新密码" type="password" placeholder="请输入新密码（至少6位）" show-password />
      </el-form-item>
      <el-form-item label="确认密码" prop="确认密码">
        <el-input v-model="changePasswordForm.确认密码" type="password" placeholder="请再次输入新密码" show-password />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="changePasswordDialogVisible = false">取消</el-button>
      <el-button type="primary" :loading="changingPassword" @click="handleChangePassword">确认修改</el-button>
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
import { ref, onMounted, onUnmounted, computed, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import TodoList from '../TodoList.vue'
import ChecklistDrawer from '../ChecklistDrawer.vue'
import { useUserStore } from '@/store/user'

const router = useRouter()
const userStore = useUserStore()
const todoCount = ref(0)
let timer: number | null = null

// 单位选择
const selectedUnitId = computed({
  get: () => userStore.已选单位ID,
  set: (val) => { /* handled by change event */ }
})

const handleUnitChange = async (unitId: number) => {
  const unit = userStore.可选单位.find(u => u.id === unitId)
  if (unit) {
    try {
      await fetch(`/api/auth/select-unit`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token: userStore.token, 单位ID: unitId })
      })
      userStore.selectUnit(unitId, unit.unit_name)
      ElMessage.success(`已切换到：${unit.unit_name}`)
    } catch (e) {
      ElMessage.error('切换单位失败')
    }
  }
}

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

const handleLogout = () => {
  userStore.logout()
  router.push('/login')
}

const showUserMgt = () => {
  router.push('/system/users')
}

// 修改密码相关
const changePasswordDialogVisible = ref(false)
const changingPassword = ref(false)
const changePasswordFormRef = ref(null)
const changePasswordForm = reactive({
  旧密码: '',
  新密码: '',
  确认密码: ''
})

const validateConfirmPassword = (_rule: any, value: string, callback: any) => {
  if (value !== changePasswordForm.新密码) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const changePasswordRules = {
  旧密码: [{ required: true, message: '请输入旧密码', trigger: 'blur' }],
  新密码: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '新密码长度不能少于6位', trigger: 'blur' }
  ],
  确认密码: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

const showChangePasswordDialog = () => {
  changePasswordForm.旧密码 = ''
  changePasswordForm.新密码 = ''
  changePasswordForm.确认密码 = ''
  changePasswordDialogVisible.value = true
}

const handleChangePassword = async () => {
  if (!changePasswordFormRef.value) return
  await changePasswordFormRef.value.validate(async (valid: boolean) => {
    if (!valid) return
    
    changingPassword.value = true
    try {
      const response = await fetch('/api/auth/change-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          token: userStore.token,
          旧密码: changePasswordForm.旧密码,
          新密码: changePasswordForm.新密码
        })
      })
      const result = await response.json()
      if (result.成功) {
        ElMessage.success('密码修改成功')
        changePasswordDialogVisible.value = false
      } else {
        ElMessage.error(result.detail || '密码修改失败')
      }
    } catch (e) {
      ElMessage.error('网络错误')
    } finally {
      changingPassword.value = false
    }
  })
}

// 退出系统（旧方法，保留兼容）
const logout = () => {
  handleLogout()
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

.unit-selector {
  width: 200px;
}

.unit-label {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.85);
  white-space: nowrap;
}

.no-unit-tag {
  cursor: pointer;
}

.unit-tag {
  font-size: 13px;
}

.unit-selector :deep(.el-input__wrapper) {
  background-color: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.3);
  box-shadow: none;
}

.unit-selector :deep(.el-input__inner) {
  color: #ffffff;
}

.unit-selector :deep(.el-input__inner::placeholder) {
  color: rgba(255, 255, 255, 0.6);
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

