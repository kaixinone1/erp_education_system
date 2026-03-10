<template>
  <div class="intermediate-table-container">
    <div class="header">
      <h2>中间表管理</h2>
      <el-button type="primary" @click="handleAdd">
        <el-icon><Plus /></el-icon>新建中间表
      </el-button>
    </div>

    <el-table :data="tableData" v-loading="loading" border stripe>
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="table_name_cn" label="表中文名" min-width="150" />
      <el-table-column prop="table_name" label="表英文名" min-width="180" />
      <el-table-column label="字段数量" width="100" align="center">
        <template #default="{ row }">
          <el-tag>{{ row.fields ? row.fields.length : 0 }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
      <el-table-column label="状态" width="80" align="center">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'danger'">
            {{ row.is_active ? '启用' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="180" fixed="right">
        <template #default="{ row }">
          <el-button size="small" type="primary" @click="handleEdit(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑中间表' : '新建中间表'"
      width="1100px"
      destroy-on-close
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="表中文名" prop="table_name_cn">
              <el-input 
                v-model="form.table_name_cn" 
                placeholder="如：退休呈报数据"
                @blur="autoTranslateTableName"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="表英文名" prop="table_name">
              <el-input v-model="form.table_name" placeholder="如：retirement_report" :disabled="isEdit" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" rows="2" placeholder="中间表描述" />
        </el-form-item>

        <el-form-item label="是否启用">
          <el-switch v-model="form.is_active" />
        </el-form-item>

        <el-form-item label="字段设计" required>
          <!-- 三部分字段选择器 -->
          <div class="field-selector-container">
            <!-- 第一部分：数据源表列表 -->
            <div class="source-tables-section">
              <div class="section-title">第一步：选择数据源表</div>
              <el-input
                v-model="tableSearchText"
                placeholder="搜索表名"
                size="small"
                clearable
                style="margin-bottom: 10px"
              />
              <div class="table-list">
                <div
                  v-for="tableCn in filteredTables"
                  :key="tableCn"
                  class="table-item"
                  :class="{ active: selectedSourceTable === (chineseToTableMap[tableCn] || tableCn) }"
                  @click="selectSourceTable(tableCn)"
                >
                  <el-icon><Document /></el-icon>
                  <span>{{ tableCn }}</span>
                  <span class="table-en-name">{{ chineseToTableMap[tableCn] }}</span>
                </div>
              </div>
            </div>

            <!-- 第二部分：字段列表 -->
            <div class="fields-section">
              <div class="section-title">第二步：选择字段（双击添加）</div>
              <el-input
                v-model="fieldSearchText"
                placeholder="搜索字段"
                size="small"
                clearable
                style="margin-bottom: 10px"
              />
              <div class="field-list">
                <div
                  v-for="field in filteredSourceFields"
                  :key="field.name"
                  class="field-item"
                  :class="{ disabled: isFieldAlreadySelected(field.name) }"
                  @dblclick="addFieldToTarget(field)"
                  :title="isFieldAlreadySelected(field.name) ? '已添加' : '双击添加到中间表'"
                >
                  <el-icon><ArrowRight /></el-icon>
                  <span>{{ field.name }}</span>
                  <span class="field-type">({{ field.type }})</span>
                </div>
                <el-empty v-if="!selectedSourceTable" description="请先选择数据源表" :image-size="60" />
                <el-empty v-else-if="filteredSourceFields.length === 0" description="该表没有字段" :image-size="60" />
              </div>
            </div>

            <!-- 第三部分：待建中间表 -->
            <div class="target-table-section">
              <div class="section-title">第三步：待建中间表字段</div>
              <div class="target-field-list">
                <div
                  v-for="(field, index) in form.fields"
                  :key="index"
                  class="target-field-item"
                >
                  <div class="field-header">
                    <span class="field-index">{{ index + 1 }}</span>
                    <el-button type="danger" text size="small" @click="removeField(index)">
                      <el-icon><Delete /></el-icon>
                    </el-button>
                  </div>
                  <el-form-item label="字段名" class="compact-form-item">
                    <el-input v-model="field.name" size="small" placeholder="字段名" />
                  </el-form-item>
                  <el-form-item label="中文标签" class="compact-form-item">
                    <el-input v-model="field.label" size="small" placeholder="中文标签" />
                  </el-form-item>
                  <el-form-item label="字段类型" class="compact-form-item">
                    <el-select v-model="field.type" size="small" style="width: 100%">
                      <el-option label="字符串 (varchar)" value="varchar" />
                      <el-option label="整数 (integer)" value="integer" />
                      <el-option label="浮点数 (numeric)" value="numeric" />
                      <el-option label="日期 (date)" value="date" />
                      <el-option label="时间戳 (timestamp)" value="timestamp" />
                      <el-option label="布尔值 (boolean)" value="boolean" />
                      <el-option label="文本 (text)" value="text" />
                    </el-select>
                  </el-form-item>
                  <el-form-item label="来源表" class="compact-form-item">
                    <el-input v-model="field.source_table" size="small" placeholder="来源表" disabled />
                  </el-form-item>
                </div>
                <el-empty v-if="form.fields.length === 0" description="从左侧双击字段添加" :image-size="60" />
              </div>
            </div>
          </div>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Document, ArrowRight, Delete } from '@element-plus/icons-vue'

const API_BASE = '/api/intermediate-table'

const loading = ref(false)
const submitting = ref(false)
const tableData = ref<any[]>([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref()

// 数据源相关
const allTables = ref<string[]>([])
const allTableFields = ref<Record<string, any[]>>({})
const selectedSourceTable = ref('') // 存储英文表名
const tableSearchText = ref('')
const fieldSearchText = ref('')
const tableToChineseMap = ref<Record<string, string>>({}) // 英文表名 -> 中文表名
const chineseToTableMap = ref<Record<string, string>>({}) // 中文表名 -> 英文表名

const form = ref({
  id: null,
  table_name: '',
  table_name_cn: '',
  description: '',
  fields: [] as any[],
  is_active: true
})

const rules = {
  table_name_cn: [{ required: true, message: '请输入表中文名', trigger: 'blur' }],
  table_name: [{ required: true, message: '请输入表英文名', trigger: 'blur' }]
}

// 过滤后的表列表
const filteredTables = computed(() => {
  if (!tableSearchText.value) return allTables.value
  const search = tableSearchText.value.toLowerCase()
  // 支持中文和英文搜索
  return allTables.value.filter(t => {
    const tableEn = chineseToTableMap.value[t] || t
    return t.toLowerCase().includes(search) || tableEn.toLowerCase().includes(search)
  })
})

// 过滤后的字段列表 - 根据英文表名获取字段
const filteredSourceFields = computed(() => {
  if (!selectedSourceTable.value) return []
  // 使用英文表名从 allTableFields 中获取字段列表
  const fields = allTableFields.value[selectedSourceTable.value] || []
  if (!fieldSearchText.value) return fields
  const search = fieldSearchText.value.toLowerCase()
  return fields.filter(f => f.name.toLowerCase().includes(search))
})

// 加载所有数据
const loadData = async () => {
  loading.value = true
  try {
    const res = await fetch(`${API_BASE}/list`)
    const result = await res.json()
    if (result.status === 'success') {
      tableData.value = result.data
    }
  } catch (e: any) {
    ElMessage.error('加载数据失败: ' + e.message)
  } finally {
    loading.value = false
  }
}

// 加载所有表和字段
const loadAllTablesAndFields = async () => {
  try {
    const res = await fetch(`${API_BASE}/all-fields`)
    const result = await res.json()
    if (result.status === 'success') {
      // 按表分组字段，同时收集中文表名
      const grouped: Record<string, any[]> = {}
      const tableNames = new Map<string, string>() // table_name -> table_name_cn
      
      for (const field of result.data) {
        tableNames.set(field.table, field.table_name_cn || field.table)
        if (!grouped[field.table]) {
          grouped[field.table] = []
        }
        grouped[field.table].push({
          name: field.value,
          label: field.label,
          type: 'varchar' // 默认类型
        })
      }
      
      // 使用中文表名
      allTables.value = Array.from(tableNames.entries())
        .map(([name, nameCn]) => nameCn)
        .sort()
      
      // 保存表名映射
      allTableFields.value = grouped
      tableToChineseMap.value = Object.fromEntries(tableNames.entries())
      chineseToTableMap.value = Object.fromEntries(
        Array.from(tableNames.entries()).map(([en, cn]) => [cn, en])
      )
    }
  } catch (e) {
    console.error('加载表和字段失败', e)
  }
}

// 自动翻译表名
const autoTranslateTableName = async () => {
  if (!form.value.table_name_cn || form.value.table_name) return
  
  try {
    const res = await fetch(`/api/intermediate-table/translate-name`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: form.value.table_name_cn })
    })
    const result = await res.json()
    if (result.status === 'success') {
      form.value.table_name = result.data
    }
  } catch (e) {
    console.error('翻译失败', e)
  }
}

// 选择数据源表
const selectSourceTable = (tableCn: string) => {
  const tableEn = chineseToTableMap.value[tableCn] || tableCn
  selectedSourceTable.value = tableEn
  fieldSearchText.value = ''
}

// 检查字段是否已添加
const isFieldAlreadySelected = (fieldName: string) => {
  return form.value.fields.some(f => f.name === fieldName)
}

// 添加字段到目标表
const addFieldToTarget = (field: any) => {
  if (isFieldAlreadySelected(field.name)) {
    ElMessage.warning('该字段已添加')
    return
  }
  
  form.value.fields.push({
    name: field.name,
    label: field.label,
    type: field.type,
    source_table: selectedSourceTable.value
  })
  
  ElMessage.success(`已添加字段: ${field.name}`)
}

// 删除字段
const removeField = (index: number) => {
  form.value.fields.splice(index, 1)
}

// 新建
const handleAdd = () => {
  isEdit.value = false
  form.value = {
    id: null,
    table_name: '',
    table_name_cn: '',
    description: '',
    fields: [],
    is_active: true
  }
  selectedSourceTable.value = ''
  dialogVisible.value = true
}

// 编辑
const handleEdit = (row: any) => {
  isEdit.value = true
  form.value = {
    id: row.id,
    table_name: row.table_name,
    table_name_cn: row.table_name_cn,
    description: row.description || '',
    fields: row.fields || [],
    is_active: row.is_active
  }
  selectedSourceTable.value = ''
  dialogVisible.value = true
}

// 删除
const handleDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm(`确定要删除中间表 "${row.table_name_cn}" 吗？`, '提示', {
      type: 'warning'
    })
    await fetch(`${API_BASE}/${row.id}`, { method: 'DELETE' })
    ElMessage.success('删除成功')
    loadData()
  } catch (e: any) {
    if (e !== 'cancel') {
      ElMessage.error('删除失败: ' + e.message)
    }
  }
}

