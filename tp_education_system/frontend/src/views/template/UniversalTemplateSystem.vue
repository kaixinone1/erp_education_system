<template>
  <div class="universal-template-system">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>通用模板自动填报系统</span>
          <div>
            <el-button type="primary" @click="showImportDialog">
              <el-icon><Upload /></el-icon>
              导入新模板
            </el-button>
          </div>
        </div>
      </template>

      <el-table :data="templates" border stripe>
        <el-table-column prop="模板ID" label="模板ID" width="150" />
        <el-table-column prop="模板名称" label="模板名称" width="200" />
        <el-table-column prop="模板类型" label="模板类型" width="120" />
        <el-table-column prop="原始文件" label="原始文件" width="200" />
        <el-table-column prop="创建时间" label="创建时间" width="180" />
        <el-table-column label="操作" width="400" fixed="right">
          <template #default="scope">
            <el-button size="small" @click="previewTemplate(scope.row)">预览</el-button>
            <el-button size="small" type="primary" @click="showFieldMappingDialog(scope.row)">配置映射</el-button>
            <el-button size="small" type="success" @click="showFillDialog(scope.row)">填报</el-button>
            <el-button size="small" type="warning" @click="exportTemplate(scope.row)">导出</el-button>
            <el-button size="small" type="danger" @click="deleteTemplate(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="importDialogVisible" title="导入新模板" width="600px">
      <el-form :model="importForm" label-width="100px">
        <el-form-item label="模板名称">
          <el-input v-model="importForm.模板名称" placeholder="请输入模板名称" />
        </el-form-item>
        <el-form-item label="模板类型">
          <el-select v-model="importForm.模板类型" placeholder="请选择模板类型">
            <el-option label="呈报表" value="呈报表" />
            <el-option label="审批表" value="审批表" />
            <el-option label="公文" value="公文" />
            <el-option label="统计表" value="统计表" />
          </el-select>
        </el-form-item>
        <el-form-item label="Excel文件">
          <el-upload
            ref="uploadRef"
            :auto-upload="false"
            :limit="1"
            accept=".xlsx,.xls"
            :on-change="handleFileChange"
            :file-list="uploadFileList"
          >
            <el-button type="primary">选择文件</el-button>
            <template #tip>
              <div class="el-upload__tip">只能上传xlsx/xls文件</div>
            </template>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="importDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="importTemplate">导入</el-button>
      </template>
    </el-dialog>

    <el-dialog 
      v-model="previewDialogVisible" 
      :title="previewTitle" 
      width="95%"
      top="2vh"
      :close-on-click-modal="false"
      destroy-on-close
    >
      <div id="luckysheet-preview" style="width: 100%; height: 75vh; margin: 0; padding: 0;"></div>
      <template #footer>
        <el-button @click="closePreviewDialog" type="primary">关闭</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="fieldMappingDialogVisible" title="字段映射配置" width="90%" top="5vh">
      <el-row :gutter="20">
        <el-col :span="16">
          <div class="mapping-preview">
            <h4>模板预览（点击单元格配置映射）</h4>
            <div id="mapping-template-preview" class="preview-container" @click="handleCellClick"></div>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="mapping-config">
            <h4>当前配置</h4>
            <el-form :model="fieldMappingForm" label-width="100px">
              <el-form-item label="字段名称">
                <el-input v-model="fieldMappingForm.字段名称" placeholder="如：姓名" />
              </el-form-item>
              <el-form-item label="行号">
                <el-input-number v-model="fieldMappingForm.行号" :min="1" />
              </el-form-item>
              <el-form-item label="列号">
                <el-input-number v-model="fieldMappingForm.列号" :min="1" />
              </el-form-item>
              <el-form-item label="数据源表">
                <el-select v-model="fieldMappingForm.数据源表" placeholder="选择表">
                  <el-option label="teacher_basic_info" value="teacher_basic_info" />
                  <el-option label="teacher_personal_identity" value="teacher_personal_identity" />
                  <el-option label="post_appointment_info" value="post_appointment_info" />
                </el-select>
              </el-form-item>
              <el-form-item label="数据源字段">
                <el-input v-model="fieldMappingForm.数据源字段" placeholder="如：name" />
              </el-form-item>
              <el-button type="primary" @click="saveFieldMapping">保存映射</el-button>
            </el-form>

            <el-divider />

            <h4>已配置的字段映射</h4>
            <el-table :data="fieldMappingsList" border size="small">
              <el-table-column prop="字段名称" label="字段名称" width="100" />
              <el-table-column prop="行号" label="行" width="60" />
              <el-table-column prop="列号" label="列" width="60" />
              <el-table-column prop="数据源" label="数据源" />
            </el-table>
          </div>
        </el-col>
      </el-row>
    </el-dialog>

    <el-dialog v-model="fillDialogVisible" title="自动填报" width="90%" top="5vh">
      <el-form :model="fillForm" label-width="100px">
        <el-form-item label="查询条件">
          <el-input v-model="fillForm.职工ID" placeholder="输入职工ID或身份证号" style="width: 300px" />
        </el-form-item>
        <el-button type="primary" @click="fillTemplate">开始填报</el-button>
      </el-form>

      <el-divider />

      <div id="filled-template-preview" class="preview-container"></div>

      <template #footer>
        <el-button @click="fillDialogVisible = false">取消</el-button>
        <el-button type="success" @click="exportFilledTemplate">导出Excel</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Upload } from '@element-plus/icons-vue'
