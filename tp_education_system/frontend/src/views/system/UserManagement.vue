<template>
  <div class="user-management">
    <div class="page-header">
      <h2>用户管理</h2>
      <el-button type="primary" @click="showCreateDialog">添加用户</el-button>
    </div>

    <el-table :data="users" border stripe v-loading="loading" style="width: 100%">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="username" label="用户名" width="150" />
      <el-table-column prop="role" label="角色" width="120">
        <template #default="{ row }">
          <el-tag :type="row.role === 'county' ? 'danger' : 'primary'">
            {{ row.role === 'county' ? '县级管理员' : '乡镇管理员' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="unit_name" label="所属单位" min-width="200" />
      <el-table-column prop="permissions" label="权限" min-width="200">
        <template #default="{ row }">
          <template v-if="row.permissions">
            <el-tag v-for="p in parsePermissions(row.permissions)" :key="p" size="small" style="margin-right: 4px">
              {{ 权限中文名(p) }}
            </el-tag>
          </template>
          <span v-else style="color: #909399">-</span>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="180">
        <template #default="{ row }">
          {{ formatDate(row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="280" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="showEditDialog(row)">修改</el-button>
          <el-button 
            size="small" 
            type="warning" 
            @click="showResetPasswordDialog(row)"
          >
            重置密码
          </el-button>
          <el-button 
            size="small" 
            type="danger" 
            @click="handleDelete(row)"
            :disabled="row.username === 'admin'"
          >
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 添加/修改用户对话框 -->
    <el-dialog
      :title="isEdit ? '修改用户' : '添加用户'"
      v-model="dialogVisible"
      width="480px"
      :close-on-click-modal="false"
    >
      <el-form ref="userFormRef" :model="userForm" :rules="userRules" label-width="100px">
        <el-form-item label="用户名" prop="用户名">
          <el-input v-model="userForm.用户名" placeholder="请输入用户名" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="密码" :prop="isEdit ? '' : '密码'">
          <el-input 
            v-model="userForm.密码" 
            type="password" 
            :placeholder="isEdit ? '留空则不修改密码' : '请输入密码'" 
            show-password
          />
        </el-form-item>
        <el-form-item label="角色" prop="角色">
          <el-select v-model="userForm.角色" placeholder="请选择角色" style="width: 100%">
            <el-option label="乡镇管理员" value="township" />
            <el-option label="县级管理员" value="county" />
          </el-select>
        </el-form-item>
        <el-form-item label="所属单位">
          <el-select v-model="userForm.单位ID" placeholder="请选择所属单位" style="width: 100%" clearable>
            <el-option
              v-for="unit in availableUnits"
              :key="unit.id"
              :label="`${unit.unit_name} (${unit.unit_level})`"
              :value="unit.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="操作权限">
          <el-checkbox-group v-model="userForm.权限">
            <el-checkbox v-for="opt in 权限选项" :key="opt.value" :label="opt.value" :value="opt.value">
              {{ opt.label }}
            </el-checkbox>
          </el-checkbox-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">
          {{ isEdit ? '保存修改' : '添加' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 重置密码对话框 -->
    <el-dialog
      v-model="resetPasswordDialogVisible"
      title="重置密码"
      width="420px"
      :close-on-click-modal="false"
    >
      <el-alert
        :title="`即将重置用户「${resetTargetUser?.username}」的密码`"
        type="warning"
        :closable="false"
        style="margin-bottom: 20px"
      />
      <el-form label-width="100px">
        <el-form-item label="新密码">
          <el-input 
            v-model="resetPasswordForm.新密码" 
            type="password" 
            placeholder="留空则自动生成8位随机密码" 
            show-password
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="resetPasswordDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="resettingPassword" @click="handleResetPassword">确认重置</el-button>
      </template>
    </el-dialog>

    <!-- 重置密码结果对话框 -->
    <el-dialog
      v-model="resetResultDialogVisible"
      title="密码重置成功"
      width="420px"
      :close-on-click-modal="false"
    >
      <el-alert
        title="请妥善保管新密码，并及时告知用户"
        type="success"
        :closable="false"
        style="margin-bottom: 20px"
      />
      <el-form label-width="100px">
        <el-form-item label="用户名">
          <el-input :model-value="resetResult.用户名" disabled />
        </el-form-item>
        <el-form-item label="新密码">
          <el-input :model-value="resetResult.新密码" disabled show-password>
            <template #append>
              <el-button @click="copyPassword">复制</el-button>
            </template>
          </el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button type="primary" @click="resetResultDialogVisible = false">知道了</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/store/user'

const userStore = useUserStore()

const users = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const submitting = ref(false)
const userFormRef = ref(null)
const editingUserId = ref(null)

const userForm = reactive({
  用户名: '',
  密码: '',
  角色: 'township',
  单位ID: null,
  权限: []
})

const userRules = {
  用户名: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  密码: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  角色: [{ required: true, message: '请选择角色', trigger: 'change' }]
}

// 模块权限选项
const 权限选项 = [
  { label: '全部权限', value: 'all' },
  { label: '系统管理', value: 'system' },
  { label: '预警督办', value: 'todo' },
  { label: '数据中心', value: 'data' },
  { label: '人事管理', value: 'personnel' },
  { label: '薪酬管理', value: 'salary' },
  { label: '学校管理', value: 'school' },
  { label: '党组织管理', value: 'party' },
  { label: '绩效管理', value: 'performance' },
  { label: '报表管理', value: 'report' }
]

const availableUnits = ref([])

const parsePermissions = (perms) => {
  if (!perms) return []
  if (Array.isArray(perms)) return perms
  try {
    return JSON.parse(perms)
  } catch {
    return [perms]
  }
}

// 权限值到中文标签的映射
const 权限标签映射 = {
  'all': '全部权限',
  'system': '系统管理',
  'todo': '预警督办',
  'data': '数据中心',
  'personnel': '人事管理',
  'salary': '薪酬管理',
  'school': '学校管理',
  'party': '党组织管理',
  'performance': '绩效管理',
  'report': '报表管理'
}

const 权限中文名 = (perm) => 权限标签映射[perm] || perm

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const d = new Date(dateStr)
  return `${d.getFullYear()}年${d.getMonth() + 1}月${d.getDate()}日 ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

const fetchUsers = async () => {
  loading.value = true
  try {
    const res = await fetch(`/api/auth/users?token=${encodeURIComponent(userStore.token)}`)
    const result = await res.json()
    if (result.成功) {
      users.value = result.数据 || []
    } else {
      ElMessage.error(result.detail || '获取用户列表失败')
    }
  } catch (e) {
    ElMessage.error('网络错误')
  } finally {
    loading.value = false
  }
}

const fetchUnits = async () => {
  try {
    const res = await fetch(`/api/auth/units?token=${encodeURIComponent(userStore.token)}`)
    const result = await res.json()
    if (result.成功) {
      availableUnits.value = result.数据 || []
    }
  } catch (e) {
    console.error('获取单位列表失败:', e)
  }
}

const showCreateDialog = () => {
  isEdit.value = false
  editingUserId.value = null
  userForm.用户名 = ''
  userForm.密码 = ''
  userForm.角色 = 'township'
  userForm.单位ID = null
  userForm.权限 = []
  dialogVisible.value = true
}

const showEditDialog = (row) => {
  isEdit.value = true
  editingUserId.value = row.id
  userForm.用户名 = row.username
  userForm.密码 = ''
  userForm.角色 = row.role
  userForm.单位ID = row.unit_id || null
  userForm.权限 = parsePermissions(row.permissions)
  dialogVisible.value = true
}

const handleSubmit = async () => {
  if (!userFormRef.value) return
  await userFormRef.value.validate(async (valid) => {
    if (!valid) return
    
    submitting.value = true
    try {
      if (isEdit.value) {
        // 修改用户
        const body = {
          token: userStore.token,
          用户ID: editingUserId.value,
          角色: userForm.角色,
          单位ID: userForm.单位ID,
          权限: userForm.权限
        }
        if (userForm.密码) {
          body.密码 = userForm.密码
        }
        const res = await fetch(`/api/auth/users/${editingUserId.value}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body)
        })
        const result = await res.json()
        if (result.成功) {
          ElMessage.success('用户已更新')
          dialogVisible.value = false
          fetchUsers()
        } else {
          ElMessage.error(result.detail || '修改失败')
        }
      } else {
        // 添加用户
        const res = await fetch('/api/auth/users', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            token: userStore.token,
            用户名: userForm.用户名,
            密码: userForm.密码,
            角色: userForm.角色,
            单位ID: userForm.单位ID,
            权限: userForm.权限
          })
        })
        const result = await res.json()
        if (result.成功) {
          ElMessage.success('用户已添加')
          dialogVisible.value = false
          fetchUsers()
        } else {
          ElMessage.error(result.detail || '添加失败')
        }
      }
    } catch (e) {
      ElMessage.error('网络错误')
    } finally {
      submitting.value = false
    }
  })
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要删除用户 "${row.username}" 吗？`, '确认删除', {
      type: 'warning'
    })
    const res = await fetch(`/api/auth/users/${row.id}?token=${encodeURIComponent(userStore.token)}`, {
      method: 'DELETE'
    })
    const result = await res.json()
    if (result.成功) {
      ElMessage.success(result.消息 || '用户已删除')
      fetchUsers()
    } else {
      ElMessage.error(result.detail || '删除失败')
    }
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

onMounted(() => {
  fetchUsers()
  fetchUnits()
})

// 重置密码相关
const resetPasswordDialogVisible = ref(false)
const resetResultDialogVisible = ref(false)
const resettingPassword = ref(false)
const resetTargetUser = ref(null)
const resetPasswordForm = reactive({
  新密码: ''
})
const resetResult = reactive({
  用户名: '',
  新密码: ''
})

const showResetPasswordDialog = (row) => {
  resetTargetUser.value = row
  resetPasswordForm.新密码 = ''
  resetPasswordDialogVisible.value = true
}

const handleResetPassword = async () => {
  resettingPassword.value = true
  try {
    const body = {
      token: userStore.token
    }
    if (resetPasswordForm.新密码) {
      body.新密码 = resetPasswordForm.新密码
    }
    const res = await fetch(`/api/auth/users/${resetTargetUser.value.id}/reset-password`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    })
    const result = await res.json()
    if (result.成功) {
      resetPasswordDialogVisible.value = false
      resetResult.用户名 = resetTargetUser.value.username
      resetResult.新密码 = result.数据?.新密码 || ''
      resetResultDialogVisible.value = true
      ElMessage.success(result.消息 || '密码已重置')
    } else {
      ElMessage.error(result.detail || '重置失败')
    }
  } catch (e) {
    ElMessage.error('网络错误')
  } finally {
    resettingPassword.value = false
  }
}

const copyPassword = () => {
  navigator.clipboard.writeText(resetResult.新密码).then(() => {
    ElMessage.success('密码已复制到剪贴板')
  }).catch(() => {
    ElMessage.error('复制失败，请手动复制')
  })
}
</script>

<style scoped>
.user-management {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
  font-size: 20px;
  color: #303133;
}
</style>