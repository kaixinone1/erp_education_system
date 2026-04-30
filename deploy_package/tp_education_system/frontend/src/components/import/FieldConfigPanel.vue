<template>
  <div class="field-config-panel">
    <!-- 配置提示区域 -->
    <el-alert
      v-if="currentConfigName"
      :title="`当前使用配置: ${currentConfigName}`"
      type="success"
      :closable="false"
      show-icon
      class="config-alert"
    />
    <el-alert
      v-else
      title="当前使用临时配置，建议保存配置以便下次使用"
      type="warning"
      :closable="false"
      show-icon
      class="config-alert"
    />

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

            <!-- 值映射 -->
            <el-table-column
              label="值映射"
              min-width="120"
            >
              <template #default="{ row }">
                <el-button
                  v-if="row.relation_type === 'to_dict'"
                  type="primary"
                  size="small"
                  @click="showValueMappingDialog(row)"
                >
                  配置映射
                </el-button>
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
        <el-table-column prop="table_name" label="英文名" min-width="120" />
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
      title="保存字段配置"
      width="550px"
    >
      <el-form :model="saveConfigForm" label-width="120px">
        <el-form-item label="保存方式" required>
          <el-radio-group v-model="saveConfigForm.save_mode">
            <el-radio label="new">新建配置</el-radio>
            <el-radio label="overwrite" :disabled="!hasExistingConfig">覆盖现有配置</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="中文表名" required>
          <el-input
            v-model="saveConfigForm.config_name"
            placeholder="请输入中文表名"
            :disabled="saveConfigForm.save_mode === 'overwrite'"
          />
        </el-form-item>
        <el-form-item label="英文表名" required>
          <el-input
            v-model="saveConfigForm.table_name"
            placeholder="系统自动生成，可手动修改"
            :disabled="saveConfigForm.save_mode === 'overwrite'"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="saveConfigDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveConfig">
          {{ saveConfigForm.save_mode === 'new' ? '新建' : '覆盖' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 值映射配置对话框 -->
    <el-dialog
      v-model="valueMappingVisible"
      title="配置值映射"
      width="600px"
    >
      <div v-if="currentMappingField">
        <p>字段: {{ currentMappingField.sourceField }}</p>
        <p>关联字典表: {{ currentMappingField.relation_table }}</p>
        <el-divider />
        <p>配置原始值到字典code的映射：</p>
        <el-table :data="valueMappingList" style="width: 100%" border>
          <el-table-column label="原始值（Excel中的值）" min-width="180">
            <template #default="{ row }">
              <el-input v-model="row.original" placeholder="如：1" size="small" />
            </template>
          </el-table-column>
          <el-table-column label="映射为（字典code）" min-width="180">
            <template #default="{ row }">
              <el-input v-model="row.mapped" placeholder="如：高层次人才" size="small" />
            </template>
          </el-table-column>
          <el-table-column label="操作" width="80">
            <template #default="{ $index }">
              <el-button type="danger" size="small" @click="removeMapping($index)">
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-button type="primary" size="small" @click="addMapping" style="margin-top: 10px;">
          添加映射
        </el-button>
      </div>
      <template #footer>
        <el-button @click="valueMappingVisible = false">取消</el-button>
        <el-button type="primary" @click="saveValueMapping">
          保存映射
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
  fileName?: string
  chineseTitle?: string
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
const loadingConfigs = ref(false)
const savedConfigs = ref<any[]>([])
const hasExistingConfig = ref(false)
const currentConfigName = ref('')
const currentConfigId = ref('')  // 当前配置ID

// 保存配置表单
const saveConfigForm = ref({
  config_name: '',
  table_name: '',
  save_mode: 'new'  // 'new' 或 'overwrite'
})

// 值映射相关状态
const valueMappingVisible = ref(false)
const currentMappingField = ref<any>(null)
const valueMappingList = ref<{original: string, mapped: string}[]>([])

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
const initFieldConfigs = async () => {
  // 首先尝试从 merged_schema_mappings.json 加载现有配置
  const existingConfig = await loadExistingFieldConfig()
  
  if (existingConfig && existingConfig.length > 0) {
    // 使用现有配置，但需要匹配当前文件的字段
    const fileFields = props.parsedData?.fields || []
    fieldConfigs.value = fileFields.map((field: string) => {
      // 查找是否有匹配的现有配置
      const existing = existingConfig.find((f: any) => 
        f.name === field || f.sourceField === field
      )
      
      if (existing) {
        return {
          sourceField: field,
          targetField: existing.targetField || existing.name || field.toLowerCase().replace(/\s+/g, '_'),
          dataType: existing.dataType || existing.type || 'VARCHAR',
          length: existing.length || 255,
          precision: existing.precision || '',
          scale: existing.scale || '',
          required: existing.required || false,
          unique: existing.unique || false,
          indexed: existing.indexed || false,
          defaultValue: existing.defaultValue || '',
          description: existing.description || existing.chinese_name || '',
          confidence: 'high',
          relation_type: existing.relation_type || 'none',
          relation_table: existing.relation_table || '',
          relation_display_field: existing.relation_display_field || 'name',
          value_mapping: existing.value_mapping || {}
        }
      }
      
      // 没有现有配置，使用默认
      return {
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
        relation_display_field: 'name',
        value_mapping: {}
      }
    })
    
    if (fieldConfigs.value.length > 0) {
      ElMessage.success('已自动加载现有字段配置，请检查并修改')
    }
  } else if (props.parsedData?.suggestedMappings) {
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
      relation_display_field: mapping.relation_display_field || 'name',
      value_mapping: mapping.value_mapping || {}
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
      relation_display_field: 'name',
      value_mapping: {}
    }))
  }
}

