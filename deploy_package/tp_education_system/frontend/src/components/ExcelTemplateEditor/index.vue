<template>
  <div class="excel-editor">
    <div class="editor-header">
      <h3>Excel模板编辑 - {{ templateName }}</h3>
      <div class="header-actions">
        <el-button @click="goBack">返回</el-button>
        <el-button type="primary" @click="saveConfig" :loading="saving">
          保存配置
        </el-button>
      </div>
    </div>

    <div class="editor-container">
      <!-- 左侧：字段配置 -->
      <div class="config-panel">
        <div class="panel-header">
          <h4>字段配置</h4>
          <el-button type="primary" size="small" @click="addField">
            <el-icon><Plus /></el-icon> 添加字段
          </el-button>
        </div>

        <el-scrollbar class="field-list">
          <div
            v-for="(field, index) in fields"
            :key="index"
            class="field-item"
            :class="{ active: selectedFieldIndex === index }"
            @click="selectField(index)"
          >
            <div class="field-header">
              <span class="field-name">{{ field.field_label || '未命名' }}</span>
              <el-button
                type="danger"
                size="small"
                circle
                @click.stop="removeField(index)"
              >
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
            <div class="field-info">
              <el-tag size="small" type="info">{{ field.cell_ref || '未设置位置' }}</el-tag>
              <span class="data-source">{{ field.data_source || '未绑定' }}</span>
            </div>
          </div>
        </el-scrollbar>

        <!-- 字段属性编辑 -->
        <div v-if="selectedField" class="field-properties">
          <h4>字段属性</h4>
          <el-form :model="selectedField" label-width="80px" size="small">
            <el-form-item label="字段名称">
              <el-input v-model="selectedField.field_label" placeholder="如：姓名" />
            </el-form-item>
            <el-form-item label="字段标识">
              <el-input v-model="selectedField.field_name" placeholder="如：name" />
            </el-form-item>
            <el-form-item label="单元格位置">
              <el-input
                v-model="selectedField.cell_ref"
                placeholder="如：B2"
                @change="onCellRefChange"
              />
              <span class="form-tip">格式：列字母+行号，如 B2、C3</span>
            </el-form-item>
            <el-form-item label="数据源">
              <el-select
                v-model="selectedField.data_source"
                style="width: 100%"
                placeholder="选择数据来源"
                filterable
              >
                <el-option-group label="教师基本信息">
                  <el-option label="姓名" value="teacher_basic_info.name" />
                  <el-option label="身份证号" value="teacher_basic_info.id_card" />
                  <el-option label="性别" value="teacher_basic_info.gender" />
                  <el-option label="出生日期" value="teacher_basic_info.archive_birth_date" />
                  <el-option label="民族" value="teacher_basic_info.ethnicity" />
                  <el-option label="籍贯" value="teacher_basic_info.native_place" />
                  <el-option label="参加工作时间" value="teacher_basic_info.work_start_date" />
                  <el-option label="联系电话" value="teacher_basic_info.contact_phone" />
                </el-option-group>
              </el-select>
            </el-form-item>
          </el-form>
        </div>
      </div>

      <!-- 右侧：Excel预览 -->
      <div class="preview-panel">
        <div class="panel-header">
          <h4>Excel预览（保留原格式）</h4>
          <div class="preview-actions">
            <el-button type="info" size="small" @click="refreshPreview">
              <el-icon><Refresh /></el-icon> 刷新
            </el-button>
            <el-button type="success" size="small" @click="previewFilledExcel">
              <el-icon><View /></el-icon> 预览填充效果
            </el-button>
          </div>
        </div>

        <!-- 使用iframe显示后端生成的HTML -->
        <div class="excel-container">
          <iframe
            ref="previewFrame"
            :src="previewUrl"
            class="preview-iframe"
            frameborder="0"
            @load="onFrameLoad"
          />
        </div>

        <!-- 缩放控制 -->
        <div class="zoom-controls">
          <el-slider
            v-model="zoomLevel"
            :min="30"
            :max="150"
            :step="10"
            show-stops
            :format-tooltip="(val) => val + '%'"
            @change="updateZoom"
          />
          <span class="zoom-label">{{ zoomLevel }}%</span>
        </div>

        <!-- 使用说明 -->
        <div class="help-tips">
          <el-alert title="使用说明" type="info" :closable="false">
            <ol>
              <li>点击"添加字段"创建新字段</li>
              <li>在右侧Excel表格中点击要填充的单元格</li>
              <li>系统会自动识别单元格位置（如 B2）</li>
              <li>选择数据源（如 teacher_basic_info.name）</li>
              <li>点击"保存配置"完成</li>
            </ol>
          </el-alert>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Delete, View, Refresh } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()

