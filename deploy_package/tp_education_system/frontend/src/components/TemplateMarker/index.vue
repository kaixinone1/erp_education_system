<template>
  <div class="template-marker">
    <div class="marker-header">
      <h2>模板字段标记 - {{ templateName }}</h2>
      <div class="header-actions">
        <el-button @click="goBack">返回</el-button>
        <el-button type="primary" @click="saveFieldMappings" :loading="saving">
          保存标记配置
        </el-button>
      </div>
    </div>

    <div class="marker-container">
      <!-- 左侧：字段列表 -->
      <div class="field-panel">
        <div class="panel-header">
          <h3>字段列表</h3>
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
              <el-tag size="small" type="info">{{ field.position_type }}</el-tag>
              <span class="data-source">{{ field.data_source || '未绑定数据源' }}</span>
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
              <el-input v-model="selectedField.field_name" placeholder="如：teacher_name" />
            </el-form-item>
            <el-form-item label="字段类型">
              <el-select v-model="selectedField.field_type" style="width: 100%">
                <el-option label="文本" value="text" />
                <el-option label="日期" value="date" />
                <el-option label="数字" value="number" />
              </el-select>
            </el-form-item>
            <el-form-item label="位置类型">
              <el-select v-model="selectedField.position_type" style="width: 100%">
                <el-option label="表格单元格" value="table" />
                <el-option label="段落" value="paragraph" />
              </el-select>
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
            <el-form-item label="默认值">
              <el-input v-model="selectedField.default_value" placeholder="可选" />
            </el-form-item>
          </el-form>

          <!-- 位置信息 - 使用从1开始的编号，更符合用户习惯 -->
          <div v-if="selectedField.position_data" class="position-info">
            <h4>位置信息</h4>
            <div v-if="selectedField.position_type === 'table'" class="position-form">
              <el-form label-width="100px" size="small">
                <el-form-item label="表格序号">
                  <el-input-number
                    :model-value="(selectedField.position_data.table_index || 0) + 1"
                    @update:model-value="(val: number | undefined) => selectedField.position_data.table_index = (val || 1) - 1"
                    :min="1"
                  />
                  <span class="form-tip">从1开始计数</span>
                </el-form-item>
                <el-form-item label="行号">
                  <el-input-number
                    :model-value="(selectedField.position_data.row_index || 0) + 1"
                    @update:model-value="(val: number | undefined) => selectedField.position_data.row_index = (val || 1) - 1"
                    :min="1"
                  />
                  <span class="form-tip">从1开始计数</span>
                </el-form-item>
                <el-form-item label="列号">
                  <el-input-number
                    :model-value="(selectedField.position_data.cell_index || 0) + 1"
                    @update:model-value="(val: number | undefined) => selectedField.position_data.cell_index = (val || 1) - 1"
                    :min="1"
                  />
                  <span class="form-tip">从1开始计数</span>
                </el-form-item>
              </el-form>
            </div>
            <div v-else-if="selectedField.position_type === 'paragraph'" class="position-form">
              <el-form label-width="100px" size="small">
                <el-form-item label="段落序号">
                  <el-input-number
                    :model-value="(selectedField.position_data.paragraph_index || 0) + 1"
                    @update:model-value="(val: number | undefined) => selectedField.position_data.paragraph_index = (val || 1) - 1"
                    :min="1"
                  />
                  <span class="form-tip">从1开始计数</span>
                </el-form-item>
              </el-form>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧：文档预览和结构分析 -->
      <div class="preview-panel">
        <div class="panel-header">
          <h3>{{ isHtmlTemplate ? 'HTML预览' : '文档结构分析' }}</h3>
          <div class="preview-actions">
            <el-button v-if="!isHtmlTemplate" type="info" size="small" @click="analyzeStructure">
              <el-icon><Search /></el-icon>
              分析结构
            </el-button>
            <el-button type="primary" size="small" @click="openTemplate">
              <el-icon><View /></el-icon>
              {{ isHtmlTemplate ? '在新窗口打开' : '下载模板' }}
            </el-button>
          </div>
        </div>

        <!-- HTML预览 -->
        <div v-if="isHtmlTemplate && previewUrl" class="html-preview-container">
          <iframe
            :src="previewUrl"
            width="100%"
            height="600px"
            frameborder="0"
            style="background: white;"
          />
        </div>

        <!-- 文档结构信息（非HTML模板） -->
        <div v-if="!isHtmlTemplate && docStructure" class="structure-info">
          <el-alert
            :title="`文档包含 ${docStructure.表格总数} 个表格，${docStructure.段落总数} 个段落`"
            type="info"
            :closable="false"
            class="structure-summary"
          />
          <div v-for="table in docStructure.表格详情" :key="table.序号" class="table-info">
            <div class="table-title">表格 {{ table.序号 }} ({{ table.行数 }}行 × {{ table.列数 }}列)</div>
            <div v-for="(preview, idx) in table.内容预览" :key="idx" class="table-preview">
              {{ preview }}
            </div>
          </div>
        </div>

        <!-- 字段位置列表 -->
        <div v-if="!isHtmlTemplate" class="document-container">
          <div class="position-preview">
            <div class="preview-title">字段位置列表</div>
            <el-table :data="fields" size="small" border>
              <el-table-column type="index" label="序号" width="50" />
              <el-table-column prop="field_label" label="字段名称" min-width="120" />
              <el-table-column prop="position_type" label="位置类型" width="100">
                <template #default="{ row }">
                  <el-tag size="small" :type="row.position_type === 'table' ? 'primary' : 'success'">
                    {{ row.position_type === 'table' ? '表格' : '段落' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="位置信息" min-width="200">
                <template #default="{ row }">
                  <div v-if="row.position_type === 'table'" class="position-detail">
                    表格{{ row.position_data?.table_index + 1 }} - 
                    第{{ row.position_data?.row_index + 1 }}行 - 
                    第{{ row.position_data?.cell_index + 1 }}列
                  </div>
                  <div v-else class="position-detail">
                    第{{ row.position_data?.paragraph_index + 1 }}段
                  </div>
                </template>
              </el-table-column>
              <el-table-column prop="data_source" label="数据来源" min-width="150" show-overflow-tooltip />
            </el-table>
            <div v-if="fields.length === 0" class="no-fields-tip">
              <el-empty description="暂无字段，请先在左侧添加字段" />
            </div>
          </div>
        </div>

        <!-- 标记提示（非HTML模板） -->
        <div v-if="!isHtmlTemplate" class="marker-tips">
          <el-alert
            title="标记说明"
            type="info"
            :closable="false"
          >
            <template #default>
              <ol>
                <li>点击"添加字段"创建新字段</li>
                <li>在左侧填写字段名称和绑定数据源</li>
                <li>设置字段在文档中的位置（表格或段落）</li>
                <li>点击"保存标记配置"完成</li>
              </ol>
            </template>
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
import { Plus, Delete, View, Document, Search } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()

// 模板信息
const templateId = computed(() => route.params.id as string)
const templateName = ref('')

// 字段列表
const fields = ref<any[]>([])
const selectedFieldIndex = ref<number | null>(null)
const saving = ref(false)
const previewUrl = ref('')

// 文档结构
const docStructure = ref<any>(null)

// 模板类型
const isHtmlTemplate = ref(false)
const fileName = ref('')

// 选中的字段
const selectedField = computed(() => {
  if (selectedFieldIndex.value === null) return null
  return fields.value[selectedFieldIndex.value]
})

// 加载模板配置
const loadTemplateConfig = async () => {
  try {
    const response = await fetch(`/api/templates/${templateId.value}/fields`)
    const result = await response.json()

    if (result.status === 'success') {
      const fieldData = result.fields || result.data || []
      fields.value = fieldData.map((field: any) => ({
        ...field,
        position_data: typeof field.position_data === 'string' 
          ? JSON.parse(field.position_data) 
          : (field.position_data || {})
      }))
    }

    // 加载模板基本信息
    const templateResponse = await fetch('/api/templates/list')
    const templateResult = await templateResponse.json()
    if (templateResult.status === 'success') {
      const templateList = templateResult.templates || templateResult.data || []
      const template = templateList.find((t: any) => t.template_id === templateId.value)
      if (template) {
        templateName.value = template.template_name
        fileName.value = template.file_name || ''
        // 检测是否为HTML模板
        isHtmlTemplate.value = fileName.value.toLowerCase().endsWith('.html') || fileName.value.toLowerCase().endsWith('.htm')
      }
    }

    // 加载预览
    loadPreview()
  } catch (error) {
    ElMessage.error('加载模板配置失败')
  }
}

// 加载文档预览
const loadPreview = async () => {
  try {
    // 调用预览API
    const response = await fetch(`/api/templates/${templateId.value}/preview?teacher_id=273`)
    
    // 检查内容类型
    const contentType = response.headers.get('content-type') || ''
    
    if (contentType.includes('text/html')) {
      // HTML直接显示
      previewUrl.value = `/api/templates/${templateId.value}/preview?teacher_id=273`
    } else {
      // JSON响应
      const result = await response.json()
      if (result.status === 'success' && result.data && result.data.download_url) {
        previewUrl.value = result.data.download_url
      } else {
        previewUrl.value = `/api/templates/${templateId.value}/download`
      }
    }
  } catch (error) {
    console.error('加载预览失败:', error)
    // 出错时直接使用预览URL
    previewUrl.value = `/api/templates/${templateId.value}/preview?teacher_id=273`
  }
}

// 查看模板 - 在新窗口打开
const openTemplate = () => {
  const url = `/api/templates/${templateId.value}/download`
  window.open(url, '_blank')
}

// 分析文档结构
const analyzeStructure = async () => {
  try {
    const response = await fetch(`/api/templates/${templateId.value}/structure`)
    const result = await response.json()

    if (result.status === 'success') {
      docStructure.value = result.data
      ElMessage.success('文档结构分析完成')
    } else {
      ElMessage.error('分析失败')
    }
  } catch (error) {
    ElMessage.error('分析文档结构失败')
  }
}

// 添加字段
const addField = () => {
  const newField = {
    field_name: `field_${fields.value.length + 1}`,
    field_label: `字段 ${fields.value.length + 1}`,
    field_type: 'text',
    position_type: 'table',
    position_data: {
      table_index: 0,
      row_index: 0,
      cell_index: 0
    },
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

// 移除字段
const removeField = async (index: number) => {
  try {
    await ElMessageBox.confirm('确定要删除这个字段吗？', '提示', {
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

// 保存字段映射
const saveFieldMappings = async () => {
  saving.value = true
  try {
    const response = await fetch(`/api/templates/${templateId.value}/fields`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(fields.value)
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
const previewFilledDocument = () => {
  window.open(`/api/template-fill/preview?template_id=${templateId.value}&business_id=273`, '_blank')
}

// 返回
const goBack = () => {
  router.push('/report/template-mgt')
}

onMounted(() => {
  loadTemplateConfig()
})
</script>

<style scoped>
.template-marker {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
}

.marker-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
}

.marker-header h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.marker-container {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.field-panel {
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

.panel-header h3 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
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

.position-info {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px dashed #dcdfe6;
}

.preview-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #fff;
}

.preview-actions {
  display: flex;
  gap: 8px;
}

.document-container {
  flex: 1;
  padding: 16px;
  background: #f5f7fa;
  overflow: auto;
}

.document-frame {
  width: 100%;
  height: 100%;
  background: #fff;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
}

.no-preview {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.preview-placeholder {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fff;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
}

.position-preview {
  background: #fff;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  padding: 16px;
}

.position-detail {
  font-size: 12px;
  color: #606266;
}

.no-fields-tip {
  padding: 40px 0;
}

.form-tip {
  margin-left: 8px;
  font-size: 12px;
  color: #909399;
}

.structure-info {
  padding: 16px;
  background: #f5f7fa;
  border-bottom: 1px solid #e4e7ed;
}

.structure-summary {
  margin-bottom: 12px;
}

.table-info {
  margin-bottom: 12px;
  padding: 12px;
  background: #fff;
  border-radius: 4px;
  border: 1px solid #e4e7ed;
}

.table-title {
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
}

.table-preview {
  font-size: 12px;
  color: #606266;
  padding: 4px 0;
  border-bottom: 1px dashed #e4e7ed;
}

.table-preview:last-child {
  border-bottom: none;
}

.preview-title {
  font-weight: 600;
  color: #303133;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #e4e7ed;
}

.marker-tips {
  padding: 16px;
  background: #fff;
  border-top: 1px solid #e4e7ed;
}

.html-preview-container {
  flex: 1;
  padding: 16px;
  background: #f5f7fa;
  overflow: auto;
}

.html-preview-container iframe {
  width: 100%;
  height: 100%;
  min-height: 600px;
  background: white;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
}
</style>
