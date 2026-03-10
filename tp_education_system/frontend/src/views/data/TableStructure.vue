<template>
  <div class="table-structure-management">
    <el-card class="box-card" style="height: calc(100vh - 120px);">
      <template #header>
        <div class="card-header">
          <span>表结构管理</span>
          <div class="header-actions">
            <el-select
              v-model="selectedTable"
              placeholder="选择数据表"
              style="width: 250px"
              @change="handleTableChange"
            >
              <el-option
              v-for="table in tableList"
              :key="table.name"
              :label="table.has_chinese_name ? table.chinese_name : table.name"
              :value="table.name"
            />
            </el-select>
            <el-button type="primary" @click="refreshTableList">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </div>
      </template>

      <div v-if="selectedTable" class="table-content">
        <!-- 表基本信息 -->
        <el-card class="info-card" shadow="never">
          <template #header>
            <div class="section-header">
              <span>表基本信息</span>
              <el-button type="primary" size="small" @click="showRenameDialog">
                修改表名
              </el-button>
            </div>
          </template>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="表名">{{ tableInfo.table_name }}</el-descriptions-item>
            <el-descriptions-item label="中文名称">{{ tableInfo.chinese_name }}</el-descriptions-item>
            <el-descriptions-item label="主键">{{ tableInfo.primary_keys?.join(', ') || '无' }}</el-descriptions-item>
            <el-descriptions-item label="字段数量">{{ tableInfo.columns?.length || 0 }}</el-descriptions-item>
          </el-descriptions>
        </el-card>

        <!-- 字段列表 -->
        <el-card class="fields-card" shadow="never" style="margin-top: 20px;">
          <template #header>
            <div class="section-header">
              <span>字段列表</span>
              <el-button type="primary" size="small" @click="showAddFieldDialog">
                <el-icon><Plus /></el-icon>
                添加字段
              </el-button>
            </div>
          </template>

          <el-table
            :data="tableInfo.columns"
            style="width: 100%"
            border
            v-loading="loading"
          >
            <el-table-column type="index" label="序号" width="60" />
            <el-table-column prop="name" label="字段名" min-width="150" />
            <el-table-column prop="chinese_name" label="中文名称" min-width="150">
              <template #default="{ row }">
                <el-input
                  v-if="row.editing"
                  v-model="row.temp_chinese_name"
                  size="small"
                />
                <span v-else>{{ getFieldChineseName(row) }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="data_type" label="数据类型" width="120" />
            <el-table-column prop="is_nullable" label="可空" width="80">
              <template #default="{ row }">
                <el-tag :type="row.is_nullable ? 'success' : 'danger'">
                  {{ row.is_nullable ? '是' : '否' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="max_length" label="长度" width="100">
              <template #default="{ row }">
                {{ row.max_length || '-' }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200" fixed="right">
              <template #default="{ row }">
                <template v-if="!isSystemField(row.name)">
                  <el-button
                    v-if="!row.editing"
                    type="primary"
                    size="small"
                    @click="startEdit(row)"
                  >
                    编辑
                  </el-button>
                  <el-button
                    v-if="row.editing"
                    type="success"
                    size="small"
                    @click="saveField(row)"
                  >
                    保存
                  </el-button>
                  <el-button
                    v-if="row.editing"
                    size="small"
                    @click="cancelEdit(row)"
                  >
                    取消
                  </el-button>
                  <el-button
                    v-if="!row.editing"
                    type="danger"
                    size="small"
                    @click="deleteField(row)"
                  >
                    删除
                  </el-button>
                </template>
                <el-tag v-else type="info" size="small">系统字段</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>

        <!-- 索引信息 -->
        <el-card class="indexes-card" shadow="never" style="margin-top: 20px;" v-if="tableInfo.indexes?.length">
          <template #header>
            <span>索引信息</span>
          </template>
          <el-table :data="tableInfo.indexes" style="width: 100%" border>
            <el-table-column type="index" label="序号" width="60" />
            <el-table-column prop="name" label="索引名" min-width="200" />
            <el-table-column prop="definition" label="定义" min-width="400" />
          </el-table>
        </el-card>

        <!-- 字段配置信息 -->
        <el-card class="field-config-card" shadow="never" style="margin-top: 20px;">
          <template #header>
            <div class="section-header">
              <span>字段属性配置 (merged_schema_mappings.json)</span>
              <div>
                <el-button type="primary" size="small" @click="loadFieldConfig" :loading="loadingFieldConfig">
                  <el-icon><Refresh /></el-icon>
                  刷新配置
                </el-button>
                <el-button type="success" size="small" @click="saveFieldConfig" :loading="savingFieldConfig">
                  <el-icon><Check /></el-icon>
                  保存配置
                </el-button>
              </div>
            </div>
          </template>
          <el-alert
            v-if="!fieldConfig.fields || fieldConfig.fields.length === 0"
            title="暂无字段配置"
            description="该表尚未在 merged_schema_mappings.json 中配置字段属性"
            type="info"
            show-icon
            :closable="false"
            style="margin-bottom: 15px;"
          />
          <el-table
            :data="fieldConfig.fields || []"
            style="width: 100%"
            border
            v-loading="loadingFieldConfig"
          >
            <el-table-column type="index" label="序号" width="60" />
            <el-table-column label="字段名" min-width="120">
              <template #default="{ row }">
                <el-input v-model="row.targetField" size="small" placeholder="字段名" />
              </template>
            </el-table-column>
            <el-table-column label="中文名称" min-width="120">
              <template #default="{ row }">
                <el-input v-model="row.sourceField" size="small" placeholder="中文名称" />
              </template>
            </el-table-column>
            <el-table-column label="数据类型" width="100">
              <template #default="{ row }">
                <el-select v-model="row.dataType" size="small" style="width: 100%">
                  <el-option label="VARCHAR" value="VARCHAR" />
                  <el-option label="INTEGER" value="INTEGER" />
                  <el-option label="DECIMAL" value="DECIMAL" />
                  <el-option label="DATE" value="DATE" />
                  <el-option label="DATETIME" value="DATETIME" />
                  <el-option label="BOOLEAN" value="BOOLEAN" />
                  <el-option label="TEXT" value="TEXT" />
                </el-select>
              </template>
            </el-table-column>
            <el-table-column label="长度" width="80">
              <template #default="{ row }">
                <el-input-number v-model="row.length" size="small" :min="1" :max="4000" style="width: 70px" />
              </template>
            </el-table-column>
            <el-table-column label="必填" width="70">
              <template #default="{ row }">
                <el-switch v-model="row.required" size="small" />
              </template>
            </el-table-column>
            <el-table-column label="唯一" width="70">
              <template #default="{ row }">
                <el-switch v-model="row.unique" size="small" />
              </template>
            </el-table-column>
            <el-table-column label="关联类型" min-width="120">
              <template #default="{ row }">
                <el-select v-model="row.relation_type" size="small" style="width: 100%" clearable placeholder="无">
                  <el-option label="字典关联 (to_dict)" value="to_dict" />
                  <el-option label="主表关联 (to_master)" value="to_master" />
                </el-select>
              </template>
            </el-table-column>
            <el-table-column label="关联表" min-width="180">
              <template #default="{ row }">
                <el-select 
                  v-model="row.relation_table" 
                  size="small" 
                  style="width: 100%" 
                  clearable 
                  placeholder="选择关联表"
                  filterable
                >
                  <el-option 
                    v-for="table in availableTables" 
                    :key="table.name" 
                    :label="table.has_chinese_name ? `${table.chinese_name} (${table.name})` : table.name"
                    :value="table.name"
                  />
                </el-select>
              </template>
            </el-table-column>
            <el-table-column label="关联字段" min-width="150">
              <template #default="{ row }">
                <el-select
                  v-model="row.relation_field"
                  size="small"
                  style="width: 100%"
                  clearable
                  placeholder="选择关联字段"
                  :disabled="!row.relation_table"
                >
                  <el-option
                    v-for="field in getTableFields(row.relation_table)"
                    :key="field.englishName"
                    :label="field.chineseName || field.englishName"
                    :value="field.englishName"
                  />
                </el-select>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100" fixed="right">
              <template #default="{ $index }">
                <el-button type="danger" size="small" @click="removeFieldConfig($index)">
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
          <div style="margin-top: 15px;">
            <el-button type="primary" size="small" @click="addFieldConfig">
              <el-icon><Plus /></el-icon>
              添加字段配置
            </el-button>
          </div>
        </el-card>
      </div>

      <el-empty v-else description="请选择要管理的数据表" />
    </el-card>

    <!-- 添加字段对话框 -->
    <el-dialog
      v-model="addFieldDialogVisible"
      title="添加字段"
      width="500px"
    >
      <el-form :model="newField" label-width="100px">
        <el-form-item label="字段名" required>
          <el-input v-model="newField.name" placeholder="请输入字段名（英文）" />
        </el-form-item>
        <el-form-item label="中文名称">
          <el-input v-model="newField.chinese_name" placeholder="请输入中文名称" />
        </el-form-item>
        <el-form-item label="数据类型" required>
          <el-select v-model="newField.type" style="width: 100%">
            <el-option label="字符串 (VARCHAR)" value="VARCHAR" />
            <el-option label="整数 (INTEGER)" value="INTEGER" />
            <el-option label="小数 (DECIMAL)" value="DECIMAL" />
            <el-option label="日期 (DATE)" value="DATE" />
            <el-option label="日期时间 (DATETIME)" value="DATETIME" />
            <el-option label="布尔值 (BOOLEAN)" value="BOOLEAN" />
            <el-option label="长文本 (TEXT)" value="TEXT" />
          </el-select>
        </el-form-item>
        <el-form-item label="长度" v-if="newField.type === 'VARCHAR'">
          <el-input-number v-model="newField.length" :min="1" :max="4000" />
        </el-form-item>
        <el-form-item label="必填">
          <el-switch v-model="newField.required" />
        </el-form-item>
        <el-form-item label="唯一">
          <el-switch v-model="newField.unique" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addFieldDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="addField">确定</el-button>
      </template>
    </el-dialog>

    <!-- 修改表名对话框 -->
    <el-dialog
      v-model="renameDialogVisible"
      title="修改表中文名称"
      width="400px"
    >
      <el-form label-width="100px">
        <el-form-item label="当前名称">
          <el-input v-model="tableInfo.chinese_name" disabled />
        </el-form-item>
        <el-form-item label="新名称" required>
          <el-input v-model="newTableName" placeholder="请输入新的中文名称" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="renameDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="renameTable">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, Plus, Check } from '@element-plus/icons-vue'

// 状态
const loading = ref(false)
const tableList = ref<any[]>([])
const selectedTable = ref('')
const tableInfo = ref<any>({})
const addFieldDialogVisible = ref(false)
const renameDialogVisible = ref(false)
const newTableName = ref('')

// 字段配置相关状态
const fieldConfig = ref<any>({
  table_name: '',
  chinese_name: '',
  fields: []
})
const loadingFieldConfig = ref(false)
const savingFieldConfig = ref(false)
const availableTables = ref<any[]>([])
// 存储表的字段信息，包含中文名和英文名 { tableName: [{englishName, chineseName}] }
const tableFieldsMap = ref<Record<string, Array<{englishName: string, chineseName: string}>>>({})

// 新字段表单
const newField = ref({
  name: '',
  chinese_name: '',
  type: 'VARCHAR',
  length: 255,
  required: false,
  unique: false
})

// 系统字段列表
const systemFields = ['id', 'created_at', 'updated_at', 'import_batch', 'code', 'teacher_id']

// 加载字段配置
const loadFieldConfig = async () => {
  if (!selectedTable.value) return
  
  loadingFieldConfig.value = true
  try {
    const response = await fetch(`/api/table-structure/${selectedTable.value}/field-config`)
    if (response.ok) {
      const result = await response.json()
      fieldConfig.value = {
        table_name: result.table_name,
        chinese_name: result.chinese_name || '',
        fields: result.fields || []
      }
    } else {
      ElMessage.error('加载字段配置失败')
    }
  } catch (error) {
    console.error('加载字段配置失败:', error)
    ElMessage.error('加载字段配置失败')
  } finally {
    loadingFieldConfig.value = false
  }
}

// 保存字段配置
const saveFieldConfig = async () => {
  if (!selectedTable.value) return
  
  savingFieldConfig.value = true
  try {
    const response = await fetch(`/api/table-structure/${selectedTable.value}/field-config`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        chinese_name: fieldConfig.value.chinese_name,
        fields: fieldConfig.value.fields
      })
    })
    
    if (response.ok) {
      ElMessage.success('字段配置保存成功')
    } else {
      const error = await response.json()
      ElMessage.error(error.detail || '保存失败')
    }
  } catch (error) {
    console.error('保存字段配置失败:', error)
    ElMessage.error('保存字段配置失败')
  } finally {
    savingFieldConfig.value = false
  }
}

// 添加字段配置
const addFieldConfig = () => {
  fieldConfig.value.fields.push({
    targetField: '',
    sourceField: '',
    dataType: 'VARCHAR',
    length: 255,
    required: false,
    unique: false,
    relation_type: 'none',
    relation_table: '',
    relation_field: ''
  })
}

// 删除字段配置
const removeFieldConfig = (index: number) => {
  ElMessageBox.confirm('确定要删除这个字段配置吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    fieldConfig.value.fields.splice(index, 1)
    ElMessage.success('已删除')
  }).catch(() => {})
}

