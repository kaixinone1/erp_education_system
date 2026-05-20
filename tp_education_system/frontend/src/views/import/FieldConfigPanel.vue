<template>
  <div class="field-config-panel">
    <div class="panel-header">
      <h3>第二步：字段配置</h3>
      <div class="header-actions">
        <el-button @click="optimizeMappings" :loading="optimizing">
          <el-icon><Wand2 /></el-icon>
          优化字段映射
        </el-button>
      </div>
    </div>
    <el-divider></el-divider>
    
    <div v-if="!fileColumns.length" class="empty-state">
      <el-empty description="请先上传文件以获取字段列表" />
    </div>
    
    <div v-else>
      <!-- 需要人工处理的字段提示 -->
      <div v-if="pendingFields.length > 0" class="pending-warning">
        <el-alert
          title="提示"
          type="warning"
          :closable="false"
          show-icon
        >
          发现 {{ pendingFields.length }} 个字段需要人工处理，请检查并手动配置：
          <el-tag v-for="field in pendingFields" :key="field.chinese_name" type="warning" size="small" class="pending-tag">
            {{ field.chinese_name }}
          </el-tag>
        </el-alert>
      </div>
      
      <!-- 字段映射表格 -->
      <el-table :data="fieldMappings" style="width: 100%" border>
        <el-table-column prop="sourceField" label="源文件字段" width="200">
          <template #default="scope">
            <el-select v-model="scope.row.sourceField" placeholder="请选择源字段" style="width: 100%;">
              <el-option
                v-for="column in fileColumns"
                :key="column"
                :label="column"
                :value="column"
              ></el-option>
            </el-select>
          </template>
        </el-table-column>
        
        <el-table-column prop="targetField" label="目标表字段" width="200">
          <template #default="scope">
            <div class="target-field-container">
              <el-select 
                v-model="scope.row.targetField" 
                placeholder="请选择目标字段" 
                style="width: 100%;"
                @change="validateField(scope.row)"
              >
                <el-option
                  v-for="field in targetFields"
                  :key="field.value"
                  :label="field.label"
                  :value="field.value"
                ></el-option>
              </el-select>
              <span 
                v-if="scope.row.validationStatus" 
                :class="['validation-badge', scope.row.validationStatus]"
                @click="showSuggestions(scope.row)"
              >
                {{ scope.row.validationStatus === 'success' ? '✓' : '⚠' }}
              </span>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="dataType" label="数据类型" width="120">
          <template #default="scope">
            <el-select v-model="scope.row.dataType" placeholder="数据类型" style="width: 100%;">
              <el-option label="字符串" value="string"></el-option>
              <el-option label="数字" value="number"></el-option>
              <el-option label="日期" value="date"></el-option>
              <el-option label="布尔值" value="boolean"></el-option>
            </el-select>
          </template>
        </el-table-column>
        
        <el-table-column prop="required" label="是否必填" width="100">
          <template #default="scope">
            <el-switch v-model="scope.row.required" />
          </template>
        </el-table-column>
        
        <el-table-column prop="confidence" label="匹配度" width="100">
          <template #default="scope">
            <el-progress 
              :percentage="scope.row.confidence ? (scope.row.confidence === 'high' ? 100 : scope.row.confidence === 'medium' ? 70 : 30) : 0"
              :stroke-width="12"
              :show-text="false"
              :color="scope.row.confidence === 'high' ? '#67c23a' : scope.row.confidence === 'medium' ? '#e6a23c' : '#f56c6c'"
            />
            <span class="confidence-text">{{ getConfidenceText(scope.row.confidence) }}</span>
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="120">
          <template #default="scope">
            <el-button
              type="text"
              size="small"
              @click="showSuggestions(scope.row)"
              title="获取翻译建议"
            >
              <el-icon><Lightbulb /></el-icon>
            </el-button>
            <el-button
              type="danger"
              size="small"
              @click="removeMapping(scope.$index)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 添加映射按钮 -->
      <div class="add-mapping">
        <el-button type="primary" @click="addMapping">
          <el-icon><Plus /></el-icon>
          添加字段映射
        </el-button>
      </div>
      
      <!-- 自动映射按钮 -->
      <div class="auto-map">
        <el-button @click="autoMapFields">
          <el-icon><Refresh /></el-icon>
          自动匹配字段
        </el-button>
      </div>
      
      <!-- 预览数据 -->
      <div v-if="sampleData.length" class="sample-data">
        <h4>文件数据预览（前5行）</h4>
        <el-table :data="sampleData" style="width: 100%" border size="small">
          <el-table-column
            v-for="column in fileColumns"
            :key="column"
            :prop="column"
            :label="column"
            :width="120"
          ></el-table-column>
        </el-table>
      </div>
    </div>
    
    <!-- 翻译建议弹窗 -->
    <el-dialog 
      v-model="suggestionDialogVisible" 
      title="翻译建议"
      width="450px"
    >
      <div v-if="currentField" class="suggestion-content">
        <div class="field-info">
          <span class="label">中文字段名：</span>
          <span class="value">{{ currentField.sourceField }}</span>
        </div>
        
        <div class="current-mapping" v-if="currentField.targetField">
          <span class="label">当前映射：</span>
          <span :class="['value', currentField.validationStatus]">{{ currentField.targetField }}</span>
          <span v-if="currentField.validationMessage" class="validation-msg">{{ currentField.validationMessage }}</span>
        </div>
        
        <div class="suggestions-list">
          <h5>建议的英文字段名：</h5>
          <el-list>
            <el-list-item 
              v-for="(suggestion, index) in suggestions" 
              :key="index"
              class="suggestion-item"
              @click="applySuggestion(suggestion)"
            >
              <span class="suggestion-name">{{ suggestion.english_name }}</span>
              <span class="suggestion-source">{{ suggestion.source }}</span>
              <span class="suggestion-confidence">{{ Math.round(suggestion.confidence * 100) }}%</span>
            </el-list-item>
          </el-list>
        </div>
        
        <div class="custom-input">
          <el-input 
            v-model="customFieldName" 
            placeholder="或手动输入英文字段名"
            @keyup.enter="applyCustomName"
          />
          <el-button @click="applyCustomName">应用</el-button>
        </div>
      </div>
    </el-dialog>
    
    <div class="panel-tip">
      <el-alert
        title="操作提示"
        type="info"
        :closable="false"
        show-icon
      >
        <ul>
          <li>请为每个需要导入的字段创建映射关系</li>
          <li>确保源字段与目标字段的数据类型匹配</li>
          <li>标记必填字段，系统会进行数据校验</li>
          <li>点击💡图标可以获取翻译建议</li>
          <li>点击"优化字段映射"按钮可以批量优化所有字段</li>
        </ul>
      </el-alert>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Plus, Refresh, Lightbulb, Wand2 } from '@element-plus/icons-vue'
