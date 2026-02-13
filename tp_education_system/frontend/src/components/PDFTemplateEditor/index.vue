<template>
  <div class="pdf-editor">
    <!-- 头部 -->
    <div class="editor-header">
      <div class="header-left">
        <el-button @click="goBack">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <h3>PDF模板编辑器 - {{ templateName }}</h3>
      </div>
      <div class="header-actions">
        <el-button type="success" :loading="extracting" @click="autoExtractFields">
          <el-icon><MagicStick /></el-icon>
          智能提取字段
        </el-button>
        <el-button type="primary" :loading="saving" @click="saveFields">
          <el-icon><Check /></el-icon>
          保存配置
        </el-button>
      </div>
    </div>

    <!-- 主体 -->
    <div class="editor-container">
      <!-- 左侧：字段配置 -->
      <div class="config-panel">
        <div class="panel-header">
          <h4>字段列表</h4>
          <el-button type="primary" size="small" @click="addField">
            <el-icon><Plus /></el-icon>
            添加字段
          </el-button>
        </div>

        <div class="field-list">
          <div
            v-for="(field, index) in fields"
            :key="index"
            class="field-item"
            :class="{ active: selectedFieldIndex === index }"
            @click="selectField(index)"
          >
            <div class="field-header">
              <span class="field-name">{{ field.field_label || '未命名字段' }}</span>
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
              <el-tag size="small" type="info">{{ field.cell_ref || '未标记' }}</el-tag>
              <el-tag
                v-if="field.confidence"
                size="small"
                :type="field.match_status === 'high' ? 'success' : field.match_status === 'medium' ? 'warning' : 'danger'"
              >
                匹配度: {{ Math.round(field.confidence * 100) }}%
              </el-tag>
            </div>
          </div>
        </div>

        <!-- 字段属性 -->
        <div v-if="selectedField" class="field-properties">
          <h4>字段属性</h4>
          <el-form label-width="80px" size="small">
            <el-form-item label="字段名称">
              <el-input v-model="selectedField.field_label" placeholder="如：姓名" />
            </el-form-item>
            <el-form-item label="坐标位置">
              <el-input v-model="selectedField.cell_ref" placeholder="点击右侧PDF标记位置" readonly>
                <template #append>
                  <el-button @click="clearPosition">清除</el-button>
                </template>
              </el-input>
            </el-form-item>
            <el-form-item label="数据源">
              <el-select v-model="selectedField.data_source" placeholder="选择数据源" style="width: 100%">
                <el-option label="姓名" value="teacher_basic_info.name" />
                <el-option label="身份证号" value="teacher_basic_info.id_card" />
                <el-option label="出生日期" value="teacher_basic_info.archive_birth_date" />
                <el-option label="民族" value="teacher_basic_info.ethnicity" />
                <el-option label="籍贯" value="teacher_basic_info.native_place" />
                <el-option label="联系电话" value="teacher_basic_info.contact_phone" />
                <el-option label="工作时间" value="teacher_basic_info.work_start_date" />
              </el-select>
            </el-form-item>
            <el-form-item label="默认值">
              <el-input v-model="selectedField.default_value" placeholder="可选" />
            </el-form-item>
          </el-form>
        </div>
      </div>

      <!-- 右侧：PDF预览 -->
      <div class="preview-panel">
        <div class="panel-header">
          <h4>PDF预览（第 {{ currentPage }}/{{ totalPages }} 页）</h4>
          <div class="preview-actions">
            <el-button-group>
              <el-button size="small" :disabled="currentPage <= 1" @click="prevPage">
                <el-icon><ArrowLeft /></el-icon> 上一页
              </el-button>
              <el-button size="small" :disabled="currentPage >= totalPages" @click="nextPage">
                下一页 <el-icon><ArrowRight /></el-icon>
              </el-button>
            </el-button-group>
            <el-button type="info" size="small" @click="refreshPreview" style="margin-left: 10px;">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
            <el-slider
              v-model="zoomLevel"
              :min="50"
              :max="150"
              :step="10"
              style="width: 120px; margin-left: 10px;"
              @change="refreshPreview"
            />
            <span class="zoom-label">{{ zoomLevel }}%</span>
          </div>
        </div>

        <!-- PDF图片预览 -->
        <div class="pdf-container" v-loading="loading">
          <div v-if="previewImage" class="pdf-wrapper">
            <img
              :src="previewImage"
              class="pdf-image"
              @click="handleImageClick"
              ref="pdfImage"
            />
          </div>
          <el-empty v-else description="加载PDF中..." />
        </div>

        <!-- 使用说明 -->
        <div class="help-tips">
          <el-alert title="使用说明" type="info" :closable="false">
            <ol>
              <li>点击"添加字段"创建新字段</li>
              <li>使用"上一页/下一页"切换PDF页面</li>
              <li>在PDF图片上点击要填充的位置</li>
              <li>系统会自动记录坐标位置和页码</li>
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
import { Plus, Delete, Check, Refresh, ArrowLeft, ArrowRight, MagicStick } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()