// 模板信息
const templateId = computed(() => route.params.id as string)
const templateName = ref('')

// 字段列表
const fields = ref<any[]>([])
const selectedFieldIndex = ref<number | null>(null)
const saving = ref(false)

// 缩放级别
const zoomLevel = ref(80)

// iframe引用
const previewFrame = ref<HTMLIFrameElement | null>(null)

// 选中的字段
const selectedField = computed(() => {
  if (selectedFieldIndex.value === null) return null
  return fields.value[selectedFieldIndex.value]
})

// 已标记的单元格
const markedCells = computed(() => {
  return fields.value
    .filter(field => field.cell_ref)
    .map(field => {
      const pos = parseCellRef(field.cell_ref)
      return pos ? { row: pos.row, col: pos.col, label: field.field_label } : null
    })
    .filter(Boolean) as Array<{ row: number; col: number; label?: string }>
})

// 当前选中的单元格
const selectedCell = computed(() => {
  if (!selectedField.value?.cell_ref) return null
  const pos = parseCellRef(selectedField.value.cell_ref)
  return pos
})

// 预览URL
const previewUrl = computed(() => {
  const params = new URLSearchParams()
  params.append('marked_cells', JSON.stringify(markedCells.value))
  if (selectedCell.value) {
    params.append('selected_row', selectedCell.value.row.toString())
    params.append('selected_col', selectedCell.value.col.toString())
  }
  return `/api/templates/${templateId.value}/preview-html?${params.toString()}`
})

// 获取列字母（0 -> A, 1 -> B, ...）
const getColumnLetter = (index: number): string => {
  let result = ''
  let num = index
  while (num >= 0) {
    result = String.fromCharCode(65 + (num % 26)) + result
    num = Math.floor(num / 26) - 1
  }
  return result
}

// 单元格字母转索引（B2 -> {col: 1, row: 1}）
const parseCellRef = (ref: string): { col: number, row: number } | null => {
  const match = ref.match(/^([A-Z]+)(\d+)$/i)
  if (!match) return null

  const colLetters = match[1].toUpperCase()
  const row = parseInt(match[2]) - 1 // 转为0索引

  let col = 0
  for (let i = 0; i < colLetters.length; i++) {
    col = col * 26 + (colLetters.charCodeAt(i) - 65 + 1)
  }
  col-- // 转为0索引

  return { col, row }
}

// 索引转单元格字母（1, 1 -> B2）
const toCellRef = (col: number, row: number): string => {
  return getColumnLetter(col) + (row + 1)
}

// 刷新预览
const refreshPreview = () => {
  // URL变化会自动刷新iframe
}

// iframe加载完成
const onFrameLoad = () => {
  updateZoom()
  // 监听iframe的postMessage
  window.addEventListener('message', handleFrameMessage)
}

// 处理iframe消息
const handleFrameMessage = (event: MessageEvent) => {
  if (event.data && event.data.type === 'cellClick') {
    const { row, col } = event.data
    if (selectedField.value) {
      selectedField.value.cell_ref = toCellRef(col, row)
      selectedField.value.position_data = {
        col_index: col,
        row_index: row
      }
    }
  }
}

// 更新缩放
const updateZoom = () => {
  if (previewFrame.value && previewFrame.value.contentDocument) {
    const body = previewFrame.value.contentDocument.body
    if (body) {
      body.style.transform = `scale(${zoomLevel.value / 100})`
      body.style.transformOrigin = 'top left'
    }
  }
}

// 加载字段配置
const loadFields = async () => {
  try {
    const response = await fetch(`/api/templates/${templateId.value}/fields`)
    const result = await response.json()

    if (result.status === 'success') {
      fields.value = result.data.map((field: any) => ({
        ...field,
        cell_ref: field.position_data ? toCellRef(
          field.position_data.col_index || 0,
          field.position_data.row_index || 0
        ) : ''
      }))
    }
  } catch (error) {
    console.error('加载字段配置失败:', error)
  }
}



