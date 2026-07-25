<template>
  <div class="auto-table-manager">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>{{ chineseName || tableName }}</span>
          <div class="header-actions">
            <el-button size="small" @click="handleRefresh">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </div>
      </template>

      <!-- 功能按钮栏 -->
      <div class="action-bar">
        <el-button type="primary" size="small" @click="handleCreate">
          <el-icon><Plus /></el-icon>
          新增
        </el-button>
        <el-button type="success" size="small" @click="handleImport">
          <el-icon><Upload /></el-icon>
          导入
        </el-button>
        <el-button type="warning" size="small" @click="handleExport">
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
        :max-height="600"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column
          v-for="field in schema"
          :key="field.name"
          :prop="field.name"
          :label="field.label || field.name"
          :width="getColumnWidth(field)"
          sortable
        />
        
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleEdit(row)">
              编辑
            </el-button>
            <el-button type="danger" size="small" @click="handleDelete(row)">
              删除
            </el-button>
            <el-button 
              v-if="tableName === 'retirement_report_data'" 
              type="success" 
              size="small" 
              @click="handleCalculate(row)"
            >
              计算
            </el-button>
            <el-button 
              type="warning" 
              size="small" 
              @click="viewReport(row)"
            >
              查看报表
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
      width="700px"
    >
      <el-form :model="formData" label-width="140px">
        <el-row :gutter="20">
          <el-col 
            :span="12" 
            v-for="field in schema" 
            :key="field.name"
          >
            <el-form-item :label="field.name">
              <el-input
                v-if="field.type === 'VARCHAR' || field.type === 'TEXT'"
                v-model="formData[field.name]"
                :type="field.type === 'TEXT' ? 'textarea' : 'text'"
                :rows="field.type === 'TEXT' ? 2 : 1"
              />
              <el-input-number
                v-else-if="field.type === 'INTEGER'"
                v-model="formData[field.name]"
                style="width: 100%"
              />
              <el-input-number
                v-else-if="field.type === 'DECIMAL'"
                v-model="formData[field.name]"
                :precision="2"
                style="width: 100%"
              />
              <el-date-picker
                v-else-if="field.type === 'DATE'"
                v-model="formData[field.name]"
                type="date"
                format="YYYY年M月D日"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
              <el-switch
                v-else-if="field.type === 'BOOLEAN'"
                v-model="formData[field.name]"
              />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave">确定</el-button>
      </template>
    </el-dialog>

    <!-- 导入弹窗 -->
    <el-dialog
      v-model="importDialogVisible"
      title="导入数据"
      width="500px"
    >
      <div class="import-options">
        <div class="import-option-card" @click="handleExportTemplate">
          <el-icon :size="32"><Download /></el-icon>
          <span class="option-title">导出模板</span>
          <span class="option-desc">下载当前表结构的Excel模板文件</span>
        </div>
        <div class="import-option-card" @click="triggerImportFile">
          <el-icon :size="32"><Upload /></el-icon>
          <span class="option-title">导入数据</span>
          <span class="option-desc">导入与本表模板一致的数据文件</span>
        </div>
      </div>
      <input
        ref="fileInputRef"
        type="file"
        accept=".xlsx,.xls"
        style="display: none"
        @change="handleFileSelected"
      />
      <div v-if="importFile" class="import-file-info">
        <el-tag type="info" closable @close="importFile = null">{{ importFile.name }}</el-tag>
        <el-button type="primary" size="small" :loading="importing" @click="handleImportSubmit" style="margin-left: 10px;">
          开始导入
        </el-button>
      </div>
      <div v-if="importResult" class="import-result">
        <el-alert
          :title="importResult.message"
          :type="importResult.status === 'success' ? 'success' : 'error'"
          :closable="false"
          show-icon
        />
        <div v-if="importResult.status === 'success'" class="import-stats">
          <span>成功导入：<strong>{{ importResult.inserted_count }}</strong> 条</span>
          <span v-if="importResult.skipped_count > 0">，跳过重复：<strong>{{ importResult.skipped_count }}</strong> 条</span>
        </div>
        <div v-if="importResult.errors && importResult.errors.length > 0" class="import-errors">
          <p class="error-title">数据验证错误：</p>
          <ul>
            <li v-for="(err, idx) in importResult.errors.slice(0, 10)" :key="idx">{{ err }}</li>
            <li v-if="importResult.errors.length > 10">... 还有 {{ importResult.errors.length - 10 }} 条错误</li>
          </ul>
        </div>
      </div>
      <template #footer>
        <el-button @click="closeImportDialog">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 重复检测对话框 -->
    <el-dialog
      v-model="duplicateDialogVisible"
      title="重复数据检测"
      width="600px"
    >
      <el-alert
        :title="`发现 ${duplicateRecords.length} 条重复记录（${duplicateKey}重复），请选择处理方式：`"
        type="warning"
        :closable="false"
        show-icon
      />
      <el-table :data="duplicateRecords" style="margin-top: 15px;" max-height="300" border>
        <el-table-column prop="key_value" :label="duplicateKey" />
        <el-table-column label="已有数据" width="80">
          <template #default="{ row }">
            <el-tag type="warning">已存在</el-tag>
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button @click="handleDuplicateCancel">取消导入</el-button>
        <el-button type="warning" @click="handleDuplicateSkip">跳过重复</el-button>
        <el-button type="danger" @click="handleDuplicateOverwrite">覆盖已有</el-button>
      </template>
    </el-dialog>

    <!-- 计算弹窗 -->
    <AutoCalculatorDialog
      v-if="tableName === 'retirement_report_data'"
      v-model="calculatorVisible"
      :table-name="tableName"
      :teacher-id="selectedTeacherId"
      @saved="handleRefresh"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, Plus, Download, Upload } from '@element-plus/icons-vue'
