<template>
  <div class="universal-report-container">
    <!-- 头部 -->
    <div class="header">
      <div class="header-left">
        <el-button link @click="goBack">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <h2 class="title">{{ templateName }}</h2>
      </div>
      <div class="header-right">
        <el-tag v-if="isManualMode" type="warning" style="margin-right: 10px">
          手工编辑模式
        </el-tag>
        <el-tag v-else type="success" style="margin-right: 10px">
          自动填报模式
        </el-tag>
        <span v-if="teacherId" class="teacher-info">
          教师: {{ teacherName || teacherId }}
        </span>
        <el-button type="success" @click="exportWord" :loading="exporting">
          <el-icon><Download /></el-icon>
          导出Word
        </el-button>
      </div>
    </div>

    <!-- 内容 -->
    <div class="content">
      <div v-if="loading" class="loading">
        <el-skeleton :rows="20" animated />
      </div>
      <div v-else-if="error" class="error">
        <el-empty :description="error" />
      </div>
      <div v-else class="preview-panel">
        <!-- 预览区域 -->
        <el-card class="preview-card">
          <template #header>
            <div class="card-header">
              <span>模板预览</span>
              <div>
                <el-tag type="info" style="margin-right: 10px;">
                  {{ pageInfo.page_size }} {{ pageInfo.orientation }}
                </el-tag>
                <el-tag :type="previewUrl ? 'success' : 'info'" style="margin-right: 10px;">
                  {{ previewUrl ? '预览已生成' : '未生成' }}
                </el-tag>
                <el-button v-if="previewUrl" type="primary" size="small" @click="downloadPreview">
                  <el-icon><Download /></el-icon>
                  下载
                </el-button>
              </div>
            </div>
          </template>
          
          <div class="preview-desc" style="margin-bottom: 15px;">
            <el-alert type="info" :closable="false" show-icon>
              <template #title>
                说明：<span class="has-data">绿色</span>为已填充数据，<span class="no-data">红色</span>为占位符
              </template>
            </el-alert>
          </div>
          
          <!-- PDF预览 -->
          <div v-if="pdfUrl" class="pdf-preview-container">
            <object
              :data="pdfUrl"
              type="application/pdf"
              class="pdf-preview-object"
            >
              <iframe 
                :src="pdfUrl" 
                class="pdf-preview-iframe"
                frameborder="0"
              ></iframe>
            </object>
          </div>
          
          <!-- Word预览（备用） -->
          <div v-else-if="previewUrl" class="word-preview-container">
            <iframe 
              :src="previewUrl" 
              class="word-preview-iframe"
              frameborder="0"
            ></iframe>
          </div>
          
          <!-- 加载中 -->
          <div v-else class="preview-loading">
            <el-skeleton :rows="10" animated />
          </div>
        </el-card>
        
        <!-- 数据映射表格（仅在自动模式显示） -->
        <el-card v-if="!isManualMode" class="mapping-card">
          <template #header>
            <div class="card-header">
              <span>字段映射状态</span>
              <el-tag type="info">{{ dataMapping.length }} 个字段</el-tag>
            </div>
          </template>
          
          <div class="data-table">
            <table>
              <thead>
                <tr>
                  <th>占位符</th>
                  <th>当前值</th>
                  <th>状态</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in dataMapping" :key="item.placeholder">
                  <td class="placeholder-cell">{{ item.placeholder }}</td>
                  <td class="value-cell">
                    <span v-if="item.has_data" class="has-value">{{ item.value }}</span>
                    <span v-else class="no-value">{{ item.display }}</span>
                  </td>
                  <td class="status-cell">
                    <el-tag v-if="item.has_data" type="success" size="small">已填充</el-tag>
                    <el-tag v-else type="danger" size="small">未填充</el-tag>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </el-card>
        
        <!-- 导出按钮 -->
        <div class="actions">
          <el-button type="primary" size="large" @click="exportWord" :loading="exporting">
            <el-icon><Download /></el-icon>
            导出填充后的Word文档
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, Download } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()

// 从路由参数获取
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

const teacherId = computed(() => {
  const rawId = route.params.teacherId
  if (!rawId) return 0
  const num = parseInt(String(rawId), 10)
  return isNaN(num) ? 0 : num
})

const teacherName = computed(() => route.query.teacher_name as string || '')
const isManualMode = computed(() => route.query.manual === 'true')

const templateName = ref('')
const previewUrl = ref('')
const pdfUrl = ref('')
const dataMapping = ref<any[]>([])
const pageInfo = ref<any>({
  page_size: 'A4',
  orientation: '纵向',
  page_width_mm: 210,
  page_height_mm: 297
})
const loading = ref(false)
const exporting = ref(false)
const error = ref('')

