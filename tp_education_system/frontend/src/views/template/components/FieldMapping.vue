<template>
  <div class="field-mapping">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>字段映射配置</span>
          <el-button type="primary" size="small" @click="addMapping">添加映射</el-button>
        </div>
      </template>

      <el-table :data="mappings" border style="width: 100%">
        <el-table-column prop="field_position" label="单元格位置" width="120" />
        <el-table-column prop="field_name" label="字段名称" width="150" />
        <el-table-column label="数据源表" width="180">
          <template #default="{ row }">
            {{ getTableLabel(row.source_table) }}
          </template>
        </el-table-column>
        <el-table-column label="目标字段" width="150">
          <template #default="{ row }">
            {{ getFieldLabel(row.source_table, row.source_field) }}
          </template>
        </el-table-column>
        <el-table-column label="字典筛选" width="200">
          <template #default="{ row }">
            <span v-if="row.dict_values && row.dict_values.length > 0">
              {{ row.dict_values.join(', ') }}
            </span>
            <span v-else style="color: #999;">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="stat_type" label="统计方式" width="120" />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row, $index }">
            <el-button type="primary" size="small" @click="editMapping(row, $index)">编辑</el-button>
            <el-button type="danger" size="small" @click="removeMapping($index)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog
      v-model="editDialogVisible"
      title="编辑字段映射"
      width="700px"
      :close-on-click-modal="false"
    >
      <el-form :model="editForm" label-width="120px">
        <el-form-item label="单元格位置">
          <el-input v-model="editForm.field_position" placeholder="例如：A1, B2, C3" />
        </el-form-item>
        
        <el-form-item label="字段名称">
          <el-input v-model="editForm.field_name" placeholder="字段名称" />
        </el-form-item>
        
        <el-form-item label="数据源表">
          <el-select 
            v-model="editForm.source_table" 
            placeholder="选择数据源表" 
            style="width: 100%"
            @change="handleTableChange"
            :loading="loadingTables"
          >
            <el-option 
              v-for="table in tableList" 
              :key="table.name" 
              :label="table.label" 
              :value="table.name"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="目标字段">
          <el-select 
            v-model="editForm.source_field" 
            placeholder="选择目标字段" 
            style="width: 100%"
            @change="handleFieldChange"
            :loading="loadingFields"
            :disabled="!editForm.source_table"
          >
            <el-option 
              v-for="field in availableFields" 
              :key="field.name" 
              :label="field.label" 
              :value="field.name"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="字典筛选" v-if="hasDictionary">
          <el-select
            v-if="!useCollapse"
            v-model="editForm.dict_values"
            multiple
            collapse-tags
            collapse-tags-tooltip
            placeholder="选择字典值"
            style="width: 100%"
          >
            <el-option 
              v-for="dict in dictionaryValues" 
              :key="dict.value" 
              :label="dict.label" 
              :value="dict.value"
            />
          </el-select>
          
          <el-collapse v-else v-model="dictCollapseActive" class="dict-collapse">
            <el-collapse-item title="点击展开查看所有字典值" name="dict">
              <div v-if="loadingDictionary" style="text-align: center; padding: 20px;">
                <el-icon class="is-loading"><Loading /></el-icon>
                <span style="margin-left: 10px;">加载字典值中...</span>
              </div>
              <div v-else-if="dictionaryValues.length === 0" style="text-align: center; padding: 20px; color: #909399;">
                暂无字典值
              </div>
              <div v-else class="dict-values-container">
                <div class="dict-values-header">
                  <el-checkbox 
                    v-model="selectAllDict" 
                    @change="handleSelectAllDict"
                    :indeterminate="isDictIndeterminate"
                  >
                    全选
                  </el-checkbox>
                  <span style="color: #909399; font-size: 13px;">
                    已选 {{ editForm.dict_values.length }} / {{ dictionaryValues.length }} 项
                  </span>
                </div>
                <el-checkbox-group v-model="editForm.dict_values" class="dict-values-list">
                  <el-checkbox 
                    v-for="dict in dictionaryValues" 
                    :key="dict.value" 
                    :value="dict.value"
                    class="dict-value-item"
                  >
                    {{ dict.label }}
                  </el-checkbox>
                </el-checkbox-group>
              </div>
            </el-collapse-item>
          </el-collapse>
        </el-form-item>
        
        <el-form-item label="统计方式">
          <el-select v-model="editForm.stat_type" placeholder="统计方式" style="width: 100%">
            <el-option label="直接取值" value="直接取值" />
            <el-option label="计数" value="计数" />
            <el-option label="求和" value="求和" />
            <el-option label="平均值" value="平均值" />
            <el-option label="最大值" value="最大值" />
            <el-option label="最小值" value="最小值" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="统计公式" v-if="editForm.stat_type !== '直接取值'">
          <el-input
            v-model="editForm.stat_formula"
            type="textarea"
            :rows="3"
            placeholder="统计公式（可选）"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="editDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveEdit">保存</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, nextTick } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'

