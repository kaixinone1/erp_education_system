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
        <el-dropdown @command="handleExport" v-if="reportHtml">
          <el-button type="success">
            <el-icon><Download /></el-icon>
            导出
            <el-icon class="el-icon--right"><ArrowDown /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="html">HTML格式</el-dropdown-item>
              <el-dropdown-item command="excel">Excel格式</el-dropdown-item>
              <el-dropdown-item command="word">Word格式（原始模板）</el-dropdown-item>
              <el-dropdown-item command="pdf">PDF格式（可直接打印）</el-dropdown-item>

            </el-dropdown-menu>
          </template>
        </el-dropdown>
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
        <div style="margin-top: 10px;">
          <el-button size="small" type="primary" @click="testApi">测试API</el-button>
          <el-button size="small" @click="loadReport">重新加载</el-button>
        </div>
        <div v-if="testResult" style="margin-top: 10px; padding: 10px; background: #f5f5f5; border-radius: 4px;">
          <pre>{{ testResult }}</pre>
        </div>
      </el-collapse-item>
    </el-collapse>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, Check, Download, ArrowDown } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()

// 从路由参数中获取模板ID（支持URL编码的中文）
const templateId = computed(() => {
  const rawId = route.params.templateId
  if (!rawId) return ''
  const idStr = String(rawId)
  try {
    return decodeURIComponent(idStr)
  } catch {
    return idStr
  }
})

// 从路由参数中获取教师ID（转换为数字）
const teacherId = computed(() => {
  const rawId = route.params.teacherId
  console.log('【ReportView】原始teacherId:', rawId, '类型:', typeof rawId)
  if (!rawId) return 0
  const num = parseInt(String(rawId), 10)
  console.log('【ReportView】解析后teacherId:', num)
  return isNaN(num) ? 0 : num
})
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
const testResult = ref('')
const pageInfo = ref<{width: number, height: number, isLandscape: boolean} | null>(null)

// 测试API
const testApi = async () => {
  testResult.value = '测试中...'
  try {
    // 确保使用正确的表名
    let actualTableName = tableName.value || 'retirement_report_data'
    if (actualTableName === 'retirement_report_form') {
      actualTableName = 'retirement_report_data'
    }
    const apiUrl = `/api/auto-table/${actualTableName}/detail/${teacherId.value}`
    testResult.value += `\nAPI URL: ${apiUrl}`
    
    const response = await fetch(apiUrl)
    testResult.value += `\n状态码: ${response.status}`
    
    const text = await response.text()
    testResult.value += `\n响应: ${text.substring(0, 500)}`
  } catch (e: any) {
    testResult.value += `\n错误: ${e.message}`
  }
}

// 返回
const goBack = () => {
  router.back()
}