// 模板信息
const templateId = computed(() => route.params.id as string)
const templateName = ref('')

// 字段列表
const fields = ref<any[]>([])
const selectedFieldIndex = ref<number | null>(null)
const saving = ref(false)
const loading = ref(false)
const extracting = ref(false)

// 预览
const previewImage = ref('')
const zoomLevel = ref(100)
const pdfImage = ref<HTMLImageElement | null>(null)
const currentPage = ref(1)
const totalPages = ref(1)

// 选中的字段
const selectedField = computed(() => {
  if (selectedFieldIndex.value === null) return null
  return fields.value[selectedFieldIndex.value]
})

// 加载字段配置
const loadFields = async () => {
  try {
    const response = await fetch(`/api/templates/${templateId.value}/fields`)
    const result = await response.json()

    if (result.status === 'success') {
      fields.value = result.data || []
      // 解析坐标位置
      fields.value.forEach(field => {
        if (field.position_data && typeof field.position_data === 'string') {
          field.position_data = JSON.parse(field.position_data)
          if (field.position_data.x !== undefined && field.position_data.y !== undefined) {
            const page = field.position_data.page || 1
            field.cell_ref = `第${page}页 (${Math.round(field.position_data.x)},${Math.round(field.position_data.y)})`
          }
        }
      })
    }
  } catch (error) {
    console.error('加载字段失败:', error)
    ElMessage.error('加载字段配置失败')
  }
}

// 加载PDF预览
const loadPreview = async () => {
  loading.value = true
  try {
    // 构建标记参数
    const marks = fields.value
      .filter(f => f.position_data && f.position_data.x !== undefined)
      .map(f => ({
        x: f.position_data.x,
        y: f.position_data.y,
        page: f.position_data.page || 1,
        label: f.field_label || '字段'
      }))

    let url = `/api/templates/${templateId.value}/preview-pdf?marks=${encodeURIComponent(JSON.stringify(marks))}&page=${currentPage.value}`

    // 添加选中标记
    if (selectedField.value && selectedField.value.position_data) {
      const pos = selectedField.value.position_data
      url += `&selected_x=${pos.x}&selected_y=${pos.y}&selected_page=${pos.page || 1}`
    }

    const response = await fetch(url)
    const result = await response.json()

    if (result.image) {
      previewImage.value = result.image
      totalPages.value = result.total_pages || 1
    }
  } catch (error) {
    console.error('加载PDF预览失败:', error)
    ElMessage.error('加载PDF预览失败')
  } finally {
    loading.value = false
  }
}

// 刷新预览
const refreshPreview = () => {
  loadPreview()
}

// 上一页
const prevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--
    loadPreview()
  }
}

// 下一页
const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
    loadPreview()
  }
}

// 处理图片点击
const handleImageClick = (event: MouseEvent) => {
  if (!selectedField.value || !pdfImage.value) return

  const img = pdfImage.value
  const rect = img.getBoundingClientRect()

  // 计算点击位置相对于图片的坐标
  const x = event.clientX - rect.left
  const y = event.clientY - rect.top

  // 考虑缩放比例
  const scale = zoomLevel.value / 100
  const actualX = Math.round(x / scale)
  const actualY = Math.round(y / scale)

  // 更新字段位置（包含页码）
  selectedField.value.cell_ref = `第${currentPage.value}页 (${actualX},${actualY})`
  selectedField.value.position_data = { x: actualX, y: actualY, page: currentPage.value }

  // 刷新预览显示标记
  loadPreview()

  ElMessage.success(`已标记位置: 第${currentPage.value}页 (${actualX}, ${actualY})`)
}

