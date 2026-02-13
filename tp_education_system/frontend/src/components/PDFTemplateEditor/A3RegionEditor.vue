<template>
  <div class="a3-region-editor">
    <!-- 头部 -->
    <div class="editor-header">
      <div class="header-left">
        <el-button @click="goBack">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <h3>A3模板编辑器 - {{ templateName }}</h3>
      </div>
      <div class="header-actions">
        <el-button 
          type="warning" 
          :loading="detecting" 
          @click="detectA3Regions"
          v-if="!regionsDetected"
        >
          <el-icon><Grid /></el-icon>
          检测A3区域（第{{ currentPage }}页）
        </el-button>
        <el-button 
          type="success" 
          :loading="extracting" 
          @click="extractFromRegions"
          v-if="regionsDetected"
        >
          <el-icon><MagicStick /></el-icon>
          分区提取字段
        </el-button>
        <el-button type="primary" :loading="saving" @click="saveFields">
          <el-icon><Check /></el-icon>
          保存配置
        </el-button>
      </div>
    </div>

    <!-- 主体 -->
    <div class="editor-container">
      <!-- 左侧：区域和字段配置 -->
      <div class="config-panel">
        <!-- 区域列表 -->
        <div v-if="regionsDetected" class="regions-section">
          <div class="panel-header">
            <h4>编辑区域（第{{ currentPage }}页）</h4>
            <el-tag type="info">{{ regions.length }}个区域</el-tag>
          </div>
          <div class="region-list">
            <div
              v-for="region in regions"
              :key="region.id"
              class="region-item"
              :class="{ active: selectedRegionId === region.id }"
              @click="selectRegion(region.id)"
            >
              <div class="region-header">
                <span class="region-name">{{ region.name }}</span>
                <el-tag size="small" type="success" v-if="region.adjusted">已调整</el-tag>
              </div>
              <div class="region-info">
                <span>字段数: {{ getRegionFieldCount(region.id) }}</span>
              </div>
            </div>
          </div>
          <div class="region-actions">
            <el-button type="primary" size="small" @click="startAdjustRegions">
              <el-icon><Edit /></el-icon>
              调整区域边界
            </el-button>
          </div>
        </div>

        <!-- 字段列表 -->
        <div class="fields-section">
          <div class="panel-header">
            <h4>字段列表 ({{ fields.length }}个)</h4>
            <el-button type="primary" size="small" @click="addField">
              <el-icon><Plus /></el-icon>
              添加字段
            </el-button>
          </div>
          
          <!-- 所有字段列表 -->
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
                <el-tag size="small" v-if="field.region_id">区域{{ field.region_id }}</el-tag>
              </div>
            </div>
          </div>
        </div>

        <!-- 字段配置 -->
        <div v-if="selectedField" class="field-config">
          <h4>字段配置</h4>
          <el-form label-position="top">
            <el-form-item label="字段名称">
              <el-input v-model="selectedField.field_name" />
            </el-form-item>
            <el-form-item label="字段标签">
              <el-input v-model="selectedField.field_label" />
            </el-form-item>
            <el-form-item label="数据源">
              <el-select v-model="selectedField.data_source" placeholder="选择数据源" clearable>
                <el-option label="姓名" value="teacher_basic_info.name" />
                <el-option label="身份证号" value="teacher_basic_info.id_card" />
                <el-option label="性别" value="teacher_basic_info.gender" />
                <el-option label="出生日期" value="teacher_basic_info.birth_date" />
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
            <!-- 区域边界覆盖层 -->
            <div v-if="regionsDetected" class="regions-overlay">
              <div
                v-for="region in regions"
                :key="region.id"
                class="region-box"
                :class="{ active: selectedRegionId === region.id, adjusting: isAdjusting }"
                :style="getRegionStyle(region)"
                @click="selectRegion(region.id)"
              >
                <div class="region-label">{{ region.name }}</div>
                <!-- 四角标记 -->
                <div
                  v-for="(corner, idx) in region.corners"
                  :key="idx"
                  class="corner-marker"
                  :class="{ active: selectedCorner?.regionId === region.id && selectedCorner?.cornerIndex === idx }"
                  :style="getCornerStyle(corner, region)"
                  @mousedown.stop="startDragCorner(region.id, idx, $event)"
                >
                  <div class="corner-label">{{ corner.position }}</div>
                </div>
              </div>
            </div>
            <!-- 字段标记 -->
            <div v-if="fields.length > 0" class="fields-overlay">
              <div
                v-for="(field, index) in fields"
                :key="index"
                class="field-marker"
                :class="{ active: selectedFieldIndex === index }"
                :style="getFieldStyle(field)"
                @click="selectField(index)"
              >
                <div class="field-marker-label">{{ field.field_label || index + 1 }}</div>
              </div>
            </div>
          </div>
          <el-empty v-else description="加载PDF中..." />
        </div>

        <!-- 调整提示 -->
        <div v-if="isAdjusting" class="adjust-tips">
          <el-alert title="调整模式" type="warning" :closable="false">
            <p>拖拽四角标记调整区域边界，调整完成后点击"确认调整"</p>
            <el-button type="primary" size="small" @click="confirmAdjust">确认调整</el-button>
            <el-button size="small" @click="cancelAdjust">取消</el-button>
          </el-alert>
        </div>

        <!-- 使用说明 -->
        <div v-else class="help-tips">
          <el-alert title="使用说明" type="info" :closable="false">
            <ol>
              <li>A3双面格式：第1页=正面（区域1、2），第2页=背面（区域3、4）</li>
              <li>点击"检测A3区域"自动识别当前页的2个编辑区域</li>
              <li>检查四角位置是否正确，点击"调整区域边界"进行微调</li>
              <li>确认区域后，点击"分区提取字段"智能识别字段</li>
              <li>切换到另一页，重复上述步骤</li>
              <li>点击"保存配置"完成</li>
            </ol>
          </el-alert>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Delete, Check, Refresh, ArrowLeft, ArrowRight, MagicStick, Grid, Edit, ArrowDown } from '@element-plus/icons-vue'