// 监听表选择变化，自动加载字段配置
watch(selectedTable, () => {
  if (selectedTable.value) {
    loadFieldConfig()
    loadAvailableTables()
  }
})

// 加载可用表列表（用于关联表选择）
const loadAvailableTables = async () => {
  try {
    const response = await fetch('/api/table-structure/tables')
    if (response.ok) {
      const result = await response.json()
      availableTables.value = result.tables || []
      // 预加载所有表的字段
      for (const table of availableTables.value) {
        await loadTableFields(table.name)
      }
    }
  } catch (error) {
    console.error('加载可用表列表失败:', error)
  }
}

// 加载指定表的字段（从字段配置中获取中文名）
const loadTableFields = async (tableName: string) => {
  if (!tableName || tableFieldsMap.value[tableName]) return

  try {
    // 首先尝试从字段配置中获取字段信息
    const configResponse = await fetch(`/api/table-structure/${tableName}/field-config`)
    if (configResponse.ok) {
      const config = await configResponse.json()
      if (config.fields && config.fields.length > 0) {
        // 从字段配置中获取中英文对照
        const fields = config.fields.map((f: any) => ({
          englishName: f.targetField || f.name || '',
          chineseName: f.sourceField || f.chinese_name || f.targetField || f.name || ''
        })).filter((f: any) => f.englishName)
        tableFieldsMap.value[tableName] = fields
        return
      }
    }

    // 如果没有字段配置，从表结构获取
    const response = await fetch(`/api/table-structure/${tableName}`)
    if (response.ok) {
      const result = await response.json()
      const fields = result.columns?.map((col: any) => ({
        englishName: col.name,
        chineseName: col.name
      })) || []
      tableFieldsMap.value[tableName] = fields
    }
  } catch (error) {
    console.error(`加载表 ${tableName} 字段失败:`, error)
  }
}

