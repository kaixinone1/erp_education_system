<template>
  <div class="data-preview-panel">
    <el-card class="panel-card">
      <template #header>
        <div class="card-header">
          <span>第三步：数据预览与验证</span>
          <div class="header-actions">
            <el-select v-model="validationLevel" size="small" style="width: 120px; margin-right: 10px;">
              <el-option label="Level 1" :value="1" />
              <el-option label="Level 2" :value="2" />
              <el-option label="Level 3" :value="3" />
              <el-option label="Level 4" :value="4" />
            </el-select>
            <el-radio-group v-model="viewMode" size="small">
              <el-radio-button label="all">全部</el-radio-button>
              <el-radio-button label="valid">合格</el-radio-button>
              <el-radio-button label="error">错误</el-radio-button>
            </el-radio-group>
            <el-button 
              type="primary" 
              size="small" 
              @click="handleValidate"
              :loading="validating"
            >
              <el-icon><Check /></el-icon>
              开始验证
            </el-button>
          </div>
        </div>
      </template>

      <div class="panel-content">
        <!-- 错误提示区域 -->
        <div v-if="errorMessage" class="error-alert">
          <el-alert
            :title="errorMessage"
            type="error"
            show-icon
            closable
            @close="errorMessage = ''"
          />
        </div>

        <!-- 验证统计信息 -->
        <div v-if="validationReport" class="validation-summary">
          <el-alert
            :title="`验证完成：共 ${validationReport.summary.total_rows} 行数据，合格 ${validationReport.summary.valid_rows} 行，错误 ${validationReport.summary.invalid_rows} 行，错误 ${validationReport.summary.total_errors} 个，警告 ${validationReport.summary.total_warnings} 个`"
            :type="validationReport.summary.invalid_rows === 0 ? 'success' : 'warning'"
            show-icon
            :closable="false"
          />
          <!-- 错误数据导出按钮 - 当有错误数据时自动激活 -->
          <div v-if="validationReport.summary.invalid_rows > 0" class="error-export-actions" style="margin-top: 10px;">
            <el-button
              type="danger"
              size="small"
              @click="exportErrorData"
              :loading="exportingErrorData"
            >
              <el-icon><Download /></el-icon>
              导出错误数据
            </el-button>
            <el-button
              type="warning"
              size="small"
              @click="exportErrorDataWithDialog"
              :loading="exportingErrorData"
            >
              <el-icon><FolderOpened /></el-icon>
              另存为错误数据
            </el-button>
          </div>
        </div>

        <!-- 数据表格 -->
        <div class="table-section">
          <el-table
            :data="filteredData"
            style="width: 100%"
            border
            max-height="500px"
            :row-class-name="getRowClassName"
          >
            <!-- 行号列 -->
            <el-table-column
              type="index"
              label="行号"
              width="60"
              fixed
            />

            <!-- 状态列 -->
            <el-table-column
              label="状态"
              width="80"
              fixed
            >
              <template #default="{ row }">
                <el-tag
                  :type="getRowStatusType(row)"
                  size="small"
                >
                  {{ getRowStatusText(row) }}
                </el-tag>
              </template>
            </el-table-column>

            <!-- 动态数据列 -->
            <el-table-column
              v-for="field in displayFields"
              :key="field.sourceField"
              :label="field.sourceField"
              min-width="120"
              show-overflow-tooltip
            >
              <template #default="{ row }">
                <div
                  :class="getCellClass(row, field.sourceField)"
                  @click="handleCellClick(row, field)"
                >
                  <template v-if="isEditing(row, field.sourceField)">
                    <el-input
                      v-model="editingValue"
                      size="small"
                      @blur="finishEdit(row, field)"
                      @keyup.enter="finishEdit(row, field)"
                      v-focus
                    />
                  </template>
                  <template v-else>
                    <div class="cell-content">
                      <span class="cell-value">{{ getCellValue(row, field.sourceField) }}</span>
                      <el-icon v-if="getCellErrors(row, field.sourceField).length > 0" class="error-icon"><Warning /></el-icon>
                    </div>
                    <!-- 直接显示错误原因 -->
                    <div v-if="getCellErrors(row, field.sourceField).length > 0" class="cell-error-message">
                      {{ getCellErrors(row, field.sourceField).join('; ') }}
                    </div>
                  </template>
                </div>
              </template>
            </el-table-column>

            <!-- 操作列 - 显示编辑/删除按钮 -->
            <el-table-column
              label="操作"
              width="150"
              fixed="right"
            >
              <template #default="{ row, $index }">
                <div class="row-actions">
                  <el-button 
                    type="primary" 
                    size="small" 
                    @click="handleEditRow(row, $index)"
                  >
                    <el-icon><Edit /></el-icon>
                    编辑
                  </el-button>
                  <el-button 
                    type="danger" 
                    size="small" 
                    @click="handleDeleteRow($index)"
                  >
                    <el-icon><Delete /></el-icon>
                    删除
                  </el-button>
                </div>
              </template>
            </el-table-column>
          </el-table>
        </div>



        <!-- 操作按钮 -->
        <div class="action-section">
          <el-button @click="handlePrevious">
            <el-icon><ArrowLeft /></el-icon>
            上一步
          </el-button>
          <el-button 
            type="primary" 
            @click="handleNextStep"
            :disabled="!canProceed"
          >
            下一步：确认导入
            <el-icon class="el-icon--right"><ArrowRight /></el-icon>
          </el-button>
        </div>
      </div>
    </el-card>
  </div>

  <!-- 错误数据编辑弹窗 -->
  <el-dialog
    v-model="editDialogVisible"
    :title="`修改第 ${editingRow?.row_index + 1} 行数据`"
    width="700px"
    destroy-on-close
  >
    <el-form
      ref="editFormRef"
      :model="editFormData"
      label-width="120px"
      style="max-height: 500px; overflow-y: auto;"
    >
      <el-form-item
        v-for="field in displayFields"
        :key="field.sourceField"
        :label="field.sourceField"
        :prop="field.sourceField"
        :error="getFieldError(field.sourceField)"
      >
        <el-input
          v-model="editFormData[field.sourceField]"
          :placeholder="`请输入${field.sourceField}`"
          clearable
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="editDialogVisible = false">取消</el-button>
      <el-button type="primary" @click="handleSaveEdit" :loading="savingEdit">
        保存并验证
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ArrowLeft, ArrowRight, Check, Warning, Edit, Delete, Download, FolderOpened } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

