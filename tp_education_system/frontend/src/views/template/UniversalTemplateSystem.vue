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
        <el-table-column prop="模板分类" label="模板分类" width="100" />
        <el-table-column prop="模板类型" label="模板类型" width="120" />
        <el-table-column prop="原始文件" label="原始文件" width="200" />
        <el-table-column prop="创建时间" label="创建时间" width="180" />
        <el-table-column label="操作" width="400" fixed="right">
          <template #default="scope">
            <el-button size="small" @click="previewTemplate(scope.row)">预览</el-button>
            <el-button size="small" type="primary" @click="showFieldMappingDialog(scope.row)">配置映射</el-button>
            <el-button size="small" type="success" @click="showFillDialog(scope.row)">填报</el-button>
            <el-dropdown style="margin-left: 6px" trigger="click">
              <el-button size="small" type="warning">
                导出<el-icon class="el-icon--right"><arrow-down /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="print" @click="handlePrint(scope.row)">
                    打印
                  </el-dropdown-item>
                  <el-dropdown-item command="excel" @click="exportTemplate(scope.row)">
                    Excel格式
                  </el-dropdown-item>
                  <el-dropdown-item command="template" @click="downloadTemplateFile(scope.row)">
                    Excel模板
                  </el-dropdown-item>
                  <el-dropdown-item v-if="libreOfficeAvailable" command="pdf" @click="exportPdf(scope.row)">
                    PDF格式
                  </el-dropdown-item>
                  <el-dropdown-item command="history" @click="openHistoryDialog(scope.row)" divided>
                    历史文件
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
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
              <el-form-item label="数据源表">
                <el-select v-model="fieldMappingForm.数据源表" placeholder="请选择数据来源表" filterable @change="onTableChange">
                  <el-option 
                    v-for="table in availableTables" 
                    :key="table.英文表名" 
                    :label="table.显示名称" 
                    :value="table.英文表名" 
                  />
                </el-select>
              </el-form-item>
              <el-form-item label="数据源字段">
                <el-select v-model="fieldMappingForm.数据源字段" placeholder="请先选择数据源表" filterable :disabled="!fieldMappingForm.数据源表">
                  <el-option 
                    v-for="field in availableFields" 
                    :key="field.字段名" 
                    :label="field.显示名称" 
                    :value="field.字段名" 
                  />
                </el-select>
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

    <el-dialog v-model="fillDialogVisible" title="自动填报" width="850px" top="3vh">
      <template v-if="currentFillTemplate.模板分类 === '单位汇总表'">
        <el-form label-width="80px">
          <el-form-item label="年月">
            <el-date-picker v-model="fillForm.年月" type="month" placeholder="选择年月" format="YYYY年M月" value-format="YYYY-MM" style="width: 220px" />
          </el-form-item>
          <el-form-item label="统计范围">
            <template v-if="fillScopeSummary">
              <el-tag type="primary" size="large" style="max-width: 500px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{{ fillScopeSummary }}</el-tag>
              <el-button size="small" style="margin-left: 10px" type="warning" plain @click="showScopeDialog">修改</el-button>
            </template>
            <template v-else>
              <span style="color: #909399; line-height: 32px;">未设置（将统计全部单位）</span>
              <el-button size="small" style="margin-left: 10px" type="primary" @click="showScopeDialog">设置</el-button>
            </template>
          </el-form-item>
          <el-form-item label="填报口径">
            <template v-if="fillCriteriaSummary">
              <el-tag type="success" size="large" style="max-width: 500px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{{ fillCriteriaSummary }}</el-tag>
              <el-button size="small" style="margin-left: 10px" type="warning" plain @click="showCriteriaDialog">修改</el-button>
            </template>
            <template v-else>
              <span style="color: #909399; line-height: 32px;">未设置（统计全部标签）</span>
              <el-button size="small" style="margin-left: 10px" type="primary" @click="showCriteriaDialog">设置</el-button>
            </template>
          </el-form-item>
        </el-form>
      </template>

      <template v-else>
        <el-form label-width="80px">
          <el-form-item label="职工查询">
            <el-select
              v-model="fillForm.职工ID"
              filterable
              remote
              reserve-keyword
              placeholder="输入身份证号、姓名或ID搜索"
              :remote-method="searchEmployee"
              :loading="employeeSearchLoading"
              style="width: 100%"
              value-key="职工ID"
              @change="onEmployeeSelect"
            >
              <el-option v-for="emp in employeeSearchResults" :key="emp.职工ID" :value="emp.职工ID">
                <span style="font-weight: bold;">{{ emp.姓名 }}</span>
                <span style="float: right; color: #8492a6; font-size: 13px;">{{ emp.身份证号 }}</span>
              </el-option>
            </el-select>
          </el-form-item>
          <el-form-item v-if="fillForm.职工ID && selectedEmployeeName" label="确认职工">
            <el-tag type="success" size="large">{{ selectedEmployeeName }}</el-tag>
          </el-form-item>
          <el-form-item label="年月">
            <el-date-picker v-model="fillForm.年月" type="month" placeholder="选择年月" format="YYYY年M月" value-format="YYYY-MM" style="width: 220px" />
          </el-form-item>
        </el-form>
      </template>

      <div v-if="fillResultHtml" id="filled-template-preview" class="preview-container" v-html="fillResultHtml"></div>

      <template #footer>
        <el-button @click="fillDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="fillTemplate">开始填报</el-button>
        <el-button type="success" @click="exportFilledTemplate" :disabled="!fillResultHtml">导出Excel</el-button>
        <el-button type="warning" @click="saveFilledTemplate" :disabled="!fillResultHtml" :loading="saving">保存</el-button>
      </template>
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
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button size="small" type="primary" @click="downloadHistoryFile(scope.row, 'Excel')">Excel下载</el-button>
            <el-button
              size="small"
              type="success"
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

    <el-dialog v-model="scopeDialogVisible" title="设置统计范围" width="600px" top="5vh">
      <div class="scope-explain">
        <el-alert type="info" :closable="false" show-icon>
          <template #title>
            从"省"开始，逐级勾选并选择具体单位。<strong>勾选到哪一级，就统计到哪一级。</strong>
          </template>
        </el-alert>
      </div>
      <div class="unit-scope">
        <div class="unit-level" v-for="level in fillLevelKeys" :key="level.label">
          <el-checkbox v-model="fillScope[level.label].勾选" :disabled="!isFillLevelCheckboxEnabled(level.label)">
            {{ level.label }}
          </el-checkbox>
          <el-select
            v-model="fillScope[level.label].unit_id"
            :placeholder="'请选择' + level.label"
            size="small"
            :disabled="!fillScope[level.label].勾选"
            style="width: 200px"
            @change="onFillUnitChange(level.label)"
          >
            <el-option v-for="u in getFillAvailableUnits(level.label)" :key="u.id" :label="u.name" :value="u.id" />
          </el-select>
        </div>
      </div>
      <div class="scope-tip">{{ fillScopeDescription }}</div>
      <template #footer>
        <el-button @click="scopeDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmScope">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="criteriaDialogVisible" title="设置填报口径" width="700px" top="5vh">
      <div class="scope-explain">
        <el-alert type="success" :closable="false" show-icon>
          <template #title>选择要纳入统计的标签条件（可多选，不选则包含所有）</template>
        </el-alert>
      </div>
      <el-checkbox-group v-model="tempCriteriaTags" class="criteria-tags">
        <el-checkbox v-for="tag in allTags" :key="tag.id" :value="tag.id" :label="tag.id">
          {{ tag.标签名称 }}
        </el-checkbox>
      </el-checkbox-group>
      <template #footer>
        <el-button @click="criteriaDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmCriteria">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowDown, Upload } from '@element-plus/icons-vue'