import axios from 'axios'

interface FieldMapping {
  sourceField: string
  targetField: string
  dataType: string
  required: boolean
  confidence?: string
  validationStatus?: string
  validationMessage?: string
  optimized?: boolean
}

interface Suggestion {
  english_name: string
  source: string
  confidence: number
}

// 文件列
const fileColumns = ref<string[]>([])

// 目标表字段
const targetFields = ref([
  { label: 'ID', value: 'id' },
  { label: '姓名', value: 'name' },
  { label: '性别', value: 'gender' },
  { label: '年龄', value: 'age' },
  { label: '工号', value: 'employee_id' },
  { label: '部门', value: 'department' },
  { label: '职位', value: 'position' },
  { label: '联系电话', value: 'phone' },
  { label: '邮箱', value: 'email' },
  { label: '入职日期', value: 'hire_date' },
  { label: '状态', value: 'status' },
  { label: '身份证号', value: 'id_card' },
  { label: '出生日期', value: 'birth_date' },
  { label: '基本工资', value: 'base_salary' },
  { label: '绩效工资', value: 'performance_pay' },
  { label: '备注', value: 'remark' },
  { label: '创建时间', value: 'created_at' },
  { label: '更新时间', value: 'updated_at' }
])

// 字段映射
const fieldMappings = ref<FieldMapping[]>([
  {
    sourceField: '',
    targetField: '',
    dataType: 'string',
    required: false
  }
])

// 样本数据
const sampleData = ref<any[]>([])

// 需要人工处理的字段
const pendingFields = ref<any[]>([])

// 优化状态
const optimizing = ref(false)

