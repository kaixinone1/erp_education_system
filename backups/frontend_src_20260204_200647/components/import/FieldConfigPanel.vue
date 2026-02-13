<template>
  <div class="field-config-panel">
    <el-card class="panel-card">
      <template #header>
        <div class="card-header">
          <span>第二步：字段属性配置</span>
          <div class="header-actions">
            <el-button type="success" size="small" @click="showLoadConfigDialog">
              <el-icon><FolderOpened /></el-icon>
              加载配置
            </el-button>
            <el-button type="warning" size="small" @click="showSaveConfigDialog">
              <el-icon><Document /></el-icon>
              保存配置
            </el-button>
            <el-button type="info" size="small" @click="showFieldDictionary">
              <el-icon><Document /></el-icon>
              字段映射表
            </el-button>
          </div>
        </div>
      </template>

      <div class="panel-content">
        <!-- 字段配置表格 -->
        <div class="table-section">
          <el-table
            :data="fieldConfigs"
            style="width: 100%"
            border
            max-height="500px"
          >
            <!-- 原始字段名 -->
            <el-table-column
              prop="sourceField"
              label="原始字段名"
              min-width="120"
              show-overflow-tooltip
            />

            <!-- 系统字段名 -->
            <el-table-column
              label="系统字段名"
              min-width="150"
            >
              <template #default="{ row, $index }">
                <el-input
                  v-model="row.targetField"
                  placeholder="请输入系统字段名"
                  size="small"
                />
              </template>
            </el-table-column>

            <!-- 数据类型 -->
            <el-table-column
              label="数据类型"
              min-width="120"
            >
              <template #default="{ row }">
                <el-select
                  v-model="row.dataType"
                  placeholder="选择类型"
                  size="small"
                  style="width: 100%"
                >
                  <el-option label="字符串(VARCHAR)" value="VARCHAR" />
                  <el-option label="整数(INTEGER)" value="INTEGER" />
                  <el-option label="小数(DECIMAL)" value="DECIMAL" />
                  <el-option label="日期(DATE)" value="DATE" />
                  <el-option label="日期时间(DATETIME)" value="DATETIME" />
                  <el-option label="布尔值(BOOLEAN)" value="BOOLEAN" />
                  <el-option label="长文本(TEXT)" value="TEXT" />
                </el-select>
              </template>
            </el-table-column>

            <!-- 长度/精度 -->
            <el-table-column
              label="长度/精度"
              min-width="100"
            >
              <template #default="{ row }">
                <el-input
                  v-if="row.dataType === 'VARCHAR'"
                  v-model.number="row.length"
                  placeholder="长度"
                  size="small"
                  type="number"
                />
                <el-input
                  v-else-if="row.dataType === 'DECIMAL'"
                  v-model="row.precision"
                  placeholder="精度"
                  size="small"
                />
                <span v-else>-</span>
              </template>
            </el-table-column>

            <!-- 是否必填 -->
            <el-table-column
              label="必填"
              width="80"
              align="center"
            >
              <template #default="{ row }">
                <el-switch
                  v-model="row.required"
                  size="small"
                />
              </template>
            </el-table-column>

            <!-- 关联类型 -->
            <el-table-column
              label="关联类型"
              min-width="120"
            >
              <template #default="{ row }">
                <el-select
                  v-model="row.relation_type"
                  placeholder="选择关联类型"
                  size="small"
                  style="width: 100%"
                >
                  <el-option label="无关联" value="none" />
                  <el-option label="关联主表" value="to_master" />
                  <el-option label="关联字典表" value="to_dict" />
                </el-select>
              </template>
            </el-table-column>

            <!-- 关联表名 -->
            <el-table-column
              label="关联表名"
              min-width="150"
            >
              <template #default="{ row }">
                <el-select
                  v-if="row.relation_type !== 'none'"
                  v-model="row.relation_table"
                  placeholder="选择关联表"
                  size="small"
                  style="width: 100%"
                  @change="onRelationTableChange(row)"
                >
                  <el-option
                    v-for="table in getRelationTables(row.relation_type)"
                    :key="table.value"
                    :label="table.label"
                    :value="table.value"
                  />
                </el-select>
                <span v-else>-</span>
              </template>
            </el-table-column>

            <!-- 显示字段 -->
            <el-table-column
              label="显示字段"
              min-width="120"
            >
              <template #default="{ row }">
                <el-select
                  v-if="row.relation_type !== 'none' && row.relation_table"
                  v-model="row.relation_display_field"
                  placeholder="选择显示字段"
                  size="small"
                  style="width: 100%"
                >
                  <el-option
                    v-for="field in getDisplayFields(row.relation_table)"
                    :key="field.value"
                    :label="field.label"
                    :value="field.value"
                  />
                </el-select>
                <el-input
                  v-else-if="row.relation_type !== 'none'"
                  v-model="row.relation_display_field"
                  placeholder="输入显示字段名"
                  size="small"
                />
                <span v-else>-</span>
              </template>
            </el-table-column>

            <!-- 操作 -->
            <el-table-column
              label="操作"
              width="80"
              align="center"
            >
              <template #default="{ row }">
                <el-switch
                  v-model="row.required"
                  size="small"
                />
              </template>
            </el-table-column>

            <!-- 是否唯一 -->
            <el-table-column
              label="唯一"
              width="80"
              align="center"
            >
              <template #default="{ row }">
                <el-switch
                  v-model="row.unique"
                  size="small"
                />
              </template>
            </el-table-column>

            <!-- 是否索引 -->
            <el-table-column
              label="索引"
              width="80"
              align="center"
            >
              <template #default="{ row }">
                <el-switch
                  v-model="row.indexed"
                  size="small"
                />
              </template>
            </el-table-column>

            <!-- 默认值 -->
            <el-table-column
              label="默认值"
              min-width="100"
            >
              <template #default="{ row }">
                <el-input
                  v-model="row.defaultValue"
                  placeholder="默认值"
                  size="small"
                />
              </template>
            </el-table-column>

            <!-- 描述 -->
            <el-table-column
              label="描述"
              min-width="120"
            >
              <template #default="{ row }">
                <el-input
                  v-model="row.description"
                  placeholder="字段描述"
                  size="small"
                />
              </template>
            </el-table-column>

            <!-- 置信度标识 -->
            <el-table-column
              label="匹配度"
              width="90"
              align="center"
            >
              <template #default="{ row }">
                <el-tag
                  :type="getConfidenceType(row.confidence)"
                  size="small"
                >
                  {{ getConfidenceLabel(row.confidence) }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- 表类型配置 -->
        <div class="table-type-section">
          <h3>表类型配置</h3>
          <el-form :inline="true" size="small">
            <el-form-item label="表类型">
              <el-select v-model="tableType" placeholder="选择表类型" style="width: 150px">
                <el-option label="主表" value="master" />
                <el-option label="子表" value="child" />
                <el-option label="字典表" value="dictionary" />
              </el-select>
            </el-form-item>
            <el-form-item label="父表" v-if="tableType === 'child'">
              <el-select 
                v-model="parentTable" 
                placeholder="选择父表" 
                style="width: 200px"
                :loading="!availableParentTables.length"
              >
                <el-option
                  v-for="table in availableParentTables"
                  :key="table.value"
                  :label="table.label"
                  :value="table.value"
                />
                <template #empty>
                  <span style="color: #999;">暂无可用主表，请刷新页面重试</span>
                </template>
              </el-select>
            </el-form-item>
          </el-form>
        </div>

        <!-- 统计信息 -->
        <div class="statistics-section">
          <el-descriptions :column="4" border>
            <el-descriptions-item label="总字段数">{{ fieldConfigs.length }}</el-descriptions-item>
            <el-descriptions-item label="必填字段">{{ requiredFieldCount }}</el-descriptions-item>
            <el-descriptions-item label="唯一字段">{{ uniqueFieldCount }}</el-descriptions-item>
            <el-descriptions-item label="索引字段">{{ indexedFieldCount }}</el-descriptions-item>
          </el-descriptions>
        </div>

        <!-- 操作按钮 -->
        <div class="action-section">
          <el-button @click="handlePrevious">
            <el-icon><ArrowLeft /></el-icon>
            上一步
          </el-button>
          <el-button type="primary" @click="handleNextStep">
            下一步：数据预览
            <el-icon class="el-icon--right"><ArrowRight /></el-icon>
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 字段映射表弹窗 -->
    <el-dialog
      v-model="dictionaryVisible"
      title="标准字段词典"
      width="800px"
    >
      <el-table
        :data="standardFields"
        style="width: 100%"
        max-height="400px"
        border
      >
        <el-table-column prop="chineseName" label="中文名称" min-width="120" />
        <el-table-column prop="englishName" label="英文字段名" min-width="120" />
        <el-table-column prop="dataType" label="数据类型" width="100" />
        <el-table-column prop="description" label="说明" min-width="200" show-overflow-tooltip />
      </el-table>
    </el-dialog>

    <!-- 加载配置文件对话框 -->
    <el-dialog
      v-model="loadConfigDialogVisible"
      title="加载字段配置"
      width="700px"
    >
      <el-table
        :data="savedConfigs"
        style="width: 100%"
        max-height="400px"
        border
        v-loading="loadingConfigs"
      >
        <el-table-column prop="display_name" label="配置名称" min-width="150" />
        <el-table-column prop="chinese_title" label="表中文名" min-width="120" />
        <el-table-column prop="table_name" label="表名" min-width="120" />
        <el-table-column prop="field_count" label="字段数" width="80" />
        <el-table-column prop="updated_at" label="更新时间" min-width="150">
          <template #default="{ row }">
            {{ formatDateTime(row.updated_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="loadConfig(row.name)">
              加载
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button @click="loadConfigDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="refreshConfigList">
          <el-icon><Refresh /></el-icon>
          刷新列表
        </el-button>
      </template>
    </el-dialog>

    <!-- 保存配置文件对话框 -->
    <el-dialog
      v-model="saveConfigDialogVisible"
      :title="isSaveAs ? '另存为配置' : '保存字段配置'"
      width="500px"
    >
      <el-form :model="saveConfigForm" label-width="100px">
        <el-form-item label="配置名称" required>
          <el-input
            v-model="saveConfigForm.config_name"
            placeholder="请输入配置名称"
          />
        </el-form-item>
        <el-form-item label="显示名称">
          <el-input
            v-model="saveConfigForm.display_name"
            placeholder="请输入显示名称（可选）"
          />
        </el-form-item>
        <el-form-item label="表中文名">
          <el-input
            v-model="saveConfigForm.chinese_title"
            placeholder="请输入表中文名"
          />
        </el-form-item>
        <el-form-item label="表名">
          <el-input
            v-model="saveConfigForm.table_name"
            placeholder="请输入表名（英文）"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="saveConfigDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveConfig">
          {{ isSaveAs ? '另存为' : '保存' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 文件已存在确认对话框 -->
    <el-dialog
      v-model="overwriteConfirmVisible"
      title="配置文件已存在"
      width="400px"
    >
      <p>配置文件 "{{ saveConfigForm.config_name }}" 已存在。</p>
      <p>您希望：</p>
      <template #footer>
        <el-button @click="overwriteConfirmVisible = false">取消</el-button>
        <el-button type="warning" @click="saveAsNewConfig">
          另存为新文件
        </el-button>
        <el-button type="primary" @click="overwriteConfig">
          覆盖原文件
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { ArrowLeft, ArrowRight, Document, FolderOpened, Refresh } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// 组件属性
const props = defineProps<{
  parsedData?: {
    fields: string[]
    suggestedMappings: any[]
  }
}>()

// 组件事件
const emit = defineEmits(['previous-step', 'next-step', 'field-configs-updated'])

// 字段配置列表
const fieldConfigs = ref<any[]>([])

// 表类型和父表
const tableType = ref('master')
const parentTable = ref('')
const availableParentTables = ref<any[]>([])

// 字段词典弹窗显示状态
const dictionaryVisible = ref(false)

// 配置文件管理相关状态
const loadConfigDialogVisible = ref(false)
const saveConfigDialogVisible = ref(false)
const overwriteConfirmVisible = ref(false)
const loadingConfigs = ref(false)
const savedConfigs = ref<any[]>([])
const isSaveAs = ref(false)
const currentConfigName = ref('')

// 保存配置表单
const saveConfigForm = ref({
  config_name: '',
  display_name: '',
  chinese_title: '',
  table_name: ''
})

// 标准字段词典
const standardFields = ref([
  { chineseName: '姓名', englishName: 'name', dataType: 'VARCHAR', description: '人员姓名' },
  { chineseName: '性别', englishName: 'gender', dataType: 'VARCHAR', description: '性别：男/女' },
  { chineseName: '年龄', englishName: 'age', dataType: 'INTEGER', description: '年龄' },
  { chineseName: '出生日期', englishName: 'birth_date', dataType: 'DATE', description: '出生日期' },
  { chineseName: '身份证号', englishName: 'id_card', dataType: 'VARCHAR', description: '身份证号码' },
  { chineseName: '联系电话', englishName: 'phone', dataType: 'VARCHAR', description: '联系电话' },
  { chineseName: '手机号码', englishName: 'mobile', dataType: 'VARCHAR', description: '手机号码' },
  { chineseName: '电子邮箱', englishName: 'email', dataType: 'VARCHAR', description: '电子邮箱地址' },
  { chineseName: '家庭地址', englishName: 'home_address', dataType: 'VARCHAR', description: '家庭住址' },
  { chineseName: '工作单位', englishName: 'work_unit', dataType: 'VARCHAR', description: '工作单位名称' },
  { chineseName: '部门', englishName: 'department', dataType: 'VARCHAR', description: '所属部门' },
  { chineseName: '职务', englishName: 'position', dataType: 'VARCHAR', description: '职务' },
  { chineseName: '职称', englishName: 'title', dataType: 'VARCHAR', description: '职称' },
  { chineseName: '学历', englishName: 'education', dataType: 'VARCHAR', description: '学历' },
  { chineseName: '学位', englishName: 'degree', dataType: 'VARCHAR', description: '学位' },
  { chineseName: '毕业院校', englishName: 'school', dataType: 'VARCHAR', description: '毕业院校' },
  { chineseName: '专业', englishName: 'major', dataType: 'VARCHAR', description: '专业' },
  { chineseName: '入职日期', englishName: 'hire_date', dataType: 'DATE', description: '入职日期' },
  { chineseName: '参加工作时间', englishName: 'work_date', dataType: 'DATE', description: '参加工作时间' },
  { chineseName: '基本工资', englishName: 'base_salary', dataType: 'DECIMAL', description: '基本工资' },
  { chineseName: '岗位工资', englishName: 'position_salary', dataType: 'DECIMAL', description: '岗位工资' },
  { chineseName: '绩效工资', englishName: 'performance_salary', dataType: 'DECIMAL', description: '绩效工资' },
  { chineseName: '政治面貌', englishName: 'political_status', dataType: 'VARCHAR', description: '政治面貌' },
  { chineseName: '入党日期', englishName: 'party_date', dataType: 'DATE', description: '入党日期' },
  { chineseName: '备注', englishName: 'remark', dataType: 'TEXT', description: '备注信息' },
  { chineseName: '状态', englishName: 'status', dataType: 'VARCHAR', description: '状态' },
])

// 计算属性：必填字段数量
const requiredFieldCount = computed(() => {
  return fieldConfigs.value.filter(f => f.required).length
})

// 计算属性：唯一字段数量
const uniqueFieldCount = computed(() => {
  return fieldConfigs.value.filter(f => f.unique).length
})

// 计算属性：索引字段数量
const indexedFieldCount = computed(() => {
  return fieldConfigs.value.filter(f => f.indexed).length
})

// 初始化字段配置
const initFieldConfigs = () => {
  if (props.parsedData?.suggestedMappings) {
    fieldConfigs.value = props.parsedData.suggestedMappings.map((mapping: any) => ({
      sourceField: mapping.source_field,
      targetField: mapping.target_field,
      dataType: mapping.data_type || 'VARCHAR',
      length: mapping.length || 255,
      precision: mapping.precision || '',
      scale: mapping.scale || '',
      required: false,
      unique: false,
      indexed: false,
      defaultValue: '',
      description: '',
      confidence: mapping.confidence || 'low',
      relation_type: mapping.relation_type || 'none',
      relation_table: mapping.relation_table || '',
      relation_display_field: mapping.relation_display_field || 'name'
    }))
  } else if (props.parsedData?.fields) {
    // 如果没有智能映射建议，使用默认配置
    fieldConfigs.value = props.parsedData.fields.map((field: string) => ({
      sourceField: field,
      targetField: field.toLowerCase().replace(/\s+/g, '_'),
      dataType: 'VARCHAR',
      length: 255,
      precision: '',
      scale: '',
      required: false,
      unique: false,
      indexed: false,
      defaultValue: '',
      description: '',
      confidence: 'low',
      relation_type: 'none',
      relation_table: '',
      relation_display_field: 'name'
    }))
  }
}

// 获取置信度标签类型
const getConfidenceType = (confidence: string) => {
  switch (confidence) {
    case 'high':
      return 'success'
    case 'medium':
      return 'warning'
    default:
      return 'info'
  }
}

// 获取置信度标签文字
const getConfidenceLabel = (confidence: string) => {
  switch (confidence) {
    case 'high':
      return '高'
    case 'medium':
      return '中'
    default:
      return '低'
  }
}

// 显示字段词典
const showFieldDictionary = () => {
  dictionaryVisible.value = true
}

// 处理上一步
const handlePrevious = () => {
  emit('previous-step')
}

// 处理下一步
const handleNextStep = () => {
  // 验证字段配置
  const invalidFields = fieldConfigs.value.filter(f => !f.targetField.trim())
  if (invalidFields.length > 0) {
    ElMessage.warning(`有 ${invalidFields.length} 个字段未设置系统字段名`)
    return
  }

  // 检查字段名重复
  const targetFields = fieldConfigs.value.map(f => f.targetField.toLowerCase())
  const duplicates = targetFields.filter((item, index) => targetFields.indexOf(item) !== index)
  if (duplicates.length > 0) {
    ElMessage.warning(`系统字段名重复: ${duplicates.join(', ')}`)
    return
  }

  // 验证子表配置
  if (tableType.value === 'child' && !parentTable.value) {
    ElMessage.warning('请选择父表')
    return
  }

  // 发送配置完成事件
  emit('field-configs-updated', fieldConfigs.value)
  emit('next-step', { 
    fieldConfigs: fieldConfigs.value,
    tableType: tableType.value,
    parentTable: parentTable.value
  })
}

// 组件挂载时初始化
onMounted(() => {
  initFieldConfigs()
  loadSchemaMappings()
})

// 监听表类型变化，当选择子表时确保父表列表已加载
watch(tableType, (newType) => {
  if (newType === 'child' && availableParentTables.value.length === 0) {
    console.log('表类型切换为child，重新加载父表列表')
    loadSchemaMappings()
  }
})

//  schema mappings
const schemaMappings = ref({
  tables: {},
  dictionaries: {}
})

// 加载 schema mappings
const loadSchemaMappings = async () => {
  try {
    console.log('开始加载schema mappings...')
    // 添加时间戳防止缓存
    const timestamp = new Date().getTime()
    const response = await fetch(`/api/data/config/schema?t=${timestamp}`, {
      headers: {
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache'
      }
    })
    console.log('API响应状态:', response.status)
    if (response.ok) {
      const data = await response.json()
      console.log('加载到的schema mappings:', data)
      schemaMappings.value = data
      console.log('更新后的schemaMappings:', schemaMappings.value)
      
      // 加载可用的父表列表（主表）
      const parentTables = []
      for (const [name, table] of Object.entries(data.tables || {})) {
        if (table.type === 'master' || !table.type) {
          parentTables.push({
            value: name,
            label: table.title || name
          })
        }
      }
      availableParentTables.value = parentTables
      console.log('可用的父表列表:', parentTables)
    } else {
      console.error('API响应失败:', response.status, await response.text())
    }
  } catch (error) {
    console.error('加载schema mappings失败:', error)
  }
}

// 获取关联表列表
const getRelationTables = (relationType) => {
  const tables = []
  
  console.log('getRelationTables called with relationType:', relationType)
  console.log('schemaMappings.value.tables:', schemaMappings.value.tables)
  
  if (relationType === 'to_master') {
    // 获取主表
    for (const [name, table] of Object.entries(schemaMappings.value.tables || {})) {
      console.log('Checking table:', name, 'type:', table?.type)
      if (table.type === 'master') {
        tables.push({
          value: name,
          label: table.title || name
        })
      }
    }
  } else if (relationType === 'to_dict') {
    // 只获取实际的数据库字典表，确保100%精准
    // 显示类型为dictionary的表，以及表名包含"dictionary"或"字典"的表
    for (const [name, table] of Object.entries(schemaMappings.value.tables)) {
      if (table.type === 'dictionary' || 
          name.toLowerCase().includes('dictionary') || 
          table.title && table.title.includes('字典')) {
        tables.push({
          value: name,
          label: table.title || name
        })
      }
    }
  }
  
  return tables
}

// 获取显示字段列表
const getDisplayFields = (tableName) => {
  const fields = []
  
  // 检查是否为主表或字典表（字典表的字段定义在tables中）
  if (schemaMappings.value.tables[tableName]) {
    const table = schemaMappings.value.tables[tableName]
    if (table.fields) {
      for (const field of table.fields) {
        if (field.name && field.name !== 'id' && field.name !== 'code' && field.name !== 'created_at' && field.name !== 'updated_at' && field.name !== 'import_batch') {
          fields.push({
            value: field.name,
            label: field.label || field.name
          })
        }
      }
    }
  }
  // 检查是否为字典表（从dictionaries中获取额外字段）
  else if (schemaMappings.value.dictionaries[tableName]) {
    const dict = schemaMappings.value.dictionaries[tableName]
    // 字典表使用 name 字段作为显示字段
    fields.push({
      value: 'name',
      label: '名称'
    })
    // 如果有其他字段，也添加进来
    if (dict.items && dict.items.length > 0 && dict.items[0]) {
      for (const key of Object.keys(dict.items[0])) {
        if (key !== 'code' && key !== 'name' && key !== 'sort_order') {
          fields.push({
            value: key,
            label: key
          })
        }
      }
    }
  }
  
  // 如果没有字段，添加默认的 name 字段
  if (fields.length === 0) {
    fields.push({
      value: 'name',
      label: '名称'
    })
  }
  
  return fields
}

// 处理关联表变化
const onRelationTableChange = (row) => {
  if (row.relation_table) {
    const fields = getDisplayFields(row.relation_table)
    if (fields.length > 0 && !row.relation_display_field) {
      row.relation_display_field = fields[0]
    }
  }
}

// ============ 配置文件管理功能 ============

// 显示加载配置对话框
const showLoadConfigDialog = () => {
  loadConfigDialogVisible.value = true
  refreshConfigList()
}

// 显示保存配置对话框
const showSaveConfigDialog = () => {
  isSaveAs.value = false
  saveConfigForm.value = {
    config_name: currentConfigName.value || '',
    display_name: '',
    chinese_title: '',
    table_name: ''
  }
  saveConfigDialogVisible.value = true
}

// 刷新配置文件列表
const refreshConfigList = async () => {
  loadingConfigs.value = true
  try {
    const response = await fetch('/api/field-configs/list')
    if (response.ok) {
      const result = await response.json()
      savedConfigs.value = result.configs || []
    } else {
      ElMessage.error('获取配置文件列表失败')
    }
  } catch (error) {
    console.error('获取配置文件列表失败:', error)
    ElMessage.error('获取配置文件列表失败')
  } finally {
    loadingConfigs.value = false
  }
}

// 加载配置
const loadConfig = async (configName: string) => {
  try {
    const response = await fetch(`/api/field-configs/${configName}`)
    if (response.ok) {
      const config = await response.json()
      
      // 加载字段配置
      if (config.field_configs && config.field_configs.length > 0) {
        fieldConfigs.value = config.field_configs
      }
      
      // 加载表类型和父表
      if (config.table_type) {
        tableType.value = config.table_type
      }
      if (config.parent_table) {
        parentTable.value = config.parent_table
      }
      
      // 记录当前配置名
      currentConfigName.value = configName
      
      ElMessage.success(`配置 "${config.display_name || configName}" 加载成功`)
      loadConfigDialogVisible.value = false
    } else {
      ElMessage.error('加载配置失败')
    }
  } catch (error) {
    console.error('加载配置失败:', error)
    ElMessage.error('加载配置失败')
  }
}

// 保存配置
const saveConfig = async () => {
  if (!saveConfigForm.value.config_name) {
    ElMessage.warning('请输入配置名称')
    return
  }
  
  const configData = {
    config_name: saveConfigForm.value.config_name,
    display_name: saveConfigForm.value.display_name || saveConfigForm.value.config_name,
    chinese_title: saveConfigForm.value.chinese_title,
    table_name: saveConfigForm.value.table_name,
    table_type: tableType.value,
    parent_table: parentTable.value,
    field_configs: fieldConfigs.value,
    overwrite: !isSaveAs.value
  }
  
  try {
    const url = isSaveAs.value ? '/api/field-configs/save-as' : '/api/field-configs/save'
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(configData)
    })
    
    const result = await response.json()
    
    if (result.status === 'exists') {
      // 文件已存在，显示确认对话框
      overwriteConfirmVisible.value = true
      return
    }
    
    if (result.status === 'success') {
      currentConfigName.value = result.config_name
      ElMessage.success(result.message)
      saveConfigDialogVisible.value = false
    } else {
      ElMessage.error(result.message || '保存失败')
    }
  } catch (error) {
    console.error('保存配置失败:', error)
    ElMessage.error('保存配置失败')
  }
}

// 覆盖原文件
const overwriteConfig = async () => {
  const configData = {
    config_name: saveConfigForm.value.config_name,
    display_name: saveConfigForm.value.display_name || saveConfigForm.value.config_name,
    chinese_title: saveConfigForm.value.chinese_title,
    table_name: saveConfigForm.value.table_name,
    table_type: tableType.value,
    parent_table: parentTable.value,
    field_configs: fieldConfigs.value,
    overwrite: true
  }
  
  try {
    const response = await fetch('/api/field-configs/save', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(configData)
    })
    
    const result = await response.json()
    
    if (result.status === 'success') {
      currentConfigName.value = result.config_name
      ElMessage.success(result.message)
      saveConfigDialogVisible.value = false
      overwriteConfirmVisible.value = false
    } else {
      ElMessage.error(result.message || '保存失败')
    }
  } catch (error) {
    console.error('保存配置失败:', error)
    ElMessage.error('保存配置失败')
  }
}

// 另存为新文件
const saveAsNewConfig = () => {
  isSaveAs.value = true
  overwriteConfirmVisible.value = false
  saveConfigDialogVisible.value = true
  // 清空配置名，让用户输入新的名称
  saveConfigForm.value.config_name = ''
  ElMessage.info('请输入新的配置名称')
}

// 格式化日期时间
const formatDateTime = (dateStr: string) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}
</script>

<style scoped>
.field-config-panel {
  padding: 20px;
}

.panel-card {
  min-height: 600px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 16px;
  font-weight: 600;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.panel-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.table-section {
  width: 100%;
}

.statistics-section {
  margin-top: 10px;
}

.action-section {
  display: flex;
  justify-content: space-between;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}
</style>