// 组件属性
const props = defineProps<{
  parsedData?: {
    preview_data: any[]
    total_rows: number
  }
  fieldConfigs?: any[]
}>()

// 组件事件
const emit = defineEmits(['previous-step', 'next-step', 'validation-complete'])

// 验证级别
const validationLevel = ref(3)

// 视图模式
const viewMode = ref('all')

// 验证状态
const validating = ref(false)
const validationReport = ref<any>(null)
const errorMessage = ref('')

// 当前展开的错误行
const activeErrorRows = ref<number[]>([0]) // 默认展开第一个

// 编辑状态
const editingCell = ref<{ rowIndex: number; field: string } | null>(null)
const editingValue = ref('')

// 弹窗编辑状态
const editDialogVisible = ref(false)
const editingRow = ref<any>(null)
const editFormData = ref<Record<string, any>>({})
const editFormRef = ref()
const savingEdit = ref(false)
const editFieldErrors = ref<Record<string, string>>({})

// 所有数据（包含验证结果）
const allData = ref<any[]>([])

// 显示字段
const displayFields = computed(() => {
  return props.fieldConfigs?.map(config => ({
    sourceField: config.sourceField,
    targetField: config.targetField
  })) || []
})

// 过滤后的数据
const filteredData = computed(() => {
  if (viewMode.value === 'all') {
    return allData.value
  } else if (viewMode.value === 'valid') {
    return allData.value.filter(row => row.is_valid)
  } else if (viewMode.value === 'error') {
    return allData.value.filter(row => !row.is_valid)
  }
  return allData.value
})

// 是否有错误
const hasErrors = computed(() => {
  return validationReport.value?.summary?.invalid_rows > 0
})