// 翻译建议弹窗
const suggestionDialogVisible = ref(false)
const currentField = ref<FieldMapping | null>(null)
const suggestions = ref<Suggestion[]>([])
const customFieldName = ref('')

// 获取匹配度文本
const getConfidenceText = (confidence?: string) => {
  switch (confidence) {
    case 'high': return '高'
    case 'medium': return '中'
    case 'low': return '低'
    default: return '-'
  }
}

// 添加映射
const addMapping = () => {
  fieldMappings.value.push({
    sourceField: '',
    targetField: '',
    dataType: 'string',
    required: false
  })
}

// 删除映射
const removeMapping = (index: number) => {
  fieldMappings.value.splice(index, 1)
}

// 自动匹配字段
const autoMapFields = async () => {
  // 简单的自动匹配逻辑：基于字段名相似度
  const fieldMap: Record<string, string> = {
    '姓名': 'name',
    '性别': 'gender',
    '年龄': 'age',
    '工号': 'employee_id',
    '部门': 'department',
    '职位': 'position',
    '联系电话': 'phone',
    '电话': 'phone',
    '手机': 'mobile',
    '邮箱': 'email',
    '入职日期': 'hire_date',
    '状态': 'status',
    '身份证号': 'id_card',
    '身份证号码': 'id_card',
    '出生日期': 'birth_date',
    '基本工资': 'base_salary',
    '绩效工资': 'performance_pay',
    '备注': 'remark'
  }
  
  // 清空现有映射
  fieldMappings.value = []
  
  // 为每个文件字段创建映射
  fileColumns.value.forEach(column => {
    let targetField = ''
    let confidence = 'low'
    
    // 尝试精确匹配
    if (fieldMap[column]) {
      targetField = fieldMap[column]
      confidence = 'high'
    } else {
      // 尝试模糊匹配
      for (const [key, value] of Object.entries(fieldMap)) {
        if (column.includes(key)) {
          targetField = value
          confidence = 'medium'
          break
        }
      }
    }
    
    fieldMappings.value.push({
      sourceField: column,
      targetField: targetField,
      dataType: 'string',
      required: true,
      confidence
    })
  })
  
  // 验证所有字段
  await validateAllFields()
}

// 验证字段
const validateField = async (field: FieldMapping) => {
  if (!field.sourceField || !field.targetField) {
    field.validationStatus = ''
    field.validationMessage = ''
    return
  }
  
  try {
    const response = await axios.post('/api/import/validate-mapping-quality', {
      chinese_name: field.sourceField,
      english_name: field.targetField
    })
    
    field.validationStatus = response.data.is_valid ? 'success' : 'warning'
    field.validationMessage = response.data.message
  } catch (error) {
    field.validationStatus = ''
    field.validationMessage = ''
  }
}

// 验证所有字段
const validateAllFields = async () => {
  for (const field of fieldMappings.value) {
    await validateField(field)
  }
}

// 获取翻译建议
const showSuggestions = async (field: FieldMapping) => {
  if (!field.sourceField) return
  
  currentField.value = field
  customFieldName.value = field.targetField || ''
  
  try {
    const response = await axios.post('/api/import/get-translation-suggestions', {
      chinese_name: field.sourceField
    })
    suggestions.value = response.data.suggestions
  } catch (error) {
    suggestions.value = []
  }
  
  suggestionDialogVisible.value = true
}

// 应用建议
const applySuggestion = (suggestion: Suggestion) => {
  if (currentField.value) {
    currentField.value.targetField = suggestion.english_name
    currentField.value.confidence = suggestion.confidence >= 0.8 ? 'high' : suggestion.confidence >= 0.5 ? 'medium' : 'low'
    validateField(currentField.value)
  }
  suggestionDialogVisible.value = false
}

// 应用自定义名称
const applyCustomName = () => {
  if (currentField.value && customFieldName.value) {
    currentField.value.targetField = customFieldName.value
    validateField(currentField.value)
  }
  suggestionDialogVisible.value = false
}