import AutoCalculatorDialog from './AutoCalculatorDialog.vue'
import { useRouter } from 'vue-router'

const router = useRouter()

interface FieldSchema {
  name: string
  type: string
  length?: number
  nullable: boolean
}

const props = defineProps<{
  tableName: string
}>()

// 状态
const loading = ref(false)
const schema = ref<FieldSchema[]>([])
const tableData = ref<any[]>([])
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

// 中文表名
const chineseName = ref('')

// 导入相关
const importDialogVisible = ref(false)
const importFile = ref<File | null>(null)
const importing = ref(false)
const importResult = ref<any>(null)
const fileInputRef = ref<HTMLInputElement | null>(null)

// 重复检测
const duplicateDialogVisible = ref(false)
const duplicateRecords = ref<any[]>([])
const duplicateKey = ref('')
const duplicateStrategy = ref<string>('')  // 当前策略，用于重新提交

// 获取表结构
const loadSchema = async () => {
  try {
    const response = await fetch(`/api/auto-table/${props.tableName}/schema`)
    const result = await response.json()
    if (result.status === 'success') {
      schema.value = result.data.fields
      chineseName.value = result.data.chinese_name || props.tableName
    }
  } catch (error) {
    console.error('加载表结构失败:', error)
    ElMessage.error('加载表结构失败')
  }
}

// 获取数据
const loadData = async () => {
  loading.value = true
  try {
    const response = await fetch(
      `/api/auto-table/${props.tableName}/list?page=${currentPage.value}&page_size=${pageSize.value}`
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
const getColumnWidth = (field: FieldSchema) => {
  if (field.type === 'DATE') return 130
  if (field.type === 'INTEGER' || field.type === 'DECIMAL') return 100
  if (field.length && field.length > 50) return 150
  return 120
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
    let url: string
    let method: string
    
    if (isEditing.value) {
      const recordId = formData.value.teacher_id || formData.value.id
      url = `/api/auto-table/${props.tableName}/update/${recordId}`
      method = 'PUT'
    } else {
      url = `/api/auto-table/${props.tableName}/create`
      method = 'POST'
    }
    
    const response = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(formData.value)
    })
    
    const result = await response.json()
    if (result.status === 'success') {
      ElMessage.success(isEditing.value ? '保存成功' : '添加成功')
      editDialogVisible.value = false
      loadData()
    } else {
      ElMessage.error(result.detail || result.message || '操作失败')
    }
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error('提交失败')
  }
}

