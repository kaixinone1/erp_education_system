<template>
  <div class="template-operator">
    <!-- 顶部标题栏 -->
    <div class="operator-header" v-if="templateName">
      <h3>
        <template v-if="moduleName">{{ moduleName }} - {{ templateName }}</template>
        <template v-else>{{ templateName }}</template>
      </h3>
    </div>

    <!-- 操作按钮区 -->
    <div class="operator-actions">
      <el-button type="primary" @click="showFillDialog" :disabled="loading">
        <el-icon v-if="loading"><Loading /></el-icon>
        填报
      </el-button>
      <el-dropdown @command="handleExportAction" :disabled="loading">
        <el-button type="warning">
          导出<el-icon class="el-icon--right"><ArrowDown /></el-icon>
        </el-button>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="excel">Excel格式</el-dropdown-item>
            <el-dropdown-item command="pdf">PDF格式</el-dropdown-item>
            <el-dropdown-item command="word">Word格式</el-dropdown-item>
            <el-dropdown-item command="template">模板</el-dropdown-item>
            <el-dropdown-item command="print">打印</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <el-icon class="is-loading"><Loading /></el-icon>
      <span>正在加载模板配置...</span>
    </div>

    <!-- 填报对话框 -->
    <el-dialog v-model="fillDialogVisible" title="自动填报" width="850px" top="3vh" @close="onFillDialogClose">
      <!-- 阶段一：参数设置表单 -->
      <template v-if="!fillParamsConfirmed">
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
                ref="employeeSelectRef"
                v-model="fillForm.职工ID"
                filterable
                remote
                placeholder="输入身份证号、姓名或ID搜索"
                :remote-method="searchEmployee"
                :loading="employeeSearchLoading"
                style="width: 100%"
                value-key="职工ID"
                @change="onEmployeeSelect"
              >
                <el-option v-for="emp in employeeSearchResults" :key="emp.职工ID" :value="emp.职工ID" :label="`${emp.职工ID}  ${emp.姓名}  ${emp.身份证号}`">
                  <span style="font-weight: bold;">{{ emp.职工ID }}</span>
                  <span>{{ emp.姓名 }}</span>
                  <span style="float: right; color: #8492a6; font-size: 13px;">{{ emp.身份证号 }}</span>
                </el-option>
              </el-select>
            </el-form-item>
            <el-form-item label="年月">
              <el-date-picker v-model="fillForm.年月" type="month" placeholder="选择年月" format="YYYY年M月" value-format="YYYY-MM" style="width: 220px" />
            </el-form-item>
          </el-form>
        </template>
      </template>

      <!-- 阶段二：HTML预览 -->
      <template v-if="fillParamsConfirmed">
        <div v-if="!fillResultHtml && isWordTemplate" class="word-template-notice">
          <el-alert type="info" :closable="false" show-icon>
            <template #title>
              Word模板不支持在线预览，请直接点击「开始填报」填充数据
            </template>
          </el-alert>
        </div>
        <div v-if="!fillResultHtml && !isWordTemplate" id="blank-template-preview" class="preview-container" ref="previewContainerRef" v-html="blankTemplateHtml"></div>
        <div v-if="fillResultHtml && isWordTemplate" class="word-template-notice">
          <el-alert type="info" :closable="false" show-icon>
            <template #title>
              Word模板已填报完成，请点击「保存」按钮生成Word和PDF文件
            </template>
          </el-alert>
        </div>
        <div v-if="fillResultHtml && !isWordTemplate" id="filled-template-preview" class="preview-container" ref="previewContainerRef" v-html="fillResultHtml"></div>
      </template>

      <template #footer>
        <el-button @click="fillDialogVisible = false">关闭</el-button>
        <el-button v-if="!fillParamsConfirmed" type="primary" @click="confirmFillParams" :loading="confirmingParams">确定</el-button>
        <el-button v-if="fillParamsConfirmed && !fillResultHtml" type="primary" @click="fillTemplate">开始填报</el-button>
        <el-button v-if="fillResultHtml" type="warning" @click="saveFilledTemplate" :loading="saving">保存</el-button>
        <el-button v-if="fillResultHtml && !remarkEditable" @click="startEditRemark">修改备注</el-button>
        <el-button v-if="fillResultHtml && remarkEditable" type="primary" @click="saveRemark">保存备注</el-button>
        <el-button v-if="fillResultHtml" @click="printPreview">打印</el-button>
      </template>
    </el-dialog>

    <!-- 文件选择对话框 -->
    <el-dialog v-model="fileSelectDialogVisible" :title="fileSelectTitle" width="650px" top="5vh">
      <div style="margin-bottom: 12px; display: flex; align-items: center; gap: 10px;">
        <span style="font-size: 13px; color: #606266;">筛选年月：</span>
        <el-date-picker v-model="fileSelectYearMonth" type="month" placeholder="全部" format="YYYY年M月" value-format="YYYY-MM" style="width: 200px" clearable @change="onFileSelectYearMonthChange" />
        <el-button size="small" @click="clearFileSelectFilter" :disabled="!fileSelectYearMonth">清除筛选</el-button>
        <span style="font-size: 12px; color: #909399;">共 {{ fileSelectRecords.length }} 条记录</span>
      </div>
      <div v-if="fileSelectRecords.length === 0" style="text-align:center;padding:30px;color:#999">
        暂无已保存的文件，请先点击「填报」按钮自动填报并保存
      </div>
      <el-table v-else :data="fileSelectRecords" style="width:100%" max-height="350">
        <el-table-column prop="保存时间" label="保存时间" width="160" />
        <el-table-column prop="文件名" label="文件名" min-width="200" show-overflow-tooltip />
        <el-table-column prop="年月" label="年月" width="100" />
        <el-table-column prop="单位名称" label="单位" min-width="120" />
        <el-table-column label="操作" width="280">
          <template #default="scope">
            <el-button v-if="fileSelectMode === 'excel'" size="small" type="success" @click="downloadSelectedFile(scope.row, 'Excel')" :disabled="!scope.row.有Excel">
              Excel下载
            </el-button>
            <el-button v-if="fileSelectMode === 'word'" size="small" type="primary" @click="downloadSelectedFile(scope.row, 'Word')" :disabled="!scope.row.有Word">
              Word下载
            </el-button>
            <el-button v-if="fileSelectMode === 'excel' || fileSelectMode === 'pdf'" size="small" type="warning" @click="downloadSelectedFile(scope.row, 'PDF')" :disabled="!scope.row.有PDF">
              PDF下载
            </el-button>
            <el-button v-if="fileSelectMode === 'print'" size="small" type="danger" @click="printSelectedFile(scope.row)">
              打印
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button @click="fileSelectDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 统计范围设置对话框 -->
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

    <!-- 填报口径设置对话框 -->
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
import { ElMessage } from 'element-plus'
import { ArrowDown, Loading } from '@element-plus/icons-vue'
import axios from 'axios'
import { useUserStore } from '@/store/user'