import axios from 'axios'

const API_BASE = '/api/universal-template'

const templates = ref([])
const importDialogVisible = ref(false)
const previewDialogVisible = ref(false)
const fieldMappingDialogVisible = ref(false)
const fillDialogVisible = ref(false)
const previewTitle = ref('')

const importForm = ref({
  模板名称: '',
  模板类型: '',
  file: null
})

const fieldMappingForm = ref({
  模板ID: '',
  字段名称: '',
  行号: 1,
  列号: 1,
  数据源表: '',
  数据源字段: ''
})

const fieldMappingsList = ref([])

const fillForm = ref({
  模板ID: '',
  职工ID: ''
})

const currentTemplateId = ref('')
const uploadRef = ref(null)
const uploadFileList = ref([])

onMounted(() => {
  loadTemplates()
})

async function loadTemplates() {
  try {
    const response = await axios.get(`${API_BASE}/list`)
    if (response.data.成功) {
      templates.value = response.data.数据
    }
  } catch (error) {
    ElMessage.error('加载模板列表失败: ' + error.message)
  }
}

function showImportDialog() {
  importForm.value = {
    模板名称: '',
    模板类型: '',
    file: null
  }
  uploadFileList.value = []
  importDialogVisible.value = true
}

function handleFileChange(file) {
  importForm.value.file = file.raw
  
  if (!importForm.value.模板名称 && file.name) {
    const fileName = file.name.replace(/\.(xlsx|xls)$/i, '')
    importForm.value.模板名称 = fileName
  }
}