// 删除
const handleDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm('确定要删除这条记录吗？', '提示', {
      type: 'warning'
    })
    
    const recordId = row.teacher_id || row.id
    const response = await fetch(
      `/api/auto-table/${props.tableName}/delete/${recordId}`,
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

// 计算
const handleCalculate = (row: any) => {
  selectedTeacherId.value = row.teacher_id
  calculatorVisible.value = true
}

// 查看报表
const viewReport = (row: any) => {
  const templateId = row.template_id || props.tableName.replace('_data', '')
  const encodedTemplateId = encodeURIComponent(templateId)
  const teacherId = row.teacher_id || 0
  router.push(`/report-view/${encodedTemplateId}/${teacherId}`)
}

// 导出
const handleExport = () => {
  ElMessage.info('导出功能开发中')
}

// ========== 导入功能 ==========

// 打开导入对话框
const handleImport = () => {
  importDialogVisible.value = true
  importFile.value = null
  importResult.value = null
}

// 关闭导入对话框
const closeImportDialog = () => {
  importDialogVisible.value = false
  importFile.value = null
  importResult.value = null
}

// 导出模板
const handleExportTemplate = async () => {
  try {
    const response = await fetch(`/api/auto-table/${props.tableName}/export-template`)
    if (!response.ok) {
      const err = await response.json()
      ElMessage.error(err.detail || '导出模板失败')
      return
    }
    
    // 下载文件
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    
    // 从响应头获取文件名
    const disposition = response.headers.get('Content-Disposition')
    let filename = `${props.tableName}_模板.xlsx`
    if (disposition) {
      const match = disposition.match(/filename\*=UTF-8''(.+)/)
      if (match) {
        filename = decodeURIComponent(match[1])
      }
    }
    a.download = filename
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('模板下载成功')
  } catch (error) {
    console.error('导出模板失败:', error)
    ElMessage.error('导出模板失败')
  }
}

// 触发文件选择
const triggerImportFile = () => {
  fileInputRef.value?.click()
}

// 文件选择
const handleFileSelected = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    importFile.value = target.files[0]
    importResult.value = null
  }
}

// 提交导入
const handleImportSubmit = async (strategy?: string) => {
  if (!importFile.value) {
    ElMessage.warning('请先选择文件')
    return
  }
  
  importing.value = true
  importResult.value = null
  
  try {
    const formData = new FormData()
    formData.append('file', importFile.value)
    formData.append('duplicate_strategy', strategy || 'cancel')
    
    const response = await fetch(`/api/auto-table/${props.tableName}/import-data`, {
      method: 'POST',
      body: formData
    })
    
    const result = await response.json()
    importResult.value = result
    
    if (result.status === 'duplicate_found') {
      // 发现重复记录，弹出处理选择
      duplicateRecords.value = result.duplicate_records || []
      duplicateKey.value = result.unique_key || ''
      duplicateStrategy.value = strategy || ''
      duplicateDialogVisible.value = true
    } else if (result.status === 'success') {
      ElMessage.success(result.message)
      loadData()
    } else {
      ElMessage.error(result.message)
    }
  } catch (error) {
    console.error('导入失败:', error)
    importResult.value = {
      status: 'error',
      message: '导入请求失败，请检查网络连接'
    }
  } finally {
    importing.value = false
  }
}

// 重复处理：取消
const handleDuplicateCancel = () => {
  duplicateDialogVisible.value = false
}

// 重复处理：跳过
const handleDuplicateSkip = () => {
  duplicateDialogVisible.value = false
  handleImportSubmit('skip')
}

// 重复处理：覆盖
const handleDuplicateOverwrite = () => {
  duplicateDialogVisible.value = false
  handleImportSubmit('overwrite')
}

// 初始化
onMounted(() => {
  loadSchema()
  loadData()
})

// 监听表名变化
watch(() => props.tableName, () => {
  loadSchema()
  loadData()
})
</script>

<style scoped>
.auto-table-manager {
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

/* 导入选项样式 */
.import-options {
  display: flex;
  gap: 20px;
  justify-content: center;
}

.import-option-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 24px 32px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  min-width: 180px;
}

.import-option-card:hover {
  border-color: #409eff;
  background-color: #ecf5ff;
}

.import-option-card .option-title {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
}

.import-option-card .option-desc {
  font-size: 12px;
  color: #909399;
  text-align: center;
}

.import-file-info {
  margin-top: 20px;
  display: flex;
  align-items: center;
}

.import-result {
  margin-top: 20px;
}

.import-stats {
  margin-top: 10px;
  padding: 10px;
  background-color: #f0f9eb;
  border-radius: 4px;
  font-size: 14px;
}

.import-errors {
  margin-top: 10px;
  padding: 10px;
  background-color: #fef0f0;
  border-radius: 4px;
  font-size: 13px;
}

.import-errors .error-title {
  font-weight: bold;
  color: #f56c6c;
  margin-bottom: 5px;
}

.import-errors ul {
  margin: 0;
  padding-left: 20px;
}

.import-errors li {
  color: #f56c6c;
  line-height: 1.6;
}
</style>