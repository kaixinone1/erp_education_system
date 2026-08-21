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

      <!-- 第二行：表选择、工作区和过滤条件 -->
      <el-row :gutter="20" class="workspace-row">
        <!-- 左侧：表选择 -->
        <el-col :span="6">
          <el-card shadow="hover" class="table-panel">
            <template #header>
              <span>选择表名</span>
            </template>
            <el-select
              v-model="selectedTable"
              placeholder="输入关键词搜索数据表"
              style="width: 100%"
              filterable
              clearable
              remote
              :remote-method="remoteSearchTable"
              :loading="tableSearchLoading"
              @change="handleTableChange"
              @clear="handleTableClear"
            >
              <el-option
                v-for="table in filteredTableList"
                :key="table.name"
                :label="table.has_chinese_name ? `${table.chinese_name} (${table.name})` : table.name"
                :value="table.name"
              />
            </el-select>
          </el-card>
        </el-col>

        <!-- 中间：字段选择（一体化树形结构） -->
        <el-col :span="8">
          <el-card shadow="hover" class="field-panel">
            <template #header>
              <div class="panel-header">
                <span>选择字段</span>
                <el-button type="primary" size="small" @click="addSelectedFields" :disabled="selectedFieldNames.length === 0">
                  添加到工作区
                </el-button>
              </div>
            </template>

            <div v-if="fieldTree.length > 0" class="field-tree">
              <div v-for="field in fieldTree" :key="field.name" class="field-node">
                <!-- 有字典的字段：显示为可展开的父级（下拉菜单） -->
                <div v-if="field.hasDict && field.options.length > 0" class="field-parent">
                  <div class="field-row" @click="toggleExpand(field.name)">
                    <el-checkbox
                      :model-value="isFieldSelected(field.name)"
                      @change="(val: boolean) => toggleFieldSelect(field.name, val)"
                      @click.stop
                    />
                    <span class="field-label">{{ field.label }}</span>
                    <el-icon v-if="field.expanded" class="expand-icon"><ArrowDown /></el-icon>
                    <el-icon v-else class="expand-icon"><ArrowRight /></el-icon>
                  </div>
                  <!-- 子选项：字典值（进一步细化选择） -->
                  <div v-if="field.expanded" class="field-children">
                    <!-- 全选/取消全选 -->
                    <div class="child-row select-all-row" @click="toggleSelectAll(field)">
                      <el-checkbox
                        :model-value="isAllSelected(field.name)"
                        :indeterminate="isPartialSelected(field.name)"
                        @change="(val: boolean) => toggleSelectAll(field, val)"
                        @click.stop
                      />
                      <span class="child-label select-all-label">全选 / 取消全选</span>
                    </div>
                    <div
                      v-for="opt in field.options"
                      :key="opt.value"
                      class="child-row"
                      :class="{ 'child-selected': isValueSelected(field.name, opt.value) }"
                      @click="toggleValueSelect(field, opt)"
                    >
                      <el-checkbox
                        :model-value="isValueSelected(field.name, opt.value)"
                        @change="(val: boolean) => toggleValueSelect(field, opt, val)"
                        @click.stop
                      />
                      <span class="child-label">{{ opt.label }}</span>
                    </div>
                  </div>
                </div>
                <!-- 无字典的字段：直接显示 -->
                <div v-else class="field-simple">
                  <el-checkbox
                    :model-value="isFieldSelected(field.name)"
                    @change="(val: boolean) => toggleFieldSelect(field.name, val)"
                  />
                  <span class="field-label">{{ field.label }}</span>
                </div>
              </div>
            </div>
            <el-empty v-else-if="selectedTable" description="加载字段中..." :image-size="60" />
            <el-empty v-else description="请先选择表" :image-size="60" />
          </el-card>
        </el-col>

        <!-- 右侧：工作区 -->
        <el-col :span="10">
          <el-card shadow="hover" class="workspace-panel">
            <template #header>
              <div class="panel-header">
                <span>工作区</span>
                <el-button type="danger" size="small" @click="clearFields" :disabled="queryFields.length === 0">清空</el-button>
              </div>
            </template>

            <div v-if="activeFilters.length > 0" class="active-filters">
              <div class="filter-title">已选过滤条件：</div>
              <el-tag
                v-for="(f, index) in activeFilters"
                :key="index"
                closable
                @close="removeFilter(index)"
                type="warning"
                class="filter-tag"
              >
                {{ f.fieldLabel }}: {{ f.valueLabel }}
              </el-tag>
            </div>

            <div class="workspace-list">
              <div
                v-for="(field, index) in queryFields"
                :key="index"
                class="workspace-item"
                draggable="true"
                @dragstart="onDragStart(index, $event)"
                @dragover.prevent="onDragOver(index)"
                @drop="onDrop(index)"
                @dragend="onDragEnd"
              >
                <span class="field-order">{{ index + 1 }}</span>
                <span class="field-label">{{ field.label }}</span>
                <span class="field-table">({{ field.tableLabel }})</span>
                <div class="field-actions">
                  <el-button link type="primary" size="small" @click="moveFieldUp(index)" :disabled="index === 0">
                    <el-icon><ArrowUpBold /></el-icon>
                  </el-button>
                  <el-button link type="primary" size="small" @click="moveFieldDown(index)" :disabled="index === queryFields.length - 1">
                    <el-icon><ArrowDownBold /></el-icon>
                  </el-button>
                  <el-button link type="danger" size="small" @click="removeField(index)">
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </div>
              </div>
            </div>

            <el-empty v-if="queryFields.length === 0 && activeFilters.length === 0" description="请从左侧选择字段" :image-size="60" />
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
        <el-checkbox v-for="tag in tagList" :key="tag.标签ID" :value="tag.标签名称" class="tag-item">
          {{ tag.标签名称 }}
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
import { Search, Download, Delete, PriceTag, ArrowDown, ArrowRight, Top, Bottom, ArrowUp, ArrowUpBold, ArrowDownBold } from '@element-plus/icons-vue'
import * as XLSX from 'xlsx'