// 获取指定表的字段列表
const getTableFields = (tableName: string): Array<{englishName: string, chineseName: string}> => {
  return tableFieldsMap.value[tableName] || []
}

// 获取表列表
const refreshTableList = async () => {
  try {
    const response = await fetch('/api/table-structure/tables')
    if (response.ok) {
      const result = await response.json()
      tableList.value = result.tables || []
    }
  } catch (error) {
    console.error('获取表列表失败:', error)
    ElMessage.error('获取表列表失败')
  }
}

// 获取表结构
const handleTableChange = async () => {
  if (!selectedTable.value) return
  
  loading.value = true
  try {
    const response = await fetch(`/api/table-structure/${selectedTable.value}`)
    if (response.ok) {
      const result = await response.json()
      // 为每个字段添加编辑状态
      result.columns = result.columns.map((col: any) => ({
        ...col,
        editing: false,
        temp_chinese_name: ''
      }))
      tableInfo.value = result
    }
  } catch (error) {
    console.error('获取表结构失败:', error)
    ElMessage.error('获取表结构失败')
  } finally {
    loading.value = false
  }
}

// 获取字段中文名称
const getFieldChineseName = (row: any) => {
  // 优先使用后端返回的 chinese_name
  if (row.chinese_name && row.chinese_name !== row.name) {
    return row.chinese_name
  }
  // 如果没有，尝试从配置中查找
  const config = tableInfo.value.config?.fields || []
  const fieldConfig = config.find((f: any) => f.name === row.name)
  return fieldConfig?.chinese_name || row.name
}

