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
        <!-- 个人模板：身份证号输入（未填报时显示） -->
        <template v-if="!activeTeacherId">
          <el-input
            v-model="idCardInput"
            placeholder="请输入身份证号码"
            style="width: 220px; margin-right: 8px;"
            clearable
            @keyup.enter="handleFillByIdCard"
          />
          <el-button type="primary" @click="handleFillByIdCard" :loading="idCardLoading">
            填报
          </el-button>
        </template>
        <template v-else>
          <el-tag type="success" style="margin-right: 10px">
            已填报
          </el-tag>
          <span v-if="activeTeacherName" class="teacher-info">
            {{ activeTeacherName }}
          </span>
          <el-button @click="resetFill" size="small">重新填报</el-button>
          <el-button type="success" @click="exportWord" :loading="exporting">
            <el-icon><Download /></el-icon>
            导出Word
          </el-button>
        </template>
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
                <el-tag :type="previewHtml ? 'success' : 'info'" style="margin-right: 10px;">
                  {{ previewHtml ? '预览已生成' : '未生成' }}
                </el-tag>
                <el-button v-if="previewHtml" type="primary" size="small" @click="downloadPreview">
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
          
          <!-- HTML预览 -->
          <div v-if="previewHtml" class="html-preview-container">
            <div class="document-preview" v-html="previewHtml"></div>
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
        
        <!-- 备注编辑卡片 -->
        <el-card v-if="!isManualMode" class="remark-card">
          <template #header>
            <div class="card-header">
              <span>备注编辑</span>
              <el-tag v-if="remarkSaved" type="success" size="small">已保存</el-tag>
            </div>
          </template>
          
          <div class="remark-content">
            <el-input
              v-model="remarkText"
              type="textarea"
              :rows="6"
              placeholder="备注内容将在自动填报后显示"
              :disabled="!remarkText && !remarkLoaded"
            />
            <div class="remark-actions">
              <el-button type="primary" @click="saveRemark" :loading="savingRemark">
                保存备注
              </el-button>
            </div>
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
const previewHtml = ref('')
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

// 身份证号填报
const idCardInput = ref('')
const idCardLoading = ref(false)
const activeTeacherId = ref(0)
const activeTeacherName = ref('')

// 备注编辑相关
const remarkText = ref('')
const remarkLoaded = ref(false)
const remarkSaved = ref(false)
const savingRemark = ref(false)

// 身份证号填报
const handleFillByIdCard = async () => {
  const idCard = idCardInput.value.trim()
  if (!idCard) {
    ElMessage.warning('请输入身份证号码')
    return
  }
  if (idCard.length !== 18) {
    ElMessage.warning('请输入正确的18位身份证号码')
    return
  }
  
  idCardLoading.value = true
  try {
    const resp = await fetch(`/api/universal-template/find-teacher-by-idcard?id_card=${encodeURIComponent(idCard)}`)
    const result = await resp.json()
    if (result.成功 && result.数据) {
      activeTeacherId.value = result.数据.id
      activeTeacherName.value = result.数据.姓名
      ElMessage.success(`找到教师：${result.数据.姓名}，正在填报数据...`)
      await loadPreviewWithIdCard(idCard)
    } else {
      ElMessage.error(result.消息 || '未找到该身份证号对应的教师')
    }
  } catch (e: any) {
    ElMessage.error('查询失败：' + (e.message || '网络错误'))
  } finally {
    idCardLoading.value = false
  }
}

// 重新填报
const resetFill = () => {
  activeTeacherId.value = 0
  activeTeacherName.value = ''
  idCardInput.value = ''
  previewHtml.value = ''
  dataMapping.value = []
}