async function importTemplate() {
  if (!importForm.value.模板名称) {
    ElMessage.warning('请输入模板名称')
    return
  }
  if (!importForm.value.模板类型) {
    ElMessage.warning('请选择模板类型')
    return
  }
  if (!importForm.value.file) {
    ElMessage.warning('请选择Excel文件')
    return
  }

  let originalFileName = ''
  let saveFileName = ''

  try {
    originalFileName = importForm.value.file.name

    const checkResponse = await axios.get(`${API_BASE}/check-filename/${encodeURIComponent(originalFileName)}`)
    
    saveFileName = originalFileName

    if (checkResponse.data.成功 && checkResponse.data.磁盘存在) {
      const referencedTemplates = checkResponse.data.被引用模板 || []

      if (referencedTemplates.length > 0) {
        const templateNames = referencedTemplates.map(t => `"${t.模板名称}"`).join('、')
        await ElMessageBox.confirm(
          `文件"${originalFileName}"已被以下模板使用：${templateNames}。覆盖将导致上述模板无法正常使用！建议重命名。`,
          '文件重名警告',
          {
            confirmButtonText: '强制覆盖',
            cancelButtonText: '重命名',
            type: 'warning',
            distinguishCancelAndClose: true
          }
        )
      } else {
        try {
          await ElMessageBox.confirm(
            `文件"${originalFileName}"已存在但未被任何模板引用，是否覆盖？`,
            '文件重名提示',
            {
              confirmButtonText: '覆盖',
              cancelButtonText: '重命名',
              type: 'info',
              distinguishCancelAndClose: true
            }
          )
        } catch (cancelErr) {
          if (cancelErr === 'cancel' || cancelErr === 'close') {
            const timestamp = new Date().toISOString().replace(/[-:T]/g, '').slice(0, 14)
            const ext = originalFileName.substring(originalFileName.lastIndexOf('.'))
            const baseName = originalFileName.substring(0, originalFileName.lastIndexOf('.'))
            saveFileName = `${baseName}_${timestamp}${ext}`
          }
        }
      }
    }

    const formData = new FormData()
    formData.append('file', importForm.value.file)
    formData.append('模板名称', importForm.value.模板名称)
    formData.append('模板类型', importForm.value.模板类型)
    formData.append('保存文件名', saveFileName)

    const response = await axios.post(`${API_BASE}/import`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })

    if (response.data.成功) {
      ElMessage.success('模板导入成功')
      importDialogVisible.value = false
      loadTemplates()
    } else {
      ElMessage.error('导入失败: ' + response.data.消息)
    }
  } catch (error) {
    if (error === 'cancel' || error === 'close') {
      const timestamp = new Date().toISOString().replace(/[-:T]/g, '').slice(0, 14)
      const ext = originalFileName.substring(originalFileName.lastIndexOf('.'))
      const baseName = originalFileName.substring(0, originalFileName.lastIndexOf('.'))
      saveFileName = `${baseName}_${timestamp}${ext}`

      const formData = new FormData()
      formData.append('file', importForm.value.file)
      formData.append('模板名称', importForm.value.模板名称)
      formData.append('模板类型', importForm.value.模板类型)
      formData.append('保存文件名', saveFileName)

      try {
        const response = await axios.post(`${API_BASE}/import`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        })
        if (response.data.成功) {
          ElMessage.success('模板导入成功（已自动重命名文件）')
          importDialogVisible.value = false
          loadTemplates()
        } else {
          ElMessage.error('导入失败: ' + response.data.消息)
        }
        return
      } catch (retryErr) {
        ElMessage.error('导入失败: ' + retryErr.message)
        return
      }
    }
    ElMessage.error('导入失败: ' + error.message)
  }
}

function renderTemplateHTML(containerId, htmlContent) {
  const container = document.getElementById(containerId)
  if (container) {
    container.innerHTML = htmlContent
  }
}

function clearPreviewContainer(containerId) {
  const container = document.getElementById(containerId)
  if (container) {
    container.innerHTML = ''
  }
}

async function previewTemplate(row) {
  try {
    previewTitle.value = `${row.模板名称} - 预览`
    previewDialogVisible.value = true
    currentTemplateId.value = row.模板ID

    await nextTick()

    const response = await axios.get(`${API_BASE}/preview/${row.模板ID}`)
    const htmlContent = response.data.数据?.HTML || ''

    renderTemplateHTML('luckysheet-preview', htmlContent)
    ElMessage.success('预览加载成功')
  } catch (error) {
    console.error('预览错误:', error)
    ElMessage.error('预览失败: ' + error.message)
  }
}