import axios from 'axios'

const API_BASE = '/api/universal-template'
const UNIT_API = '/api/unit'

const templates = ref([])
const importDialogVisible = ref(false)
const previewDialogVisible = ref(false)
const fieldMappingDialogVisible = ref(false)
const fillDialogVisible = ref(false)
const previewTitle = ref('')
const libreOfficeAvailable = ref(false)
const saving = ref(false)
const historyDialogVisible = ref(false)
const historyDateRange = ref([])
const historyRecords = ref([])
const historyTemplateId = ref('')

const fillLevelKeys = [
  { label: '省', index: 0 },
  { label: '地区', index: 1 },
  { label: '县', index: 2 },
  { label: '镇', index: 3 },
  { label: '学校', index: 4 }
]

function makeFillEmptyScope() {
  return {
    省: { 勾选: false, unit_id: null, unit_name: '' },
    地区: { 勾选: false, unit_id: null, unit_name: '' },
    县: { 勾选: false, unit_id: null, unit_name: '' },
    镇: { 勾选: false, unit_id: null, unit_name: '' },
    学校: { 勾选: false, unit_id: null, unit_name: '' }
  }
}

const fillScope = ref(makeFillEmptyScope())
const fillUnitLevels = ref({
  省: [],
  地区: [],
  县: [],
  镇: [],
  学校: []
})
const fillCriteriaTags = ref([])
const tempCriteriaTags = ref([])
const currentFillTemplate = ref({})
const allTags = ref([])
const scopeDialogVisible = ref(false)
const criteriaDialogVisible = ref(false)
const employeeSearchLoading = ref(false)
const employeeSearchResults = ref([])
const selectedEmployeeName = ref('')
const fillResultHtml = ref('')