// 提交
const handleSubmit = async () => {
  await formRef.value?.validate()
  
  if (form.value.fields.length === 0) {
    ElMessage.error('请至少添加一个字段')
    return
  }
  
  submitting.value = true
  try {
    const data = { ...form.value }
    if (isEdit.value) {
      await fetch(`${API_BASE}/${data.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      })
      ElMessage.success('更新成功')
    } else {
      await fetch(`${API_BASE}/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      })
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    loadData()
  } catch (e: any) {
    ElMessage.error('操作失败: ' + e.message)
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  loadData()
  loadAllTablesAndFields()
})
</script>

<style scoped>
.intermediate-table-container {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header h2 {
  margin: 0;
}

/* 三部分字段选择器样式 */
.field-selector-container {
  display: flex;
  gap: 15px;
  height: 450px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  padding: 15px;
  background: #f5f7fa;
}

.source-tables-section,
.fields-section,
.target-table-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: white;
  border-radius: 4px;
  padding: 10px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.section-title {
  font-weight: bold;
  margin-bottom: 10px;
  color: #303133;
  font-size: 14px;
}

/* 表列表样式 */
.table-list {
  flex: 1;
  overflow-y: auto;
}

.table-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 10px;
  cursor: pointer;
  border-radius: 4px;
  transition: background 0.2s;
}

.table-item:hover {
  background: #ecf5ff;
}

.table-item.active {
  background: #409eff;
  color: white;
}

.table-en-name {
  font-size: 12px;
  color: #909399;
  margin-left: auto;
}

/* 字段列表样式 */
.field-list {
  flex: 1;
  overflow-y: auto;
}

.field-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 10px;
  cursor: pointer;
  border-radius: 4px;
  transition: background 0.2s;
}

.field-item:hover {
  background: #ecf5ff;
}

.field-item.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.field-type {
  font-size: 12px;
  color: #909399;
}

/* 目标表字段样式 */
.target-field-list {
  flex: 1;
  overflow-y: auto;
}

.target-field-item {
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 10px;
  margin-bottom: 10px;
  background: #fafafa;
}

.field-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.field-index {
  background: #409eff;
  color: white;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
}

.compact-form-item {
  margin-bottom: 8px;
}

.compact-form-item :deep(.el-form-item__label) {
  font-size: 12px;
  padding-right: 8px;
}
</style>