function renderTemplateWithMetadata(metadata) {
  const { cells, styles, dimensions, merged_cells, page_setup, page_margins } = metadata
  
  const maxRow = dimensions.max_row || 20
  const maxCol = dimensions.max_column || 10
  
  const mergedMap = new Map()
  merged_cells.forEach(mc => {
    for (let r = mc.r; r < mc.r + mc.rs; r++) {
      for (let c = mc.c; c < mc.c + mc.cs; c++) {
        if (r === mc.r && c === mc.c) {
          mergedMap.set(`${r}-${c}`, { rs: mc.rs, cs: mc.cs, isMaster: true })
        } else {
          mergedMap.set(`${r}-${c}`, { isMaster: false })
        }
      }
    }
  })
  
  const cellData = new Map()
  cells.forEach(cell => {
    cellData.set(`${cell.r}-${cell.c}`, cell.v)
  })
  
  const styleMap = new Map()
  Object.keys(styles).forEach(key => {
    const match = key.match(/^([A-Z]+)(\d+)$/)
    if (match) {
      const col = match[1].charCodeAt(0) - 'A'.charCodeAt(0)
      const row = parseInt(match[2]) - 1
      styleMap.set(`${row}-${col}`, styles[key])
    }
  })
  
  let html = `<style>
    .template-preview { 
      overflow: auto; 
      max-height: 600px; 
      margin: 10px;
    }
    .template-table { 
      border-collapse: collapse; 
      border: 1px solid #000;
      min-width: 100%;
    }
    .template-cell { 
      border: 1px solid #000; 
      padding: 2px; 
      min-height: 20px;
      position: relative;
    }
  </style>
  <div class="template-preview">
    <table class="template-table">`
  
  for (let r = 0; r < maxRow; r++) {
    const rowHeight = dimensions.rows?.[r + 1] || 20
    html += `<tr style="height: ${rowHeight}px;">`
    
    for (let c = 0; c < maxCol; c++) {
      const key = `${r}-${c}`
      const mergedInfo = mergedMap.get(key)
      const cellValue = cellData.get(key)
      const style = styleMap.get(key)
      const colWidth = dimensions.columns?.[String.fromCharCode('A'.charCodeAt(0) + c)] || 80
      
      if (mergedInfo && !mergedInfo.isMaster) continue
      
      let cellStyle = `width: ${colWidth}px;`
      
      if (style) {
        if (style.font) {
          if (style.font.name) cellStyle += ` font-family: ${style.font.name};`
          if (style.font.size) cellStyle += ` font-size: ${style.font.size}pt;`
          if (style.font.bold) cellStyle += ` font-weight: bold;`
          if (style.font.italic) cellStyle += ` font-style: italic;`
          if (style.font.color) cellStyle += ` color: #${style.font.color};`
          if (style.font.strike) cellStyle += ` text-decoration: line-through;`
        }
        
        if (style.fill) {
          if (style.fill.fgColor) cellStyle += ` background-color: #${style.fill.fgColor};`
        }
        
        if (style.alignment) {
          if (style.alignment.horizontal) cellStyle += ` text-align: ${style.alignment.horizontal};`
          if (style.alignment.vertical) cellStyle += ` vertical-align: ${style.alignment.vertical};`
          if (style.alignment.wrapText) cellStyle += ` white-space: pre-wrap; word-wrap: break-word;`
        }
        
        if (style.border) {
          if (style.border.top) cellStyle += ` border-top: ${getBorderStyle(style.border.top)};`
          if (style.border.bottom) cellStyle += ` border-bottom: ${getBorderStyle(style.border.bottom)};`
          if (style.border.left) cellStyle += ` border-left: ${getBorderStyle(style.border.left)};`
          if (style.border.right) cellStyle += ` border-right: ${getBorderStyle(style.border.right)};`
        }
      }
      
      const rowspan = mergedInfo?.rs || 1
      const colspan = mergedInfo?.cs || 1
      const value = cellValue?.m || cellValue?.v || ''
      
      html += `<td class="template-cell" style="${cellStyle}" rowspan="${rowspan}" colspan="${colspan}">${escapeHtml(value)}</td>`
    }
    html += '</tr>'
  }
  
  html += '</table></div>'
  return html
}

function getBorderStyle(border) {
  const styleMap = {
    'thin': '1px solid',
    'medium': '2px solid',
    'thick': '3px solid',
    'dashed': '1px dashed',
    'dotted': '1px dotted',
    'double': '3px double'
  }
  const style = styleMap[border.style] || '1px solid'
  const color = border.color ? `#${border.color}` : '#000000'
  return `${style} ${color}`
}