interface FieldNode {
  name: string
  label: string
  hasDict: boolean
  expanded: boolean
  options: { value: any, label: string }[]
}

interface ActiveFilter {
  field: string
  fieldLabel: string
  table: string
  tableLabel: string
  values: any[]
  valueLabel: string
}

const tableList = ref<{name: string, chinese_name: string, has_chinese_name: boolean}[]>([])
const filteredTableList = ref<{name: string, chinese_name: string, has_chinese_name: boolean}[]>([])
const tableSearchLoading = ref(false)
const selectedTable = ref('')
const fieldTree = ref<FieldNode[]>([])
const selectedFieldNames = ref<string[]>([])
const queryFields = ref<{name: string, label: string, table: string, tableLabel: string}[]>([])
const tagList = ref<{id: number, name: string}[]>([])
const selectedTags = ref<string[]>([])
const showTagDialog = ref(false)
const activeFilters = ref<ActiveFilter[]>([])
const querying = ref(false)
const exporting = ref(false)
const queryResult = ref<any[]>([])

const resultColumns = computed(() => {
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
      filteredTableList.value = result.tables
    }
  } catch (error) {
    console.error('加载表列表失败:', error)
  }
}

const loadTags = async () => {
  try {
    const response = await fetch('/api/aggregate-query/tags')
    const result = await response.json()
    if (result.状态 === '成功') {
      tagList.value = result.标签列表
    }
  } catch (error) {
    console.error('加载标签列表失败:', error)
  }
}

// 远程搜索表（中文名+英文名模糊匹配）
const remoteSearchTable = (query: string) => {
  tableSearchLoading.value = true
  try {
    if (!query || query.trim() === '') {
      filteredTableList.value = tableList.value
    } else {
      const keyword = query.toLowerCase()
      filteredTableList.value = tableList.value.filter((table: any) => {
        const chineseName = (table.chinese_name || '').toLowerCase()
        const englishName = (table.name || '').toLowerCase()
        return chineseName.includes(keyword) || englishName.includes(keyword)
      })
    }
  } finally {
    tableSearchLoading.value = false
  }
}