// 错误行
const errorRows = computed(() => {
  return allData.value.filter(row => !row.is_valid)
})

// 是否可以进行下一步
const canProceed = computed(() => {
  if (!validationReport.value) return false
  // 允许有警告，但不允许有错误
  return validationReport.value.summary.invalid_rows === 0
})

// 初始化数据
const initData = () => {
  if (props.parsedData?.preview_data) {
    allData.value = props.parsedData.preview_data.map((row, index) => ({
      row_index: index,
      data: row,
      errors: [],
      warnings: [],
      is_valid: true
    }))
  }
}

// 获取单元格值
const getCellValue = (row: any, fieldName: string) => {
  return row.data?.[fieldName] ?? ''
}

// 执行验证
const handleValidate = async () => {
  // 清除之前的错误信息
  errorMessage.value = ''
  
  if (!props.parsedData?.preview_data || props.parsedData.preview_data.length === 0) {
    errorMessage.value = '没有数据可验证，请返回第一步重新上传文件'
    ElMessage.warning('没有数据可验证')
    return
  }
  
  if (!props.fieldConfigs || props.fieldConfigs.length === 0) {
    errorMessage.value = '没有字段配置，请返回第二步配置字段'
    ElMessage.warning('没有字段配置')
    return
  }
  
  validating.value = true
  
  try {
    console.log('开始验证，数据量:', props.parsedData.preview_data.length)
    console.log('字段配置:', props.fieldConfigs)
    console.log('验证级别:', validationLevel.value)
    
    const response = await fetch('http://127.0.0.1:8000/api/import/validate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        data: props.parsedData.preview_data,
        field_configs: props.fieldConfigs,
        validation_level: validationLevel.value
      })
    })
    
    console.log('验证响应状态:', response.status)
    
    if (response.ok) {
      const result = await response.json()
      console.log('验证结果:', result)
      validationReport.value = result
      
      // 更新数据状态
      allData.value = result.validated_data
      
      emit('validation-complete', result)
      
      if (result.summary.invalid_rows === 0) {
        ElMessage.success('验证通过，所有数据合格')
      } else {
        ElMessage.warning(`发现 ${result.summary.invalid_rows} 行数据有错误，请修正后重新验证`)
      }
    } else {
      let errorDetail = '验证失败'
      try {
        const error = await response.json()
        errorDetail = error.detail || error.message || `HTTP ${response.status}: ${response.statusText}`
      } catch (e) {
        errorDetail = `HTTP ${response.status}: ${response.statusText}`
      }
      errorMessage.value = errorDetail
      ElMessage.error(errorDetail)
    }
  } catch (error: any) {
    console.error('验证失败:', error)
    const errorMsg = error.message || '验证失败，请检查网络连接或后端服务是否正常运行'
    errorMessage.value = errorMsg
    ElMessage.error(errorMsg)
  } finally {
    validating.value = false
  }
}

// 获取行样式类名
const getRowClassName = ({ row }: { row: any }) => {
  if (!row.is_valid) {
    return 'error-row'
  }
  if (row.warnings && row.warnings.length > 0) {
    return 'warning-row'
  }
  return ''
}

// 获取行状态类型
const getRowStatusType = (row: any) => {
  if (!row.is_valid) {
    return 'danger'
  }
  if (row.warnings && row.warnings.length > 0) {
    return 'warning'
  }
  return 'success'
}

// 获取行状态文本
const getRowStatusText = (row: any) => {
  if (!row.is_valid) {
    return '错误'
  }
  if (row.warnings && row.warnings.length > 0) {
    return '警告'
  }
  return '合格'
}

// 获取单元格样式类名
const getCellClass = (row: any, fieldName: string) => {
  const errors = getCellErrors(row, fieldName)
  if (errors.length > 0) {
    return 'cell-error'
  }
  const warnings = getCellWarnings(row, fieldName)
  if (warnings.length > 0) {
    return 'cell-warning'
  }
  return ''
}