// 计算预览容器样式
const previewContainerStyle = computed(() => {
  const info = pageInfo.value
  const isLandscape = info.orientation === '横向'
  const width = isLandscape ? info.page_height_mm : info.page_width_mm
  const height = isLandscape ? info.page_width_mm : info.page_height_mm
  
  // 根据页面大小和容器宽度计算合适的缩放比例
  // A3 横向双页模板内容较宽，需要更小的缩放
  const containerWidth = 1200  // 预览容器大约宽度(px)
  const mmToPx = 3.78  // 1mm ≈ 3.78px
  const pageWidthPx = width * mmToPx
  
  // 计算缩放比例
  let scale = (containerWidth / pageWidthPx) * 0.9
  
  // A3 横向页面使用更小的缩放
  if (info.page_size === 'A3' && isLandscape) {
    scale = 0.35  // A3横向双页需要更小的缩放
  } else if (info.page_size === 'A3') {
    scale = 0.5
  } else if (info.page_size === 'A4' && isLandscape) {
    scale = 0.6
  } else {
    scale = 0.8
  }
  
  return {
    width: `${width}mm`,
    minHeight: `${height}mm`,
    transform: `scale(${scale})`,
    transformOrigin: 'top left',
    margin: '0 20px 0 0',
    background: '#fff',
    boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
    padding: '10mm',
    flexShrink: 0
  }
})

// 加载模板信息和预览
const loadTemplate = async () => {
  loading.value = true
  error.value = ''
  
  console.log('【UniversalReportView】页面加载:', {
    templateId: templateId.value,
    teacherId: teacherId.value,
    teacherName: teacherName.value
  })
  
  try {
    const encodedId = encodeURIComponent(templateId.value)
    
    // 加载模板信息
    const response = await fetch(`/api/universal-templates/${encodedId}`)
    if (!response.ok) {
      throw new Error('模板不存在')
    }
    
    const result = await response.json()
    if (result.status === 'success') {
      templateName.value = result.data.template_name || templateId.value
      // 获取页面设置
      if (result.data.page_info) {
        pageInfo.value = result.data.page_info
      }
      console.log('【UniversalReportView】模板加载成功:', templateName.value, '页面设置:', pageInfo.value)
    } else {
      throw new Error(result.detail || '加载模板失败')
    }
    
    // 加载预览
    await loadPreview()
    
  } catch (e: any) {
    error.value = e.message || '加载模板失败'
    ElMessage.error(error.value)
  } finally {
    loading.value = false
  }
}

// 加载预览
const loadPreview = async () => {
  // 手动编辑模式：只加载空模板，不获取数据
  if (isManualMode.value) {
    console.log('【UniversalReportView】手动编辑模式，加载空模板')
    try {
      const encodedId = encodeURIComponent(templateId.value)
      // 使用 teacher_id=0 获取空模板预览
      const response = await fetch(`/api/universal-templates/${encodedId}/preview?teacher_id=0`)
      if (!response.ok) throw new Error('加载预览失败')
      const result = await response.json()
      if (result.status === 'success') {
        const baseUrl = window.location.origin
        previewUrl.value = result.preview_url ? baseUrl + result.preview_url : ''
        pdfUrl.value = result.pdf_url ? baseUrl + result.pdf_url : ''
        // 手动模式不显示数据映射表格
        dataMapping.value = []
        if (result.page_info) {
          pageInfo.value = result.page_info
        }
      }
    } catch (e: any) {
      console.error('【UniversalReportView】加载预览失败:', e)
    }
    return
  }

  // 自动填报模式
  try {
    const encodedId = encodeURIComponent(templateId.value)
    console.log('【UniversalReportView】加载预览:', {
      templateId: templateId.value,
      teacherId: teacherId.value,
      encodedId,
      url: `/api/universal-templates/${encodedId}/preview?teacher_id=${teacherId.value}`
    })

    const response = await fetch(`/api/universal-templates/${encodedId}/preview?teacher_id=${teacherId.value}`)

    if (!response.ok) {
      throw new Error('加载预览失败')
    }

    const result = await response.json()
    console.log('【UniversalReportView】预览结果:', result)

    if (result.status === 'success') {
      // 添加基础URL到相对路径
      const baseUrl = window.location.origin
      previewUrl.value = result.preview_url ? baseUrl + result.preview_url : ''
      pdfUrl.value = result.pdf_url ? baseUrl + result.pdf_url : ''
      dataMapping.value = result.data_mapping || []
      // 获取页面设置
      if (result.page_info) {
        pageInfo.value = result.page_info
      }
      console.log('【UniversalReportView】设置数据:', {
        previewUrl: previewUrl.value,
        pdfUrl: pdfUrl.value,
        dataMappingLength: dataMapping.value.length,
        pageInfo: pageInfo.value
      })
    }
  } catch (e: any) {
    console.error('【UniversalReportView】加载预览失败:', e)
  }
}