// 加载现有字段配置
const loadExistingFieldConfig = async (): Promise<any[]> => {
  try {
    // 从文件名推断表名
    const fileName = props.fileName || ''
    const chineseTitle = fileName.replace(/\.[^/.]+$/, '').replace(/\s+/g, '').replace(/\(\d+\)$/, '').replace(/_\d+$/, '').replace(/-\d+$/, '')
    
    // 先尝试通过中文名查找表名
    const response = await fetch('/api/table-structure/mappings')
    if (!response.ok) return []
    
    const mappings = await response.json()
    const tableInfo = mappings.mappings?.[chineseTitle]
    
    if (!tableInfo || !tableInfo.english_name) return []
    
    // 获取该表的字段配置
    const configResponse = await fetch(`/api/table-structure/${tableInfo.english_name}/field-config`)
    if (!configResponse.ok) return []
    
    const config = await configResponse.json()
    return config.fields || []
  } catch (error) {
    console.error('加载现有字段配置失败:', error)
    return []
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
            label: table.chinese_name || table.title || name
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
          label: table.chinese_name || table.title || name
        })
      }
    }
  } else if (relationType === 'to_dict') {
    // 只获取实际的数据库字典表，确保100%精准
    // 显示类型为dictionary的表，以及表名包含"dictionary"或"字典"的表
    for (const [name, table] of Object.entries(schemaMappings.value.tables)) {
      if (table.type === 'dictionary' || 
          name.toLowerCase().includes('dictionary') || 
          (table.chinese_name && table.chinese_name.includes('字典')) ||
          (table.title && table.title.includes('字典'))) {
        tables.push({
          value: name,
          label: table.chinese_name || table.title || name
        })
      }
    }
  }
  
  return tables
}

