<template>
  <div class="intermediate-table-manager">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>{{ config?.chinese_name || tableName }}</span>
          <div class="header-actions">
            <el-input
              v-model="searchKeyword"
              placeholder="请输入搜索关键词"
              size="small"
              style="width: 200px; margin-right: 10px;"
              clearable
              @keyup.enter="handleSearch"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
            <el-button size="small" @click="handleRefresh">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </div>
      </template>

      <!-- 功能按钮栏 -->
      <div class="action-bar">
        <el-button 
          v-if="features?.crud" 
          type="primary" 
          size="small" 
          @click="handleCreate"
        >
          <el-icon><Plus /></el-icon>
          新增
        </el-button>
        <el-button 
          v-if="features?.crud && selectedRows.length > 0" 
          type="danger" 
          size="small" 
          @click="handleBatchDelete"
        >
          <el-icon><Delete /></el-icon>
          删除
        </el-button>
        <el-button 
          v-if="features?.export?.length > 0" 
          type="success" 
          size="small" 
          @click="handleExport"
        >
          <el-icon><Download /></el-icon>
          导出
        </el-button>
      </div>

      <!-- 数据表格 -->
      <el-table
        :data="tableData"
        style="width: 100%"
        border
        v-loading="loading"
        @selection-change="handleSelectionChange"
        :max-height="600"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="id" label="ID" width="80" />
        
        <el-table-column
          v-for="field in displayFields"
          :key="field.name"
          :prop="field.name"
          :label="field.name"
          :width="getColumnWidth(field)"
          sortable
        />
        
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button 
              v-if="features?.crud" 
              type="primary" 
              size="small" 
              @click="handleEdit(row)"
            >
              编辑
            </el-button>
            <el-button 
              v-if="features?.crud" 
              type="danger" 
              size="small" 
              @click="handleDelete(row)"
            >
              删除
            </el-button>
            <el-button 
              v-if="features?.calculator" 
              type="success" 
              size="small" 
              @click="handleCalculate(row)"
            >
              计算
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-section">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 编辑弹窗 -->
    <el-dialog
      v-model="editDialogVisible"
      :title="isEditing ? '编辑' : '新增'"
      width="600px"
    >
      <el-form :model="formData" label-width="120px">
        <el-form-item
          v-for="field in editableFields"
          :key="field.name"
          :label="field.name"
        >
          <el-input
            v-if="field.type === 'VARCHAR' || field.type === 'TEXT'"
            v-model="formData[field.name]"
            :type="field.type === 'TEXT' ? 'textarea' : 'text'"
            :rows="3"
          />
          <el-input-number
            v-else-if="field.type === 'INTEGER'"
            v-model="formData[field.name]"
          />
          <el-input-number
            v-else-if="field.type === 'DECIMAL'"
            v-model="formData[field.name]"
            :precision="2"
          />
          <el-date-picker
            v-else-if="field.type === 'DATE'"
            v-model="formData[field.name]"
            type="date"
            format="YYYY年M月D日"
            value-format="YYYY-MM-DD"
          />
          <el-switch
            v-else-if="field.type === 'BOOLEAN'"
            v-model="formData[field.name]"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave">确定</el-button>
      </template>
    </el-dialog>

    <!-- 计算弹窗 -->
    <IntermediateCalculatorDialog
      v-if="features?.calculator"
      v-model="calculatorVisible"
      :table-name="tableName"
      :teacher-id="selectedTeacherId"
      :config="config?.calculations"
      @saved="handleRefresh"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, Plus, Delete, Download } from '@element-plus/icons-vue'
import IntermediateCalculatorDialog from './IntermediateCalculatorDialog.vue'

interface FieldConfig {
  name: string
  type: string
  length?: number
  required?: boolean
  calculated?: boolean
}

interface TableConfig {
  table_name: string
  chinese_name: string
  fields: FieldConfig[]
  features: {
    crud?: boolean
    export?: string[]
    calculator?: boolean
    import?: boolean
  }
  calculations?: Record<string, any>
}

const props = defineProps<{
  tableName: string
}>()

// 状态
const loading = ref(false)
const config = ref<TableConfig | null>(null)
const tableData = ref<any[]>([])
const selectedRows = ref<any[]>([])
const searchKeyword = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

// 编辑弹窗
const editDialogVisible = ref(false)
const isEditing = ref(false)
const formData = ref<Record<string, any>>({})

// 计算弹窗
const calculatorVisible = ref(false)
const selectedTeacherId = ref<number | null>(null)