// 清空表选择
const handleTableClear = () => {
  selectedTable.value = ''
  filteredTableList.value = tableList.value
  fieldTree.value = []
  selectedFieldNames.value = []
}

const handleTableChange = async () => {
  selectedFieldNames.value = []
  if (!selectedTable.value) {
    fieldTree.value = []
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
      const tableInfo = tableList.value.find(t => t.name === selectedTable.value)
      fieldTree.value = result.fields.map((f: any) => ({
        name: f.name,
        label: f.label,
        hasDict: f.has_dict || f.hasDict || false,
        expanded: false,
        options: []
      }))

      for (const field of fieldTree.value) {
        if (field.hasDict) {
          await loadDictOptions(field)
        }
      }
    }
  } catch (error) {
    console.error('加载字段列表失败:', error)
  }
}

const loadDictOptions = async (field: FieldNode) => {
  try {
    const response = await fetch('/api/aggregate-query/dict-values', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        table_name: selectedTable.value,
        field_name: field.name
      })
    })
    const result = await response.json()
    if (result.status === 'success') {
      field.options = result.values.map((v: any) => ({
        value: v.value,
        label: v.label
      }))
    }
  } catch (error) {
    console.error('加载字典选项失败:', error)
  }
}

const isFieldSelected = (fieldName: string) => {
  return selectedFieldNames.value.includes(fieldName)
}

const toggleFieldSelect = (fieldName: string, selected: boolean) => {
  if (selected) {
    if (!selectedFieldNames.value.includes(fieldName)) {
      selectedFieldNames.value.push(fieldName)
    }
  } else {
    selectedFieldNames.value = selectedFieldNames.value.filter(n => n !== fieldName)
  }
}

const isValueSelected = (fieldName: string, value: any) => {
  const filter = activeFilters.value.find(f => f.field === fieldName)
  return filter && filter.values.includes(value)
}

// 判断是否全选
const isAllSelected = (fieldName: string) => {
  const field = fieldTree.value.find(f => f.name === fieldName)
  if (!field || field.options.length === 0) return false
  const filter = activeFilters.value.find(f => f.field === fieldName)
  if (!filter) return false
  return filter.values.length === field.options.length
}

// 判断是否部分选中（用于 indeterminate 半选状态）
const isPartialSelected = (fieldName: string) => {
  const field = fieldTree.value.find(f => f.name === fieldName)
  if (!field || field.options.length === 0) return false
  const filter = activeFilters.value.find(f => f.field === fieldName)
  if (!filter || filter.values.length === 0) return false
  return filter.values.length < field.options.length
}

// 将字段自动加入工作区（如果尚未加入）
const autoAddToWorkspace = (field: FieldNode) => {
  const tableInfo = tableList.value.find(t => t.name === selectedTable.value)
  if (!queryFields.value.find(f => f.name === field.name && f.table === selectedTable.value)) {
    queryFields.value.push({
      name: field.name,
      label: field.label,
      table: selectedTable.value,
      tableLabel: tableInfo?.chinese_name || selectedTable.value
    })
  }
}

// 全选/取消全选
const toggleSelectAll = (field: FieldNode, val?: boolean) => {
  const tableInfo = tableList.value.find(t => t.name === selectedTable.value)
  let filter = activeFilters.value.find(f => f.field === field.name)

  // 判断新状态：如果传了val就用val，否则取反当前全选状态
  const shouldSelectAll = val !== undefined ? val : !isAllSelected(field.name)

  if (shouldSelectAll) {
    // 全选
    if (!filter) {
      filter = {
        field: field.name,
        fieldLabel: field.label,
        table: selectedTable.value,
        tableLabel: tableInfo?.chinese_name || selectedTable.value,
        values: [],
        valueLabel: ''
      }
      activeFilters.value.push(filter)
    }
    filter.values = field.options.map(o => o.value)
    filter.valueLabel = '全部'
    autoAddToWorkspace(field)
  } else {
    // 取消全选
    if (filter) {
      activeFilters.value = activeFilters.value.filter(f => f.field !== field.name)
    }
  }
}