const userStore = useUserStore()

const props = defineProps({
  templateId: {
    type: String,
    required: true
  },
  moduleName: {
    type: String,
    default: ''
  }
})

const API_BASE = '/api/universal-template'
const UNIT_API = '/api/unit'

const loading = ref(true)
const templateName = ref('')
const saving = ref(false)
const fillDialogVisible = ref(false)
const fillParamsConfirmed = ref(false)
const confirmingParams = ref(false)
const fillResultHtml = ref('')
const isWordTemplate = ref(false)
const blankTemplateHtml = ref('')
const previewContainerRef = ref(null)
const remarkEditable = ref(false)
const editedRemark = ref('')
const filledConfigFromFill = ref(null)

const fileSelectDialogVisible = ref(false)
const fileSelectTitle = ref('')
const fileSelectActionLabel = ref('')
const fileSelectRecords = ref([])
const fileSelectMode = ref('excel')
const fileSelectRow = ref(null)
const fileSelectYearMonth = ref('')

const scopeDialogVisible = ref(false)
const criteriaDialogVisible = ref(false)

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
const employeeSearchLoading = ref(false)
const employeeSearchResults = ref([])
const selectedEmployeeName = ref('')
const employeeSelectRef = ref(null)

const fillForm = ref({
  模板ID: '',
  职工ID: '',
  年月: ''
})

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

onMounted(async () => {
  await loadTemplateConfig()
  await loadFillUnitLevels()
  await loadAllTags()
})