// 判断是否为系统字段
const isSystemField = (fieldName: string) => {
  return systemFields.includes(fieldName.toLowerCase())
}

// 开始编辑
const startEdit = (row: any) => {
  row.temp_chinese_name = getFieldChineseName(row)
  row.editing = true
}

// 取消编辑
const cancelEdit = (row: any) => {
  row.editing = false
  row.temp_chinese_name = ''
}

// 保存字段
const saveField = async (row: any) => {
  try {
    const response = await fetch(`/api/table-structure/${selectedTable.value}/field/${row.name}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        chinese_name: row.temp_chinese_name
      })
    })
    
    if (response.ok) {
      ElMessage.success('字段更新成功')
      row.editing = false
      handleTableChange() // 刷新数据
    } else {
      const error = await response.text()
      ElMessage.error(`更新失败: ${error}`)
    }
  } catch (error) {
    console.error('保存字段失败:', error)
    ElMessage.error('保存字段失败')
  }
}

// 删除字段
const deleteField = async (row: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除字段 "${row.name}" 吗？此操作不可恢复！`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const response = await fetch(`/api/table-structure/${selectedTable.value}/field/${row.name}`, {
      method: 'DELETE'
    })
    
    if (response.ok) {
      ElMessage.success('字段删除成功')
      handleTableChange() // 刷新数据
    } else {
      const error = await response.text()
      ElMessage.error(`删除失败: ${error}`)
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除字段失败:', error)
      ElMessage.error('删除字段失败')
    }
  }
}

// 显示添加字段对话框
const showAddFieldDialog = () => {
  newField.value = {
    name: '',
    chinese_name: '',
    type: 'VARCHAR',
    length: 255,
    required: false,
    unique: false
  }
  addFieldDialogVisible.value = true
}

// 添加字段
const addField = async () => {
  if (!newField.value.name) {
    ElMessage.warning('请输入字段名')
    return
  }
  
  try {
    const response = await fetch(`/api/table-structure/${selectedTable.value}/field`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(newField.value)
    })
    
    if (response.ok) {
      ElMessage.success('字段添加成功')
      addFieldDialogVisible.value = false
      handleTableChange() // 刷新数据
    } else {
      const error = await response.text()
      ElMessage.error(`添加失败: ${error}`)
    }
  } catch (error) {
    console.error('添加字段失败:', error)
    ElMessage.error('添加字段失败')
  }
}

// 显示重命名对话框
const showRenameDialog = () => {
  newTableName.value = tableInfo.value.chinese_name
  renameDialogVisible.value = true
}

// 修改表名
const renameTable = async () => {
  if (!newTableName.value) {
    ElMessage.warning('请输入新的表名')
    return
  }
  
  try {
    const response = await fetch(`/api/table-structure/${selectedTable.value}/rename`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ chinese_name: newTableName.value })
    })
    
    if (response.ok) {
      ElMessage.success('表名修改成功')
      renameDialogVisible.value = false
      handleTableChange() // 刷新数据
      refreshTableList() // 刷新表列表
    } else {
      const error = await response.text()
      ElMessage.error(`修改失败: ${error}`)
    }
  } catch (error) {
    console.error('修改表名失败:', error)
    ElMessage.error('修改表名失败')
  }
}

// 初始化
onMounted(() => {
  refreshTableList()
})
</script>

<style scoped>
.table-structure-management {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.info-card,
.fields-card,
.indexes-card {
  margin-bottom: 0;
}
</style>
