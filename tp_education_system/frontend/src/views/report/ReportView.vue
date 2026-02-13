<template>
  <div class="report-view-container">
    <!-- 头部 -->
    <div class="header">
      <div class="header-left">
        <el-button link @click="goBack">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <h2 class="title">{{ reportTitle }}</h2>
      </div>
      <div class="header-right">
        <span v-if="teacherId" class="teacher-info">
          教师: {{ teacherName || teacherId }}
        </span>
        <el-button type="primary" @click="saveReport" :loading="saving" v-if="mode === 'fill'">
          <el-icon><Check /></el-icon>
          保存
        </el-button>
        <el-button type="success" @click="exportReport">
          <el-icon><Download /></el-icon>
          导出
        </el-button>
      </div>
    </div>

    <!-- 报表内容 -->
    <div class="content">
      <div v-if="loading" class="loading">
        <el-skeleton :rows="20" animated />
      </div>
      <div v-else-if="error" class="error">
        <el-empty :description="error" />
      </div>
      <div v-else ref="reportRef" class="report-content" v-html="reportHtml"></div>
    </div>

    <!-- 调试信息 -->
    <el-collapse v-model="activeNames" class="debug-panel">
      <el-collapse-item title="调试信息" name="debug">
        <div>模板ID: {{ templateId }}</div>
        <div>中间表: {{ tableName }}</div>
        <div>教师ID: {{ teacherId }}</div>
        <div>模式: {{ mode }}</div>
      </el-collapse-item>
    </el-collapse>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, Check, Download } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()

// 路由参数 - URL中使用的是template_id（如：职工退休呈报表html）
const templateId = computed(() => route.params.templateId as string)
const teacherId = computed(() => parseInt(route.params.teacherId as string) || 0)
const mode = computed(() => (route.query.mode as string) || 'fill')
const tableNameFromQuery = computed(() => route.query.table as string || '')

// 状态
const loading = ref(true)
const error = ref('')
const saving = ref(false)
const activeNames = ref(['debug'])  // 默认展开调试信息
const reportRef = ref<HTMLDivElement | null>(null)

// 数据
const reportTitle = ref('')
const teacherName = ref('')
const tableName = ref('')
const reportData = ref<Record<string, any>>({})
const reportHtml = ref('')

// 返回
const goBack = () => {
  router.back()
}

// 加载报表
const loadReport = async () => {
  loading.value = true
  error.value = ''

  try {
    console.log('【ReportView】加载报表:', {
      templateId: templateId.value,
      teacherId: teacherId.value,
      mode: mode.value
    })

    // 检查 templateId 是否有效
    if (!templateId.value || templateId.value === 'undefined') {
      throw new Error(`模板ID无效: ${templateId.value}`)
    }

    // 1. 获取模板信息
    const encodedTemplateId = encodeURIComponent(templateId.value)
    const templateResponse = await fetch(`/api/templates/${encodedTemplateId}`)

    if (!templateResponse.ok) {
      throw new Error(`找不到模板: ${templateId.value}`)
    }

    const templateInfo = await templateResponse.json()
    reportTitle.value = templateInfo.template_name || templateId.value

    console.log('【ReportView】找到模板:', {
      templateId: templateId.value,
      templateName: reportTitle.value
    })

    // 2. 获取中间表数据
    // 优先使用query参数中的table名
    if (tableNameFromQuery.value) {
      tableName.value = tableNameFromQuery.value
    } else {
      // 默认使用 retirement_report_data
      tableName.value = 'retirement_report_data'
    }

    let data: Record<string, any> = {}
    if (teacherId.value) {
      try {
        const dataResponse = await fetch(`/api/auto-table/${tableName.value}/detail/${teacherId.value}`)
        if (dataResponse.ok) {
          const result = await dataResponse.json()
          if (result.status === 'success' && result.data) {
            data = result.data
            teacherName.value = data['姓名'] || ''
          }
        }
      } catch (e) {
        console.log('中间表无数据或不存在:', e)
      }
    }

    reportData.value = data

    // 3. 获取模板HTML
    const htmlResponse = await fetch(`/api/templates/${encodedTemplateId}/content`)
    if (!htmlResponse.ok) {
      throw new Error('无法加载模板内容')
    }
    let html = await htmlResponse.text()

    // 4. 填充数据
    html = fillTemplateData(html, data)

    reportHtml.value = html

  } catch (err: any) {
    error.value = err.message || '加载报表失败'
    ElMessage.error(error.value)
    console.error('【ReportView】加载失败:', err)
  } finally {
    loading.value = false
  }
}

// 填充模板数据
const fillTemplateData = (html: string, data: Record<string, any>): string => {
  let result = html

  // 替换 {{字段名}}
  result = result.replace(/\{\{(\w+)\}\}/g, (match, field) => {
    const value = data[field]
    if (value !== undefined && value !== null && value !== '') {
      return String(value)
    }
    return match  // 无数据时保留占位符
  })

  return result
}

// 保存报表
const saveReport = async () => {
  if (!reportRef.value) return

  saving.value = true
  try {
    const formData = extractDataFromDOM(reportRef.value)

    const response = await fetch(`/api/auto-table/${tableName.value}/update/${teacherId.value}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(formData)
    })

    const result = await response.json()
    if (result.status === 'success') {
      ElMessage.success('保存成功')
    } else {
      throw new Error(result.message || '保存失败')
    }
  } catch (err: any) {
    ElMessage.error(err.message || '保存失败')
  } finally {
    saving.value = false
  }
}

// 从DOM提取数据
const extractDataFromDOM = (container: HTMLDivElement): Record<string, any> => {
  const data: Record<string, any> = {}
  const fields = container.querySelectorAll('[data-field]')
  fields.forEach(field => {
    const fieldName = field.getAttribute('data-field')
    if (fieldName) {
      if (field instanceof HTMLInputElement || field instanceof HTMLTextAreaElement) {
        data[fieldName] = field.value
      } else if (field instanceof HTMLSelectElement) {
        data[fieldName] = field.value
      } else if (field.isContentEditable) {
        data[fieldName] = field.innerText
      } else {
        data[fieldName] = field.textContent || ''
      }
    }
  })
  return data
}

// 导出报表
const exportReport = async () => {
  try {
    const response = await fetch(`/api/templates/${templateId.value}/export`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        teacher_id: teacherId.value,
        data: reportData.value
      })
    })

    if (response.ok) {
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${reportTitle.value}_${teacherId.value}.docx`
      a.click()
      window.URL.revokeObjectURL(url)
      ElMessage.success('导出成功')
    } else {
      throw new Error('导出失败')
    }
  } catch (err: any) {
    ElMessage.error(err.message || '导出失败')
  }
}

onMounted(() => {
  loadReport()
})
</script>

<style scoped>
.report-view-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  background: #fff;
  border-bottom: 1px solid #dcdfe6;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 15px;
}

.title {
  font-size: 18px;
  font-weight: bold;
  margin: 0;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 15px;
}

.teacher-info {
  color: #606266;
  font-size: 14px;
}

.content {
  flex: 1;
  overflow: auto;
  padding: 20px;
}

.loading {
  max-width: 800px;
  margin: 0 auto;
  background: #fff;
  padding: 20px;
  border-radius: 4px;
}

.error {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
}

.report-content {
  max-width: 800px;
  margin: 0 auto;
  background: #fff;
  padding: 40px;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  min-height: 800px;
}

.debug-panel {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: #fff;
  border-top: 1px solid #dcdfe6;
  z-index: 100;
}
</style>