// 加载报表
const loadReport = async () => {
  loading.value = true
  error.value = ''

  try {
    console.log('【ReportView】当前URL:', window.location.href)
    console.log('【ReportView】路由参数:', {
      params: route.params,
      query: route.query,
      fullPath: route.fullPath
    })
    console.log('【ReportView】加载报表:', {
      templateId: templateId.value,
      teacherId: teacherId.value,
      teacherIdType: typeof teacherId.value,
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

    // 1.5 获取页面信息（尺寸、方向）
    try {
      const pageInfoResponse = await fetch(`/api/templates/${encodedTemplateId}/page-info`)
      if (pageInfoResponse.ok) {
        const pageInfoData = await pageInfoResponse.json()
        if (pageInfoData.status === 'success') {
          pageInfo.value = {
            width: pageInfoData.page_width,
            height: pageInfoData.page_height,
            isLandscape: pageInfoData.is_landscape,
            paperSize: pageInfoData.paper_size || 'A4'
          }
          console.log('【ReportView】页面信息:', pageInfo.value, '来源:', pageInfoData.source)
        }
      }
    } catch (e) {
      console.log('【ReportView】获取页面信息失败:', e)
      // 使用默认A4纵向
      pageInfo.value = { width: 595, height: 842, isLandscape: false, paperSize: 'A4' }
    }

    // 2. 获取中间表数据
    // 优先使用query参数中的table名
    if (tableNameFromQuery.value) {
      tableName.value = tableNameFromQuery.value
      // 兼容旧配置：retirement_report_form -> retirement_report_data
      if (tableName.value === 'retirement_report_form') {
        console.log('【ReportView】表名映射: retirement_report_form -> retirement_report_data')
        tableName.value = 'retirement_report_data'
      }
    } else {
      // 默认使用 retirement_report_data
      tableName.value = 'retirement_report_data'
    }

    console.log('【ReportView】准备获取数据:', {
      teacherId: teacherId.value,
      tableName: tableName.value,
      hasTeacherId: !!teacherId.value
    })

    let data: Record<string, any> = {}
    // teacherId 为 0 也是合法的（表示未指定教师），只要有 templateId 就调用 API
    if (templateId.value) {
      try {
        // 使用统一的模板填报API
        // 对templateId进行URL编码，确保中文能正确传递
        const encodedTemplateId = encodeURIComponent(templateId.value)
        const apiUrl = `/api/template-field-mapping/fill-data/${encodedTemplateId}?teacher_id=${teacherId.value}`
        console.log('【ReportView】调用API:', apiUrl)
        
        const dataResponse = await fetch(apiUrl)
        console.log('【ReportView】API响应状态:', dataResponse.status, dataResponse.ok)
        
        if (dataResponse.ok) {
          const result = await dataResponse.json()
          console.log('【ReportView】API响应结果:', result)
          
          if (result.status === 'success') {
            data = result.data || {}
            teacherName.value = data['姓名'] || ''
            
            if (Object.keys(data).length === 0) {
              console.warn('【ReportView】暂无数据:', result)
              ElMessage.warning('暂无填报数据')
            } else {
              console.log('【ReportView】获取到数据:', Object.keys(data))
            }
          } else {
            console.warn('【ReportView】API返回异常:', result)
            ElMessage.warning('获取数据失败: ' + (result.message || '未知错误'))
          }
        } else {
          const errorText = await dataResponse.text()
          console.error('【ReportView】API调用失败:', dataResponse.status, errorText)
          ElMessage.error(`获取数据失败: ${dataResponse.status}`)
        }
      } catch (e) {
        console.error('【ReportView】获取数据异常:', e)
        ElMessage.error('获取数据失败，请检查网络连接')
      }
    } else {
      console.warn('【ReportView】templateId为空，跳过数据获取')
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

  // 第一步：提取所有 {{...}} 占位符（包含HTML标签）
  const placeholderRegex = /\{\{([^}]+)\}\}/g
  const matches = result.match(placeholderRegex) || []

  console.log('【fillTemplateData】找到占位符数量:', matches.length)

  // 第二步：处理每个占位符
  matches.forEach((match) => {
    // 提取 {{ 和 }} 之间的内容
    const content = match.slice(2, -2)

    // 清理HTML标签，只保留纯文本
    const tempDiv = document.createElement('div')
    tempDiv.innerHTML = content
    const fieldName = tempDiv.textContent?.trim().replace(/\s+/g, '') || ''

    console.log('【fillTemplateData】处理占位符:', { original: match.slice(0, 50), fieldName })

    if (fieldName) {
      const value = data[fieldName]
      if (value !== undefined && value !== null && value !== '') {
        // 替换整个占位符为数据值
        result = result.replace(match, String(value))
      } else {
        console.log('【fillTemplateData】无数据，保留占位符:', fieldName)
      }
    }
  })

  return result
}

// 保存报表
const saveReport = async () => {
  if (!reportRef.value) return

  saving.value = true
  try {
    const formData = extractDataFromDOM(reportRef.value)

    // 使用新框架API
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

// 处理导出命令
const handleExport = (format: string) => {
  switch (format) {
    case 'html':
      exportAsHtml()
      break
    case 'excel':
      exportAsExcel()
      break
    case 'word':
      exportAsWord()
      break
    case 'pdf':
      exportAsPdf()
      break
  }
}



// 获取打印样式（根据页面尺寸）
const getPrintStyles = () => {
  const isLandscape = pageInfo.value?.isLandscape || false
  const paperSizeName = pageInfo.value?.paperSize || 'A4'
  const paperSize = isLandscape ? `${paperSizeName} landscape` : paperSizeName
  
  console.log('【导出】纸张设置:', { paperSize, paperSizeName, isLandscape })
  
  return `
    @page {
      size: ${paperSize};
      margin: 10mm;
    }
    @media print {
      body { margin: 0; }
      .no-print { display: none !important; }
    }
  `
}

// 导出为HTML
const exportAsHtml = () => {
  try {
    if (!reportHtml.value) {
      ElMessage.warning('报表内容为空，无法导出')
      return
    }

    const fullHtml = `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>${reportTitle.value}</title>
  <style>
    ${getPrintStyles()}
    body { 
      font-family: "SimSun", "宋体", serif; 
      margin: 20px; 
    }
    table { border-collapse: collapse; width: 100%; }
    td, th { border: 1px solid #000; padding: 8px; }
  </style>
</head>
<body>
  ${reportHtml.value}
</body>
</html>`

    const blob = new Blob([fullHtml], { type: 'text/html;charset=utf-8' })
    downloadBlob(blob, `${reportTitle.value}_${teacherId.value || 'preview'}.html`)
    ElMessage.success('HTML导出成功')
  } catch (err: any) {
    console.error('HTML导出失败:', err)
    ElMessage.error('HTML导出失败: ' + err.message)
  }
}

// 导出为Excel（后端生成，按照报表格式排版）
const exportAsExcel = async () => {
  try {
    if (!reportData.value || Object.keys(reportData.value).length === 0) {
      ElMessage.warning('报表数据为空，无法导出')
      return
    }

    ElMessage.info('正在生成Excel，请稍候...')

    const encodedTemplateId = encodeURIComponent(templateId.value)
    const response = await fetch(`/api/templates/${encodedTemplateId}/export-excel`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        teacher_id: teacherId.value,
        data: reportData.value
      })
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.detail || 'Excel生成失败')
    }

    // 获取Excel文件
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${reportTitle.value}_${teacherId.value || 'preview'}_报表.xlsx`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)

    ElMessage.success('Excel导出成功')
  } catch (err: any) {
    console.error('Excel导出失败:', err)
    ElMessage.error('Excel导出失败: ' + err.message)
  }
}

// 导出为Word（使用原始Word模板）
const exportAsWord = async () => {
  try {
    if (!reportData.value || Object.keys(reportData.value).length === 0) {
      ElMessage.warning('报表数据为空，无法导出')
      return
    }

    ElMessage.info('正在生成Word文档，请稍候...')

    const encodedTemplateId = encodeURIComponent(templateId.value)
    const response = await fetch(`/api/templates/${encodedTemplateId}/export-word`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        teacher_id: teacherId.value,
        data: reportData.value
      })
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.detail || 'Word生成失败')
    }

    // 获取Word文件
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `职工退休呈报表_${teacherId.value || 'preview'}_已填充.docx`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)

    ElMessage.success('Word导出成功（使用原始模板）')
  } catch (err: any) {
    console.error('Word导出失败:', err)
    ElMessage.error('Word导出失败: ' + err.message)
  }
}

// 导出为PDF（后端生成真正的PDF文件）
const exportAsPdf = async () => {
  try {
    if (!reportData.value || Object.keys(reportData.value).length === 0) {
      ElMessage.warning('报表数据为空，无法导出')
      return
    }

    ElMessage.info('正在生成PDF，请稍候...')

    const encodedTemplateId = encodeURIComponent(templateId.value)
    const response = await fetch(`/api/templates/${encodedTemplateId}/export-pdf`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        teacher_id: teacherId.value,
        data: reportData.value
      })
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.detail || 'PDF生成失败')
    }

    // 获取PDF文件
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${reportTitle.value}_${teacherId.value || 'preview'}_报表.pdf`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)

    ElMessage.success('PDF导出成功，可直接打印')
  } catch (err: any) {
    console.error('PDF导出失败:', err)
    ElMessage.error('PDF导出失败: ' + err.message)
  }
}

// 下载Blob文件
const downloadBlob = (blob: Blob, filename: string) => {
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  window.URL.revokeObjectURL(url)
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
  width: 100%;
  height: 100%;
  max-width: 100%;
  margin: 0 auto;
  background: #fff;
  padding: 20px;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  overflow: auto;
  display: flex;
  flex-direction: column;
  align-items: center;
}

/* 报表内容自适应 */
.report-content :deep(*) {
  max-width: 100% !important;
  box-sizing: border-box;
}

/* 表格自适应 */
.report-content :deep(table) {
  width: 100% !important;
  max-width: 100%;
  table-layout: auto;
}

/* 图片自适应 */
.report-content :deep(img) {
  max-width: 100% !important;
  height: auto;
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