const toggleExpand = (fieldName: string) => {
  const field = fieldTree.value.find(f => f.name === fieldName)
  if (field) {
    field.expanded = !field.expanded
  }
}

const toggleValueSelect = (field: FieldNode, opt: { value: any, label: string }, selected?: boolean) => {
  const tableInfo = tableList.value.find(t => t.name === selectedTable.value)
  let filter = activeFilters.value.find(f => f.field === field.name)

  if (!filter) {
    filter = {
      field: field.name,
      fieldLabel: field.label,
      table: selectedTable.value,
      tableLabel: tableInfo?.chinese_name || selectedTable.value,
      values: [],
      valueLabel: ''
    }
    activeFilters.value.push(filter)
  }

  if (selected === undefined || selected) {
    if (!filter.values.includes(opt.value)) {
      filter.values.push(opt.value)
      filter.valueLabel = field.options
        .filter(o => filter!.values.includes(o.value))
        .map(o => o.label)
        .join(', ')
    }
    autoAddToWorkspace(field)
  } else {
    filter.values = filter.values.filter(v => v !== opt.value)
    filter.valueLabel = field.options
      .filter(o => filter!.values.includes(o.value))
      .map(o => o.label)
      .join(', ')
    if (filter.values.length === 0) {
      activeFilters.value = activeFilters.value.filter(f => f.field !== field.name)
    }
  }
}

const removeFilter = (index: number) => {
  activeFilters.value.splice(index, 1)
}

const addSelectedFields = () => {
  const tableInfo = tableList.value.find(t => t.name === selectedTable.value)
  for (const fieldName of selectedFieldNames.value) {
    const fieldInfo = fieldTree.value.find(f => f.name === fieldName)
    if (fieldInfo && !queryFields.value.find(f => f.name === fieldName && f.table === selectedTable.value)) {
      queryFields.value.push({
        name: fieldName,
        label: fieldInfo.label,
        table: selectedTable.value,
        tableLabel: tableInfo?.chinese_name || selectedTable.value
      })
    }
  }
  selectedFieldNames.value = []
}

const removeField = (index: number) => {
  queryFields.value.splice(index, 1)
}

const moveFieldUp = (index: number) => {
  if (index > 0) {
    const temp = queryFields.value[index]
    queryFields.value[index] = queryFields.value[index - 1]
    queryFields.value[index - 1] = temp
  }
}

const moveFieldDown = (index: number) => {
  if (index < queryFields.value.length - 1) {
    const temp = queryFields.value[index]
    queryFields.value[index] = queryFields.value[index + 1]
    queryFields.value[index + 1] = temp
  }
}

// 拖拽排序
const dragIndex = ref<number | null>(null)

const onDragStart = (index: number, event: DragEvent) => {
  dragIndex.value = index
  if (event.dataTransfer) {
    event.dataTransfer.effectAllowed = 'move'
  }
}

const onDragOver = (index: number) => {
}

const onDrop = (targetIndex: number) => {
  if (dragIndex.value !== null && dragIndex.value !== targetIndex) {
    const temp = queryFields.value[dragIndex.value]
    queryFields.value[dragIndex.value] = queryFields.value[targetIndex]
    queryFields.value[targetIndex] = temp
    dragIndex.value = null
  }
}

const onDragEnd = () => {
  dragIndex.value = null
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
        tags: selectedTags.value.length > 0 ? selectedTags.value : undefined,
        filters: activeFilters.value.length > 0 ? activeFilters.value.map(f => ({
          field: f.field,
          table: f.table,
          values: f.values
        })) : undefined
      })
    })

    const result = await response.json()
    if (result.status === 'success') {
      queryResult.value = result.data
      ElMessage.success(`查询成功，共 ${result.data.length} 条数据`)
    } else {
      ElMessage.error(result.message || '查询失败')
    }
  } catch (error) {
    console.error('查询失败:', error)
    ElMessage.error('查询失败')
  } finally {
    querying.value = false
  }
}

