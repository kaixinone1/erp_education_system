<template>
  <div class="template-manager">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>模板管理中心</span>
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
        <el-table-column prop="模板分类" label="模板分类" width="100" />
        <el-table-column prop="模板类型" label="模板类型" width="120" />
        <el-table-column prop="原始文件" label="原始文件" width="200" />
        <el-table-column prop="创建时间" label="创建时间" width="180" />
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="scope">
            <el-button size="small" @click="previewTemplate(scope.row)">预览</el-button>
            <el-button size="small" type="primary" @click="showFieldMappingDialog(scope.row)">配置映射</el-button>
            <el-button size="small" type="danger" @click="deleteTemplate(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="importDialogVisible" title="导入新模板" width="650px">
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
        <el-form-item label="模板分类">
          <el-radio-group v-model="importForm.模板分类">
            <el-radio value="单位汇总表">单位汇总表（统计类）</el-radio>
            <el-radio value="个人表">个人表（明细类）</el-radio>
          </el-radio-group>
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
              <el-form-item label="数据来源">
                <el-radio-group v-model="fieldMappingForm.数据来源类型" @change="onSourceTypeChange">
                  <el-radio value="数据库字段">数据库字段</el-radio>
                  <el-radio value="公式计算">公式计算</el-radio>
                </el-radio-group>
              </el-form-item>
              <template v-if="fieldMappingForm.数据来源类型 === '数据库字段'">
                <el-form-item label="数据源表">
                  <el-select ref="tableSelectRef" v-model="fieldMappingForm.数据源表" placeholder="请选择数据来源表" filterable @change="onTableChange">
                    <el-option 
                      v-for="table in availableTables" 
                      :key="table.英文表名" 
                      :label="table.显示名称" 
                      :value="table.英文表名" 
                    />
                  </el-select>
                </el-form-item>
                <el-form-item label="数据源字段">
                  <el-select ref="fieldSelectRef" v-model="fieldMappingForm.数据源字段" placeholder="请先选择数据源表" filterable :disabled="!fieldMappingForm.数据源表" @change="onFieldChange">
                    <el-option 
                      v-for="field in availableFields" 
                      :key="field.字段名" 
                      :label="field.显示名称" 
                      :value="field.字段名" 
                    />
                  </el-select>
                </el-form-item>
                <el-form-item v-if="currentFieldDictValues.length > 0" label="可选值筛选">
                  <el-select 
                    :key="(fieldMappingForm.数据源表 || '') + '|' + (fieldMappingForm.数据源字段 || '')"
                    ref="dictSelectRef"
                    v-model="fieldMappingForm.字典值选择" 
                    multiple 
                    filterable 
                    collapse-tags
                    collapse-tags-tooltip
                    placeholder="请选择要统计的值（可多选，留空=全选）" 
                    style="width: 100%"
                    @change="nextTick(() => { if (dictSelectRef) dictSelectRef.query = '' })"
                  >
                    <el-option 
                      v-for="val in currentFieldDictValues" 
                      :key="typeof val === 'object' ? val.值 : val" 
                      :label="typeof val === 'object' ? val.标签 : val" 
                      :value="typeof val === 'object' ? val.值 : val" 
                    />
                  </el-select>
                  <div style="color:#909399;font-size:12px;margin-top:4px;">共 {{ currentFieldDictValues.length }} 个可选值，可多选筛选</div>
                </el-form-item>
                <el-form-item label="统计方法">
                  <el-select v-model="fieldMappingForm.统计方法" placeholder="请选择统计方法">
                    <el-option label="计数" value="计数" />
                    <el-option label="求和" value="求和" />
                    <el-option label="平均值" value="平均值" />
                    <el-option label="最大值" value="最大值" />
                    <el-option label="最小值" value="最小值" />
                    <el-option label="求积" value="求积" />
                    <el-option label="取值" value="取值" />
                  </el-select>
                </el-form-item>
              </template>
              <template v-if="fieldMappingForm.数据来源类型 === '公式计算'">
                <el-form-item label="公式表达式">
                  <el-input 
                    v-model="fieldMappingForm.公式表达式" 
                    type="textarea"
                    :rows="2"
                    placeholder="如：{绩效工资标准} * {绩效工资系数}"
                  />
                </el-form-item>
                <div style="color:#909399;font-size:12px;margin:0 0 12px 0;padding-left:100px;line-height:1.6;">
                  用法说明：用 <code>{`{字段名称}`}</code> 引用此模板中已配置映射的字段名。<br/>
                  支持：<code>+</code> <code>-</code> <code>*</code> <code>/</code> <code>%</code> <code>^</code> 和 <code>()</code><br/>
                  支持函数：<code>SUM(a,b,c)</code> <code>AVG(a,b,c)</code> <code>MAX(a,b,c)</code> <code>MIN(a,b,c)</code>
                  <code>IF(条件, 真值, 假值)</code> <code>ROUND(x, n)</code> <code>ABS(x)</code>
                </div>
              </template>
              <el-button type="primary" @click="saveFieldMapping">保存映射</el-button>
            </el-form>

            <el-divider />

            <h4>已配置的字段映射</h4>
            <div style="max-height: 300px; overflow-y: auto;">
              <el-table :data="fieldMappingsList" border size="small">
                <el-table-column prop="字段名称" label="字段名称" width="100" />
                <el-table-column prop="行号" label="行" width="60" />
                <el-table-column prop="列号" label="列" width="60" />
                <el-table-column label="数据源">
                  <template #default="scope">
                    {{ scope.row.数据源_中文 || scope.row.数据源 }}
                  </template>
                </el-table-column>
                <el-table-column prop="统计方法" label="统计方法" width="80" />
                <el-table-column label="操作" width="60" fixed="right">
                  <template #default="scope">
                    <el-button type="danger" size="small" link @click="deleteFieldMapping(scope.row)">删除</el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </div>
        </el-col>
      </el-row>
    </el-dialog>

    <el-dialog v-model="historyDialogVisible" title="历史文件查询" width="700px" top="5vh">
      <el-form :inline="true">
        <el-form-item label="日期范围">
          <el-date-picker
            v-model="historyDateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="起始日期"
            end-placeholder="截止日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="queryHistory">查询</el-button>
        </el-form-item>
      </el-form>
      <el-table :data="historyRecords" style="width: 100%" max-height="400">
        <el-table-column prop="保存时间" label="保存时间" width="160" />
        <el-table-column prop="年月" label="年月" width="100" />
        <el-table-column label="操作" width="280">
          <template #default="scope">
            <el-button size="small" type="primary" @click="downloadHistoryFile(scope.row, 'Excel')">Excel下载</el-button>
            <el-button
              size="small"
              type="success"
              @click="downloadHistoryFile(scope.row, 'Word')"
              :disabled="!scope.row.Word路径"
            >
              Word下载
            </el-button>
            <el-button
              size="small"
              type="warning"
              @click="downloadHistoryFile(scope.row, 'PDF')"
              :disabled="!scope.row.PDF路径"
            >
              PDF下载
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button @click="historyDialogVisible = false">关闭</el-button>
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
const previewTitle = ref('')
const currentTemplateId = ref('')
const historyDialogVisible = ref(false)
const historyDateRange = ref([])
const historyRecords = ref([])
const historyTemplateId = ref('')

