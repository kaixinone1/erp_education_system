<template>
  <div class="template-fill-page">
    <!-- 顶部工具栏 -->
    <div class="fill-header">
      <div class="header-left">
        <el-button @click="goBack">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <h2>{{ templateName }} - 填报</h2>
      </div>
      <div class="header-info">
        <span class="teacher-name">教师：{{ teacherName }}</span>
      </div>
      <div class="header-actions">
        <el-button type="success" @click="fillWithData" :loading="filling">
          <el-icon><DataLine /></el-icon>
          自动填充数据
        </el-button>
        <el-button type="primary" @click="downloadDocument" :loading="downloading">
          <el-icon><Download /></el-icon>
          下载文档
        </el-button>
      </div>
    </div>

    <!-- 主体区域 -->
    <div class="fill-container">
      <!-- 左侧：表单预览 -->
      <div class="form-panel">
        <div class="panel-header">
          <h3>表单预览</h3>
          <el-alert
            title="数据已自动填充，可直接下载或修改后下载"
            type="success"
            :closable="false"
            show-icon
          />
        </div>
        <div class="form-container" ref="formContainer">
          <div v-html="filledHtml" class="form-content"></div>
        </div>
      </div>

      <!-- 右侧：数据核对 -->
      <div class="data-panel">
        <div class="panel-header">
          <h3>数据核对</h3>
        </div>
        
        <el-scrollbar class="data-list">
          <el-descriptions :column="1" border>
            <el-descriptions-item label="姓名">{{ teacherData.name || '-' }}</el-descriptions-item>
            <el-descriptions-item label="性别">{{ teacherData.gender || '-' }}</el-descriptions-item>
            <el-descriptions-item label="身份证号">{{ teacherData.id_card || '-' }}</el-descriptions-item>
            <el-descriptions-item label="出生日期">{{ teacherData.birth_date || '-' }}</el-descriptions-item>
            <el-descriptions-item label="民族">{{ teacherData.ethnicity || '-' }}</el-descriptions-item>
            <el-descriptions-item label="籍贯">{{ teacherData.native_place || '-' }}</el-descriptions-item>
            <el-descriptions-item label="参加工作时间">{{ teacherData.work_start_date || '-' }}</el-descriptions-item>
            <el-descriptions-item label="联系电话">{{ teacherData.contact_phone || '-' }}</el-descriptions-item>
            <el-descriptions-item label="档案出生日期">{{ teacherData.archive_birth_date || '-' }}</el-descriptions-item>
          </el-descriptions>
        </el-scrollbar>
      </div>
    </div>

    <!-- 下载对话框 -->
    <el-dialog
      v-model="showDownloadDialog"
      title="下载文档"
      width="400px"
    >
      <p>请选择下载格式：</p>
      <div class="download-options">
        <el-radio-group v-model="downloadFormat">
          <el-radio label="html">HTML格式（网页）</el-radio>
          <el-radio label="excel">Excel格式</el-radio>
          <el-radio label="word">Word格式</el-radio>
        </el-radio-group>
      </div>
      <template #footer>
        <el-button @click="showDownloadDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmDownload" :loading="downloading">
          下载
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, DataLine, Download } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const templateId = route.params.id as string
// 从URL参数获取教师ID，如果没有则报错（不再使用硬编码默认值）
const teacherId = route.query.teacher_id as string

// 如果没有教师ID，显示错误并返回
if (!teacherId) {
  ElMessage.error('缺少教师ID参数，请从待办工作清单中进入')
}

// 数据
const templateName = ref('')
const teacherName = ref('')
const filledHtml = ref('')
const teacherData = ref<Record<string, any>>({})
const filling = ref(false)
const downloading = ref(false)
const showDownloadDialog = ref(false)
const downloadFormat = ref('html')
const formContainer = ref<HTMLElement | null>(null)

// 加载模板和数据
const loadTemplateAndData = async () => {
  try {
    // 获取模板信息
    const templateResponse = await fetch(`/api/templates/list`)
    const templateResult = await templateResponse.json()
    if (templateResult.status === 'success') {
      const templates = templateResult.templates || templateResult.data || []
      const template = templates.find((t: any) => t.template_id === templateId)
      if (template) {
        templateName.value = template.template_name
      }
    }

    // 获取教师数据
    try {
      const teacherResponse = await fetch(`/api/retirement/search-by-name?id=${teacherId}`)
      if (teacherResponse.ok) {
        const teacherResult = await teacherResponse.json()
        const teachers = teacherResult.data || []
        if (teachers.length > 0) {
          const teacher = teachers[0]
          teacherData.value = {
            name: teacher.teacher_name,
            id_card: teacher.id_card,
            gender: teacher.gender,
            birth_date: teacher.birth_date,
            ethnicity: teacher.ethnicity,
            native_place: teacher.native_place,
            work_start_date: teacher.work_start_date,
            contact_phone: teacher.contact_phone,
            archive_birth_date: teacher.archive_birth_date
          }
          teacherName.value = teacher.teacher_name || '未知'
        }
      }
    } catch (e) {
      console.error('获取教师数据失败:', e)
    }

    // 获取可填写HTML
    const htmlResponse = await fetch(`/api/templates/${templateId}/preview?teacher_id=${teacherId}`)
    filledHtml.value = await htmlResponse.text()

    // 自动填充数据
    setTimeout(() => {
      fillWithData()
    }, 500)
  } catch (error) {
    console.error('加载失败:', error)
    ElMessage.error('加载模板或数据失败')
  }
}