// 获取单元格错误
const getCellErrors = (row: any, fieldName: string) => {
  const targetField = props.fieldConfigs?.find(
    c => c.sourceField === fieldName
  )?.targetField
  
  if (!targetField || !row.errors) return []
  
  return row.errors
    .filter((e: any) => e.field === targetField)
    .map((e: any) => e.message)
}

// 获取单元格警告
const getCellWarnings = (row: any, fieldName: string) => {
  const targetField = props.fieldConfigs?.find(
    c => c.sourceField === fieldName
  )?.targetField
  
  if (!targetField || !row.warnings) return []
  
  return row.warnings
    .filter((w: any) => w.field === targetField)
    .map((w: any) => w.message)
}

// 是否正在编辑
const isEditing = (row: any, fieldName: string) => {
  return editingCell.value?.rowIndex === row.row_index && 
         editingCell.value?.field === fieldName
}

// 处理单元格点击
const handleCellClick = (row: any, field: any) => {
  editingCell.value = { rowIndex: row.row_index, field: field.sourceField }
  editingValue.value = getCellValue(row, field.sourceField)
}

// 完成编辑
const finishEdit = (row: any, field: any) => {
  if (editingCell.value) {
    row.data[field.sourceField] = editingValue.value
    editingCell.value = null
    editingValue.value = ''
    
    // 清除该单元格的验证结果（需要重新验证）
    if (row.errors) {
      const targetField = field.targetField
      row.errors = row.errors.filter((e: any) => e.field !== targetField)
    }
    if (row.warnings) {
      const targetField = field.targetField
      row.warnings = row.warnings.filter((w: any) => w.field !== targetField)
    }
    
    ElMessage.success('数据已更新，请重新验证')
  }
}

// 获取错误级别类型
const getErrorLevelType = (level: number) => {
  switch (level) {
    case 1:
      return 'danger'
    case 2:
      return 'warning'
    case 3:
      return 'info'
    default:
      return 'info'
  }
}

// 处理上一步
const handlePrevious = () => {
  emit('previous-step')
}

// 处理下一步
const handleNextStep = () => {
  if (!canProceed.value) {
    ElMessage.warning('请先修正所有错误')
    return
  }

  emit('next-step', {
    validatedData: allData.value,
    validationReport: validationReport.value
  })
}

// 处理修改错误行
const handleEditErrorRow = (row: any) => {
  // 设置当前编辑的行
  editingRow.value = row
  // 复制行数据到表单
  editFormData.value = { ...row.data }
  // 清除之前的错误信息
  editFieldErrors.value = {}
  // 打开弹窗
  editDialogVisible.value = true
}

// 获取字段错误信息
const getFieldError = (fieldName: string): string => {
  return editFieldErrors.value[fieldName] || ''
}

// 保存编辑并验证
const handleSaveEdit = async () => {
  if (!editingRow.value) return

  savingEdit.value = true
  editFieldErrors.value = {}

  try {
    // 准备验证数据
    const rowToValidate = {
      ...editingRow.value,
      data: editFormData.value
    }

    // 调用后端验证API
    const response = await fetch('http://127.0.0.1:8000/api/import/validate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        data: [editFormData.value],
        field_configs: props.fieldConfigs,
        validation_level: validationLevel.value
      })
    })

    if (response.ok) {
      const result = await response.json()

      // 更新行数据
      const rowIndex = allData.value.findIndex(r => r.row_index === editingRow.value.row_index)
      if (rowIndex !== -1) {
        const validatedRow = result.validated_data[0]

        // 更新数据
        allData.value[rowIndex].data = editFormData.value
        allData.value[rowIndex].errors = validatedRow.errors || []
        allData.value[rowIndex].warnings = validatedRow.warnings || []
        allData.value[rowIndex].is_valid = validatedRow.is_valid

        if (validatedRow.is_valid) {
          // 验证通过，更新统计信息
          if (validationReport.value) {
            validationReport.value.summary.valid_rows++
            validationReport.value.summary.invalid_rows--
            validationReport.value.summary.total_errors -= editingRow.value.errors?.length || 0
            validationReport.value.summary.total_warnings -= editingRow.value.warnings?.length || 0
          }
          ElMessage.success('修改成功，数据已验证通过！')
          // 关闭弹窗
          editDialogVisible.value = false
        } else {
          // 验证未通过，显示错误信息
          if (validatedRow.errors) {
            validatedRow.errors.forEach((error: any) => {
              if (error.field) {
                // 找到对应的sourceField
                const fieldConfig = props.fieldConfigs?.find(
                  (config: any) => config.targetField === error.field
                )
                if (fieldConfig) {
                  editFieldErrors.value[fieldConfig.sourceField] = error.message
                }
              }
            })
          }
          ElMessage.warning('数据仍有错误，请继续修改')
        }
      }
    } else {
      const error = await response.json()
      ElMessage.error(error.detail || '验证失败')
    }
  } catch (error: any) {
    console.error('保存编辑失败:', error)
    ElMessage.error(error.message || '保存失败')
  } finally {
    savingEdit.value = false
  }
}