// 添加字段
const addField = () => {
  const newField = {
    field_name: `field_${fields.value.length + 1}`,
    field_label: '',
    data_source: '',
    cell_ref: '',
    position_data: null,
    default_value: '',
    sort_order: fields.value.length
  }
  fields.value.push(newField)
  selectedFieldIndex.value = fields.value.length - 1
}

// 选择字段
const selectField = (index: number) => {
  selectedFieldIndex.value = index
  // 如果字段有页码信息，切换到对应页面
  const field = fields.value[index]
  if (field && field.position_data && field.position_data.page) {
    currentPage.value = field.position_data.page
  }
  loadPreview()
}

// 移除字段
const removeField = async (index: number) => {
  try {
    await ElMessageBox.confirm('确定要删除这个字段吗？', '提示', {
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
    loadPreview()
  } catch {
    // 取消删除
  }
}

// 清除位置
const clearPosition = () => {
  if (selectedField.value) {
    selectedField.value.cell_ref = ''
    selectedField.value.position_data = null
    loadPreview()
  }
}

// 智能提取字段
const autoExtractFields = async () => {
  extracting.value = true
  try {
    const response = await fetch(`/api/templates/${templateId.value}/extract-fields`)
    const result = await response.json()

    if (result.status === 'success') {
      // 清空现有字段
      fields.value = []

      // 添加提取的字段
      result.matches.forEach((match: any, index: number) => {
        const templateField = match.template_field
        const matchedField = match.matched_field

        fields.value.push({
          field_name: `field_${index + 1}`,
          field_label: templateField.name,
          data_source: matchedField ? matchedField.name : '',
          cell_ref: `第${templateField.page}页 (${Math.round(templateField.x)},${Math.round(templateField.y)})`,
          position_data: {
            x: Math.round(templateField.x),
            y: Math.round(templateField.y),
            page: templateField.page
          },
          default_value: '',
          sort_order: index,
          confidence: match.confidence,
          match_status: match.confidence > 0.8 ? 'high' : match.confidence > 0.5 ? 'medium' : 'low'
        })
      })

      ElMessage.success(`成功提取 ${fields.value.length} 个字段`)
      loadPreview()
    } else {
      ElMessage.error(result.message || '提取失败')
    }
  } catch (error) {
    console.error('提取字段失败:', error)
    ElMessage.error('提取字段失败')
  } finally {
    extracting.value = false
  }
}

// 保存字段配置
const saveFields = async () => {
  // 验证
  for (const field of fields.value) {
    if (!field.field_label) {
      ElMessage.warning('请填写所有字段的名称')
      return
    }
    if (!field.cell_ref) {
      ElMessage.warning(`字段 "${field.field_label}" 未标记位置`)
      return
    }
  }

  saving.value = true
  try {
    // 准备保存的数据
    const saveData = fields.value.map((field, index) => ({
      field_name: field.field_name,
      field_label: field.field_label,
      data_source: field.data_source,
      cell_ref: field.cell_ref,
      position_data: field.position_data,
      default_value: field.default_value,
      sort_order: index
    }))

    const response = await fetch(`/api/templates/${templateId.value}/fields`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ fields: saveData })
    })

    const result = await response.json()

    if (result.status === 'success') {
      ElMessage.success('保存成功')
    } else {
      ElMessage.error(result.message || '保存失败')
    }
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

// 返回
const goBack = () => {
  router.push('/report/template-mgt')
}

onMounted(() => {
  loadFields()
  loadPreview()
})
</script>

<style scoped>
.pdf-editor {
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

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
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
  display: flex;
  flex-direction: column;
  background: #fff;
  border-right: 1px solid #e4e7ed;
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
  align-items: center;
  gap: 8px;
}

.zoom-label {
  font-size: 12px;
  color: #606266;
  min-width: 40px;
}

.field-list {
  flex: 1;
  padding: 8px;
  overflow-y: auto;
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

.preview-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #fff;
}

.pdf-container {
  flex: 1;
  padding: 16px;
  background: #f0f0f0;
  overflow: auto;
  display: flex;
  justify-content: center;
  align-items: flex-start;
}

.pdf-wrapper {
  background: white;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.pdf-image {
  max-width: 100%;
  cursor: crosshair;
  display: block;
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