const fillScopeSummary = computed(() => {
  const s = fillScope.value
  const parts = []
  for (let i = 0; i < fillLevelKeys.length; i++) {
    const l = fillLevelKeys[i]
    if (s[l.label].勾选 && s[l.label].unit_name) {
      parts.push(s[l.label].unit_name)
    }
  }
  return parts.length > 0 ? parts.join(' ＞ ') : ''
})

const fillCriteriaSummary = computed(() => {
  if (fillCriteriaTags.value.length === 0) return ''
  const names = fillCriteriaTags.value.map(tid => {
    const tag = allTags.value.find(t => t.id === tid)
    return tag ? tag.标签名称 : String(tid)
  })
  if (names.length <= 5) return names.join('、')
  return names.slice(0, 5).join('、') + ` 等${names.length}个`
})

const fillScopeDescription = computed(() => {
  const s = fillScope.value
  const parts = []
  for (let i = 0; i < fillLevelKeys.length; i++) {
    const l = fillLevelKeys[i]
    if (s[l.label].勾选 && s[l.label].unit_name) {
      parts.push({ label: l.label, name: s[l.label].unit_name })
    }
  }
  if (parts.length === 0) {
    const anyChecked = fillLevelKeys.some(l => s[l.label].勾选)
    if (anyChecked) {
      return '⚠️ 已勾选级别但未选择具体单位，请从"省"开始逐级选择'
    }
    return '⚠️ 未设置统计范围 — 将统计全部单位'
  }
  const pathStr = parts.map(p => p.name).join(' ＞ ')
  const deepest = parts[parts.length - 1]
  if (deepest.label === '学校') {
    return `📍 ${pathStr} → 仅覆盖本校`
  }
  const belowLevels = {
    '省': '省、地区、县、镇、学校',
    '地区': '地区、县、镇、学校',
    '县': '县、镇、学校',
    '镇': '镇、学校'
  }
  const below = belowLevels[deepest.label] || '下级全部单位'
  return `📍 ${pathStr} → 覆盖本${deepest.label}及下属${below}`
})

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
  数据源表: '',
  数据源字段: ''
})

const fieldMappingsList = ref([])
const availableTables = ref([])
const availableFields = ref([])

const fillForm = ref({
  模板ID: '',
  职工ID: '',
  年月: ''
})

const currentTemplateId = ref('')
const uploadRef = ref(null)
const uploadFileList = ref([])

onMounted(() => {
  loadTemplates()
  checkLibreOffice()
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
    模板分类: '单位汇总表',
    file: null
  }
  uploadFileList.value = []
  importDialogVisible.value = true
}

async function loadFillUnitLevels() {
  try {
    const response = await axios.get(`${UNIT_API}/levels`)
    if (response.data.success) {
      fillUnitLevels.value = response.data.levels
    }
  } catch (error) {
    console.error('加载单位层级失败:', error)
  }
}

async function loadAllTags() {
  try {
    const response = await axios.get(`${API_BASE}/tags`)
    if (response.data.成功) {
      allTags.value = response.data.数据 || []
    }
  } catch (error) {
    console.error('加载标签列表失败:', error)
  }
}