function escapeHtml(text) {
  if (!text) return ''
  const map = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;'
  }
  return text.toString().replace(/[&<>"']/g, m => map[m])
}

function closePreviewDialog() {
  clearPreviewContainer('luckysheet-preview')
  previewDialogVisible.value = false
}

async function showFieldMappingDialog(row) {
  currentTemplateId.value = row.模板ID
  fieldMappingForm.value.模板ID = row.模板ID
  fieldMappingDialogVisible.value = true

  try {
    const response = await axios.get(`${API_BASE}/preview/${row.模板ID}`)
    if (response.data.成功) {
      await nextTick()
      const previewDiv = document.getElementById('mapping-template-preview')
      if (previewDiv) {
        previewDiv.innerHTML = response.data.数据.HTML
      }
    }

    const mappingsResponse = await axios.get(`${API_BASE}/field-mappings/${row.模板ID}`)
    if (mappingsResponse.data.成功) {
      const mappings = mappingsResponse.data.数据
      fieldMappingsList.value = Object.keys(mappings).map(key => ({
        字段名称: key,
        行号: mappings[key].行,
        列号: mappings[key].列,
        数据源: mappings[key].数据源
      }))
    }
  } catch (error) {
    ElMessage.error('加载失败: ' + error.message)
  }
}

function handleCellClick(event) {
  const cell = event.target.closest('td')
  if (!cell) return

  const row = cell.parentElement
  const table = row.parentElement
  const rowIndex = Array.from(table.children).indexOf(row) + 1
  const colIndex = Array.from(row.children).indexOf(cell) + 1

  fieldMappingForm.value.行号 = rowIndex
  fieldMappingForm.value.列号 = colIndex

  ElMessage.info(`已选中第${rowIndex}行第${colIndex}列`)
}

async function saveFieldMapping() {
  if (!fieldMappingForm.value.字段名称) {
    ElMessage.warning('请输入字段名称')
    return
  }
  if (!fieldMappingForm.value.数据源表 || !fieldMappingForm.value.数据源字段) {
    ElMessage.warning('请配置数据源')
    return
  }

  try {
    const response = await axios.post(`${API_BASE}/field-mapping`, {
      模板ID: fieldMappingForm.value.模板ID,
      字段名称: fieldMappingForm.value.字段名称,
      行号: fieldMappingForm.value.行号,
      列号: fieldMappingForm.value.列号,
      数据源: `${fieldMappingForm.value.数据源表}.${fieldMappingForm.value.数据源字段}`
    })

    if (response.data.成功) {
      ElMessage.success('字段映射保存成功')

      const mappingsResponse = await axios.get(`${API_BASE}/field-mappings/${fieldMappingForm.value.模板ID}`)
      if (mappingsResponse.data.成功) {
        const mappings = mappingsResponse.data.数据
        fieldMappingsList.value = Object.keys(mappings).map(key => ({
          字段名称: key,
          行号: mappings[key].行,
          列号: mappings[key].列,
          数据源: mappings[key].数据源
        }))
      }
    }
  } catch (error) {
    ElMessage.error('保存失败: ' + error.message)
  }
}

function showFillDialog(row) {
  currentTemplateId.value = row.模板ID
  fillForm.value.模板ID = row.模板ID
  fillForm.value.职工ID = ''
  fillDialogVisible.value = true
}

async function fillTemplate() {
  if (!fillForm.value.职工ID) {
    ElMessage.warning('请输入职工ID')
    return
  }

  try {
    const response = await axios.post(`${API_BASE}/fill`, {
      模板ID: fillForm.value.模板ID,
      查询条件: {
        职工ID: fillForm.value.职工ID
      }
    })

    if (response.data.成功) {
      await nextTick()
      clearPreviewContainer('filled-template-preview')

      const htmlContent = response.data.数据.HTML || ''
      renderTemplateHTML('filled-template-preview', htmlContent)
      ElMessage.success('数据填报成功')
    }
  } catch (error) {
    ElMessage.error('填报失败: ' + error.message)
  }
}

async function exportTemplate(row) {
  try {
    const response = await axios.get(`${API_BASE}/export-preview/${row.模板ID}`, {
      responseType: 'blob'
    })

    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `${row.模板名称}_预览.xlsx`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)

    ElMessage.success('导出成功')
  } catch (error) {
    ElMessage.error('导出失败: ' + error.message)
  }
}

async function exportFilledTemplate() {
  try {
    const response = await axios.post(`${API_BASE}/export`, {
      模板ID: fillForm.value.模板ID,
      查询条件: {
        职工ID: fillForm.value.职工ID
      }
    }, {
      responseType: 'blob'
    })

    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `填报结果.xlsx`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)

    ElMessage.success('导出成功')
  } catch (error) {
    ElMessage.error('导出失败: ' + error.message)
  }
}

async function deleteTemplate(row) {
  try {
    await ElMessageBox.confirm('确定要删除该模板吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    const response = await axios.delete(`${API_BASE}/${row.模板ID}`)
    if (response.data.成功) {
      ElMessage.success('删除成功')
      loadTemplates()
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败: ' + error.message)
    }
  }
}
</script>

<style scoped>
.universal-template-system {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.preview-container {
  width: 100%;
  overflow: auto;
  border: 1px solid #dcdfe6;
  padding: 20px;
  background: #fff;
  max-height: 70vh;
}

.mapping-preview {
  border: 1px solid #dcdfe6;
  padding: 15px;
  border-radius: 4px;
}

.mapping-config {
  border: 1px solid #dcdfe6;
  padding: 15px;
  border-radius: 4px;
}

.mapping-config h4 {
  margin-bottom: 15px;
  color: #303133;
}
</style>