// 使用身份证号加载预览
const loadPreviewWithIdCard = async (idCard: string) => {
  loading.value = true
  error.value = ''
  try {
    const encodedId = encodeURIComponent(templateId.value)
    const resp = await fetch(`/api/universal-template/preview/${encodedId}?id_card=${encodeURIComponent(idCard)}`)
    if (!resp.ok) throw new Error('加载预览失败')
    const result = await resp.json()
    if (result.成功 && result.数据) {
      previewHtml.value = result.数据.HTML || ''
      // 提取备注
      if (result.数据.备注) {
        remarkText.value = result.数据.备注
        remarkLoaded.value = true
      }
      ElMessage.success('数据填报完成')
    }
  } catch (e: any) {
    error.value = e.message || '加载预览失败'
    ElMessage.error(error.value)
  } finally {
    loading.value = false
  }
}

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
    
    // 加载模板信息（修正URL：/api/universal-template/config/{id}）
    const response = await fetch(`/api/universal-template/config/${encodedId}`)
    if (!response.ok) {
      throw new Error('模板不存在')
    }
    
    const result = await response.json()
    if (result.成功) {
      const config = result.数据
      templateName.value = config['模板名称'] || config.template_name || templateId.value
      // 获取页面设置
      if (config['页面设置']) {
        const ps = config['页面设置']
        pageInfo.value = {
          page_size: ps['纸张大小'] || 'A4',
          orientation: ps['方向'] || '纵向',
          page_width_mm: ps['宽度_mm'] || 210,
          page_height_mm: ps['高度_mm'] || 297
        }
      }
      console.log('【UniversalReportView】模板加载成功:', templateName.value, '页面设置:', pageInfo.value)
    } else {
      throw new Error(result.消息 || '加载模板失败')
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
      const response = await fetch(`/api/universal-template/preview/${encodedId}?teacher_id=0`)
      if (!response.ok) throw new Error('加载预览失败')
      const result = await response.json()
      if (result.成功 && result.数据) {
        previewHtml.value = result.数据.HTML || ''
        dataMapping.value = []
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
      url: `/api/universal-template/preview/${encodedId}?teacher_id=${teacherId.value}`
    })

    const response = await fetch(`/api/universal-template/preview/${encodedId}?teacher_id=${teacherId.value}`)

    if (!response.ok) {
      throw new Error('加载预览失败')
    }

    const result = await response.json()
    console.log('【UniversalReportView】预览结果:', result)

    if (result.成功 && result.数据) {
      const data = result.数据
      previewHtml.value = data.HTML || ''
      dataMapping.value = data.metadata?.cells?.map((cell: any) => ({
        placeholder: cell.v?.m || '',
        value: cell.v?.v || '',
        display: cell.v?.m || '',
        has_data: cell.v?.v !== cell.v?.m
      })) || []
      
      // 获取备注
      if (data.备注) {
        remarkText.value = data.备注
        remarkLoaded.value = true
      }
      
      console.log('【UniversalReportView】设置数据:', {
        previewHtmlLength: previewHtml.value.length,
        dataMappingLength: dataMapping.value.length,
        remark: remarkText.value
      })
    }
  } catch (e: any) {
    console.error('【UniversalReportView】加载预览失败:', e)
  }
  
  // 加载备注
  await loadRemark()
}

// 加载备注
const loadRemark = async () => {
  if (isManualMode.value) return
  try {
    const response = await fetch('/api/universal-template/fill', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        模板ID: templateId.value,
        查询条件: teacherId.value > 0 ? { 职工ID: String(teacherId.value) } : {}
      })
    })
    if (!response.ok) return
    const result = await response.json()
    if (result.成功 && result.数据?.备注) {
      remarkText.value = result.数据.备注
      remarkLoaded.value = true
    }
  } catch (e) {
    console.error('加载备注失败:', e)
  }
}

// 保存备注
const saveRemark = async () => {
  savingRemark.value = true
  try {
    const response = await fetch('/api/universal-template/save-remark', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        模板ID: templateId.value,
        模板名称: templateName.value,
        单位名称: activeTeacherName.value || '',
        年月: '',
        备注: remarkText.value
      })
    })
    if (!response.ok) throw new Error('保存失败')
    const result = await response.json()
    if (result.成功) {
      ElMessage.success('备注保存成功')
      remarkSaved.value = true
    } else {
      ElMessage.error(result.消息 || '保存失败')
    }
  } catch (e: any) {
    ElMessage.error('保存备注失败: ' + e.message)
  } finally {
    savingRemark.value = false
  }
}
const downloadPreview = () => {
  // 将HTML内容转为Blob下载
  if (!previewHtml.value) return
  const blob = new Blob([previewHtml.value], { type: 'text/html;charset=utf-8' })
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `${templateName.value}_预览.html`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  window.URL.revokeObjectURL(url)
}

// 导出Word
const exportWord = async () => {
  if (!templateId.value || !activeTeacherId.value) {
    ElMessage.error('请先输入身份证号码并填报数据')
    return
  }
  
  exporting.value = true
  
  try {
    const response = await fetch(`/api/universal-template/export`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        模板ID: templateId.value,
        查询条件: { 身份证号: idCardInput.value.trim() }
      })
    })
    
    if (!response.ok) {
      throw new Error('导出失败')
    }
    
    const blob = await response.blob()
    const downloadUrl = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = downloadUrl
    a.download = `${templateName.value}_${activeTeacherName.value || idCardInput.value}.xlsx`
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

.preview-card, .mapping-card, .remark-card {
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

.remark-content {
  padding: 10px 0;
}

.remark-actions {
  margin-top: 15px;
  text-align: right;
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

/* HTML预览容器 */
.html-preview-container {
  width: 100%;
  background: #f0f2f5;
  border-radius: 4px;
  overflow: auto;
  max-height: 85vh;
  padding: 10px;
}

.preview-loading {
  padding: 40px;
}

/* 文档预览样式 */
.document-preview {
  background: #fff;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
  margin: 0 auto;
  padding: 10px;
  min-width: fit-content;
}

.document-preview :deep(table) {
  border-collapse: collapse;
  margin: 0 auto;
}

.document-preview :deep(td),
.document-preview :deep(th) {
  border: 1px solid #000;
  padding: 2px 4px;
  vertical-align: middle;
}

.document-preview :deep(p) {
  margin: 4px 0;
  line-height: 1.4;
}

/* 打印时显示分页 */
@media print {
  .document-preview {
    box-shadow: none;
    padding: 0;
    margin: 0;
  }
  .html-preview-container {
    overflow: visible !important;
    max-height: none !important;
    padding: 0 !important;
    background: #fff !important;
  }
}

/* 保留占位符高亮 */
.document-preview :deep(.has-data) {
  background-color: #e8f5e9;
}
.document-preview :deep(.no-data) {
  background-color: #ffebee;
}
</style>

