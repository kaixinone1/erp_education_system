<template>
  <div class="template-import-test">
    <el-card class="main-card">
      <template #header>
        <div class="card-header">
          <h2>测试导入模板功能</h2>
          <div class="header-actions">
            <el-button type="info" @click="showHelp">
              <el-icon><QuestionFilled /></el-icon>
              帮助
            </el-button>
          </div>
        </div>
      </template>

      <!-- 上传区域 -->
      <div class="upload-section" v-if="!selectedTemplate">
        <el-upload
          class="upload-area"
          drag
          :auto-upload="false"
          :on-change="handleFileChange"
          :on-success="handleSuccess"
          :on-error="handleError"
          :show-file-list="false"
          :limit="1"
          accept=".html,.htm"
        >
          <el-icon class="el-icon--upload"><upload-filled /></el-icon>
          <div class="el-upload__text">
            拖拽文件到此处或 <em>点击上传</em>
          </div>
          <template #tip>
            <div class="el-upload__tip" style="color: #E6A23C;">
              ⚠️ <strong>推荐使用HTML格式</strong><br/>
              请将Excel/Word文件另存为HTML后上传，可100%还原模板样式<br/>
              操作：文件 → 另存为 → 网页(*.html)
            </div>
          </template>
        </el-upload>
        
        <div class="recent-templates" v-if="templates.length > 0">
          <h3>已上传的模板</h3>
          <el-table :data="templates" style="width: 100%">
            <el-table-column prop="filename" label="文件名" width="200" />
            <el-table-column prop="file_type" label="类型" width="100">
              <template #default="{ row }">
                <el-tag>{{ row.file_type.toUpperCase() }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="upload_time" label="上传时间" />
            <el-table-column label="操作" width="250">
              <template #default="{ row }">
                <el-button type="primary" size="small" @click="openTemplate(row)">
                  打开编辑
                </el-button>
                <el-button type="danger" size="small" @click="deleteTemplate(row.id)">
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>

      <!-- 编辑区域 -->
      <div class="edit-section" v-else>
        <div class="edit-toolbar">
          <el-button @click="goBack">
            <el-icon><ArrowLeft /></el-icon>
            返回
          </el-button>
          <div class="toolbar-center">
            <span class="template-name">{{ selectedTemplate.filename }}</span>
            <el-tag type="info">{{ selectedTemplate.file_type.toUpperCase() }}</el-tag>
          </div>
          <div class="toolbar-actions">
            <el-button type="success" @click="saveData">
              <el-icon><Check /></el-icon>
              保存数据
            </el-button>
            <el-button type="warning" @click="showExportDialog">
              <el-icon><Download /></el-icon>
              导出
            </el-button>
          </div>
        </div>

        <div class="edit-container">
          <!-- 左侧预览编辑器 -->
          <div class="preview-editor">
            <div class="panel-header">
              <h3>模板预览与编辑</h3>
              <el-alert
                title="说明：点击可编辑的单元格直接输入数据"
                type="info"
                :closable="false"
                show-icon
                style="margin-top: 10px;"
              />
            </div>
            <div class="html-preview-container" ref="previewContainer">
              <iframe
                ref="iframeRef"
                class="preview-iframe"
                :src="previewSrc || undefined"
                :srcdoc="previewHtml || undefined"
                @load="onIframeLoad"
              ></iframe>
            </div>
          </div>

          <!-- 右侧数据面板 -->
          <div class="data-panel">
            <div class="panel-header">
              <h3>数据字段</h3>
              <el-button type="primary" size="small" @click="autoExtract">
                <el-icon><MagicStick /></el-icon>
                智能提取
              </el-button>
            </div>
            <div class="fields-list">
              <div
                v-for="(field, index) in fields"
                :key="index"
                class="field-item"
              >
                <div class="field-label">{{ field.label || field.name }}</div>
                <el-input
                  v-model="formData[field.name]"
                  size="small"
                  :placeholder="field.label || field.name"
                  @change="updatePreviewData"
                />
              </div>
              <el-empty v-if="fields.length === 0" description="暂无字段，点击智能提取" />
            </div>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 导出对话框 -->
    <el-dialog v-model="exportDialogVisible" title="导出模板" width="450px">
      <el-form label-width="100px">
        <el-form-item label="导出格式">
          <el-radio-group v-model="exportFormat">
            <el-radio label="html">HTML（推荐，100%保留格式）</el-radio>
            <el-radio label="pdf">PDF（用浏览器打印）</el-radio>
            <el-radio label="xlsx">Excel（可能丢失格式）</el-radio>
            <el-radio label="docx">Word（可能丢失格式）</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-alert
          v-if="exportFormat === 'xlsx' || exportFormat === 'docx'"
          title="注意：Excel/Word格式可能无法100%保留原样式"
          type="warning"
          :closable="false"
          style="margin-top: 10px;"
        />
      </el-form>
      <template #footer>
        <el-button @click="exportDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="doExport" :loading="exporting">
          导出
        </el-button>
      </template>
    </el-dialog>

    <!-- 帮助对话框 -->
    <el-dialog v-model="helpDialogVisible" title="使用帮助" width="600px">
      <div class="help-content">
        <h4>功能说明</h4>
        <ul>
          <li><strong>支持格式：</strong>HTML、PDF、EXCEL、WORD</li>
          <li><strong>100%还原：</strong>上传后完全保持原模板的行高、列宽、字体、字号等样式</li>
          <li><strong>在线编辑：</strong>在网页上直接点击可编辑区域填写数据</li>
          <li><strong>数据提取：</strong>智能识别模板中的可填写字段</li>
          <li><strong>格式导出：</strong>支持导出与原模板格式一致的文件</li>
        </ul>
        <h4>操作步骤</h4>
        <ol>
          <li>上传您的模板文件</li>
          <li>系统自动解析并100%还原模板样式</li>
          <li>点击"智能提取"识别可填写字段</li>
          <li>在预览区域或右侧数据面板填写数据</li>
          <li>保存数据并导出您需要的格式</li>
        </ol>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  UploadFilled,
  QuestionFilled,
  ArrowLeft,
  Check,
  Download,
  MagicStick
} from '@element-plus/icons-vue'
import * as XLSX from 'xlsx'
import mammoth from 'mammoth'

