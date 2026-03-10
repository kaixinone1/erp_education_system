<template>
  <el-dialog
    v-model="visible"
    :title="`手工编辑 - ${templateName}`"
    width="95%"
    top="5vh"
    :close-on-click-modal="false"
    :destroy-on-close="true"
    class="manual-editor-dialog"
  >
    <div class="editor-container">
      <!-- 工具栏 -->
      <div class="toolbar">
        <el-button-group>
          <el-button type="primary" @click="saveDocument" :loading="saving">
            <el-icon><Check /></el-icon>
            保存
          </el-button>
          <el-button @click="downloadDocument">
            <el-icon><Download /></el-icon>
            下载
          </el-button>
        </el-button-group>
        
        <el-divider direction="vertical" />
        
        <span class="file-info">
          <el-tag :type="fileType === 'docx' ? 'primary' : 'success'">
            {{ fileType.toUpperCase() }}
          </el-tag>
          <span class="edit-mode">手工编辑模式</span>
          <el-tooltip content="您正在编辑模板文件本身，修改会保存到模板中">
            <el-icon><QuestionFilled /></el-icon>
          </el-tooltip>
        </span>
      </div>

      <!-- 编辑器区域 -->
      <div class="editor-wrapper">
        <!-- Word 编辑器 -->
        <div v-if="fileType === 'docx'" class="word-editor">
          <iframe
            v-if="documentUrl"
            :src="documentUrl"
            width="100%"
            height="100%"
            frameborder="0"
          />
        </div>

        <!-- Excel 编辑器 -->
        <div v-else-if="fileType === 'xlsx' || fileType === 'xls'" class="excel-editor">
          <el-alert
            title="提示：您正在编辑模板文件。{{占位符}} 会在导出时自动替换为实际数据。"
            type="info"
            :closable="false"
            style="margin: 10px 20px 0 20px"
          />
          <div v-if="excelData.length > 0" class="spreadsheet-container">
            <table class="excel-table">
              <tbody>
                <tr v-for="(row, rowIndex) in excelData" :key="rowIndex">
                  <td 
                    v-for="(cell, colIndex) in row" 
                    :key="colIndex"
                    :class="{ 'cell-editing': editingCell === `${rowIndex}-${colIndex}` }"
                    @dblclick="startEdit(rowIndex, colIndex, cell)"
                  >
                    <input
                      v-if="editingCell === `${rowIndex}-${colIndex}`"
                      v-model="editingValue"
                      @blur="finishEdit(rowIndex, colIndex)"
                      @keyup.enter="finishEdit(rowIndex, colIndex)"
                      ref="editInput"
                      class="cell-input"
                    />
                    <span v-else class="cell-content">{{ cell }}</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- 加载中 -->
        <div v-else class="loading">
          <el-skeleton :rows="20" animated />
        </div>
      </div>
    </div>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Check, Download, QuestionFilled } from '@element-plus/icons-vue'

const props = defineProps<{
  modelValue: boolean
  templateId: string
  templateName: string
  fileType: string
  filePath: string
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
  (e: 'saved', data: any): void
}>()

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const saving = ref(false)
const documentUrl = ref('')
const excelData = ref<any[][]>([])
const editingCell = ref('')
const editingValue = ref('')
const originalData = ref<any[][]>([])

// 加载文档
const loadDocument = async () => {
  if (!props.templateId) return
  
  try {
    if (props.fileType === 'docx') {
      // Word 文档：使用微软 Office Online 或本地预览
      const response = await fetch(`/api/universal-templates/${encodeURIComponent(props.templateId)}/preview?teacher_id=0`)
      const result = await response.json()
      if (result.status === 'success' && result.preview_url) {
        documentUrl.value = result.preview_url
      }
    } else if (props.fileType === 'xlsx' || props.fileType === 'xls') {
      // Excel：加载数据到表格
      await loadExcelData()
    }
  } catch (e) {
    ElMessage.error('加载文档失败')
  }
}

// 加载 Excel 数据
const loadExcelData = async () => {
  try {
    const response = await fetch(`/api/universal-templates/${encodeURIComponent(props.templateId)}/excel-data`)
    const result = await response.json()
    if (result.status === 'success') {
      excelData.value = result.data || []
      originalData.value = JSON.parse(JSON.stringify(excelData.value))
    }
  } catch (e) {
    ElMessage.error('加载Excel数据失败')
  }
}

// 开始编辑单元格
const startEdit = (row: number, col: number, value: any) => {
  editingCell.value = `${row}-${col}`
  editingValue.value = String(value || '')
  nextTick(() => {
    const input = document.querySelector('.cell-input') as HTMLInputElement
    if (input) {
      input.focus()
      input.select()
    }
  })
}

// 完成编辑
const finishEdit = (row: number, col: number) => {
  if (editingCell.value === `${row}-${col}`) {
    excelData.value[row][col] = editingValue.value
    editingCell.value = ''
    editingValue.value = ''
  }
}

// 保存文档
const saveDocument = async () => {
  saving.value = true
  try {
    if (props.fileType === 'xlsx' || props.fileType === 'xls') {
      // 保存 Excel 数据
      const response = await fetch(`/api/universal-templates/${encodeURIComponent(props.templateId)}/save-excel`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ data: excelData.value })
      })
      const result = await response.json()
      if (result.status === 'success') {
        ElMessage.success('保存成功')
        originalData.value = JSON.parse(JSON.stringify(excelData.value))
        emit('saved', result)
      }
    } else {
      ElMessage.success('Word文档保存功能需要集成OnlyOffice或类似服务')
    }
  } catch (e) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

// 下载文档
const downloadDocument = () => {
  const link = document.createElement('a')
  link.href = `/api/universal-templates/download/${encodeURIComponent(props.templateId)}`
  link.download = `${props.templateName}.${props.fileType}`
  link.click()
}

// 监听对话框打开
watch(() => props.modelValue, (val) => {
  if (val) {
    loadDocument()
  }
})
</script>

<style scoped>
.manual-editor-dialog :deep(.el-dialog__body) {
  padding: 0;
  height: calc(90vh - 120px);
}

.editor-container {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.toolbar {
  padding: 15px 20px;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
  gap: 15px;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.edit-mode {
  color: #606266;
  font-size: 14px;
}

.editor-wrapper {
  flex: 1;
  overflow: auto;
  padding: 20px;
  background: #f5f7fa;
}

.word-editor,
.excel-editor {
  height: 100%;
  background: white;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.word-editor iframe {
  width: 100%;
  height: 100%;
  border: none;
}

.spreadsheet-container {
  padding: 20px;
  overflow: auto;
  max-height: calc(90vh - 200px);
}

.excel-table {
  border-collapse: collapse;
  background: white;
  table-layout: fixed;
}

.excel-table td {
  border: 1px solid #dcdfe6;
  padding: 6px 8px;
  min-width: 60px;
  max-width: 200px;
  height: 28px;
  cursor: pointer;
  font-size: 13px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.excel-table td:hover {
  background: #f5f7fa;
}

.excel-table td.cell-editing {
  padding: 0;
}

.cell-content {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.cell-input {
  width: 100%;
  height: 100%;
  border: none;
  padding: 8px 12px;
  font-size: 14px;
  outline: none;
  background: #ecf5ff;
}

.loading {
  padding: 40px;
}
</style>
