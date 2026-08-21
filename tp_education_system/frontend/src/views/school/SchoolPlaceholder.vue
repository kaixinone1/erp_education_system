<template>
  <div class="placeholder-container">
    <div class="placeholder-content">
      <el-icon :size="64" color="#909399">
        <component :is="iconComponent" />
      </el-icon>
      <h2>{{ pageTitle }}</h2>
      <p class="description">该功能模块正在规划中，敬请期待</p>
      <p class="hint">如需添加相关数据，请先在"学校管理"模块下导入数据表</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { User, Calendar } from '@element-plus/icons-vue'

const route = useRoute()

const pageTitle = computed(() => {
  if (route.path.includes('student')) return '学生管理'
  if (route.path.includes('attendance')) return '考勤管理'
  return '功能开发中'
})

const iconComponent = computed(() => {
  if (route.path.includes('student')) return User
  if (route.path.includes('attendance')) return Calendar
  return null
})
</script>

<style scoped>
.placeholder-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 60vh;
}
.placeholder-content {
  text-align: center;
  color: #909399;
}
.placeholder-content h2 {
  margin: 20px 0 10px;
  font-size: 24px;
  color: #606266;
}
.description {
  font-size: 16px;
  margin-bottom: 8px;
}
.hint {
  font-size: 13px;
  color: #c0c4cc;
}
</style>