const importForm = ref({
  模板名称: '',
  模板类型: '',
  模板分类: '单位汇总表',
  file: null
})

const fieldMappingForm = ref({
  模板ID: '',
  字段名称: '',
  行号: 1,
  列号: 1,
  数据来源类型: '数据库字段',
  数据源表: '',
  数据源字段: '',
  字典值选择: [],
  统计方法: '求和',
  公式表达式: ''
})

const fieldMappingsList = ref([])
const currentFieldDictValues = ref([])
const availableTables = ref([])
const availableFields = ref([])
const tableSelectRef = ref(null)
const fieldSelectRef = ref(null)
const dictSelectRef = ref(null)

const uploadRef = ref(null)
const uploadFileList = ref([])

onMounted(() => {
  loadTemplates()
})

async function loadTemplates() {
  try {
    const resp = await fetch(`${API_BASE}/list`)
    const data = await resp.json()
    if (data.成功) {
      templates.value = data.数据
    }
  } catch (error) {
    ElMessage.error('加载模板列表失败: ' + error.message)
  }
}

function showImportDialog() {
  importForm.value = {
    模板名称: '',
    模板类型: '',
    模板分类: '单位汇总表',
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
  if (!importForm.value.模板分类) {
    ElMessage.warning('请选择模板分类')
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
    formData.append('模板分类', importForm.value.模板分类)
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
      formData.append('模板分类', importForm.value.模板分类)
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
    const templateType = response.data.数据?.模板类型 || ''

    if (templateType === 'word') {
      const container = document.getElementById('luckysheet-preview')
      if (container) {
        container.innerHTML = '<div style="text-align:center;padding:60px 20px;color:#909399;"><p style="font-size:16px;margin-bottom:10px;">Word模板不支持在线预览</p><p style="font-size:14px;">请使用填报功能生成Word和PDF文件</p></div>'
      }
      ElMessage.info('Word模板不支持在线预览')
      return
    }

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

async function loadAvailableTables() {
  try {
    const resp = await fetch(`${API_BASE}/available-tables`)
    const data = await resp.json()
    if (data.成功) {
      availableTables.value = data.数据
    }
  } catch (error) {
    console.error('加载数据表列表失败:', error)
  }
}

async function onTableChange(tableName) {
  availableFields.value = []
  fieldMappingForm.value.数据源字段 = ''
  fieldMappingForm.value.字典值选择 = []
  currentFieldDictValues.value = []
  if (!tableName) {
    return
  }
  try {
    const resp = await fetch(`${API_BASE}/table-columns/${encodeURIComponent(tableName)}`)
    const data = await resp.json()
    availableFields.value = data.成功 ? (data.数据 || []) : []
  } catch (error) {
    availableFields.value = []
    console.error('加载表字段失败:', error)
    ElMessage.error('加载表字段失败: ' + error.message)
  }
  nextTick(() => { if (tableSelectRef.value) tableSelectRef.value.query = '' })
}

async function onFieldChange(fieldName) {
  fieldMappingForm.value.字典值选择 = []
  currentFieldDictValues.value = []
  if (!fieldName) return
  const tableName = fieldMappingForm.value.数据源表
  const field = availableFields.value.find(f => f.字段名 === fieldName)
  if (field && field.字典可选值 && field.字典可选值.length > 0) {
    currentFieldDictValues.value = field.字典可选值
  } else if (field && tableName) {
    try {
      const url = `${API_BASE}/table-distinct-values/${encodeURIComponent(tableName)}/${encodeURIComponent(fieldName)}`
      const resp = await fetch(url)
      const data = await resp.json()
      if (data.成功 && data.数据 && data.数据.length > 0) {
        field.字典可选值 = data.数据
        currentFieldDictValues.value = data.数据
      } else if (data.成功 && data.数据 && data.数据.length === 0) {
        currentFieldDictValues.value = []
      }
    } catch (e) {
      console.error(`[可选值] ${tableName}.${fieldName} 请求失败:`, e)
    }
  }
  nextTick(() => {
    if (fieldSelectRef.value) fieldSelectRef.value.query = ''
    if (dictSelectRef.value) dictSelectRef.value.query = ''
  })
}

async function showFieldMappingDialog(row) {
  if (!row || !row.模板ID) {
    ElMessage.warning('模板数据异常，请刷新页面重试')
    return
  }

  const templateId = row.模板ID
  currentTemplateId.value = templateId
  fieldMappingForm.value.模板ID = templateId
  fieldMappingForm.value.数据来源类型 = '数据库字段'
  fieldMappingForm.value.数据源表 = ''
  fieldMappingForm.value.数据源字段 = ''
  fieldMappingForm.value.字典值选择 = []
  fieldMappingForm.value.统计方法 = '求和'
  fieldMappingForm.value.公式表达式 = ''
  currentFieldDictValues.value = []
  availableFields.value = []
  fieldMappingDialogVisible.value = true

  loadAvailableTables()

  try {
    const resp = await fetch(`${API_BASE}/preview/${templateId}`)
    const data = await resp.json()
    if (data.成功) {
      await nextTick()
      const previewDiv = document.getElementById('mapping-template-preview')
      if (previewDiv) {
        previewDiv.innerHTML = data.数据.HTML
      }
    }

    const mResp = await fetch(`${API_BASE}/field-mappings/${templateId}`)
    const mData = await mResp.json()
    if (mData.成功) {
      const mappings = mData.数据
      fieldMappingsList.value = Object.keys(mappings).map(key => {
        const m = mappings[key]
        const isFormula = m.转换函数 && !['计数','求和','平均值','最大值','最小值','求积','取值'].includes(m.转换函数)
        return {
          字段名称: key,
          行号: m.行,
          列号: m.列,
          数据源: isFormula ? `公式: ${m.转换函数}` : (m.数据源 || ''),
          数据源_中文: isFormula ? `公式: ${m.转换函数}` : (m.数据源_中文 || ''),
          统计方法: isFormula ? '公式' : (m.转换函数 || '')
        }
      })
    }
  } catch (error) {
    ElMessage.error('加载失败: ' + error.message)
  }
}

function handleCellClick(event) {
  const cell = event.target.closest('td')
  if (!cell) return

  const rowIndex = parseInt(cell.getAttribute('data-row') || '0')
  const colIndex = parseInt(cell.getAttribute('data-col') || '0')

  if (!rowIndex || !colIndex) {
    const row = cell.parentElement
    const table = row.parentElement
    const domRow = Array.from(table.children).indexOf(row) + 1
    const domCol = Array.from(row.children).indexOf(cell) + 1
    ElMessage.warning(`无法获取单元格坐标，使用DOM位置：第${domRow}行第${domCol}列`)
    fieldMappingForm.value.行号 = domRow
    fieldMappingForm.value.列号 = domCol
    return
  }

  fieldMappingForm.value.行号 = rowIndex
  fieldMappingForm.value.列号 = colIndex

  ElMessage.info(`已选中第${rowIndex}行第${colIndex}列`)
}

async function saveFieldMapping() {
  if (!fieldMappingForm.value.字段名称) {
    ElMessage.warning('请输入字段名称')
    return
  }

  const duplicate = fieldMappingsList.value.find(
    m => m.字段名称 === fieldMappingForm.value.字段名称
  )
  if (duplicate) {
    try {
      await ElMessageBox.confirm(
        `字段名称"${fieldMappingForm.value.字段名称}"已存在（行${duplicate.行号}列${duplicate.列号}），是否覆盖？`,
        '名称重复',
        { confirmButtonText: '覆盖', cancelButtonText: '取消', type: 'warning' }
      )
    } catch {
      return
    }
  }

  const isDbField = fieldMappingForm.value.数据来源类型 === '数据库字段'

  if (isDbField && (!fieldMappingForm.value.数据源表 || !fieldMappingForm.value.数据源字段)) {
    ElMessage.warning('请配置数据源')
    return
  }

  if (!isDbField && !fieldMappingForm.value.公式表达式) {
    ElMessage.warning('请输入公式表达式')
    return
  }

  try {
    const requestBody = {
      模板ID: fieldMappingForm.value.模板ID,
      字段名称: fieldMappingForm.value.字段名称,
      行号: fieldMappingForm.value.行号,
      列号: fieldMappingForm.value.列号,
      数据源: isDbField
        ? `${fieldMappingForm.value.数据源表}.${fieldMappingForm.value.数据源字段}`
        : '',
      转换函数: isDbField
        ? fieldMappingForm.value.统计方法
        : fieldMappingForm.value.公式表达式,
      字典值选择: fieldMappingForm.value.字典值选择 || []
    }
    const response = await axios.post(`${API_BASE}/field-mapping`, requestBody)

    if (response.data.成功) {
      ElMessage.success('字段映射保存成功')

      const mappingsResponse = await axios.get(`${API_BASE}/field-mappings/${fieldMappingForm.value.模板ID}`)
      if (mappingsResponse.data.成功) {
        const mappings = mappingsResponse.data.数据
        fieldMappingsList.value = Object.keys(mappings).map(key => {
          const m = mappings[key]
          const isFormula = m.转换函数 && !['计数','求和','平均值','最大值','最小值','求积','取值'].includes(m.转换函数)
          return {
            字段名称: key,
            行号: m.行,
            列号: m.列,
            数据源: isFormula ? `公式: ${m.转换函数}` : (m.数据源 || ''),
            数据源_中文: isFormula ? `公式: ${m.转换函数}` : (m.数据源_中文 || ''),
            统计方法: isFormula ? '公式' : (m.转换函数 || ''),
            字典值选择: m.字典值选择 || []
          }
        })
      }
    }
  } catch (error) {
    ElMessage.error('保存失败: ' + error.message)
  }
}

async function deleteFieldMapping(row) {
  try {
    await ElMessageBox.confirm(`确定要删除字段"${row.字段名称}"的映射吗？`, '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    const resp = await fetch(
      `${API_BASE}/field-mapping/${encodeURIComponent(fieldMappingForm.value.模板ID)}/${encodeURIComponent(row.字段名称)}`,
      { method: 'DELETE' }
    )
    const data = await resp.json()
    if (data.成功) {
      ElMessage.success('已删除')
      const mappingsResponse = await fetch(`${API_BASE}/field-mappings/${fieldMappingForm.value.模板ID}`)
      const mappingsData = await mappingsResponse.json()
      if (mappingsData.成功) {
        const mappings = mappingsData.数据
        fieldMappingsList.value = Object.keys(mappings).map(key => {
          const m = mappings[key]
          const isFormula = m.转换函数 && !['计数','求和','平均值','最大值','最小值','求积','取值'].includes(m.转换函数)
          return {
            字段名称: key,
            行号: m.行,
            列号: m.列,
            数据源: isFormula ? `公式: ${m.转换函数}` : (m.数据源 || ''),
            数据源_中文: isFormula ? `公式: ${m.转换函数}` : (m.数据源_中文 || ''),
            统计方法: isFormula ? '公式' : (m.转换函数 || '')
          }
        })
      }
    } else {
      ElMessage.error(data.消息 || '删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败: ' + error.message)
    }
  }
}

function onSourceTypeChange(newType) {
  if (newType === '公式计算') {
    fieldMappingForm.value.数据源表 = ''
    fieldMappingForm.value.数据源字段 = ''
    fieldMappingForm.value.字典值选择 = []
    currentFieldDictValues.value = []
    availableFields.value = []
  } else {
    fieldMappingForm.value.公式表达式 = ''
  }
}

function openHistoryDialog(row) {
  historyTemplateId.value = row.模板ID
  historyDateRange.value = []
  historyRecords.value = []
  historyDialogVisible.value = true
}

async function queryHistory() {
  try {
    const body = { 模板ID: historyTemplateId.value }
    if (historyDateRange.value && historyDateRange.value.length === 2) {
      body.起始日期 = historyDateRange.value[0]
      body.截止日期 = historyDateRange.value[1]
    }
    const response = await axios.post(`${API_BASE}/history`, body)
    historyRecords.value = response.data.数据 || []
    if (historyRecords.value.length === 0) {
      ElMessage.info('未找到历史文件')
    }
  } catch (error) {
    ElMessage.error('查询失败: ' + (error.response?.data?.detail || error.message))
  }
}

function downloadHistoryFile(record, format) {
  const url = `${API_BASE}/history-file/${record.ID}?format=${format}`
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', '')
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
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
.template-manager {
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