function onFillUnitChange(changedLevel) {
  const levelData = fillUnitLevels.value[changedLevel]
  const selectedId = fillScope.value[changedLevel].unit_id
  if (selectedId && levelData) {
    const found = levelData.find(u => u.id === selectedId)
    if (found) {
      fillScope.value[changedLevel].unit_name = found.name
    }
  } else {
    fillScope.value[changedLevel].unit_name = ''
  }
  
  const currentIdx = fillLevelKeys.findIndex(l => l.label === changedLevel)
  for (let i = currentIdx + 1; i < fillLevelKeys.length; i++) {
    const label = fillLevelKeys[i].label
    fillScope.value[label].unit_id = null
    fillScope.value[label].unit_name = ''
  }
}

function getFillAvailableUnits(level) {
  const idx = fillLevelKeys.findIndex(l => l.label === level)
  if (idx === 0) {
    return fillUnitLevels.value[level] || []
  }
  const parentLevel = fillLevelKeys[idx - 1].label
  const parentId = fillScope.value[parentLevel].unit_id
  if (!parentId) return []
  return (fillUnitLevels.value[level] || []).filter(u => u.parent_id === parentId)
}

function isFillLevelCheckboxEnabled(level) {
  const idx = fillLevelKeys.findIndex(l => l.label === level)
  if (idx === 0) return true
  const parentLevel = fillLevelKeys[idx - 1].label
  return fillScope.value[parentLevel].勾选 && fillScope.value[parentLevel].unit_id
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
    const response = await axios.get(`${API_BASE}/available-tables`)
    if (response.data.成功) {
      availableTables.value = response.data.数据
    }
  } catch (error) {
    console.error('加载数据表列表失败:', error)
  }
}

async function onTableChange(tableName) {
  if (!tableName) {
    availableFields.value = []
    fieldMappingForm.value.数据源字段 = ''
    return
  }
  try {
    const response = await axios.get(`${API_BASE}/table-columns/${encodeURIComponent(tableName)}`)
    if (response.data.成功) {
      availableFields.value = response.data.数据
    }
  } catch (error) {
    console.error('加载表字段失败:', error)
    ElMessage.error('加载表字段失败: ' + error.message)
  }
}

async function showFieldMappingDialog(row) {
  currentTemplateId.value = row.模板ID
  fieldMappingForm.value.模板ID = row.模板ID
  fieldMappingForm.value.数据源表 = ''
  fieldMappingForm.value.数据源字段 = ''
  availableFields.value = []
  fieldMappingDialogVisible.value = true

  loadAvailableTables()

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
  currentFillTemplate.value = row
  fillForm.value.模板ID = row.模板ID
  fillForm.value.职工ID = ''
  fillForm.value.年月 = ''
  fillScope.value = makeFillEmptyScope()
  fillCriteriaTags.value = []
  fillResultHtml.value = ''
  selectedEmployeeName.value = ''
  employeeSearchResults.value = []
  fillDialogVisible.value = true

  if (row.模板分类 === '单位汇总表') {
    loadFillUnitLevels()
    loadAllTags()
  }
}

function showScopeDialog() {
  scopeDialogVisible.value = true
}

function confirmScope() {
  scopeDialogVisible.value = false
}

function showCriteriaDialog() {
  tempCriteriaTags.value = [...fillCriteriaTags.value]
  criteriaDialogVisible.value = true
  if (allTags.value.length === 0) {
    loadAllTags()
  }
}

function confirmCriteria() {
  fillCriteriaTags.value = [...tempCriteriaTags.value]
  criteriaDialogVisible.value = false
}

async function searchEmployee(keyword) {
  if (!keyword || keyword.length < 1) {
    employeeSearchResults.value = []
    return
  }
  employeeSearchLoading.value = true
  try {
    const response = await axios.get(`${API_BASE}/search-employee`, {
      params: { keyword }
    })
    if (response.data.成功) {
      employeeSearchResults.value = response.data.数据 || []
      if (response.data.数据 && response.data.数据.length === 1) {
        selectedEmployeeName.value = response.data.数据[0].姓名
      }
    }
  } catch (error) {
    console.error('搜索职工失败:', error)
  } finally {
    employeeSearchLoading.value = false
  }
}

function onEmployeeSelect(empId) {
  const emp = employeeSearchResults.value.find(e => e.职工ID === empId)
  selectedEmployeeName.value = emp ? emp.姓名 : ''
}

