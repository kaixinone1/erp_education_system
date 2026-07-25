<template>
  <div class="login-container">
    <!-- 登录表单 -->
    <div class="login-card" v-if="!showUnitSelect">
      <div class="login-header">
        <h1>教育人事管理系统</h1>
        <p>用户登录</p>
      </div>
      
      <el-form
        ref="loginFormRef"
        :model="loginForm"
        :rules="loginRules"
        class="login-form"
        @submit.prevent="handleLogin"
      >
        <el-form-item prop="用户名">
          <el-input
            v-model="loginForm.用户名"
            placeholder="请输入用户名"
            :prefix-icon="User"
            size="large"
          />
        </el-form-item>
        
        <el-form-item prop="密码">
          <el-input
            v-model="loginForm.密码"
            type="password"
            placeholder="请输入密码"
            :prefix-icon="Lock"
            size="large"
            show-password
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            class="login-btn"
            @click="handleLogin"
          >
            登 录
          </el-button>
        </el-form-item>
      </el-form>
      
      <div class="login-footer">
        <span>初始用户名：admin / 密码：admin666</span>
        <el-button link type="primary" @click="showForgotPassword" style="margin-left: 12px">忘记密码？</el-button>
      </div>
    </div>

    <!-- 单位选择卡片 -->
    <div class="login-card" v-else>
      <div class="login-header">
        <h1>选择工作单位</h1>
        <p>欢迎您，{{ userStore.userInfo.name }}</p>
        <p style="color: #909399; font-size: 13px; margin-top: 4px">
          请选择您当前要处理的单位，封面上的单位名称将使用此选择
        </p>
      </div>

      <el-form class="login-form" @submit.prevent="handleUnitConfirm">
        <el-form-item>
          <el-select
            v-model="selectedUnitId"
            placeholder="请选择工作单位"
            size="large"
            style="width: 100%"
            filterable
          >
            <el-option
              v-for="unit in userStore.可选单位"
              :key="unit.id"
              :label="unit.unit_name"
              :value="unit.id"
            >
              <div style="display: flex; justify-content: space-between; align-items: center">
                <span>{{ unit.unit_name }}</span>
                <el-tag size="small" :type="unit.unit_level === '县' ? 'danger' : unit.unit_level === '镇' ? 'warning' : 'info'">
                  {{ unit.unit_level }}
                </el-tag>
              </div>
            </el-option>
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="unitLoading"
            :disabled="!selectedUnitId"
            class="login-btn"
            @click="handleUnitConfirm"
          >
            确认并进入系统
          </el-button>
        </el-form-item>
      </el-form>

      <div class="login-footer">
        <span>选择单位后可在顶部导航栏随时切换</span>
      </div>
    </div>

    <!-- 忘记密码对话框 -->
    <el-dialog
      v-model="forgotPasswordVisible"
      title="忘记密码"
      width="420px"
      :close-on-click-modal="false"
    >
      <el-alert
        title="密码找回说明"
        type="info"
        :closable="false"
        style="margin-bottom: 20px"
      >
        <template #default>
          <p style="margin: 0; line-height: 1.8">
            本系统为内部管理系统，不提供自助找回密码功能。<br />
            如忘记密码，请联系<strong>县级管理员</strong>为您重置密码。<br />
            重置后您将获得一个新密码，请及时修改。
          </p>
        </template>
      </el-alert>
      <template #footer>
        <el-button type="primary" @click="forgotPasswordVisible = false">我知道了</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import { useUserStore } from '@/store/user'

const router = useRouter()
const userStore = useUserStore()

const loginFormRef = ref(null)
const loading = ref(false)
const unitLoading = ref(false)
const showUnitSelect = ref(false)
const selectedUnitId = ref(null)
const forgotPasswordVisible = ref(false)

const loginForm = reactive({
  用户名: '',
  密码: ''
})

const loginRules = {
  用户名: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  密码: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

// 页面加载时：如果已登录但未选单位，显示单位选择界面
onMounted(async () => {
  if (userStore.isLoggedIn && userStore.token && !userStore.已选单位ID) {
    await loadUnits()
    if (userStore.可选单位.length === 1) {
      const unit = userStore.可选单位[0]
      await selectUnit(unit.id, unit.unit_name)
      router.push('/')
    } else if (userStore.可选单位.length > 1) {
      showUnitSelect.value = true
    }
  }
})

const handleLogin = async () => {
  if (!loginFormRef.value) return
  await loginFormRef.value.validate(async (valid) => {
    if (!valid) return
    
    loading.value = true
    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          用户名: loginForm.用户名,
          密码: loginForm.密码
        })
      })
      
      const result = await response.json()
      
      if (result.成功) {
        // 保存登录信息
        userStore.setLoginInfo({
          token: result.数据.token,
          用户名: result.数据.用户名,
          角色: result.数据.角色,
          权限: result.数据.权限 || []
        })
        
        // 加载可选单位列表
        await loadUnits()
        
        // 如果只有一个可选单位，自动选择
        if (userStore.可选单位.length === 1) {
          const unit = userStore.可选单位[0]
          await selectUnit(unit.id, unit.unit_name)
          ElMessage.success(`登录成功，已自动选择：${unit.unit_name}`)
          router.push('/')
        } else if (userStore.可选单位.length > 1) {
          // 多个单位，显示选择界面
          showUnitSelect.value = true
          ElMessage.success('登录成功，请选择工作单位')
        } else {
          // 没有可选单位，直接进入
          ElMessage.success('登录成功')
          router.push('/')
        }
      } else {
        ElMessage.error(result.detail || '登录失败')
      }
    } catch (e) {
      ElMessage.error('网络错误，请检查服务器连接')
      console.error(e)
    } finally {
      loading.value = false
    }
  })
}

const loadUnits = async () => {
  try {
    const token = userStore.token
    const response = await fetch(`/api/auth/units?token=${encodeURIComponent(token)}`)
    const result = await response.json()
    if (result.成功) {
      userStore.setAvailableUnits(result.数据 || [])
    }
  } catch (e) {
    console.error('加载单位列表失败:', e)
  }
}

const selectUnit = async (unitId, unitName) => {
  try {
    await fetch('/api/auth/select-unit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ token: userStore.token, 单位ID: unitId })
    })
    userStore.selectUnit(unitId, unitName)
  } catch (e) {
    console.error('选择单位失败:', e)
  }
}

const handleUnitConfirm = async () => {
  if (!selectedUnitId.value) {
    ElMessage.warning('请选择工作单位')
    return
  }
  
  unitLoading.value = true
  try {
    const unit = userStore.可选单位.find(u => u.id === selectedUnitId.value)
    if (unit) {
      await selectUnit(unit.id, unit.unit_name)
      ElMessage.success(`已选择：${unit.unit_name}`)
      router.push('/')
    }
  } catch (e) {
    ElMessage.error('选择单位失败')
  } finally {
    unitLoading.value = false
  }
}

const showForgotPassword = () => {
  forgotPasswordVisible.value = true
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  width: 420px;
  padding: 40px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.login-header h1 {
  font-size: 22px;
  color: #303133;
  margin: 0 0 8px 0;
}

.login-header p {
  font-size: 14px;
  color: #909399;
  margin: 0;
}

.login-form {
  margin-top: 20px;
}

.login-btn {
  width: 100%;
}

.login-footer {
  text-align: center;
  margin-top: 20px;
  font-size: 12px;
  color: #c0c4cc;
}
</style>