// 状态
const templates = ref<any[]>([])
const selectedTemplate = ref<any>(null)
const fields = ref<any[]>([])
const formData = ref<any>({})
const exportDialogVisible = ref(false)
const helpDialogVisible = ref(false)
const exportFormat = ref('html')
const exporting = ref(false)
const iframeRef = ref<HTMLIFrameElement | null>(null)
const previewContainer = ref<HTMLElement | null>(null)
const previewHtml = ref('')
const previewSrc = ref('')

// 加载模板列表
const loadTemplates = async () => {
  try {
    const response = await fetch('/api/template-import-test/list')
    const result = await response.json()
    if (result.status === 'success') {
      templates.value = result.templates || []
    }
  } catch (error) {
    console.error('加载模板列表失败:', error)
  }
}

// 上传成功回调
const handleSuccess = (response: any) => {
  console.log('上传成功:', response)
}

// 上传失败回调
const handleError = (error: any) => {
  console.error('上传错误:', error)
}

// 处理文件上传
const handleFileChange = async (file: any) => {
  console.log('handleFileChange被调用, file:', file)
  
  // 检查是否有文件
  if (!file || !file.raw) {
    console.log('没有文件或文件无效')
    return
  }
  
  try {
    console.log('准备上传文件:', file.name)
    const formDataObj = new FormData()
    formDataObj.append('file', file.raw)
    
    console.log('发送请求到 /api/template-import-test/upload')
    const response = await fetch('/api/template-import-test/upload', {
      method: 'POST',
      body: formDataObj
    })
    
    console.log('响应状态码:', response.status)
    console.log('响应对象:', response)
    
    if (!response.ok) {
      throw new Error(`HTTP错误: ${response.status}`)
    }
    
    const result = await response.json()
    console.log('响应结果:', result)
    
    if (result.status === 'success') {
      ElMessage.success('上传成功！')
      await loadTemplates()
      await nextTick()
      openTemplate(result.template)
    } else {
      ElMessage.error(result.message || '上传失败')
    }
  } catch (error: any) {
    console.error('上传异常:', error)
    ElMessage.error(`上传失败: ${error.message || '未知错误'}`)
  }
}

// 打开模板
const openTemplate = async (template: any) => {
  selectedTemplate.value = template
  formData.value = {}
  fields.value = []
  
  await nextTick()
  await loadPreview()
  await loadTemplateData()
}