// 批量优化字段映射
const optimizeMappings = async () => {
  optimizing.value = true
  
  try {
    const response = await axios.post('/api/import/optimize-field-names', {
      field_configs: fieldMappings.value.map(f => ({
        chinese_name: f.sourceField,
        targetField: f.targetField
      }))
    })
    
    const processedConfigs = response.data.processed_configs
    pendingFields.value = response.data.pending_fields
    
    // 更新字段映射
    processedConfigs.forEach((config: any, index: number) => {
      if (fieldMappings.value[index]) {
        if (config.english_name) {
          fieldMappings.value[index].targetField = config.english_name
          fieldMappings.value[index].optimized = config.optimized
        }
      }
    })
    
    // 验证所有字段
    await validateAllFields()
    
    // 提示用户
    if (pendingFields.value.length > 0) {
      ElMessage.warning(`优化完成！有 ${pendingFields.value.length} 个字段需要人工处理`)
    } else {
      ElMessage.success('优化完成！所有字段已优化')
    }
  } catch (error) {
    ElMessage.error('优化失败，请重试')
  } finally {
    optimizing.value = false
  }
}

// 初始化
onMounted(() => {
  // 模拟文件列（实际项目中应从后端获取）
  fileColumns.value = ['姓名', '性别', '年龄', '工号', '部门', '职位', '联系电话', '邮箱', '入职日期', '状态']
  
  // 模拟样本数据
  sampleData.value = [
    {
      '姓名': '张三',
      '性别': '男',
      '年龄': 30,
      '工号': 'T001',
      '部门': '第一中学',
      '职位': '教师',
      '联系电话': '13800138001',
      '邮箱': 'zhangsan@example.com',
      '入职日期': '2020-01-01',
      '状态': '在职'
    },
    {
      '姓名': '李四',
      '性别': '女',
      '年龄': 25,
      '工号': 'T002',
      '部门': '第二中学',
      '职位': '教师',
      '联系电话': '13800138002',
      '邮箱': 'lisi@example.com',
      '入职日期': '2021-01-01',
      '状态': '在职'
    }
  ]
  
  // 自动生成映射
  autoMapFields()
})

// 导出数据供父组件使用
defineExpose({
  fieldMappings,
  fileColumns,
  sampleData,
  addMapping,
  removeMapping,
  autoMapFields,
  optimizeMappings
})
</script>

<style scoped>
.field-config-panel {
  padding: 20px;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.empty-state {
  padding: 40px 0;
  text-align: center;
}

.pending-warning {
  margin-bottom: 20px;
}

.pending-tag {
  margin-left: 8px;
}

.target-field-container {
  position: relative;
}

.validation-badge {
  position: absolute;
  right: 5px;
  top: 50%;
  transform: translateY(-50%);
  width: 20px;
  height: 20px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  cursor: pointer;
}

.validation-badge.success {
  background-color: #67c23a;
  color: white;
}

.validation-badge.warning {
  background-color: #e6a23c;
  color: white;
}

.confidence-text {
  margin-left: 8px;
  font-size: 12px;
  color: #666;
}

.add-mapping {
  margin-top: 20px;
  margin-bottom: 20px;
}

.auto-map {
  margin-bottom: 30px;
}

.sample-data {
  margin-top: 30px;
}

.sample-data h4 {
  margin-bottom: 10px;
}

.panel-tip {
  margin-top: 30px;
}

/* 翻译建议弹窗样式 */
.suggestion-content {
  padding: 10px;
}

.field-info, .current-mapping {
  margin-bottom: 15px;
}

.field-info .label, .current-mapping .label {
  font-weight: bold;
  margin-right: 8px;
}

.field-info .value, .current-mapping .value {
  color: #666;
}

.current-mapping .value.success {
  color: #67c23a;
}

.current-mapping .value.warning {
  color: #e6a23c;
}

.validation-msg {
  display: block;
  font-size: 12px;
  color: #999;
  margin-top: 5px;
}

.suggestions-list {
  margin-bottom: 20px;
}

.suggestions-list h5 {
  margin-bottom: 10px;
}

.suggestion-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.suggestion-item:hover {
  background-color: #f5f7fa;
}

.suggestion-name {
  font-weight: bold;
}

.suggestion-source {
  font-size: 12px;
  color: #999;
}

.suggestion-confidence {
  font-size: 12px;
  color: #67c23a;
}

.custom-input {
  display: flex;
  gap: 10px;
}

.custom-input el-input {
  flex: 1;
}
</style>