interface Region {
  id: number
  name: string
  bounds: {
    x0: number
    y0: number
    x1: number
    y1: number
  }
  corners: {
    x: number
    y: number
    position: string
  }[]
  adjusted?: boolean
}

interface Field {
  field_name: string
  field_label: string
  data_source: string
  cell_ref: string
  position_data?: {
    x: number
    y: number
    page: number
  }
  default_value: string
  sort_order: number
  confidence?: number
  match_status?: string
  region_id?: number
}

const route = useRoute()
const router = useRouter()
const templateId = ref(route.params.id as string)
const templateName = ref('')

// 状态
const loading = ref(false)
const detecting = ref(false)
const extracting = ref(false)
const saving = ref(false)
const regionsDetected = ref(false)
const isAdjusting = ref(false)

// 数据
const regions = ref<Region[]>([])
const fields = ref<Field[]>([])
const previewImage = ref('')
const currentPage = ref(1)
const totalPages = ref(1)
const scale = ref(1)
const pdfImage = ref<HTMLImageElement | null>(null)

// 选中状态
const selectedRegionId = ref<number | null>(null)
const selectedFieldIndex = ref<number | null>(null)
const selectedCorner = ref<{ regionId: number; cornerIndex: number } | null>(null)
const dragStart = ref({ x: 0, y: 0 })

// 计算属性
const selectedField = computed(() => {
  if (selectedFieldIndex.value === null) return null
  return fields.value[selectedFieldIndex.value]
})

// 获取区域的字段数
const getRegionFieldCount = (regionId: number) => {
  return fields.value.filter(f => f.region_id === regionId).length
}

// 获取字段样式
const getFieldStyle = (field: Field) => {
  if (!field.position_data) return {}
  return {
    left: `${field.position_data.x * scale.value}px`,
    top: `${field.position_data.y * scale.value}px`,
    width: '60px',
    height: '20px'
  }
}

// 初始化
onMounted(() => {
  loadTemplateInfo()
  loadPreview()
})

// 加载模板信息
const loadTemplateInfo = async () => {
  try {
    const response = await fetch(`/api/templates/${templateId.value}`)
    const result = await response.json()
    if (result.status === 'success') {
      templateName.value = result.data.name
    }
  } catch (error) {
    console.error('加载模板信息失败:', error)
  }
}

// 返回
const goBack = () => {
  router.back()
}