// 加载预览
const loadPreview = async () => {
  if (!selectedTemplate.value) return
  try {
    const fileId = selectedTemplate.value.id
    const fileType = (selectedTemplate.value.file_type || 'html').toLowerCase()
    if (fileType === 'html' || fileType === 'htm') {
      previewSrc.value = `/api/template-import-test/${fileId}/raw-file`
      previewHtml.value = ''
      return
    }
    if (fileType === 'xlsx' || fileType === 'xls') {
      const response = await fetch(`/api/template-import-test/${fileId}/raw-file`)
      const arrayBuffer = await response.arrayBuffer()
      const workbook = XLSX.read(arrayBuffer, { type: 'array', cellStyles: true })
      let allHtml = '<div style="font-family: SimSun, serif;">'
      workbook.SheetNames.forEach((sheetName: string) => {
        const worksheet = workbook.Sheets[sheetName]
        let tableHtml = '<table>'
        const range = XLSX.utils.decode_range(worksheet['!ref'] || 'A1')
        const merges = worksheet['!merges'] || []
        
        // 创建单元格二维数组
        const cells: any[][] = []
        for (let R = range.s.r; R <= range.e.r; R++) {
          cells[R] = []
          for (let C = range.s.c; C <= range.e.c; C++) {
            const cellRef = XLSX.utils.encode_cell({ r: R, c: C })
            const cell = worksheet[cellRef]
            cells[R][C] = { cell, style: '', rowspan: 1, colspan: 1, processed: false }
          }
        }
        
        // 处理合并单元格
        merges.forEach((merge: any) => {
          const startR = merge.s.r, endR = merge.e.r
          const startC = merge.s.c, endC = merge.e.c
          const rowspan = endR - startR + 1
          const colspan = endC - startC + 1
          if (cells[startR] && cells[startR][startC]) {
            cells[startR][startC].rowspan = rowspan
            cells[startR][startC].colspan = colspan
            for (let R = startR; R <= endR; R++) {
              for (let C = startC; C <= endC; C++) {
                if (R !== startR || C !== startC) {
                  if (cells[R] && cells[R][C]) cells[R][C].processed = true
                }
              }
            }
          }
        })
        
        // 生成HTML
        for (let R = range.s.r; R <= range.e.r; R++) {
          tableHtml += '<tr>'
          for (let C = range.s.c; C <= range.e.c; C++) {
            const cellData = cells[R]?.[C]
            if (!cellData || cellData.processed) { tableHtml += ''; continue }
            const cell = cellData.cell
            let style = ''
            if (cell?.s) { const s = cell.s; if (s.font) { if (s.font.sz) style += `font-size:${s.font.sz}pt;`; if (s.font.b) style += 'font-weight:bold;'; if (s.font.i) style += 'font-style:italic;'; } if (s.fill && s.fill.fgColor && s.fill.fgColor.rgb) style += `background-color:${s.fill.fgColor.rgb};`; if (s.alignment) { if (s.alignment.horizontal) style += `text-align:${s.alignment.horizontal};`; if (s.alignment.vertical) style += `vertical-align:${s.alignment.vertical};`; } }
            const value = cell?.v !== undefined ? cell.v : ''
            const rowspan = cellData.rowspan > 1 ? `rowspan="${cellData.rowspan}"` : ''
            const colspan = cellData.colspan > 1 ? `colspan="${cellData.colspan}"` : ''
            tableHtml += `<td style="${style}" ${rowspan} ${colspan}>${value}</td>`
          }
          tableHtml += '</tr>'
        }
        tableHtml += '</table>'
        allHtml += `<h3>${sheetName}</h3>${tableHtml}`
      })
      allHtml += '</div>'
      previewHtml.value = `<!DOCTYPE html><html><head><meta charset="utf-8"><style>body{font-family:SimSun,serif;margin:20px;background:#fff}table{border-collapse:collapse;width:100%;margin-bottom:20px}td,th{border:1px solid #000;padding:4px;white-space:nowrap}th{background:#f0f0f0;font-weight:bold;text-align:center}h3{color:#333;margin:20px 0 10px}</style></head><body>${allHtml}</body></html>`
      previewSrc.value = ''
      return
    }
    if (fileType === 'docx' || fileType === 'doc') {
      const response = await fetch(`/api/template-import-test/${fileId}/raw-file`)
      const arrayBuffer = await response.arrayBuffer()
      const result = await mammoth.convertToHtml({ arrayBuffer })
      previewHtml.value = `<!DOCTYPE html><html><head><meta charset="utf-8"><style>body{font-family:SimSun,serif;margin:20px;background:#fff}table{border-collapse:collapse;width:100%;margin-bottom:10px}td,th{border:1px solid #000;padding:8px}th{background:#f0f0f0}h1,h2,h3{text-align:center}</style></head><body>${result.value}</body></html>`
      previewSrc.value = ''
      return
    }
    previewHtml.value = `<div style="padding:40px;text-align:center"><p>暂不支持预览此格式</p></div>`
    previewSrc.value = ''
  } catch (error) { console.error('加载预览失败:', error); ElMessage.error('加载预览失败') }
}

