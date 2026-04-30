<template>
  <div class="aggregate-query-page">
    <el-card class="page-card">
      <template #header>
        <div class="card-header">
          <h2>聚合查询</h2>
          <el-button type="primary" @click="showTagDialog = true">
            <el-icon><PriceTag /></el-icon>
            标签筛选 {{ selectedTags.length > 0 ? `(${selectedTags.length})` : '' }}
          </el-button>
        </div>
      </template>

      <!-- 第一行：操作按钮 -->
      <div class="action-row">
        <el-button type="primary" size="large" @click="executeQuery" :loading="querying" :disabled="queryFields.length === 0">
          <el-icon><Search /></el-icon>
          查询数据
        </el-button>
        <el-button type="success" size="large" @click="exportExcel" :loading="exporting" :disabled="queryResult.length === 0">
          <el-icon><Download /></el-icon>
          导出Excel
        </el-button>
      </div>

      <!-- 第二行：表选择和字段工作区 -->
      <el-row :gutter="20" class="workspace-row">
        <!-- 左侧：表选择 + 字段选择 -->
        <el-col :span="6">
          <el-card shadow="hover" class="table-field-panel">
            <!-- 表选择 -->
            <div class="table-selector">
              <span class="label">选择表名：</span>
              <el-select v-model="selectedTable" placeholder="请选择表" @change="handleTableChange">
                <el-option v-for="table in tableList" :key="table.name" :label="table.label" :value="table.name" />
              </el-select>
            </div>

            <!-- 字段选择 -->
            <div v-if="tableFields.length > 0" class="field-selector">
              <div class="field-header">
                <span class="label">选择字段：</span>
                <el-button type="primary" size="small" @click="addSelectedFields" :disabled="selectedFields.length === 0">
                  添加到工作区
                </el-button>
              </div>
              <el-checkbox-group v-model="selectedFields" class="field-list">
                <el-checkbox v-for="field in tableFields" :key="field.name" :value="field.name" class="field-item">
                  {{ field.label }}
                </el-checkbox>
              </el-checkbox-group>
            </div>
          </el-card>
        </el-col>

        <!-- 右侧：工作区 -->
        <el-col :span="18">
          <el-card shadow="hover" class="workspace-panel">
            <template #header>
              <div class="panel-header">
                <span>工作区（已选字段）</span>
                <el-button type="danger" size="small" @click="clearFields" :disabled="queryFields.length === 0">清空</el-button>
              </div>
            </template>

            <div class="workspace-list">
              <div v-for="(field, index) in queryFields" :key="index" class="workspace-item">
                <span class="field-order">{{ index + 1 }}</span>
                <span class="field-label">{{ field.label }}</span>
                <span class="field-table">({{ field.tableLabel }})</span>
                <el-button link type="danger" size="small" @click="removeField(index)">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </div>
            </div>

            <el-empty v-if="queryFields.length === 0" description="请从左侧选择表和字段" :image-size="60" />
          </el-card>
        </el-col>
      </el-row>

      <!-- 查询结果 -->
      <el-card shadow="hover" class="result-panel" v-if="queryResult.length > 0">
        <template #header>
          <div class="panel-header">
            <span>查询结果 ({{ queryResult.length }} 条)</span>
          </div>
        </template>
        <el-table :data="queryResult.slice(0, 100)" max-height="400" size="small">
          <el-table-column v-for="col in resultColumns" :key="col" :prop="col" :label="col" />
        </el-table>
        <div v-if="queryResult.length > 100" class="result-tip">
          还有 {{ queryResult.length - 100 }} 条数据，请导出查看全部
        </div>
      </el-card>
    </el-card>

    <!-- 标签筛选弹窗 -->
    <el-dialog v-model="showTagDialog" title="标签筛选（多选）" width="500px">
      <el-checkbox-group v-model="selectedTags" class="tag-list">
        <el-checkbox v-for="tag in tagList" :key="tag.id" :value="tag.name" class="tag-item">
          {{ tag.name }}
        </el-checkbox>
      </el-checkbox-group>
      <template #footer>
        <el-button @click="showTagDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmTags">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Download, Delete, PriceTag } from '@element-plus/icons-vue'

const tableList = ref<{name: string, label: string}[]>([])
const selectedTable = ref('')
const tableFields = ref<{name: string, label: string, type: string}[]>([])
const selectedFields = ref<string[]>([])
const queryFields = ref<{name: string, label: string, table: string, tableLabel: string}[]>([])
const tagList = ref<{id: number, name: string}[]>([])
const selectedTags = ref<string[]>([])
const showTagDialog = ref(false)
const querying = ref(false)
const exporting = ref(false)
const queryResult = ref<any[]>([])

const resultColumns = computed(() => {
  // 使用用户选择的字段顺序
  return queryFields.value.map(f => f.label)
})

onMounted(async () => {
  await loadTables()
  await loadTags()
})

const loadTables = async () => {
  try {
    const response = await fetch('/api/aggregate-query/tables')
    const result = await response.json()
    if (result.status === 'success') {
      tableList.value = result.tables
    }
  } catch (error) {
    console.error('加载表列表失败:', error)
  }
}

