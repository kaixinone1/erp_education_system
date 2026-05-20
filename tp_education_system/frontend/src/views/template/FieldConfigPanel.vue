<template>
  <div class="field-config-panel">
    <el-card class="config-card">
      <template #header>
        <div class="card-header">
          <span class="title">字段配置</span>
          <div class="header-actions">
            <el-button size="small" type="primary" @click="optimizeMappings">
              <el-icon><Wand2 /></el-icon>
              优化字段映射
            </el-button>
            <el-button size="small" @click="validateMappings">
              <el-icon><CheckCircle /></el-icon>
              验证映射
            </el-button>
          </div>
        </div>
      </template>

      <!-- 字段列表 -->
      <div v-if="fields.length > 0" class="field-list">
        <el-table
          :data="fields"
          border
          :height="tableHeight"
          stripe
        >
          <el-table-column
            label="序号"
            type="index"
            width="60"
          />
          <el-table-column
            label="中文字段名"
            prop="chinese_name"
            width="150"
          />
          <el-table-column
            label="英文字段名"
            width="150"
          >
            <template #default="scope">
              <el-input
                v-model="scope.row.english_name"
                size="small"
                @blur="updateField(scope.row)"
              />
            </template>
          </el-table-column>
          <el-table-column
            label="数据源表"
            width="120"
          >
            <template #default="scope">
              <el-select
                v-model="scope.row.data_table"
                size="small"
                placeholder="选择表"
                @change="updateField(scope.row)"
              >
                <el-option
                  v-for="table in availableTables"
                  :key="table.name"
                  :label="table.label"
                  :value="table.name"
                />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column
            label="数据源字段"
            width="120"
          >
            <template #default="scope">
              <el-select
                v-model="scope.row.data_field"
                size="small"
                placeholder="选择字段"
                :disabled="!scope.row.data_table"
                @change="updateField(scope.row)"
              >
                <el-option
                  v-for="field in getFieldsForTable(scope.row.data_table)"
                  :key="field.name"
                  :label="field.label"
                  :value="field.name"
                />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column
            label="转换函数"
            width="120"
          >
            <template #default="scope">
              <el-select
                v-model="scope.row.transform_func"
                size="small"
                placeholder="选择函数"
                @change="updateField(scope.row)"
              >
                <el-option label="无" value="" />
                <el-option label="日期格式化" value="format_date" />
                <el-option label="货币格式化" value="format_currency" />
                <el-option label="数字格式化" value="format_number" />
                <el-option label="百分比" value="format_percent" />
                <el-option label="转大写" value="to_upper" />
                <el-option label="转小写" value="to_lower" />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column
            label="默认值"
            width="100"
          >
            <template #default="scope">
              <el-input
                v-model="scope.row.default_value"
                size="small"
                placeholder="默认值"
                @blur="updateField(scope.row)"
              />
            </template>
          </el-table-column>
          <el-table-column
            label="置信度"
            width="100"
          >
            <template #default="scope">
              <span :class="getConfidenceClass(scope.row.mapping_confidence)">
                {{ (scope.row.mapping_confidence * 100).toFixed(0) }}%
              </span>
            </template>
          </el-table-column>
          <el-table-column
            label="状态"
            width="80"
          >
            <template #default="scope">
              <el-tag :type="getStatusType(scope.row)">
                {{ getStatusText(scope.row) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column
            label="操作"
            width="100"
          >
            <template #default="scope">
              <el-button
                size="small"
                @click="showSuggestions(scope.row)"
                :disabled="!scope.row.chinese_name"
              >
                <el-icon><Lightbulb /></el-icon>
                建议
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <div v-else class="empty-state">
        <el-alert type="info" :closable="false">
          暂无字段配置，请先导入模板
        </el-alert>
      </div>

      <!-- 待处理字段提示 -->
      <div v-if="pendingFields.length > 0" class="pending-warning">
        <el-alert
          type="warning"
          :closable="false"
        >
          <template #title>
            <span>有 {{ pendingFields.length }} 个字段需要人工处理</span>
          </template>
          <template #description>
            <span class="pending-list">{{ pendingFields.join(', ') }}</span>
          </template>
        </el-alert>
      </div>
    </el-card>

    <!-- 翻译建议弹窗 -->
    <el-dialog
      v-model="showSuggestionDialog"
      title="翻译建议"
      width="500px"
    >
      <div v-if="currentSuggestions.length > 0" class="suggestions-list">
        <div
          v-for="(suggestion, index) in currentSuggestions"
          :key="index"
          class="suggestion-item"
          @click="selectSuggestion(suggestion)"
        >
          <div class="suggestion-info">
            <span class="suggestion-name">{{ suggestion.english_name }}</span>
            <span class="suggestion-source">{{ suggestion.source }}</span>
          </div>
          <div class="suggestion-confidence">
            <el-progress
              :percentage="Math.round(suggestion.confidence * 100)"
              :show-text="false"
              :width="80"
            />
            <span class="confidence-text">{{ (suggestion.confidence * 100).toFixed(0) }}%</span>
          </div>
        </div>
      </div>
      <div v-else class="no-suggestions">
        暂无翻译建议
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Wand2, CheckCircle, Lightbulb } from '@element-plus/icons-vue'
import axios from 'axios'

const props = defineProps({
  templateId: {
    type: String,
    default: ''
  },
  initialFields: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['update'])

const fields = ref([])
const availableTables = ref([])
const tableFields = ref({})
const tableHeight = ref('400px')
const showSuggestionDialog = ref(false)
const currentField = ref(null)
const currentSuggestions = ref([])

const pendingFields = computed(() => {
  return fields.value
    .filter(f => f.mapping_confidence < 0.5 || !f.english_name)
    .map(f => f.chinese_name)
})

async function loadTables() {
  try {
    const response = await axios.get('/api/data/tables')
    if (response.data && response.data.tables) {
      availableTables.value = response.data.tables.map(t => ({
        name: t.name,
        label: t.label || t.name
      }))
    }
  } catch (error) {
    console.error('加载表列表失败:', error)
  }
}

async function loadFields(tableName) {
  if (tableFields.value[tableName]) return
  
  try {
    const response = await axios.get(`/api/data/table/${tableName}/fields`)
    if (response.data && response.data.fields) {
      tableFields.value[tableName] = response.data.fields.map(f => ({
        name: f.name,
        label: f.label || f.name
      }))
    }
  } catch (error) {
    console.error(`加载表 ${tableName} 的字段失败:`, error)
  }
}

function getFieldsForTable(tableName) {
  if (!tableName) return []
  loadFields(tableName)
  return tableFields.value[tableName] || []
}

function updateField(field) {
  emit('update', { fields: fields.value })
}

async function optimizeMappings() {
  if (!props.templateId) {
    ElMessage.warning('请先选择模板')
    return
  }
  
  try {
    const response = await axios.post(
      `/api/templates/${props.templateId}/optimize-mappings`
    )
    
    if (response.data.optimized_mappings) {
      const mappings = response.data.optimized_mappings
      fields.value = fields.value.map(f => ({
        ...f,
        ...mappings[f.chinese_name]
      }))
      ElMessage.success(response.data.message)
      emit('update', { fields: fields.value })
    }
  } catch (error) {
    ElMessage.error('优化失败：' + error.message)
  }
}

async function validateMappings() {
  try {
    const fieldMappings = {}
    fields.value.forEach(f => {
      fieldMappings[f.chinese_name] = {
        data_source: f.data_table && f.data_field ? `${f.data_table}.${f.data_field}` : null,
        transform_func: f.transform_func,
        default_value: f.default_value
      }
    })
    
    const response = await axios.post(
      `/api/templates/${props.templateId}/validate-mappings`,
      { field_mappings: fieldMappings }
    )
    
    if (response.data.valid) {
      ElMessage.success('验证通过，所有字段映射配置正确')
    } else {
      ElMessage.error(`发现 ${response.data.errors.length} 个错误`)
      response.data.errors.forEach(err => {
        console.error(`${err.field}: ${err.error}`)
      })
    }
  } catch (error) {
    ElMessage.error('验证失败：' + error.message)
  }
}

async function showSuggestions(field) {
  currentField.value = field
  try {
    const response = await axios.post(
      '/api/mapping-optimizer/suggestions',
      { chinese_name: field.chinese_name }
    )
    currentSuggestions.value = response.data.suggestions
    showSuggestionDialog.value = true
  } catch (error) {
    ElMessage.error('获取建议失败：' + error.message)
  }
}

function selectSuggestion(suggestion) {
  if (currentField.value) {
    currentField.value.english_name = suggestion.english_name
    currentField.value.mapping_confidence = suggestion.confidence
    emit('update', { fields: fields.value })
  }
  showSuggestionDialog.value = false
}

function getConfidenceClass(confidence) {
  if (confidence >= 0.8) return 'confidence-high'
  if (confidence >= 0.5) return 'confidence-medium'
  return 'confidence-low'
}

function getStatusType(field) {
  if (!field.english_name) return 'danger'
  if (field.mapping_confidence >= 0.8) return 'success'
  if (field.mapping_confidence >= 0.5) return 'warning'
  return 'info'
}

function getStatusText(field) {
  if (!field.english_name) return '未配置'
  if (field.mapping_confidence >= 0.8) return '良好'
  if (field.mapping_confidence >= 0.5) return '一般'
  return '待优化'
}

onMounted(() => {
  fields.value = props.initialFields.map(f => ({
    ...f,
    english_name: f.english_name || '',
    data_table: f.data_table || '',
    data_field: f.data_field || '',
    transform_func: f.transform_func || '',
    default_value: f.default_value || '',
    mapping_confidence: f.mapping_confidence || 0
  }))
  
  loadTables()
  
  const updateHeight = () => {
    tableHeight.value = `${window.innerHeight - 350}px`
  }
  updateHeight()
  window.addEventListener('resize', updateHeight)
})
</script>

<style scoped>
.field-config-panel {
  padding: 20px;
}

.config-card {
  min-height: calc(100vh - 120px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title {
  font-size: 18px;
  font-weight: bold;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.field-list {
  margin-top: 10px;
}

.empty-state {
  padding: 40px;
  text-align: center;
}

.pending-warning {
  margin-top: 15px;
}

.pending-list {
  display: block;
  margin-top: 5px;
  font-size: 13px;
}

.suggestions-list {
  max-height: 300px;
  overflow-y: auto;
}

.suggestion-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  border-bottom: 1px solid #e4e7ed;
  cursor: pointer;
  transition: background-color 0.2s;
}

.suggestion-item:hover {
  background-color: #f5f7fa;
}

.suggestion-info {
  flex: 1;
}

.suggestion-name {
  display: block;
  font-weight: 500;
}

.suggestion-source {
  display: block;
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.suggestion-confidence {
  display: flex;
  align-items: center;
  gap: 8px;
}

.confidence-text {
  font-size: 12px;
  color: #606266;
  width: 40px;
}

.no-suggestions {
  padding: 40px;
  text-align: center;
  color: #909399;
}

.confidence-high {
  color: #67c23a;
  font-weight: 500;
}

.confidence-medium {
  color: #e6a23c;
  font-weight: 500;
}

.confidence-low {
  color: #f56c6c;
  font-weight: 500;
}
</style>