// 检测A3四区域
const detectA3Regions = async () => {
  detecting.value = true
  try {
    // 先尝试加载已保存的区域
    const savedResponse = await fetch(`/api/templates/${templateId.value}/regions?page=${currentPage.value}`)
    const savedResult = await savedResponse.json()
    
    if (savedResult.status === 'success' && savedResult.regions && savedResult.regions.length > 0) {
      // 使用已保存的区域
      regions.value = savedResult.regions.map((r: any) => ({
        id: r.id,
        name: r.name,
        bounds: r.bounds,
        corners: [
          { x: r.bounds.x0, y: r.bounds.y0, position: '左上' },
          { x: r.bounds.x1, y: r.bounds.y0, position: '右上' },
          { x: r.bounds.x0, y: r.bounds.y1, position: '左下' },
          { x: r.bounds.x1, y: r.bounds.y1, position: '右下' }
        ],
        adjusted: true
      }))
      regionsDetected.value = true
      await nextTick()
      if (pdfImage.value) {
        // 获取页面宽度用于计算缩放比例
        const response = await fetch(`/api/templates/${templateId.value}/a3-regions?page=${currentPage.value}`)
        const result = await response.json()
        if (result.status === 'success' && result.page_width) {
          scale.value = pdfImage.value.width / result.page_width
        }
      }
      ElMessage.success(`已加载保存的区域设置，第${currentPage.value}页`)
    } else {
      // 没有已保存的区域，进行自动检测
      const response = await fetch(`/api/templates/${templateId.value}/a3-regions?page=${currentPage.value}`)
      const result = await response.json()

      if (result.status === 'success') {
        if (result.is_a3) {
          regions.value = result.regions
          regionsDetected.value = true
          // 计算缩放比例 - 等待图片加载完成
          await nextTick()
          if (pdfImage.value) {
            scale.value = pdfImage.value.width / result.page_width
            console.log('缩放比例:', scale.value, '图片宽度:', pdfImage.value.width, '页面宽度:', result.page_width)
          } else {
            // 如果图片还没加载，使用默认比例
            scale.value = 1
            console.warn('PDF图片未加载，使用默认缩放比例1')
          }
          // 根据页码显示不同的提示
          const pageNames = currentPage.value === 1 ? '区域1（左前）、区域2（右前）' : '区域3（左后）、区域4（右后）'
          ElMessage.success(`检测到A3格式，第${currentPage.value}页：${pageNames}`)
        } else {
          ElMessage.info(result.message)
        }
      } else {
        ElMessage.error('区域检测失败')
      }
    }
  } catch (error) {
    console.error('检测失败:', error)
    ElMessage.error('检测失败')
  } finally {
    detecting.value = false
  }
}

// 获取区域样式
const getRegionStyle = (region: Region) => {
  return {
    left: `${region.bounds.x0 * scale.value}px`,
    top: `${region.bounds.y0 * scale.value}px`,
    width: `${(region.bounds.x1 - region.bounds.x0) * scale.value}px`,
    height: `${(region.bounds.y1 - region.bounds.y0) * scale.value}px`
  }
}

// 获取角标样式 - 相对于区域框的偏移
const getCornerStyle = (corner: { x: number; y: number }, region: Region) => {
  // 计算相对于区域左上角的偏移
  const relativeX = (corner.x - region.bounds.x0) * scale.value - 10
  const relativeY = (corner.y - region.bounds.y0) * scale.value - 10
  return {
    left: `${relativeX}px`,
    top: `${relativeY}px`
  }
}

// 选择区域
const selectRegion = (regionId: number) => {
  selectedRegionId.value = regionId
}

// 开始调整区域
const startAdjustRegions = () => {
  isAdjusting.value = true
  ElMessage.info('拖拽四角标记调整区域边界')
}

// 开始拖拽角标
const startDragCorner = (regionId: number, cornerIndex: number, event: MouseEvent) => {
  if (!isAdjusting.value) return
  
  selectedCorner.value = { regionId, cornerIndex }
  dragStart.value = { x: event.clientX, y: event.clientY }
  
  document.addEventListener('mousemove', onDragCorner)
  document.addEventListener('mouseup', stopDragCorner)
}

// 拖拽中
const onDragCorner = (event: MouseEvent) => {
  if (!selectedCorner.value || !pdfImage.value) return
  
  const dx = (event.clientX - dragStart.value.x) / scale.value
  const dy = (event.clientY - dragStart.value.y) / scale.value
  
  const region = regions.value.find(r => r.id === selectedCorner.value!.regionId)
  if (region) {
    const corner = region.corners[selectedCorner.value.cornerIndex]
    corner.x += dx
    corner.y += dy
    
    // 更新边界
    updateRegionBounds(region)
    
    dragStart.value = { x: event.clientX, y: event.clientY }
  }
}