// 加载模板数据
const loadTemplateData = async () => {
  if (!selectedTemplate.value) return
  
  try {
    const response = await fetch(`/api/template-import-test/${selectedTemplate.value.id}/data`)
    const result = await response.json()
    if (result.status === 'success') {
      formData.value = result.data || {}
    }
  } catch (error) {
    console.error('加载数据失败:', error)
  }
}

// iframe加载完成
const onIframeLoad = () => {
  setupEditableCells()
}

// 设置可编辑单元格
const setupEditableCells = () => {
  if (!iframeRef.value) return
  
  const iframe = iframeRef.value
  const doc = iframe.contentDocument || iframe.contentWindow?.document
  if (!doc) return
  
  const editableCells = doc.querySelectorAll('.editable-cell, [data-field]')
  editableCells.forEach((cell: any) => {
    cell.style.cursor = 'pointer'
    cell.style.minHeight = '30px'
    
    // 添加点击事件
    cell.addEventListener('click', () => {
      const fieldName = cell.dataset.field || `field_${Date.now()}`
      
      if (!formData.value[fieldName]) {
        formData.value[fieldName] = ''
        
        if (!fields.value.find(f => f.name === fieldName)) {
          fields.value.push({
            name: fieldName,
            label: cell.previousElementSibling?.textContent?.trim() || fieldName
          })
        }
      }
      
      // 创建输入框
      if (!cell.querySelector('input')) {
        const input = doc.createElement('input')
        input.type = 'text'
        input.value = formData.value[fieldName] || ''
        input.style.cssText = `
          width: 95%;
          height: 100%;
          border: none;
          background: transparent;
          font-family: inherit;
          font-size: inherit;
          text-align: inherit;
        `
        input.addEventListener('input', (e: any) => {
          formData.value[fieldName] = e.target.value
        })
        
        cell.innerHTML = ''
        cell.appendChild(input)
        input.focus()
      }
    })
  })
}

// 智能提取字段
const autoExtract = () => {
  if (!iframeRef.value) return
  
  const iframe = iframeRef.value
  const doc = iframe.contentDocument || iframe.contentWindow?.document
  if (!doc) return
  
  const extractedFields: any[] = []
  const cells = doc.querySelectorAll('td, th')
  
  cells.forEach((cell: any, index: any) => {
    const text = cell.textContent?.trim() || ''
    
    if (text && text.length < 20 && !extractedFields.find(f => f.label === text)) {
      if (text.includes('：') || text.includes(':') || 
          ['姓名', '性别', '年龄', '日期', '金额', '备注', '说明'].some(key => text.includes(key))) {
        
        const fieldName = `field_${index}`
        extractedFields.push({
          name: fieldName,
          label: text.replace(/[:：]$/, '')
        })
        
        formData.value[fieldName] = ''
      }
    }
  })
  
  fields.value = extractedFields
  
  if (fields.value.length > 0) {
    ElMessage.success(`智能提取了 ${fields.value.length} 个字段`)
  } else {
    ElMessage.info('未识别到字段，请手动点击单元格添加')
  }
}

// 更新预览数据
const updatePreviewData = () => {
  // 双向更新预览中的输入框
  if (!iframeRef.value) return
  
  const iframe = iframeRef.value
  const doc = iframe.contentDocument || iframe.contentWindow?.document
  if (!doc) return
  
  Object.entries(formData.value).forEach(([key, value]) => {
    const inputs = doc.querySelectorAll(`[data-field="${key}"] input, input[name="${key}"]`)
    inputs.forEach((input: any) => {
      if (input.value !== value) {
        input.value = value
      }
    })
  })
}