// 处理删除错误行（旧方法，保留兼容）
const handleDeleteErrorRow = (row: any) => {
  const rowIndex = allData.value.findIndex(r => r.row_index === row.row_index)
  if (rowIndex !== -1) {
    // 从数据中删除该行
    allData.value.splice(rowIndex, 1)
    // 更新验证报告
    if (validationReport.value) {
      validationReport.value.summary.total_rows--
      validationReport.value.summary.invalid_rows--
    }
    ElMessage.success(`已删除第 ${row.row_index + 1} 行数据`)
  }
}

// 判断行是否有错误（用于显示操作按钮）
const hasRowErrors = (row: any): boolean => {
  return !row.is_valid || (row.errors && row.errors.length > 0)
}

// 处理编辑行（表格操作列使用）
const handleEditRow = (row: any, index: number) => {
  // 设置当前编辑的行
  editingRow.value = row
  // 复制行数据到表单
  editFormData.value = { ...row.data }
  // 清除之前的错误信息
  editFieldErrors.value = {}
  // 打开弹窗
  editDialogVisible.value = true
}

// 处理删除行（表格操作列使用）
const handleDeleteRow = (index: number) => {
  if (index >= 0 && index < allData.value.length) {
    const row = allData.value[index]
    // 从数据中删除该行
    allData.value.splice(index, 1)
    // 更新验证报告
    if (validationReport.value) {
      validationReport.value.summary.total_rows--
      if (!row.is_valid) {
        validationReport.value.summary.invalid_rows--
      } else {
        validationReport.value.summary.valid_rows--
      }
    }
    ElMessage.success(`已删除第 ${index + 1} 行数据`)
  }
}

// 导出错误数据状态
const exportingErrorData = ref(false)

// 导出错误数据（直接下载）
const exportErrorData = async () => {
  if (!errorRows.value || errorRows.value.length === 0) {
    ElMessage.warning('没有错误数据可导出')
    return
  }

  exportingErrorData.value = true

  try {
    // 获取原始表头
    const originalHeaders = displayFields.value.map(f => f.sourceField)

    // 准备错误数据
    const errorData = errorRows.value.map(row => ({
      ...row.data,
      error: row.errors?.map((e: any) => e.message).join('; ') || ''
    }))

    // 调用后端API导出
    const response = await fetch('/api/import/export-error-data', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        error_data: errorData,
        original_headers: originalHeaders,
        file_name: '数据验证'
      })
    })

    if (response.ok) {
      // 获取文件名
      const contentDisposition = response.headers.get('content-disposition')
      let fileName = '错误数据.xlsx'
      if (contentDisposition) {
        const match = contentDisposition.match(/filename="(.+)"/)
        if (match) {
          fileName = match[1]
        }
      }

      // 下载文件
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = fileName
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)

      ElMessage.success('错误数据已导出')
    } else {
      throw new Error('导出失败')
    }
  } catch (error) {
    console.error('导出错误数据失败:', error)
    ElMessage.error('导出错误数据失败')
  } finally {
    exportingErrorData.value = false
  }
}