// 停止拖拽
const stopDragCorner = () => {
  selectedCorner.value = null
  document.removeEventListener('mousemove', onDragCorner)
  document.removeEventListener('mouseup', stopDragCorner)
}

// 更新区域边界
const updateRegionBounds = (region: Region) => {
  const xs = region.corners.map(c => c.x)
  const ys = region.corners.map(c => c.y)
  region.bounds.x0 = Math.min(...xs)
  region.bounds.x1 = Math.max(...xs)
  region.bounds.y0 = Math.min(...ys)
  region.bounds.y1 = Math.max(...ys)
  region.adjusted = true
}

// 确认调整并自动保存
const confirmAdjust = async () => {
  isAdjusting.value = false
  
  // 自动保存区域边框
  try {
    const response = await fetch(`/api/templates/${templateId.value}/regions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        page: currentPage.value,
        regions: regions.value.map(r => ({
          id: r.id,
          name: r.name,
          bounds: r.bounds
        }))
      })
    })
    
    const result = await response.json()
    if (result.status === 'success') {
      ElMessage.success('区域边界调整完成并已保存')
    } else {
      ElMessage.warning('区域边界调整完成，但保存失败')
    }
  } catch (error) {
    console.error('保存区域边框失败:', error)
    ElMessage.warning('区域边界调整完成，但保存失败')
  }
}

// 取消调整
const cancelAdjust = () => {
  isAdjusting.value = false
  // 重新加载原始区域
  detectA3Regions()
}

// 从区域提取字段
const extractFromRegions = async () => {
  extracting.value = true
  try {
    const response = await fetch(`/api/templates/${templateId.value}/a3-regions/extract`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        page: currentPage.value,
        regions: regions.value.map(r => ({
          id: r.id,
          bounds: r.bounds
        }))
      })
    })
    const result = await response.json()

    if (result.status === 'success') {
      console.log('提取结果:', result)
      // 转换字段格式
      const extractedFields = result.fields.map((f: any, index: number) => ({
        field_name: f.name || `field_${index}`,
        field_label: f.label || f.name || `字段${index + 1}`,
        data_source: '',
        cell_ref: `第${f.page}页 (${Math.round(f.x)},${Math.round(f.y)})`,
        position_data: {
          x: f.x,
          y: f.y,
          page: f.page
        },
        default_value: '',
        sort_order: index,
        confidence: f.confidence,
        match_status: f.confidence > 0.8 ? 'high' : f.confidence > 0.5 ? 'medium' : 'low',
        region_id: f.region_id
      }))
      
      // 使用解构赋值强制触发响应式更新
      fields.value = [...extractedFields]
      console.log('转换后的字段:', extractedFields)
      console.log('当前字段列表长度:', fields.value.length)
      ElMessage.success(`成功提取 ${extractedFields.length} 个字段`)
    } else {
      console.error('提取失败:', result)
      ElMessage.error('提取失败')
    }
  } catch (error) {
    console.error('提取失败:', error)
    ElMessage.error('提取失败')
  } finally {
    extracting.value = false
  }
}

// 加载预览
const loadPreview = async () => {
  loading.value = true
  try {
    const response = await fetch(`/api/templates/${templateId.value}/preview-pdf?page=${currentPage.value}`)
    const result = await response.json()
    
    if (result.image) {
      previewImage.value = result.image
      totalPages.value = result.total_pages
    }
  } catch (error) {
    console.error('加载预览失败:', error)
    ElMessage.error('加载预览失败')
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
    // 切换页面后重置区域检测状态
    regionsDetected.value = false
    regions.value = []
    fields.value = []
  }
}

// 下一页
const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
    loadPreview()
    // 切换页面后重置区域检测状态
    regionsDetected.value = false
    regions.value = []
    fields.value = []
  }
}

// 添加字段
const addField = () => {
  const newField: Field = {
    field_name: `field_${fields.value.length + 1}`,
    field_label: '',
    data_source: '',
    cell_ref: '',
    position_data: undefined,
    default_value: '',
    sort_order: fields.value.length,
    region_id: selectedRegionId.value || undefined
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
  } catch {
    // 用户取消
  }
}

// 保存字段（区域边框在确认调整时已自动保存）
const saveFields = async () => {
  saving.value = true
  try {
    const response = await fetch(`/api/templates/${templateId.value}/fields`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        fields: fields.value
      })
    })
    
    const result = await response.json()
    if (result.status === 'success') {
      ElMessage.success('字段保存成功')
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

// 处理图片点击
const handleImageClick = (event: MouseEvent) => {
  // 可以在这里添加点击标记字段的逻辑
}
</script>

<style scoped>
.a3-region-editor {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f5f7fa;
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: white;
  border-bottom: 1px solid #e4e7ed;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-left h3 {
  margin: 0;
  font-size: 18px;
  color: #303133;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.editor-container {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.config-panel {
  width: 360px;
  background: white;
  border-right: 1px solid #e4e7ed;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #e4e7ed;
}

.panel-header h4 {
  margin: 0;
  font-size: 16px;
  color: #303133;
}

.regions-section,
.fields-section {
  padding: 16px;
  border-bottom: 1px solid #e4e7ed;
}

.region-list {
  margin-top: 12px;
}

.region-item {
  padding: 12px;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.region-item:hover {
  border-color: #409eff;
}

.region-item.active {
  border-color: #409eff;
  background: #f0f9ff;
}

.region-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.region-name {
  font-weight: 500;
  color: #303133;
}

.region-info {
  font-size: 12px;
  color: #909399;
}

.region-actions {
  margin-top: 12px;
  display: flex;
  gap: 8px;
}

.field-list {
  margin-top: 12px;
  max-height: 300px;
  overflow-y: auto;
}

.field-item {
  padding: 12px;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.field-item:hover {
  border-color: #409eff;
}

.field-item.active {
  border-color: #409eff;
  background: #f0f9ff;
}

.field-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.field-name {
  font-weight: 500;
  color: #303133;
}

.field-info {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.field-config {
  padding: 16px;
  flex: 1;
}

.field-config h4 {
  margin: 0 0 16px 0;
  font-size: 16px;
  color: #303133;
}

.preview-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 16px;
  overflow: auto;
}

.pdf-container {
  flex: 1;
  background: white;
  border-radius: 4px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  padding: 16px;
  overflow: auto;
}

.pdf-wrapper {
  position: relative;
  display: inline-block;
}

.pdf-image {
  display: block;
  max-width: 100%;
}

/* 区域覆盖层 */
.regions-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.region-box {
  position: absolute;
  border: 2px dashed #409eff;
  background: rgba(64, 158, 255, 0.05);
  pointer-events: auto;
  cursor: pointer;
}

.region-box.active {
  border-color: #f56c6c;
  background: rgba(245, 108, 108, 0.1);
}

.region-box.adjusting {
  border-style: solid;
  border-width: 3px;
  border-color: #e6a23c;
  background: rgba(230, 162, 60, 0.1);
  box-shadow: 0 0 10px rgba(230, 162, 60, 0.5);
}

.region-label {
  position: absolute;
  top: -24px;
  left: 0;
  background: #409eff;
  color: white;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.region-box.active .region-label {
  background: #f56c6c;
}

/* 四角标记 */
.corner-marker {
  position: absolute;
  width: 24px;
  height: 24px;
  background: #409eff;
  border: 4px solid white;
  border-radius: 50%;
  cursor: nwse-resize;
  z-index: 1000;
  display: none;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.6);
  transition: transform 0.1s;
}

.corner-marker:hover {
  transform: scale(1.3);
  background: #66b1ff;
}

.region-box.adjusting .corner-marker {
  display: block !important;
}

.corner-marker.active {
  background: #f56c6c;
  transform: scale(1.4);
  border-color: #ffe6e6;
}

.corner-label {
  position: absolute;
  top: -24px;
  left: 50%;
  transform: translateX(-50%);
  background: #333;
  color: white;
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: bold;
  white-space: nowrap;
  box-shadow: 0 2px 4px rgba(0,0,0,0.3);
}

/* 字段标记 */
.fields-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.field-marker {
  position: absolute;
  width: 60px;
  height: 20px;
  background: rgba(103, 194, 58, 0.3);
  border: 2px solid #67c23a;
  border-radius: 4px;
  pointer-events: auto;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.field-marker:hover {
  background: rgba(103, 194, 58, 0.5);
}

.field-marker.active {
  background: rgba(245, 108, 108, 0.3);
  border-color: #f56c6c;
}

.field-marker-label {
  font-size: 10px;
  color: #333;
  font-weight: bold;
}

/* 提示 */
.adjust-tips,
.help-tips {
  margin-top: 16px;
}

.zoom-label {
  font-size: 12px;
  color: #666;
  min-width: 40px;
}
</style>