const exportExcel = () => {
  if (queryResult.value.length === 0) {
    ElMessage.warning('没有数据可导出')
    return
  }

  try {
    const data = queryResult.value.map((row: any) => {
      const newRow: any = {}
      for (const col of resultColumns.value) {
        newRow[col] = row[col]
      }
      return newRow
    })

    const worksheet = XLSX.utils.json_to_sheet(data)
    const workbook = XLSX.utils.book_new()
    XLSX.utils.book_append_sheet(workbook, worksheet, '查询结果')

    const colWidths = resultColumns.value.map(col => ({
      wch: Math.max(col.length, 15)
    }))
    worksheet['!cols'] = colWidths

    const fileName = `聚合查询结果_${new Date().toLocaleDateString('zh-CN').replace(/\//g, '-')}.xlsx`
    XLSX.writeFile(workbook, fileName)
    ElMessage.success('导出成功')
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败')
  }
}
</script>

<style scoped>
.aggregate-query-page {
  padding: 20px;
}

.page-card {
  max-width: 1400px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h2 {
  margin: 0;
}

.action-row {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.workspace-row {
  margin-bottom: 20px;
}

.table-panel,
.field-panel,
.workspace-panel {
  height: 100%;
  min-height: 400px;
}

.field-panel {
  overflow-y: auto;
  max-height: 500px;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.field-tree {
  padding: 10px 0;
}

.field-node {
  margin-bottom: 5px;
}

.field-parent {
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  margin-bottom: 5px;
  overflow: hidden;
}

.field-row {
  display: flex;
  align-items: center;
  padding: 8px 10px;
  cursor: pointer;
  background: #f5f7fa;
}

.field-row:hover {
  background: #ecf5ff;
}

.field-label {
  flex: 1;
  margin-left: 8px;
}

.expand-icon {
  margin-left: 5px;
  color: #909399;
}

.field-children {
  padding: 5px 10px 5px 35px;
  background: #fff;
}

.child-row {
  display: flex;
  align-items: center;
  padding: 6px 8px;
  cursor: pointer;
  border-radius: 4px;
}

.child-row:hover {
  background: #ecf5ff;
}

.child-row.child-selected {
  background: #fffbe6;
}

.select-all-row {
  border-bottom: 1px solid #e4e7ed;
  margin-bottom: 4px;
  padding-bottom: 6px;
  background: #f0f9ff;
}

.select-all-row:hover {
  background: #e6f4ff;
}

.select-all-label {
  font-weight: bold;
  color: #409eff;
}

.child-label {
  margin-left: 8px;
  color: #606266;
}

.field-simple {
  display: flex;
  align-items: center;
  padding: 5px 0;
}

.active-filters {
  margin-bottom: 15px;
  padding-bottom: 15px;
  border-bottom: 1px solid #eee;
}

.filter-title {
  font-weight: bold;
  margin-bottom: 10px;
  color: #606266;
}

.filter-tag {
  margin-right: 5px;
  margin-bottom: 5px;
}

.workspace-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.workspace-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  background: #f5f5f5;
  border-radius: 4px;
  cursor: move;
}

.workspace-item:hover {
  background: #e8f4ff;
}

.field-actions {
  display: flex;
  gap: 2px;
}

.field-order {
  width: 24px;
  height: 24px;
  background: #409eff;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
}

.field-table {
  color: #999;
  font-size: 12px;
}

.result-panel {
  margin-top: 20px;
}

.result-tip {
  text-align: center;
  padding: 10px;
  color: #999;
}

.tag-list {
  display: flex;
  flex-direction: column;
}

.tag-item {
  margin-bottom: 10px;
}
</style>