async function fillTemplate() {
  try {
    const requestBody = {
      模板ID: fillForm.value.模板ID,
      查询条件: {}
    }

    if (fillForm.value.职工ID) {
      requestBody.查询条件.职工ID = fillForm.value.职工ID
    }
    if (fillForm.value.年月) {
      requestBody.查询条件.年月 = fillForm.value.年月
    }

    if (currentFillTemplate.value.模板分类 === '单位汇总表') {
      const scopeData = { 单位范围: {} }
      for (const key of Object.keys(fillScope.value)) {
        const item = fillScope.value[key]
        if (item.勾选 && item.unit_id) {
          scopeData.单位范围[key] = { unit_id: item.unit_id, unit_name: item.unit_name }
        }
      }
      requestBody.统计范围 = scopeData
      requestBody.填报口径 = { 标签ID列表: fillCriteriaTags.value }
    }

    const response = await axios.post(`${API_BASE}/fill`, requestBody)

    if (response.data.成功) {
      fillResultHtml.value = response.data.数据?.HTML || ''
      ElMessage.success('数据填报成功')
    }
  } catch (error) {
    ElMessage.error('填报失败: ' + error.message)
  }
}

async function downloadTemplateFile(row) {
  try {
    const response = await axios.get(`${API_BASE}/download-template/${row.模板ID}`, {
      responseType: 'blob'
    })
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `${row.模板名称}_模板.xlsx`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    ElMessage.success('模板下载成功')
  } catch (error) {
    ElMessage.error('下载失败: ' + error.message)
  }
}