// 获取显示字段列表 - 显示中文字段名
const getDisplayFields = (tableName) => {
  const fields = []

  // 检查是否为主表或字典表（字典表的字段定义在tables中）
  if (schemaMappings.value.tables[tableName]) {
    const table = schemaMappings.value.tables[tableName]
    if (table.fields) {
      for (const field of table.fields) {
        // 跳过系统字段
        const fieldName = field.name || field.targetField || field.english_name
        if (fieldName && fieldName !== 'id' && fieldName !== 'code' && fieldName !== 'created_at' && fieldName !== 'updated_at' && fieldName !== 'import_batch') {
          // 优先使用中文字段名 (sourceField 或 chinese_name)
          const chineseName = field.sourceField || field.chinese_name || field.label
          fields.push({
            value: fieldName,
            label: chineseName || fieldName
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
const showSaveConfigDialog = async () => {
  // 从 props 获取文件中文名
  const fileChineseName = props.chineseTitle ||
                          props.fileName?.replace(/\.[^/.]+$/, '') ||
                          currentConfigName.value ||
                          ''

  // 配置名称 = 当前文件中文名
  const defaultConfigName = fileChineseName || ''

  // 获取英文表名（优先从映射表读取，否则调用后端API翻译）
  let defaultTableName = ''
  if (fileChineseName) {
    defaultTableName = await getEnglishTableName(fileChineseName)
  }

  // 检查是否已有现有配置
  const existingConfig = await checkExistingConfig(fileChineseName, defaultTableName)
  hasExistingConfig.value = existingConfig

  saveConfigForm.value = {
    config_name: defaultConfigName,
    table_name: defaultTableName,
    save_mode: existingConfig ? 'overwrite' : 'new'
  }
  saveConfigDialogVisible.value = true
}

// 检查是否已有现有配置
const checkExistingConfig = async (chineseName: string, englishName: string): Promise<boolean> => {
  try {
    if (!englishName) return false
    
    // 检查 merged_schema_mappings.json 中是否有该表的配置
    const response = await fetch(`/api/table-structure/${englishName}/field-config`)
    if (response.ok) {
      const result = await response.json()
      return result.fields && result.fields.length > 0
    }
    return false
  } catch (error) {
    console.error('检查现有配置失败:', error)
    return false
  }
}

// 获取英文表名 - 优先从统一映射表读取，否则调用后端API
const getEnglishTableName = async (chineseName: string): Promise<string> => {
  try {
    // 1. 首先尝试从 table_name_mappings.json 读取已有映射
    const response = await fetch(`/api/table-structure/mappings`)
    if (response.ok) {
      const result = await response.json()
      const mappings = result.mappings || {}
      const reverseMappings = result.reverse_mappings || {}

      // 检查是否已有映射
      if (mappings[chineseName]) {
        const existingName = mappings[chineseName].english_name
        console.log(`使用已有表名映射: ${chineseName} -> ${existingName}`)
        return existingName
      }
    }

    // 2. 如果没有已有映射，调用后端翻译API
    console.log(`调用后端翻译API: ${chineseName}`)
    const translateResponse = await fetch('/api/import/translate-table-name', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        chinese_name: chineseName,
        module_name: ''
      })
    })

    if (translateResponse.ok) {
      const result = await translateResponse.json()
      console.log(`后端翻译结果: ${chineseName} -> ${result.english_name}`)
      return result.english_name
    }
  } catch (error) {
    console.error('获取英文表名失败:', error)
  }

  // 3. 如果都失败，使用前端本地翻译作为后备
  console.warn(`使用前端本地翻译作为后备: ${chineseName}`)
  return generateEnglishTableName(chineseName)
}

// 生成英文表名 - 使用与后端一致的智能分词翻译规则
const generateEnglishTableName = (chineseName: string): string => {
  // 核心实体映射
  const coreEntities: Record<string, string> = {
    '教师基础信息': 'teacher_basic_info',
    '教师': 'teacher',
    '学生': 'student',
    '员工': 'employee',
    '党员': 'party_member',
    '人事': 'hr',
    '工资': 'salary',
    '党建': 'party_building',
    '课程': 'course',
    '年级': 'grade',
    '班级': 'class',
    '学历': 'education',
    '职称': 'title',
    '职务': 'position',
    '资格证': 'certificate',
    '考勤': 'attendance',
    '活动': 'activity',
    '部门': 'department',
    '单位': 'unit',
    '身份证': 'id_card',
    '人才': 'talent',
    '数据': 'data'
  }

  // 业务对象映射
  const businessObjects: Record<string, string> = {
    '基础信息': 'basic_info',
    '基础数据': 'basic_data',
    '个人身份': 'personal_identity',
    '职务字典': 'position_dictionary',
    '报表': 'report',
    '记录': 'record',
    '关系': 'relation',
    '字典': 'dictionary',
    '明细': 'detail',
    '考勤明细': 'attendance_detail',
    '信息': 'info',
    '数据': 'data',
    '管理': 'management',
    '统计': 'statistics',
    '汇总': 'summary',
    '分析': 'analysis',
    '档案': 'archive',
    '证书': 'certificate',
    '证明': 'proof',
    '合同': 'contract',
    '考核': 'assessment',
    '评价': 'evaluation',
    '培训': 'training',
    '调动': 'transfer',
    '离职': 'resignation',
    '退休': 'retirement',
    '招聘': 'recruitment',
    '入职': 'onboarding',
    '类型': 'type',
    '层次': 'level',
    '类别': 'category',
    '等级': 'grade'
  }

  // 检测是否是字典表
  const isDictionary = chineseName.includes('字典') ||
                       chineseName.includes('类型') ||
                       chineseName.includes('层次') ||
                       chineseName.includes('类别')

  // 智能分词翻译 - 匹配所有词汇并按位置排序
  const translatedParts: string[] = []
  const matchedPositions = new Set<number>()

  // 合并词典
  const fullDictionary: Record<string, string> = { ...coreEntities, ...businessObjects }

  // 按长度从长到短排序，优先匹配长词
  const sortedWords = Object.keys(fullDictionary).sort((a, b) => b.length - a.length)

  // 找出所有匹配的词汇及其位置
  interface Match {
    word: string
    translation: string
    position: number
    length: number
  }
  const matches: Match[] = []

  for (const word of sortedWords) {
    let pos = 0
    while (pos < chineseName.length) {
      const idx = chineseName.indexOf(word, pos)
      if (idx === -1) break

      // 检查这个位置是否已经被匹配
      let isOverlapping = false
      for (let p = idx; p < idx + word.length; p++) {
        if (matchedPositions.has(p)) {
          isOverlapping = true
          break
        }
      }

      if (!isOverlapping) {
        matches.push({
          word,
          translation: fullDictionary[word],
          position: idx,
          length: word.length
        })
        // 标记已匹配的位置
        for (let p = idx; p < idx + word.length; p++) {
          matchedPositions.add(p)
        }
      }

      pos = idx + 1
    }
  }

  // 按位置排序匹配结果
  matches.sort((a, b) => a.position - b.position)

  // 提取翻译结果
  for (const match of matches) {
    translatedParts.push(match.translation)
  }

  // 如果没有匹配到任何内容，使用默认值
  if (translatedParts.length === 0) {
    translatedParts.push('data')
  }

  // 构建英文表名
  if (isDictionary) {
    return `dict_${translatedParts.join('_')}`.toLowerCase()
  } else {
    return translatedParts.join('_').toLowerCase()
  }
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
      
      // 记录当前配置名和ID
      currentConfigName.value = configName
      currentConfigId.value = config.config_id || ''
      
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
  if (saveConfigForm.value.save_mode === 'new') {
    if (!saveConfigForm.value.config_name) {
      ElMessage.warning('请输入中文表名')
      return
    }
    if (!saveConfigForm.value.table_name) {
      ElMessage.warning('请输入英文表名')
      return
    }
  }
  
  const isOverwrite = saveConfigForm.value.save_mode === 'overwrite'
  
  const configData = {
    config_name: saveConfigForm.value.config_name,
    display_name: saveConfigForm.value.config_name,
    chinese_title: saveConfigForm.value.config_name,
    table_name: saveConfigForm.value.table_name,
    table_type: tableType.value,
    parent_table: parentTable.value,
    field_configs: fieldConfigs.value,
    overwrite: isOverwrite  // 根据 save_mode 决定是否覆盖
  }
  
  try {
    const response = await fetch('/api/field-configs/save', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(configData)
    })
    
    const result = await response.json()
    
    if (result.status === 'exists') {
      // 文件已存在，提示用户选择覆盖或修改名称
      ElMessage.warning('配置已存在，请选择"覆盖现有配置"或修改配置名称')
      return
    }
    
    if (result.status === 'name_conflict') {
      // 中文表名重复
      ElMessage.error(result.message)
      return
    }
    
    if (result.status === 'table_name_conflict') {
      // 英文表名重复
      ElMessage.error(result.message)
      return
    }
    
    if (result.status === 'success') {
      currentConfigName.value = result.config_name
      currentConfigId.value = result.config_id || ''
      ElMessage.success(result.message)
      saveConfigDialogVisible.value = false
      
      // 显示配置已保存的提示
      const actionText = isOverwrite ? '已覆盖' : '已新建'
      ElMessage.success(`配置${actionText}：中文名"${saveConfigForm.value.config_name}"，英文名"${saveConfigForm.value.table_name}"`)
    } else {
      ElMessage.error(result.message || '保存失败')
    }
  } catch (error) {
    console.error('保存配置失败:', error)
    ElMessage.error('保存配置失败')
  }
}



// 格式化日期时间
const formatDateTime = (dateStr: string) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

// 显示值映射对话框
const showValueMappingDialog = (row: any) => {
  currentMappingField.value = row
  
  // 加载已有的映射配置
  if (row.value_mapping && Object.keys(row.value_mapping).length > 0) {
    valueMappingList.value = Object.entries(row.value_mapping).map(([original, mapped]) => ({
      original,
      mapped: mapped as string
    }))
  } else {
    // 默认添加两个空映射
    valueMappingList.value = [
      { original: '', mapped: '' }
    ]
  }
  
  valueMappingVisible.value = true
}

// 添加映射
const addMapping = () => {
  valueMappingList.value.push({ original: '', mapped: '' })
}

// 删除映射
const removeMapping = (index: number) => {
  valueMappingList.value.splice(index, 1)
}

// 保存值映射
const saveValueMapping = () => {
  if (!currentMappingField.value) return
  
  // 转换为对象格式
  const mapping: Record<string, string> = {}
  valueMappingList.value.forEach(item => {
    if (item.original && item.mapped) {
      mapping[item.original] = item.mapped
    }
  })
  
  // 保存到字段配置
  currentMappingField.value.value_mapping = mapping
  
  ElMessage.success('值映射配置已保存')
  valueMappingVisible.value = false
}
</script>

<style scoped>
.field-config-panel {
  padding: 20px;
}

.config-alert {
  margin-bottom: 15px;
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