// 单元格位置变化
const onCellRefChange = (value: string) => {
  if (selectedField.value) {
    const pos = parseCellRef(value)
    if (pos) {
      selectedField.value.position_data = {
        col_index: pos.col,
        row_index: pos.row
      }
    }
  }
}

// 添加字段
const addField = () => {
  const newField = {
    field_name: `field_${fields.value.length + 1}`,
    field_label: `字段 ${fields.value.length + 1}`,
    field_type: 'text',
    cell_ref: '',
    position_data: {},
    data_source: '',
    default_value: ''
  }
  fields.value.push(newField)
  selectedFieldIndex.value = fields.value.length - 1
}

// 选择字段
const selectField = (index: number) => {
  selectedFieldIndex.value = index
}

// 删除字段
const removeField = async (index: number) => {
  try {
    await ElMessageBox.confirm('确定删除这个字段吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    fields.value.splice(index, 1)
    if (selectedFieldIndex.value === index) {
      selectedFieldIndex.value = null
    } else if (selectedFieldIndex.value !== null && selectedFieldIndex.value > index) {
      selectedFieldIndex.value--
    }
    ElMessage.success('删除成功')
  } catch {
    // 取消删除
  }
}

// 保存配置
const saveConfig = async () => {
  saving.value = true
  try {
    // 转换字段格式
    const saveFields = fields.value.map(field => ({
      ...field,
      position_type: 'cell',
      position_data: field.cell_ref ? {
        col_index: parseCellRef(field.cell_ref)?.col || 0,
        row_index: parseCellRef(field.cell_ref)?.row || 0
      } : {}
    }))

    const response = await fetch(`/api/templates/${templateId.value}/fields`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(saveFields)
    })

    const result = await response.json()
    if (result.status === 'success') {
      ElMessage.success('保存成功')
    } else {
      ElMessage.error(result.message || '保存失败')
    }
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

// 预览填充效果
const previewFilledExcel = async () => {
  try {
    const response = await fetch(`/api/templates/${templateId.value}/preview-excel?teacher_id=273`)
    if (response.ok) {
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      window.open(url, '_blank')
    } else {
      ElMessage.error('预览生成失败')
    }
  } catch (error) {
    ElMessage.error('预览失败')
  }
}

// 返回
const goBack = () => {
  router.push('/report/template-mgt')
}

onMounted(() => {
  loadFields()
})

// 清理事件监听器
import { onUnmounted } from 'vue'
onUnmounted(() => {
  window.removeEventListener('message', handleFrameMessage)
})
</script>

<style scoped>
.excel-editor {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
}

.editor-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.editor-container {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.config-panel {
  width: 380px;
  background: #fff;
  border-right: 1px solid #e4e7ed;
  display: flex;
  flex-direction: column;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #e4e7ed;
}

.panel-header h4 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
}

.preview-actions {
  display: flex;
  gap: 8px;
}

.field-list {
  flex: 1;
  padding: 8px;
}

.field-item {
  padding: 12px;
  margin-bottom: 8px;
  background: #f5f7fa;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.field-item:hover {
  background: #e6f2ff;
}

.field-item.active {
  background: #409eff;
  color: #fff;
}

.field-item.active .field-info .data-source {
  color: rgba(255, 255, 255, 0.8);
}

.field-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.field-name {
  font-weight: 500;
}

.field-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.field-info .data-source {
  font-size: 12px;
  color: #909399;
}

.field-properties {
  padding: 16px;
  border-top: 1px solid #e4e7ed;
  background: #fafafa;
}

.field-properties h4 {
  margin: 0 0 12px 0;
  font-size: 13px;
  font-weight: 600;
  color: #606266;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.preview-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #fff;
}

.excel-container {
  flex: 1;
  background: #f0f0f0;
  overflow: auto;
  position: relative;
}

.preview-iframe {
  width: 100%;
  height: 100%;
  border: none;
  background: #f0f0f0;
}

.zoom-controls {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 16px;
  background: #fff;
  border-top: 1px solid #e4e7ed;
}

.zoom-controls .el-slider {
  flex: 1;
}

.zoom-label {
  font-size: 12px;
  color: #606266;
  min-width: 40px;
  text-align: right;
}

.help-tips {
  padding: 16px;
  background: #fff;
  border-top: 1px solid #e4e7ed;
}

.help-tips ol {
  margin: 0;
  padding-left: 20px;
}

.help-tips li {
  margin: 4px 0;
}
</style>