const loadTags = async () => {
  try {
    const response = await fetch('/api/aggregate-query/tags')
    const result = await response.json()
    if (result.status === 'success') {
      tagList.value = result.tags
    }
  } catch (error) {
    console.error('加载标签列表失败:', error)
  }
}

const handleTableChange = async () => {
  selectedFields.value = []
  if (!selectedTable.value) {
    tableFields.value = []
    return
  }
  
  try {
    const response = await fetch('/api/aggregate-query/fields', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ table_name: selectedTable.value })
    })
    const result = await response.json()
    if (result.status === 'success') {
      tableFields.value = result.fields
    }
  } catch (error) {
    console.error('加载字段列表失败:', error)
  }
}

const addSelectedFields = () => {
  const tableInfo = tableList.value.find(t => t.name === selectedTable.value)
  for (const fieldName of selectedFields.value) {
    const fieldInfo = tableFields.value.find(f => f.name === fieldName)
    if (fieldInfo && !queryFields.value.find(f => f.name === fieldName && f.table === selectedTable.value)) {
      queryFields.value.push({
        name: fieldName,
        label: fieldInfo.label,
        table: selectedTable.value,
        tableLabel: tableInfo?.label || selectedTable.value
      })
    }
  }
  selectedFields.value = []
}

const removeField = (index: number) => {
  queryFields.value.splice(index, 1)
}

const clearFields = () => {
  queryFields.value = []
  queryResult.value = []
}

const confirmTags = () => {
  showTagDialog.value = false
}

const executeQuery = async () => {
  if (queryFields.value.length === 0) {
    ElMessage.warning('请先选择字段')
    return
  }
  
  querying.value = true
  try {
    const tableFieldsMap: Record<string, {name: string, label: string}[]> = {}
    for (const field of queryFields.value) {
      if (!tableFieldsMap[field.table]) {
        tableFieldsMap[field.table] = []
      }
      tableFieldsMap[field.table].push({ name: field.name, label: field.label })
    }
    
    const tables = Object.entries(tableFieldsMap).map(([table_name, fields]) => ({
      table_name,
      fields
    }))
    
    const response = await fetch('/api/aggregate-query/query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        tables,
        tags: selectedTags.value.length > 0 ? selectedTags.value : undefined
      })
    })
    
    const result = await response.json()
    if (result.status === 'success') {
      queryResult.value = result.data
      ElMessage.success(`查询成功，共 ${result.data.length} 条数据`)
    } else {
      ElMessage.error(result.detail || '查询失败')
    }
  } catch (error: any) {
    console.error('查询失败:', error)
    ElMessage.error(error.message || '查询失败')
  } finally {
    querying.value = false
  }
}

const exportExcel = async () => {
  if (queryResult.value.length === 0) {
    ElMessage.warning('没有数据可导出')
    return
  }
  
  exporting.value = true
  try {
    const filename = `聚合查询_${new Date().toISOString().slice(0, 10)}`
    
    const response = await fetch('/api/aggregate-query/export', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        data: queryResult.value,
        filename
      })
    })
    
    if (response.ok) {
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = filename + '.xlsx'
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
      ElMessage.success('导出成功')
    } else {
      ElMessage.error('导出失败')
    }
  } catch (error: any) {
    console.error('导出失败:', error)
    ElMessage.error(error.message || '导出失败')
  } finally {
    exporting.value = false
  }
}
</script>

<style scoped>
.aggregate-query-page {
  padding: 20px;
}

.page-card {
  min-height: calc(100vh - 40px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h2 {
  margin: 0;
  font-size: 20px;
}

.action-row {
  display: flex;
  gap: 15px;
  padding: 15px 0;
  border-bottom: 1px solid #eee;
  margin-bottom: 15px;
}

.workspace-row {
  margin-bottom: 15px;
}

.table-field-panel, .workspace-panel {
  min-height: 300px;
}

.table-selector {
  margin-bottom: 15px;
}

.table-selector .el-select {
  width: 25% !important;
  min-width: 150px;
}

.table-selector .label, .field-header .label {
  font-weight: bold;
  display: block;
  margin-bottom: 8px;
}

.field-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.field-list {
  display: flex;
  flex-direction: column;
  max-height: 200px;
  overflow-y: auto;
  border: 1px solid #eee;
  padding: 10px;
  border-radius: 4px;
}

.field-item {
  margin: 3px 0;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
}

.workspace-list {
  max-height: 220px;
  overflow-y: auto;
}

.workspace-item {
  display: flex;
  align-items: center;
  padding: 8px 10px;
  margin: 5px 0;
  background: #f5f7fa;
  border-radius: 4px;
}

.workspace-item:hover {
  background: #ecf5ff;
}

.field-order {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  background: #409eff;
  color: white;
  border-radius: 50%;
  font-size: 12px;
  margin-right: 10px;
}

.workspace-item .field-label {
  flex: 1;
}

.workspace-item .field-table {
  color: #999;
  font-size: 12px;
  margin-right: 10px;
}

.result-tip {
  text-align: center;
  padding: 10px;
  color: #999;
  font-size: 12px;
}

.tag-list {
  display: flex;
  flex-direction: column;
  max-height: 300px;
  overflow-y: auto;
}

.tag-item {
  margin: 5px 0;
}
</style>