function getExportFilename(response, defaultName) {
  const contentDisposition = response.headers['content-disposition']
  if (contentDisposition) {
    const match5987 = contentDisposition.match(/filename\*=utf-8''(.+)/i)
    if (match5987 && match5987[1]) {
      return decodeURIComponent(match5987[1])
    }
    const match = contentDisposition.match(/filename[^;=\n]*=["']?((["']).*?\2|[^;\n]*)["']?/i)
    if (match && match[1]) {
      return match[1].replace(/["']/g, '')
    }
  }
  return defaultName
}

function getFillRequestBodyForRow(row) {
  if (fillForm.value.模板ID !== row.模板ID) {
    return null
  }
  const requestBody = {
    模板ID: row.模板ID,
    查询条件: {}
  }
  if (fillForm.value.职工ID) {
    requestBody.查询条件.职工ID = fillForm.value.职工ID
  }
  if (fillForm.value.年月) {
    requestBody.查询条件.年月 = fillForm.value.年月
  }
  if (row.模板分类 === '单位汇总表') {
    const scopeData = { 单位范围: {} }
    for (const key of Object.keys(fillScope.value)) {
      const item = fillScope.value[key]
      if (item.勾选 && item.unit_id) {
        scopeData.单位范围[key] = { unit_id: item.unit_id, unit_name: item.unit_name }
      }
    }
    requestBody.统计范围 = scopeData
    requestBody.填报口径 = { 标签ID列表: fillCriteriaTags.value }
  }
  return requestBody
}

async function exportTemplate(row) {
  try {
    const requestBody = getFillRequestBodyForRow(row)
    if (!requestBody) {
      ElMessage.warning('请先点击"填报"按钮，设置查询条件后再导出')
      return
    }
    const response = await axios.post(`${API_BASE}/export`, requestBody, {
      responseType: 'blob'
    })
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', getExportFilename(response, `${row.模板名称}.xlsx`))
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    ElMessage.success('导出成功')
  } catch (error) {
    ElMessage.error('导出失败: ' + (error.response?.data?.detail || error.message))
  }
}

async function handlePrint(row) {
  try {
    const response = await axios.get(`${API_BASE}/preview/${row.模板ID}`)
    if (response.data.成功 && response.data.数据 && response.data.数据.HTML) {
      const printWindow = window.open('', '_blank', 'width=1000,height=800')
      printWindow.document.write(`
        <html>
          <head><title>${row.模板名称}</title></head>
          <body>${response.data.数据.HTML}</body>
        </html>
      `)
      printWindow.document.close()
      printWindow.focus()
      printWindow.print()
    }
  } catch (error) {
    ElMessage.error('打印失败: ' + error.message)
  }
}

async function exportPdf(row) {
  try {
    const requestBody = getFillRequestBodyForRow(row)
    if (!requestBody) {
      ElMessage.warning('请先点击"填报"按钮，设置查询条件后再导出')
      return
    }
    ElMessage.info('正在生成PDF，请稍候...')
    const response = await axios.post(`${API_BASE}/export-pdf`, requestBody, {
      responseType: 'blob'
    })
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', getExportFilename(response, `${row.模板名称}.pdf`))
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    ElMessage.success('PDF导出成功')
  } catch (error) {
    ElMessage.error('PDF导出失败: ' + (error.response?.data?.detail || error.message))
  }
}

async function checkLibreOffice() {
  try {
    const response = await axios.get(`${API_BASE}/check-libreoffice`)
    libreOfficeAvailable.value = response.data.可用
  } catch {
    libreOfficeAvailable.value = false
  }
}

async function exportFilledTemplate() {
  try {
    const requestBody = {
      模板ID: fillForm.value.模板ID,
      查询条件: {}
    }
    if (fillForm.value.职工ID) {
      requestBody.查询条件.职工ID = fillForm.value.职工ID
    }
    if (fillForm.value.年月) {
      requestBody.查询条件.年月 = fillForm.value.年月
    }
    if (currentFillTemplate.value.模板分类 === '单位汇总表') {
      const scopeData = { 单位范围: {} }
      for (const key of Object.keys(fillScope.value)) {
        const item = fillScope.value[key]
        if (item.勾选 && item.unit_id) {
          scopeData.单位范围[key] = { unit_id: item.unit_id, unit_name: item.unit_name }
        }
      }
      requestBody.统计范围 = scopeData
      requestBody.填报口径 = { 标签ID列表: fillCriteriaTags.value }
    }

    const response = await axios.post(`${API_BASE}/export`, requestBody, {
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

async function saveFilledTemplate() {
  try {
    saving.value = true
    const requestBody = {
      模板ID: fillForm.value.模板ID,
      查询条件: {}
    }
    if (fillForm.value.职工ID) {
      requestBody.查询条件.职工ID = fillForm.value.职工ID
    }
    if (fillForm.value.年月) {
      requestBody.查询条件.年月 = fillForm.value.年月
    }
    if (currentFillTemplate.value.模板分类 === '单位汇总表') {
      const scopeData = { 单位范围: {} }
      for (const key of Object.keys(fillScope.value)) {
        const item = fillScope.value[key]
        if (item.勾选 && item.unit_id) {
          scopeData.单位范围[key] = { unit_id: item.unit_id, unit_name: item.unit_name }
        }
      }
      requestBody.统计范围 = scopeData
      requestBody.填报口径 = { 标签ID列表: fillCriteriaTags.value }
    }
    const response = await axios.post(`${API_BASE}/save`, requestBody)
    if (response.data.成功) {
      ElMessage.success(`保存成功！Excel: ${response.data.数据.Excel文件}${response.data.数据.PDF文件 ? '  PDF: ' + response.data.数据.PDF文件 : ''}`)
    }
  } catch (error) {
    ElMessage.error('保存失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    saving.value = false
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
.universal-template-system {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.scope-explain {
  margin-bottom: 10px;
}

.unit-scope {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.unit-level {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 4px 8px;
  border-radius: 4px;
  background: #f5f7fa;
}

.unit-level:hover {
  background: #ecf5ff;
}

.scope-tip {
  margin-top: 10px;
  padding: 8px 12px;
  background: linear-gradient(135deg, #f0f9eb 0%, #e1f3d8 100%);
  border-left: 4px solid #67c23a;
  border-radius: 4px;
  color: #303133;
  font-size: 14px;
  font-weight: 500;
}

.political-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 8px 0;
}

.political-tags .el-checkbox {
  margin-right: 0;
  padding: 6px 12px;
  background: #fdf6ec;
  border: 1px solid #faecd8;
  border-radius: 4px;
}

.criteria-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 8px 0;
}

.criteria-tags .el-checkbox {
  margin-right: 0;
  padding: 6px 12px;
  background: #f0f9eb;
  border: 1px solid #e1f3d8;
  border-radius: 4px;
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