const props = defineProps({
  templateId: {
    type: Number,
    required: true
  },
  metadata: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['mapping-change'])

const mappings = ref([])
const editDialogVisible = ref(false)
const editForm = ref({
  field_name: '',
  field_position: '',
  source_table: '',
  source_field: '',
  dict_values: [],
  stat_type: '直接取值',
  stat_formula: null
})
const editIndex = ref(-1)

const tableList = ref([])
const availableFields = ref([])
const dictionaryValues = ref([])
const hasDictionary = ref(false)
const isDictTable = ref(false)
const dictTableConfig = ref(null)

const loadingTables = ref(false)
const loadingFields = ref(false)
const loadingDictionary = ref(false)

const allFieldsCache = ref({})

const dictCollapseActive = ref([])
const selectAllDict = ref(false)
const isDictIndeterminate = ref(false)
const useCollapse = ref(false)

watch(() => props.templateId, async (newVal) => {
  if (newVal) {
    await loadMappings()
  }
})

watch(mappings, (newVal) => {
  emit('mapping-change', newVal)
}, { deep: true })

onMounted(async () => {
  await loadTables()
  if (props.templateId) {
    await loadMappings()
  }
})

async function loadTables() {
  loadingTables.value = true
  try {
    const response = await axios.get('/api/template-data-fill/tables')
    if (response.data.status === 'success') {
      tableList.value = response.data.tables
    }
  } catch (error) {
    ElMessage.error('加载表列表失败：' + error.message)
  } finally {
    loadingTables.value = false
  }
}

async function loadMappings() {
  try {
    const response = await axios.get(`/api/template/field-mapping/${props.templateId}`)
    if (response.data.success && response.data.mappings.length > 0) {
      mappings.value = response.data.mappings
      
      const tables = [...new Set(mappings.value.map(m => m.source_table).filter(t => t))]
      for (const tableName of tables) {
        if (!allFieldsCache.value[tableName]) {
          await loadTableFieldsToCache(tableName)
        }
      }
    } else if (props.metadata) {
      autoGenerateMappings()
    }
  } catch (error) {
    ElMessage.error('加载字段映射失败：' + error.message)
  }
}

async function loadTableFieldsToCache(tableName) {
  try {
    const response = await axios.get(`/api/template-data-fill/table-fields/${tableName}`)
    if (response.data.status === 'success') {
      allFieldsCache.value[tableName] = response.data.fields
    }
  } catch (error) {
    console.error('加载字段列表失败：', error)
  }
}

function autoGenerateMappings() {
  if (!props.metadata || !props.metadata.cells) {
    return
  }
  
  mappings.value = []
  
  const cells = props.metadata.cells
  const addedPositions = new Set()
  
  for (const cell of cells) {
    if (cell.value && !cell.is_merged) {
      const position = getCellPosition(cell.row, cell.col)
      
      if (!addedPositions.has(position)) {
        mappings.value.push({
          field_name: cell.value,
          field_position: position,
          source_table: '',
          source_field: '',
          dict_values: [],
          stat_type: '直接取值',
          stat_formula: null
        })
        addedPositions.add(position)
      }
    }
  }
}

function getCellPosition(row, col) {
  const columnLetter = String.fromCharCode(65 + col)
  return `${columnLetter}${row + 1}`
}

function getTableLabel(tableName) {
  if (!tableName) return '-'
  const table = tableList.value.find(t => t.name === tableName)
  return table ? table.label : tableName
}

function getFieldLabel(tableName, fieldName) {
  if (!fieldName) return '-'
  
  if (tableName && allFieldsCache.value[tableName]) {
    const field = allFieldsCache.value[tableName].find(f => f.name === fieldName)
    if (field) {
      return field.label
    }
  }
  
  const field = availableFields.value.find(f => f.name === fieldName)
  return field ? field.label : fieldName
}

async function handleTableChange(tableName) {
  editForm.value.source_field = ''
  editForm.value.dict_values = []
  hasDictionary.value = false
  dictionaryValues.value = []
  isDictTable.value = false
  dictTableConfig.value = null
  
  if (!tableName) {
    availableFields.value = []
    return
  }
  
  if (allFieldsCache.value[tableName]) {
    availableFields.value = allFieldsCache.value[tableName].fields
    isDictTable.value = allFieldsCache.value[tableName].is_dict_table
    dictTableConfig.value = allFieldsCache.value[tableName].dict_table_config
  } else {
    loadingFields.value = true
    try {
      const response = await axios.get(`/api/template-data-fill/table-fields/${tableName}`)
      if (response.data.status === 'success') {
        availableFields.value = response.data.fields
        isDictTable.value = response.data.is_dict_table
        dictTableConfig.value = response.data.dict_table_config
        allFieldsCache.value[tableName] = {
          fields: response.data.fields,
          is_dict_table: response.data.is_dict_table,
          dict_table_config: response.data.dict_table_config
        }
      }
    } catch (error) {
      ElMessage.error('加载字段列表失败：' + error.message)
    } finally {
      loadingFields.value = false
    }
  }
}

async function handleFieldChange(fieldName) {
  editForm.value.dict_values = []
  hasDictionary.value = false
  dictionaryValues.value = []
  selectAllDict.value = false
  isDictIndeterminate.value = false
  dictCollapseActive.value = []
  
  if (!fieldName || !editForm.value.source_table) {
    return
  }
  
  const field = availableFields.value.find(f => f.name === fieldName)
  
  // 如果是字典表，使用字段的unique_values
  if (isDictTable.value && field && field.unique_values && field.unique_values.length > 0) {
    hasDictionary.value = true
    // 转换数据结构：{value, count} -> {value, label}
    dictionaryValues.value = field.unique_values.map(item => ({
      value: item.value,
      label: item.value,
      count: item.count
    }))
    useCollapse.value = field.unique_count > 20
    console.log(`[字典表] 字段: ${fieldName}, 唯一值数量: ${field.unique_count}, 使用${useCollapse.value ? '折叠菜单' : '下拉菜单'}`)
    return
  }
  
  // 如果字段关联了字典表，使用缓存的字典值
  if (field && field.has_dict && field.dict_values && field.dict_values.length > 0) {
    hasDictionary.value = true
    dictionaryValues.value = field.dict_values
    useCollapse.value = field.dict_count > 20
    console.log(`[缓存命中] 字段: ${fieldName}, 字典值数量: ${field.dict_count}, 使用${useCollapse.value ? '折叠菜单' : '下拉菜单'}`)
    return
  }
  
  loadingDictionary.value = true
  try {
    const response = await axios.get(
      `/api/template-data-fill/field-dictionary/${editForm.value.source_table}/${fieldName}`
    )
    if (response.data.status === 'success' && response.data.has_dictionary) {
      hasDictionary.value = true
      dictionaryValues.value = response.data.values
      useCollapse.value = dictionaryValues.value.length > 20
      console.log(`[API查询] 字段: ${fieldName}, 字典值数量: ${dictionaryValues.value.length}, 使用${useCollapse.value ? '折叠菜单' : '下拉菜单'}`)
    }
  } catch (error) {
    console.error('加载字典值失败：', error)
  } finally {
    loadingDictionary.value = false
  }
}

function handleSelectAllDict(val) {
  if (val) {
    editForm.value.dict_values = dictionaryValues.value.map(d => d.value)
  } else {
    editForm.value.dict_values = []
  }
  isDictIndeterminate.value = false
}

watch(() => editForm.value.dict_values, (newVal) => {
  if (newVal.length === 0) {
    selectAllDict.value = false
    isDictIndeterminate.value = false
  } else if (newVal.length === dictionaryValues.value.length) {
    selectAllDict.value = true
    isDictIndeterminate.value = false
  } else {
    selectAllDict.value = false
    isDictIndeterminate.value = true
  }
})

function addMapping() {
  editIndex.value = -1
  editForm.value = {
    field_name: '',
    field_position: '',
    source_table: '',
    source_field: '',
    dict_values: [],
    stat_type: '直接取值',
    stat_formula: null
  }
  hasDictionary.value = false
  dictionaryValues.value = []
  editDialogVisible.value = true
}

async function editMapping(row, index) {
  editIndex.value = index
  editForm.value = { 
    ...row,
    dict_values: row.dict_values || []
  }
  
  if (row.source_table) {
    await handleTableChange(row.source_table)
  }
  
  if (row.source_field) {
    await handleFieldChange(row.source_field)
  }
  
  editDialogVisible.value = true
}

async function saveEdit() {
  try {
    if (!editForm.value.field_name) {
      ElMessage.warning('请输入字段名称')
      return
    }
    
    if (!editForm.value.field_position) {
      ElMessage.warning('请输入单元格位置')
      return
    }
    
    if (!editForm.value.source_table) {
      ElMessage.warning('请选择数据源表')
      return
    }
    
    if (!editForm.value.source_field) {
      ElMessage.warning('请选择目标字段')
      return
    }
    
    const formData = { ...editForm.value }
    
    editDialogVisible.value = false
    await nextTick()
    
    if (editIndex.value === -1) {
      mappings.value.push(formData)
    } else {
      mappings.value[editIndex.value] = formData
    }
    
    ElMessage.success(editIndex.value === -1 ? '添加成功' : '保存成功')
    console.log('[对话框] 已关闭并保存数据')
  } catch (error) {
    console.error('保存字段映射失败：', error)
    ElMessage.error('保存失败：' + error.message)
  }
}

function removeMapping(index) {
  console.log('[删除] 准备删除索引:', index, '总数量:', mappings.value.length)
  
  if (index < 0 || index >= mappings.value.length) {
    ElMessage.error('删除失败：索引无效')
    return
  }
  
  ElMessageBox.confirm(
    '确定要删除该字段映射吗？',
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    const removed = mappings.value.splice(index, 1)
    console.log('[删除] 已删除:', removed)
    ElMessage.success('删除成功')
  }).catch(() => {
    console.log('[删除] 用户取消删除')
  })
}
</script>

<style scoped>
.field-mapping {
  margin: 20px 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.dict-collapse {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
}

.dict-values-container {
  padding: 10px;
}

.dict-values-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid #ebeef5;
}

.dict-values-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.dict-value-item {
  margin-right: 0;
  margin-bottom: 0;
}
</style>