// 保存数据
const saveData = async () => {
  if (!selectedTemplate.value) return
  
  try {
    const response = await fetch(`/api/template-import-test/${selectedTemplate.value.id}/data`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ data: formData.value })
    })
    
    const result = await response.json()
    if (result.status === 'success') {
      ElMessage.success('数据保存成功！')
    } else {
      ElMessage.error(result.message || '保存失败')
    }
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

// 显示导出对话框
const showExportDialog = () => {
  exportDialogVisible.value = true
}

// 执行导出
const doExport = async () => {
  if (!selectedTemplate.value) return
  
  exporting.value = true
  try {
    const response = await fetch(
      `/api/template-import-test/${selectedTemplate.value.id}/export`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ format: exportFormat.value })
      }
    )
    
    if (!response.ok) {
      const errorText = await response.text()
      ElMessage.error('导出失败: ' + errorText)
      return
    }
    
    const contentType = response.headers.get('content-type')
    if (contentType && contentType.includes('application/json')) {
      const result = await response.json()
      ElMessage.error(result.detail || '导出失败')
    } else {
      const blob = await response.blob()
      const contentDisposition = response.headers.get('content-disposition')
      let filename = `导出文件.${exportFormat.value}`
      if (contentDisposition) {
        const match = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/)
        if (match) {
          filename = match[1].replace(/['"]/g, '')
        }
      }
      
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
      
      ElMessage.success('导出成功！')
      exportDialogVisible.value = false
    }
  } catch (error) {
    console.error('导出错误:', error)
    ElMessage.error('导出失败: ' + error.message)
  } finally {
    exporting.value = false
  }
}

// 删除模板
const deleteTemplate = async (id: string) => {
  try {
    await ElMessageBox.confirm('确定删除这个模板吗？', '提示', { type: 'warning' })
    
    const response = await fetch(`/api/template-import-test/${id}`, {
      method: 'DELETE'
    })
    
    const result = await response.json()
    if (result.status === 'success') {
      ElMessage.success('删除成功')
      await loadTemplates()
    }
  } catch {
    // 取消
  }
}

// 返回
const goBack = () => {
  selectedTemplate.value = null
  fields.value = []
  formData.value = {}
}

// 显示帮助
const showHelp = () => {
  helpDialogVisible.value = true
}

onMounted(() => {
  loadTemplates()
})
</script>

<style scoped>
.template-import-test {
  padding: 20px;
}

.main-card {
  min-height: calc(100vh - 140px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h2 {
  margin: 0;
  font-size: 20px;
}

.upload-section {
  padding: 20px 0;
}

.upload-area {
  margin-bottom: 30px;
}

.upload-area :deep(.el-upload-dragger) {
  width: 100%;
}

.recent-templates h3 {
  margin-bottom: 15px;
  font-size: 16px;
}

.edit-section {
  padding: 10px 0;
}

.edit-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  background: #f5f7fa;
  border-radius: 8px;
  margin-bottom: 20px;
}

.toolbar-center {
  display: flex;
  align-items: center;
  gap: 10px;
}

.template-name {
  font-size: 16px;
  font-weight: 600;
}

.toolbar-actions {
  display: flex;
  gap: 10px;
}

.edit-container {
  display: flex;
  gap: 20px;
  height: calc(100vh - 300px);
}

.preview-editor {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
}

.data-panel {
  width: 350px;
  display: flex;
  flex-direction: column;
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
}

.panel-header {
  padding: 15px;
  border-bottom: 1px solid #e4e7ed;
  background: #fafafa;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.panel-header h3 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
}

.html-preview-container {
  flex: 1;
  overflow: auto;
  background: #f5f7fa;
  padding: 0;
  display: flex;
  justify-content: center;
}

.preview-iframe {
  width: 100%;
  height: 100%;
  min-height: 800px;
  border: none;
  background: #fff;
  box-shadow: none;
  /* 确保100%还原样式 */
  transform: none;
  -webkit-transform: none;
  zoom: 1;
  -webkit-zoom: 1;
}

.fields-list {
  flex: 1;
  overflow: auto;
  padding: 15px;
}

.field-item {
  margin-bottom: 15px;
}

.field-label {
  font-size: 12px;
  color: #606266;
  margin-bottom: 5px;
}

.help-content {
  line-height: 1.8;
}

.help-content h4 {
  margin: 15px 0 10px;
  font-size: 14px;
}

.help-content ul, .help-content ol {
  padding-left: 20px;
}

.help-content li {
  margin-bottom: 8px;
}
</style>