// 自动填充数据 - 使用字段映射配置
const fillWithData = async () => {
  filling.value = true
  try {
    // 使用新的字段映射API获取填报数据
    const fillDataResponse = await fetch(`/api/template-field-mapping/fill-data/${templateId}?teacher_id=${teacherId}`)
    const fillDataResult = await fillDataResponse.json()
    
    if (fillDataResult.status === 'success') {
      const fillData = fillDataResult.data || {}
      
      // 填充每个字段（根据占位符）
      Object.entries(fillData).forEach(([placeholder, value]) => {
        // 支持多种占位符格式：{字段名} 或 {{字段名}}
        const inputs = formContainer.value?.querySelectorAll(`input[name="${placeholder}"]`)
        inputs?.forEach((input: Element) => {
          (input as HTMLInputElement).value = String(value || '')
        })
        
        // 也尝试查找带有特定data属性的元素
        const dataElements = formContainer.value?.querySelectorAll(`[data-field="${placeholder}"]`)
        dataElements?.forEach((el: Element) => {
          if (el instanceof HTMLInputElement || el instanceof HTMLTextAreaElement) {
            el.value = String(value || '')
          } else {
            el.textContent = String(value || '')
          }
        })
      })
      
      ElMessage.success('数据填充完成')
    } else {
      throw new Error(fillDataResult.message || '获取填报数据失败')
    }
  } catch (error: any) {
    console.error('填充失败:', error)
    ElMessage.error(error.message || '数据填充失败，请检查字段映射配置')
  } finally {
    filling.value = false
  }
}

// 显示下载对话框
const downloadDocument = () => {
  showDownloadDialog.value = true
}

// 确认下载
const confirmDownload = async () => {
  downloading.value = true
  try {
    let url = ''
    let filename = ''
    
    switch (downloadFormat.value) {
      case 'html':
        // 获取当前填充后的HTML内容
        const formHtml = formContainer.value?.innerHTML || ''
        
        // 创建完整的HTML文档
        const fullHtml = `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>${templateName.value}</title>
  <style>
    body { margin: 20px; }
    table { border-collapse: collapse; width: 100%; }
    td, th { border: 1px solid #000; padding: 5px; }
    input { border: none; background: transparent; width: 95%; }
    @media print {
      input { border: none; }
      body { margin: 0; }
    }
  </style>
</head>
<body>
  ${formHtml}
</body>
</html>`
        
        // 创建下载
        const blob = new Blob([fullHtml], { type: 'text/html' })
        url = URL.createObjectURL(blob)
        filename = `${templateName.value}_${teacherName.value}.html`
        break
        
      case 'excel':
        url = `/api/templates/${templateId}/preview-excel?teacher_id=${teacherId}`
        filename = `${templateName.value}_${teacherName.value}.xlsx`
        break
        
      case 'word':
        url = `/api/templates/${templateId}/preview-word?teacher_id=${teacherId}`
        filename = `${templateName.value}_${teacherName.value}.docx`
        break
    }
    
    if (url) {
      const link = document.createElement('a')
      link.href = url
      link.download = filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      
      if (downloadFormat.value === 'html') {
        URL.revokeObjectURL(url)
      }
      
      ElMessage.success('下载成功')
      showDownloadDialog.value = false
    }
  } catch (error) {
    console.error('下载失败:', error)
    ElMessage.error('下载失败')
  } finally {
    downloading.value = false
  }
}

// 返回
const goBack = () => {
  router.back()
}

onMounted(() => {
  loadTemplateAndData()
})
</script>

<style scoped>
.template-fill-page {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
}

.fill-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-left h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.header-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.teacher-name {
  font-size: 14px;
  color: #606266;
  background: #f0f9ff;
  padding: 6px 12px;
  border-radius: 4px;
  border: 1px solid #91d5ff;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.fill-container {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.form-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #fff;
  border-right: 1px solid #e4e7ed;
}

.panel-header {
  padding: 16px;
  border-bottom: 1px solid #e4e7ed;
  background: #fafafa;
}

.panel-header h3 {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 600;
}

.form-container {
  flex: 1;
  padding: 20px;
  overflow: auto;
  background: #f5f7fa;
}

.form-content {
  background: #fff;
  padding: 20px;
  min-height: 100%;
}

.form-content :deep(table) {
  border-collapse: collapse;
  width: 100%;
}

.form-content :deep(td),
.form-content :deep(th) {
  border: 1px solid #000;
  padding: 8px;
}

.form-content :deep(input) {
  width: 95%;
  border: none;
  background: transparent;
  font-size: inherit;
}

.data-panel {
  width: 350px;
  display: flex;
  flex-direction: column;
  background: #fff;
}

.data-list {
  flex: 1;
  padding: 16px;
}

.download-options {
  padding: 20px 0;
}

.download-options .el-radio {
  display: block;
  margin-bottom: 15px;
}
</style>