// 计算属性
const features = computed(() => config.value?.features || {})

const displayFields = computed(() => {
  if (!config.value) return []
  // 显示所有字段，包括计算字段
  return config.value.fields
})

const editableFields = computed(() => {
  if (!config.value) return []
  return config.value.fields.filter(f => !f.calculated)
})

// 获取配置
const loadConfig = async () => {
  try {
    const response = await fetch(`/api/intermediate/${props.tableName}/config`)
    const result = await response.json()
    if (result.status === 'success') {
      config.value = result.data
    }
  } catch (error) {
    console.error('加载配置失败:', error)
    ElMessage.error('加载配置失败')
  }
}

// 获取数据
const loadData = async () => {
  loading.value = true
  try {
    const response = await fetch(
      `/api/intermediate/${props.tableName}/list?page=${currentPage.value}&page_size=${pageSize.value}`
    )
    const result = await response.json()
    if (result.status === 'success') {
      tableData.value = result.data
      total.value = result.total
    }
  } catch (error) {
    console.error('加载数据失败:', error)
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

// 获取列宽
const getColumnWidth = (field: FieldConfig) => {
  if (field.type === 'DATE') return 120
  if (field.type === 'INTEGER' || field.type === 'DECIMAL') return 100
  if (field.length && field.length > 50) return 200
  return 120
}

// 选择变化
const handleSelectionChange = (rows: any[]) => {
  selectedRows.value = rows
}

// 搜索
const handleSearch = () => {
  currentPage.value = 1
  loadData()
}

// 刷新
const handleRefresh = () => {
  loadData()
}

// 分页
const handleSizeChange = (size: number) => {
  pageSize.value = size
  loadData()
}

const handleCurrentChange = (page: number) => {
  currentPage.value = page
  loadData()
}

// 新增
const handleCreate = () => {
  isEditing.value = false
  formData.value = {}
  editDialogVisible.value = true
}

// 编辑
const handleEdit = (row: any) => {
  isEditing.value = true
  formData.value = { ...row }
  editDialogVisible.value = true
}

// 保存
const handleSave = async () => {
  try {
    const url = `/api/intermediate/${props.tableName}/${isEditing.value ? 'update/' + formData.value.teacher_id : 'save'}`
    const method = isEditing.value ? 'PUT' : 'POST'
    
    const response = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(formData.value)
    })
    
    const result = await response.json()
    if (result.status === 'success') {
      ElMessage.success('保存成功')
      editDialogVisible.value = false
      loadData()
    } else {
      ElMessage.error(result.message || '保存失败')
    }
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error('保存失败')
  }
}

// 删除
const handleDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm('确定要删除这条记录吗？', '提示', {
      type: 'warning'
    })
    
    const response = await fetch(
      `/api/intermediate/${props.tableName}/delete/${row.teacher_id}`,
      { method: 'DELETE' }
    )
    
    const result = await response.json()
    if (result.status === 'success') {
      ElMessage.success('删除成功')
      loadData()
    } else {
      ElMessage.error(result.message || '删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

// 批量删除
const handleBatchDelete = async () => {
  if (selectedRows.value.length === 0) {
    ElMessage.warning('请选择要删除的记录')
    return
  }
  
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedRows.value.length} 条记录吗？`,
      '提示',
      { type: 'warning' }
    )
    
    // 逐个删除
    for (const row of selectedRows.value) {
      await fetch(
        `/api/intermediate/${props.tableName}/delete/${row.teacher_id}`,
        { method: 'DELETE' }
      )
    }
    
    ElMessage.success('批量删除成功')
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('批量删除失败:', error)
      ElMessage.error('批量删除失败')
    }
  }
}

// 计算
const handleCalculate = (row: any) => {
  selectedTeacherId.value = row.teacher_id
  calculatorVisible.value = true
}

// 导出
const handleExport = () => {
  // 导出功能待实现
  ElMessage.info('导出功能开发中')
}

// 初始化
onMounted(() => {
  loadConfig()
  loadData()
})

// 监听表名变化
watch(() => props.tableName, () => {
  loadConfig()
  loadData()
})
</script>

<style scoped>
.intermediate-table-manager {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  align-items: center;
}

.action-bar {
  margin-bottom: 20px;
  display: flex;
  gap: 10px;
}

.pagination-section {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

:deep(.el-table) {
  overflow-x: auto;
}

:deep(.el-table__body-wrapper) {
  overflow-x: auto;
}
</style>