// 下载预览文件
const downloadPreview = () => {
  if (!previewUrl.value) return
  
  const link = document.createElement('a')
  link.href = previewUrl.value
  link.download = `${templateName.value}_预览.docx`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

// 导出Word
const exportWord = async () => {
  if (!templateId.value || !teacherId.value) {
    ElMessage.error('模板ID或教师ID无效')
    return
  }
  
  exporting.value = true
  
  try {
    const encodedId = encodeURIComponent(templateId.value)
    const url = `/api/universal-templates/${encodedId}/export?teacher_id=${teacherId.value}&teacher_name=${encodeURIComponent(teacherName.value || '')}`
    
    const response = await fetch(url)
    
    if (!response.ok) {
      throw new Error('导出失败')
    }
    
    const blob = await response.blob()
    const downloadUrl = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = downloadUrl
    a.download = `${templateName.value}_${teacherName.value || teacherId.value}.docx`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(downloadUrl)
    
    ElMessage.success('导出成功')
  } catch (e: any) {
    ElMessage.error(e.message || '导出失败')
  } finally {
    exporting.value = false
  }
}

const goBack = () => {
  router.back()
}

onMounted(() => {
  loadTemplate()
})
</script>

<style scoped>
.universal-report-container {
  padding: 20px;
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 20px;
  border-bottom: 1px solid #e4e7ed;
  margin-bottom: 20px;
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

.header-right {
  display: flex;
  align-items: center;
  gap: 15px;
}

.teacher-info {
  color: #606266;
}

.content {
  flex: 1;
  overflow: auto;
}

.loading, .error {
  padding: 40px;
}

.preview-panel {
  width: 98%;
  max-width: 98%;
  margin: 0 auto;
  padding: 10px;
}

.preview-card, .mapping-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.preview-actions {
  text-align: center;
  padding: 20px;
}

.preview-desc {
  color: #606266;
  margin-bottom: 20px;
  line-height: 1.8;
}

.has-data {
  color: #67C23A;
  font-weight: bold;
}

.no-data {
  color: #F56C6C;
  font-weight: bold;
}

.data-table {
  max-height: 400px;
  overflow: auto;
}

.data-table table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th,
.data-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #e4e7ed;
}

.data-table th {
  background: #f5f7fa;
  font-weight: bold;
  color: #606266;
}

.placeholder-cell {
  width: 30%;
  font-family: monospace;
  color: #409EFF;
  background: #f5f7fa;
}

.value-cell .has-value {
  color: #67C23A;
}

.value-cell .no-value {
  color: #F56C6C;
  font-family: monospace;
}

.status-cell {
  width: 100px;
  text-align: center;
}

.actions {
  text-align: center;
  margin-top: 30px;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

/* 预览卡片 */
.preview-card {
  width: 100%;
  margin: 0 auto 20px;
}

/* PDF预览容器 */
.pdf-preview-container {
  width: 100%;
  height: 900px;
  background: #f0f2f5;
  border-radius: 4px;
  overflow: hidden;
}

.pdf-preview-object {
  width: 100%;
  height: 100%;
  border: none;
}

.pdf-preview-iframe {
  width: 100%;
  height: 100%;
  border: none;
}

/* Word预览容器 */
.word-preview-container {
  width: 100%;
  height: 800px;
  background: #f0f2f5;
  border-radius: 4px;
  overflow: hidden;
}

.word-preview-iframe {
  width: 100%;
  height: 100%;
  border: none;
}

.preview-loading {
  padding: 40px;
}

/* 预览滚动容器 */
.preview-scroll-container {
  overflow: auto;
  padding: 20px;
  background: #f0f2f5;
  border-radius: 4px;
  min-height: 600px;
  display: flex;
  justify-content: flex-start;
  align-items: flex-start;
}

/* 文档预览样式 */
.document-preview {
  padding: 20mm;
  background: #fff;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
  margin: 0 auto;
}

.document-preview :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 5px 0;
  table-layout: fixed;
}

.document-preview :deep(td),
.document-preview :deep(th) {
  border: 1px solid #000;
  padding: 4px 6px;
  text-align: left;
  font-size: 11px;
  vertical-align: top;
  word-wrap: break-word;
}

.document-preview :deep(p) {
  margin: 4px 0;
  line-height: 1.4;
  font-size: 11px;
}

/* 占位符样式 */
.document-preview :deep(*) {
  color: #333;
}
</style>