async function loadTemplateConfig() {
  try {
    const response = await axios.get(`${API_BASE}/config/${props.templateId}`)
    if (response.data.成功) {
      const config = response.data.数据
      currentFillTemplate.value = {
        模板ID: props.templateId,
        模板名称: config.模板名称 || '',
        模板分类: config.模板分类 || '个人表',
        模板类型: config.模板类型 || 'excel',
        原始文件: config.原始文件路径 || ''
      }
      templateName.value = config.模板名称 || ''
      fillForm.value.模板ID = props.templateId
    }
  } catch (error) {
    console.error('加载模板配置失败:', error)
    ElMessage.error('加载模板配置失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
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

function showFillDialog() {
  fillForm.value.职工ID = ''
  fillForm.value.年月 = ''
  fillScope.value = makeFillEmptyScope()
  fillCriteriaTags.value = []
  fillResultHtml.value = ''
  blankTemplateHtml.value = ''
  fillParamsConfirmed.value = false
  selectedEmployeeName.value = ''
  employeeSearchResults.value = []
  remarkEditable.value = false
  editedRemark.value = ''
  filledConfigFromFill.value = null
  isWordTemplate.value = false
  fillDialogVisible.value = true

  if (currentFillTemplate.value.模板分类 === '单位汇总表') {
    loadFillUnitLevels()
    loadAllTags()
  }
}

function onFillDialogClose() {
  fillParamsConfirmed.value = false
  fillResultHtml.value = ''
  blankTemplateHtml.value = ''
  remarkEditable.value = false
  editedRemark.value = ''
  filledConfigFromFill.value = null
  isWordTemplate.value = false
}

async function confirmFillParams() {
  if (currentFillTemplate.value.模板分类 !== '单位汇总表') {
    if (!fillForm.value.职工ID) {
      ElMessage.warning('请选择职工')
      return
    }
  }
  if (!fillForm.value.年月) {
    ElMessage.warning('请选择年月')
    return
  }

  confirmingParams.value = true
  try {
    let url = currentFillTemplate.value.模板分类 === '单位汇总表'
      ? `${API_BASE}/preview/${fillForm.value.模板ID}`
      : `${API_BASE}/preview/${fillForm.value.模板ID}?teacher_id=0`
    if (fillForm.value.年月) {
      url += (url.includes('?') ? '&' : '?') + `年月=${encodeURIComponent(fillForm.value.年月)}`
    }
    const response = await axios.get(url)
    if (response.data.成功) {
      if (response.data.数据?.模板类型 === 'word') {
        isWordTemplate.value = true
        blankTemplateHtml.value = ''
        fillParamsConfirmed.value = true
        ElMessage.success('Word模板已加载，请点击「开始填报」填充数据')
      } else {
        blankTemplateHtml.value = response.data.数据?.HTML || ''
        fillParamsConfirmed.value = true
        ElMessage.success('参数已确认，请点击「开始填报」填充数据')
      }
    }
  } catch (error) {
    ElMessage.error('加载模板失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    confirmingParams.value = false
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
      查询条件: {},
      封面单位: userStore.当前单位名称 || ''
    }

    if (fillForm.value.职工ID) {
      requestBody.查询条件.职工ID = fillForm.value.职工ID
    }
    if (fillForm.value.年月) {
      requestBody.查询条件.年月 = fillForm.value.年月
    }

    if (currentFillTemplate.value.模板分类 === '单位汇总表') {
      const scopeData = { 单位范围: {} }
      let hasAnyScope = false
      for (const key of Object.keys(fillScope.value)) {
        const item = fillScope.value[key]
        if (item.勾选 && item.unit_id) {
          scopeData.单位范围[key] = { unit_id: item.unit_id, unit_name: item.unit_name }
          hasAnyScope = true
        }
      }
      const hasAnyTags = fillCriteriaTags.value && fillCriteriaTags.value.length > 0
      if (hasAnyScope) {
        requestBody.统计范围 = scopeData
      }
      if (hasAnyTags) {
        requestBody.填报口径 = { 标签ID列表: fillCriteriaTags.value }
      }
    }

    const response = await axios.post(`${API_BASE}/fill`, requestBody)

    if (response.data.成功) {
      fillResultHtml.value = response.data.数据?.HTML || ''
      if (response.data.数据?.模板类型 === 'word') {
        isWordTemplate.value = true
        if (!fillResultHtml.value) {
          fillResultHtml.value = 'word'
        }
      } else {
        isWordTemplate.value = false
      }
      filledConfigFromFill.value = response.data.数据?.配置 || null
      remarkEditable.value = false
      ElMessage.success('数据填报成功')
    }
  } catch (error) {
    console.error('[填报] 失败:', error.message, error)
    ElMessage.error('填报失败: ' + error.message)
  }
}

async function saveFilledTemplate() {
  try {
    saving.value = true
    const requestBody = {
      模板ID: fillForm.value.模板ID,
      查询条件: {},
      封面单位: userStore.当前单位名称 || ''
    }
    if (fillForm.value.职工ID) {
      requestBody.查询条件.职工ID = fillForm.value.职工ID
    }
    if (fillForm.value.年月) {
      requestBody.查询条件.年月 = fillForm.value.年月
    }
    if (currentFillTemplate.value.模板分类 === '单位汇总表') {
      const scopeData = { 单位范围: {} }
      let hasAnyScope3 = false
      for (const key of Object.keys(fillScope.value)) {
        const item = fillScope.value[key]
        if (item.勾选 && item.unit_id) {
          scopeData.单位范围[key] = { unit_id: item.unit_id, unit_name: item.unit_name }
          hasAnyScope3 = true
        }
      }
      const hasAnyTags3 = fillCriteriaTags.value && fillCriteriaTags.value.length > 0
      if (hasAnyScope3) {
        requestBody.统计范围 = scopeData
      }
      if (hasAnyTags3) {
        requestBody.填报口径 = { 标签ID列表: fillCriteriaTags.value }
      }
    }

    if (filledConfigFromFill.value) {
      requestBody.填报配置 = filledConfigFromFill.value
    }

    const remark = getEditedRemark()
    if (remark) {
      requestBody.备注 = remark
    }

    const response = await axios.post(`${API_BASE}/save`, requestBody)
    if (response.data.成功) {
      const wordFile = response.data.数据?.Word文件
      const pdfFile = response.data.数据?.PDF文件
      const excelFile = response.data.数据?.Excel文件
      let msg = '保存成功！'
      if (wordFile) msg += ` Word: ${wordFile}`
      if (pdfFile) msg += ` PDF: ${pdfFile}`
      if (excelFile) msg += ` Excel: ${excelFile}`
      ElMessage.success(msg)
    }
  } catch (error) {
    ElMessage.error('保存失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    saving.value = false
  }
}

function printPreview() {
  if (!fillResultHtml.value) {
    ElMessage.warning('没有可打印的内容')
    return
  }
  const fullHtml = `<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>打印预览</title>
  <style>
    body { margin: 20px; }
    @media print {
      body { margin: 0; }
    }
  </style>
</head>
<body>
  ${fillResultHtml.value}
</body>
</html>`

  // iframe 的 contentDocument.write() 写入的内容，浏览器打印预览无法渲染
  // 必须使用 window.open 创建顶层窗口，document.write 写入同源内容，打印预览才能正常显示
  // 窗口定位到屏幕外，用户看不到，打印完成后自动关闭
  const printWindow = window.open('about:blank', '_blank', 'left=-9999,top=-9999,width=800,height=600')
  if (!printWindow) {
    ElMessage.warning('请允许弹出窗口以使用打印功能')
    return
  }
  printWindow.document.write(fullHtml)
  printWindow.document.close()
  printWindow.onload = () => {
    setTimeout(() => {
      printWindow.print()
      printWindow.close()
    }, 300)
  }
}

function handleExportAction(command) {
  const row = currentFillTemplate.value
  if (!row || !row.模板ID) {
    ElMessage.warning('请先加载模板配置')
    return
  }
  switch (command) {
    case 'excel':
      openFileSelectDialog(row, 'excel')
      break
    case 'pdf':
      openFileSelectDialog(row, 'pdf')
      break
    case 'word':
      openFileSelectDialog(row, 'word')
      break
    case 'template':
      downloadTemplateFile(row)
      break
    case 'print':
      openFileSelectDialog(row, 'print')
      break
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
    const filename = getExportFilename(response, `${row.模板名称}_模板.xlsx`)
    link.setAttribute('download', filename)
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

async function fetchSavedFiles(templateId, yearMonth) {
  let url = `${API_BASE}/saved-files/${templateId}`
  if (yearMonth) {
    const [y, mStr] = yearMonth.split('-')
    const m = parseInt(mStr)
    const ymFormatted = `${y}年${m}月`
    url += `?年月=${encodeURIComponent(ymFormatted)}`
  }
  const response = await axios.get(url)
  return response.data.数据 || []
}

async function openFileSelectDialog(row, mode) {
  fileSelectRow.value = row
  fileSelectMode.value = mode
  fileSelectYearMonth.value = ''
  if (mode === 'pdf') {
    fileSelectTitle.value = '选择要导出的PDF文件'
    fileSelectActionLabel.value = '导出PDF'
  } else if (mode === 'word') {
    fileSelectTitle.value = '选择要导出的Word文件'
    fileSelectActionLabel.value = '导出Word'
  } else if (mode === 'print') {
    fileSelectTitle.value = '选择要打印的文件'
    fileSelectActionLabel.value = '打印'
  } else {
    fileSelectTitle.value = '选择要导出的Excel文件'
    fileSelectActionLabel.value = '导出Excel'
  }
  try {
    fileSelectRecords.value = await fetchSavedFiles(row.模板ID, '')
  } catch (error) {
    fileSelectRecords.value = []
    ElMessage.error('获取文件列表失败: ' + (error.response?.data?.detail || error.message))
  }
  fileSelectDialogVisible.value = true
}

async function onFileSelectYearMonthChange(value) {
  if (!fileSelectRow.value) return
  try {
    fileSelectRecords.value = await fetchSavedFiles(fileSelectRow.value.模板ID, value || '')
  } catch (error) {
    fileSelectRecords.value = []
    ElMessage.error('获取文件列表失败: ' + (error.response?.data?.detail || error.message))
  }
}

function clearFileSelectFilter() {
  fileSelectYearMonth.value = ''
  onFileSelectYearMonthChange('')
}

function downloadSelectedFile(record, format = 'Word') {
  fileSelectDialogVisible.value = false
  if (format === 'Excel') {
    if (!record.有Excel) {
      ElMessage.warning('该记录无Excel文件')
      return
    }
    const link = document.createElement('a')
    link.href = `${API_BASE}/history-file/${record.ID}?format=Excel`
    link.setAttribute('download', '')
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    ElMessage.success('Excel导出成功')
  } else if (format === 'Word') {
    if (!record.有Word) {
      ElMessage.warning('该记录无Word文件')
      return
    }
    const link = document.createElement('a')
    link.href = `${API_BASE}/history-file/${record.ID}?format=Word`
    link.setAttribute('download', '')
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    ElMessage.success('Word下载成功')
  } else if (format === 'PDF') {
    if (!record.有PDF) {
      ElMessage.warning('该记录无PDF文件')
      return
    }
    const link = document.createElement('a')
    link.href = `${API_BASE}/history-file/${record.ID}?format=PDF`
    link.setAttribute('download', '')
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    ElMessage.success('PDF下载成功')
  }
}

async function printSelectedFile(record) {
  fileSelectDialogVisible.value = false
  try {
    const response = await axios.get(`${API_BASE}/history-file/${record.ID}?format=HTML`, {
      responseType: 'text'
    })
    const htmlContent = response.data
    if (!htmlContent || htmlContent.trim().length === 0) {
      ElMessage.warning('该记录无HTML文件，请先保存后重试')
      return
    }

    // 提取 body 内容和样式，统一包裹在干净文档结构中
    let bodyContent = htmlContent
    let extraStyles = ''

    const bodyMatch = htmlContent.match(/<body[^>]*>([\s\S]*)<\/body>/i)
    if (bodyMatch) {
      bodyContent = bodyMatch[1]
    }

    const styleMatches = htmlContent.match(/<style[^>]*>[\s\S]*?<\/style>/gi)
    if (styleMatches) {
      extraStyles = styleMatches.join('\n')
    }

    const fullHtml = `<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>打印预览</title>
  ${extraStyles}
  <style>
    body { margin: 20px; }
    @media print {
      body { margin: 0; }
    }
  </style>
</head>
<body>
  ${bodyContent}
</body>
</html>`

    // iframe 的 contentDocument.write() 写入的内容，浏览器打印预览无法渲染
    // 必须使用 window.open 创建顶层窗口，document.write 写入同源内容，打印预览才能正常显示
    // 窗口定位到屏幕外，用户看不到，打印完成后自动关闭
    const printWindow = window.open('about:blank', '_blank', 'left=-9999,top=-9999,width=800,height=600')
    if (!printWindow) {
      ElMessage.warning('请允许弹出窗口以使用打印功能')
      return
    }
    printWindow.document.write(fullHtml)
    printWindow.document.close()
    printWindow.onload = () => {
      setTimeout(() => {
        printWindow.print()
        printWindow.close()
      }, 300)
    }
    ElMessage.success('正在打开打印对话框...')
  } catch (error) {
    ElMessage.error('获取打印内容失败: ' + (error.response?.data?.detail || error.message))
  }
}

function makeRemarkEditable() {
  const container = previewContainerRef.value
  if (!container) return

  // 第一优先级：通过 data-row 和 data-col 属性精确匹配备注单元格 (A28 = 行28,列1)
  const remarkCell = container.querySelector('td[data-row="28"][data-col="1"]')
  if (remarkCell) {
    remarkCell.setAttribute('contenteditable', 'true')
    remarkCell.style.backgroundColor = '#fffbe6'
    remarkCell.style.border = '2px dashed #faad14'
    remarkCell.style.padding = '4px'
    remarkCell.title = '点击此处直接编辑备注内容，完成后点击下方「保存备注」按钮'
    remarkEditable.value = true
    return
  }

  // 第二优先级：回退到文本匹配（仅匹配纯"备注"文本的单元格，避免误匹配含"备注"的其他内容）
  const allCells = container.querySelectorAll('td')
  for (const cell of allCells) {
    const text = (cell.textContent || '').trim()
    if (text === '备注' || text === '备注：') {
      cell.setAttribute('contenteditable', 'true')
      cell.style.backgroundColor = '#fffbe6'
      cell.style.border = '2px dashed #faad14'
      cell.style.padding = '4px'
      cell.title = '点击此处直接编辑备注内容，完成后点击下方「保存备注」按钮'
      remarkEditable.value = true
      return
    }
  }
}

function lockRemark() {
  const container = previewContainerRef.value
  if (!container) return
  const editableCells = container.querySelectorAll('[contenteditable="true"]')
  editableCells.forEach((cell) => {
    cell.removeAttribute('contenteditable')
    cell.style.backgroundColor = ''
    cell.style.border = ''
    cell.style.padding = ''
    cell.title = ''
  })
  remarkEditable.value = false
}

async function startEditRemark() {
  await nextTick()
  makeRemarkEditable()
}

async function saveRemark() {
  const container = previewContainerRef.value
  if (!container) {
    ElMessage.error('未找到备注区域')
    return
  }

  const editableCell = container.querySelector('[contenteditable="true"]')
  if (!editableCell) {
    ElMessage.error('未找到可编辑的备注栏')
    return
  }

  let remarkContent = (editableCell.innerText || editableCell.textContent || '').trim()
  if (!remarkContent.includes('\n')) {
    const html = editableCell.innerHTML || ''
    if (/<br/i.test(html) || /<div/i.test(html) || /<p/i.test(html)) {
      remarkContent = html
        .replace(/<br\s*\/?>/gi, '\n')
        .replace(/<div[^>]*>/gi, '\n')
        .replace(/<\/div>/gi, '')
        .replace(/<p[^>]*>/gi, '\n')
        .replace(/<\/p>/gi, '')
        .replace(/<[^>]+>/g, '')
        .replace(/\n{2,}/g, '\n')
        .trim()
    }
  }

  const cleanedRemark = remarkContent.replace(/^备注[：:]\s*/, '')

  editedRemark.value = cleanedRemark

  if (filledConfigFromFill.value && filledConfigFromFill.value.单元格数据) {
    // 第一优先级：精确行号+列号匹配（A28 = 行28,列1）
    let updated = false
    for (const cell of filledConfigFromFill.value.单元格数据) {
      if (cell.行号 === 28 && cell.列号 === 1) {
        cell.显示值 = cleanedRemark ? `备注：\n${cleanedRemark}` : cleanedRemark
        cell.值 = cell.显示值
        updated = true
        break
      }
    }
    // 第二优先级：回退到文本匹配
    if (!updated) {
      for (const cell of filledConfigFromFill.value.单元格数据) {
        const 显示值 = String(cell.显示值 || '').trim()
        if (显示值 === '备注' || 显示值 === '备注：') {
          cell.显示值 = cleanedRemark ? `备注：\n${cleanedRemark}` : cleanedRemark
          cell.值 = cell.显示值
          break
        }
      }
    }
  }

  lockRemark()
  ElMessage.success('备注已保存到缓存，请点击「保存」按钮保存完整文件')
}

function getEditedRemark() {
  if (editedRemark.value) {
    return editedRemark.value
  }
  const container = previewContainerRef.value
  if (container) {
    const editableCell = container.querySelector('[contenteditable="true"]')
    if (editableCell) {
      const text = (editableCell.textContent || '').trim()
      if (text) return text
    }
  }
  return ''
}
</script>

<style scoped>
.template-operator {
  display: flex;
  flex-direction: column;
}

.operator-header {
  margin-bottom: 12px;
}

.operator-header h3 {
  margin: 0;
  font-size: 16px;
  color: #303133;
}

.operator-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.loading-state {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 20px;
  color: #909399;
  font-size: 14px;
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

.word-template-notice {
  padding: 20px 0;
}
</style>