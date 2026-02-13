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
        <el-button circle class="notification-button">
          <el-icon><Bell /></el-icon>
        </el-button>
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
</template>

<script setup lang="ts">
import { School, Bell, ArrowDown } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'

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