// 导出错误数据（使用Windows另存为对话框）
const exportErrorDataWithDialog = async () => {
  if (!errorRows.value || errorRows.value.length === 0) {
    ElMessage.warning('没有错误数据可导出')
    return
  }

  exportingErrorData.value = true

  try {
    // 获取原始表头
    const originalHeaders = displayFields.value.map(f => f.sourceField)

    // 准备错误数据
    const errorData = errorRows.value.map(row => ({
      ...row.data,
      error: row.errors?.map((e: any) => e.message).join('; ') || ''
    }))

    // 生成默认文件名
    const today = new Date().toISOString().split('T')[0]
    const defaultFileName = `数据验证错误数据${today}.xlsx`

    // 使用File System Access API（如果支持）
    if ('showSaveFilePicker' in window) {
      try {
        const fileHandle = await (window as any).showSaveFilePicker({
          suggestedName: defaultFileName,
          types: [{
            description: 'Excel文件',
            accept: { 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'] }
          }]
        })

        // 调用后端API获取数据
        const response = await fetch('/api/import/export-error-data', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            error_data: errorData,
            original_headers: originalHeaders,
            file_name: '数据验证'
          })
        })

        if (response.ok) {
          const blob = await response.blob()
          const writable = await fileHandle.createWritable()
          await writable.write(blob)
          await writable.close()
          ElMessage.success('错误数据已保存')
        }
      } catch (err: any) {
        if (err.name !== 'AbortError') {
          console.error('保存失败:', err)
          // 如果File System Access API失败，回退到普通下载
          await exportErrorData()
        }
      }
    } else {
      // 浏览器不支持File System Access API，使用普通下载
      await exportErrorData()
    }
  } catch (error) {
    console.error('导出错误数据失败:', error)
    ElMessage.error('导出错误数据失败')
  } finally {
    exportingErrorData.value = false
  }
}

// 自定义指令：自动聚焦
const vFocus = {
  mounted: (el: HTMLElement) => {
    el.querySelector('input')?.focus()
  }
}

// 组件挂载时初始化
onMounted(() => {
  initData()
})
</script>

<style scoped>
.data-preview-panel {
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
  gap: 15px;
  align-items: center;
}

.panel-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.error-alert {
  margin-bottom: 10px;
}

.validation-summary {
  margin-bottom: 10px;
}

.table-section {
  width: 100%;
}

:deep(.error-row) {
  background-color: #fef0f0 !important;
}

:deep(.warning-row) {
  background-color: #fdf6ec !important;
}

.cell-error {
  background-color: #fef0f0;
  border: 1px solid #f56c6c;
  padding: 4px 6px;
  border-radius: 4px;
  cursor: pointer;
}

.cell-warning {
  background-color: #fdf6ec;
  border: 1px solid #e6a23c;
  padding: 4px 6px;
  border-radius: 4px;
  cursor: pointer;
}

.cell-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.cell-value {
  flex: 1;
}

.cell-error-message {
  color: #f56c6c;
  font-size: 11px;
  margin-top: 4px;
  line-height: 1.3;
  word-break: break-all;
}

.error-icon {
  margin-left: 5px;
  color: #f56c6c;
  flex-shrink: 0;
}

.error-details {
  margin-top: 20px;
}

.error-details h4 {
  margin: 0 0 15px 0;
  color: #606266;
}

.error-message {
  color: #f56c6c;
  margin-right: 10px;
}

.warning-message {
  color: #e6a23c;
  margin-right: 10px;
}

.error-section-title,
.warning-section-title,
.data-section-title {
  font-weight: 600;
  margin-bottom: 10px;
  color: #606266;
}

.error-section-title {
  color: #f56c6c;
}

.warning-section-title {
  color: #e6a23c;
}

.action-section {
  display: flex;
  justify-content: space-between;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}

/* 行操作按钮样式 */
.row-actions {
  display: flex;
  gap: 5px;
  justify-content: center;
}

.row-actions .el-button {
  padding: 4px 8px;
  font-size: 12px;
}

.row-actions .el-button .el-icon {
  margin-right: 2px;
  font-size: 12px;
}
</style>
