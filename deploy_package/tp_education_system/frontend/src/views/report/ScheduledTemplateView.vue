<template>
  <div class="scheduled-template-container">
    <!-- 头部 -->
    <div class="header">
      <div class="header-left">
        <h2 class="title">固定时段任务模板</h2>
        <el-tag type="warning">定时任务</el-tag>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="refreshList">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </div>

    <!-- 模板列表 -->
    <div class="template-list">
      <el-row :gutter="20">
        <el-col :span="8" v-for="template in scheduledTemplates" :key="template.template_id">
          <el-card class="template-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <span class="template-name">{{ template.template_name }}</span>
                <el-tag size="small" :type="template.file_type === 'docx' ? 'primary' : 'success'">
                  {{ template.file_type.toUpperCase() }}
                </el-tag>
              </div>
            </template>
            
            <div class="template-info">
              <p><strong>执行周期:</strong> {{ getScheduleText(template.activation_config) }}</p>
              <p><strong>任务说明:</strong> {{ template.activation_config?.description || '无' }}</p>
              <p><strong>占位符数:</strong> {{ (template.placeholders || []).length }} 个</p>
            </div>
            
            <div class="template-actions">
              <el-button type="primary" @click="openTemplate(template)">
                <el-icon><Document /></el-icon>
                打开填报
              </el-button>
              <el-button type="success" @click="previewTemplate(template)">
                <el-icon><View /></el-icon>
                预览
              </el-button>
            </div>
          </el-card>
        </el-col>
      </el-row>
      
      <el-empty v-if="scheduledTemplates.length === 0" description="暂无固定时段任务模板" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Refresh, Document, View } from '@element-plus/icons-vue'

const router = useRouter()

const scheduledTemplates = ref<any[]>([])
const loading = ref(false)

// 获取固定时段任务模板列表
const loadScheduledTemplates = async () => {
  loading.value = true
  try {
    const response = await fetch('/api/universal-templates/list?activation_type=scheduled_task')
    const result = await response.json()
    if (result.status === 'success') {
      scheduledTemplates.value = result.data || []
    }
  } catch (e: any) {
    ElMessage.error('加载模板列表失败')
  } finally {
    loading.value = false
  }
}

// 获取执行周期文本
const getScheduleText = (config: any) => {
  if (!config) return '未配置'
  
  switch (config.schedule_type) {
    case 'monthly':
      return `每月 ${config.day_of_month || 1} 日`
    case 'quarterly':
      return `每季度 ${(config.months || []).join(', ')} 月`
    case 'yearly':
      return `每年 ${config.month_of_year || 1} 月 ${config.day_of_month || 1} 日`
    case 'custom':
      return `自定义: ${config.cron_expression || ''}`
    default:
      return '未配置'
  }
}

// 打开模板填报
const openTemplate = (template: any) => {
  // 跳转到通用报表填报页面
  // 这里需要一个教师选择对话框，或者使用默认教师
  router.push({
    name: 'UniversalReport',
    params: {
      templateId: encodeURIComponent(template.template_id),
      teacherId: '0' // 0 表示需要选择教师
    }
  })
}

// 预览模板
const previewTemplate = (template: any) => {
  router.push({
    name: 'UniversalReport',
    params: {
      templateId: encodeURIComponent(template.template_id),
      teacherId: '0'
    }
  })
}

const refreshList = () => {
  loadScheduledTemplates()
}

onMounted(() => {
  loadScheduledTemplates()
})
</script>

<style scoped>
.scheduled-template-container {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #e4e7ed;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 15px;
}

.title {
  margin: 0;
  font-size: 20px;
}

.template-list {
  margin-top: 20px;
}

.template-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.template-name {
  font-weight: bold;
  font-size: 16px;
}

.template-info {
  margin: 15px 0;
}

.template-info p {
  margin: 8px 0;
  color: #606266;
}

.template-actions {
  display: flex;
  gap: 10px;
  margin-top: 15px;
}
</style>
