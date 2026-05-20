<template>
  <!-- 模板管理页面 - 支持数据填报功能 -->
  <div class="template-management">
    <h2 class="page-title">模板管理</h2>

    <div class="operation-bar">
      <el-button type="primary" @click="showUploadDialog">
        <el-icon><Upload /></el-icon>
        上传模板
      </el-button>
      <el-button type="success" @click="showDataFillDialog" :disabled="templates.length === 0">
        <el-icon><Document /></el-icon>
        数据填报
      </el-button>
    </div>

    <el-card class="template-list-card">
      <el-table :data="templates" v-loading="loading" border>
        <el-table-column prop="name" label="模板名称" min-width="200" />
        <el-table-column prop="type" label="模板类型" width="150">
          <template #default="{ row }">
            <el-tag>{{ row.type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="placeholders" label="占位符" min-width="300">
          <template #default="{ row }">
            <el-tag v-for="(ph, index) in row.placeholders" :key="index" size="small" class="placeholder-tag">
              {{ ph }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="400" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="editTemplate(row)">
              编辑
            </el-button>
            <el-button type="info" size="small" @click="previewTemplate(row)">
              预览
            </el-button>
            <el-button type="success" size="small" @click="startDataFill(row)">
              填报
            </el-button>
            <el-button type="warning" size="small" @click="downloadTemplate(row)">
              下载
            </el-button>
            <el-button type="danger" size="small" @click="deleteTemplate(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="uploadDialogVisible" title="上传模板" width="600px">
      <el-form :model="uploadForm" label-width="100px">
        <el-form-item label="模板名称" required>
          <el-input v-model="uploadForm.name" placeholder="如：退休呈报表" />
        </el-form-item>
        <el-form-item label="模板类型" required>
          <el-select v-model="uploadForm.type" placeholder="选择类型" style="width: 100%">
            <el-option label="退休业务" value="retirement" />
            <el-option label="职务升降" value="position" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="模板文件" required>
          <el-upload
            ref="uploadRef"
            action="#"
            :auto-upload="false"
            :on-change="handleFileChange"
            :limit="1"
            accept=".doc,.docx,.pdf,.xlsx,.xls"
          >
            <el-button type="primary">选择文件</el-button>
            <template #tip>
              <div class="el-upload__tip">
                支持 .doc, .docx, .pdf, .xlsx, .xls 格式<br>
                Word文件中使用 {{占位符}} 标记需要填充的位置<br>
                Excel文件支持完整样式复制
              </div>
            </template>
          </el-upload>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="uploadForm.description" type="textarea" rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="uploadDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitUpload" :loading="uploading">
          上传
        </el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="dataFillDialogVisible" title="数据填报配置" width="90%" top="5vh">
      <div class="data-fill-container">
        <el-row :gutter="20">
          <el-col :span="24">
            <el-card shadow="hover" class="config-card">
              <template #header>
                <div class="card-header">
                  <span>第一步：标签筛选（限定统计口径）</span>
                </div>
              </template>
              <div class="tag-filter-section">
                <el-button type="primary" @click="showTagDialog = true">
                  <el-icon><PriceTag /></el-icon>
                  标签筛选 {{ selectedTags.length > 0 ? `(${selectedTags.length})` : '' }}
                </el-button>
                <div v-if="selectedTags.length > 0" class="selected-tags">
                  <el-tag 
                    v-for="tag in selectedTags" 
                    :key="tag" 
                    closable 
                    @close="removeTag(tag)"
                    style="margin-right: 8px; margin-bottom: 8px;"
                  >
                    {{ tag }}
                  </el-tag>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>

        <el-row :gutter="20" style="margin-top: 20px;">
          <el-col :span="24">
            <el-card shadow="hover" class="config-card">
              <template #header>
                <div class="card-header">
                  <span>第二步：字段映射配置</span>
                </div>
              </template>
              <el-table :data="fieldMappings" border size="small" max-height="400">
                <el-table-column prop="placeholder" label="占位符" width="180" fixed />
                
                <el-table-column prop="source_table" label="数据源表" width="200">
                  <template #default="{ row }">
                    <el-select 
                      v-model="row.source_table" 
                      placeholder="选择表"
                      @change="handleTableChangeForMapping(row)"
                      size="small"
                      style="width: 100%"
                    >
                      <el-option 
                        v-for="table in tableList" 
                        :key="table.name" 
                        :label="table.label" 
                        :value="table.name"
                      />
                    </el-select>
                  </template>
                </el-table-column>
                
                <el-table-column prop="source_field" label="源字段" width="180">
                  <template #default="{ row }">
                    <el-select 
                      v-model="row.source_field" 
                      placeholder="选择字段"
                      @change="handleFieldChangeForMapping(row)"
                      size="small"
                      style="width: 100%"
                      :disabled="!row.source_table"
                    >
                      <el-option 
                        v-for="field in row.availableFields" 
                        :key="field.name" 
                        :label="field.label" 
                        :value="field.name"
                      />
                    </el-select>
                  </template>
                </el-table-column>
                
                <el-table-column prop="dict_filter" label="字典筛选" width="250">
                  <template #default="{ row }">
                    <div v-if="row.hasDictionary" class="dict-filter-cell">
                      <el-select 
                        v-model="row.dict_values" 
                        placeholder="选择字典值"
                        multiple
                        collapse-tags
                        collapse-tags-tooltip
                        size="small"
                        style="width: 100%"
                      >
                        <el-option 
                          v-for="dict in row.dictionaryValues" 
                          :key="dict.value" 
                          :label="dict.label" 
                          :value="dict.value"
                        />
                      </el-select>
                    </div>
                    <span v-else style="color: #999;">-</span>
                  </template>
                </el-table-column>
                
                <el-table-column prop="aggregate_type" label="统计方式" width="130">
                  <template #default="{ row }">
                    <el-select v-model="row.aggregate_type" placeholder="选择" size="small" style="width: 100%">
                      <el-option label="直接取值" value="direct" />
                      <el-option label="计数" value="count" />
                      <el-option label="求和" value="sum" />
                      <el-option label="平均值" value="avg" />
                      <el-option label="最大值" value="max" />
                      <el-option label="最小值" value="min" />
                    </el-select>
                  </template>
                </el-table-column>
              </el-table>
            </el-card>
          </el-col>
        </el-row>

        <el-row :gutter="20" style="margin-top: 20px;">
          <el-col :span="24">
            <el-card shadow="hover" class="config-card">
              <template #header>
                <div class="card-header">
                  <span>第三步：操作</span>
                </div>
              </template>
              <div class="action-buttons">
                <el-button type="primary" size="large" @click="previewData" :loading="previewing">
                  <el-icon><View /></el-icon>
                  预览数据
                </el-button>
                <el-button type="success" size="large" @click="fillTemplate" :loading="filling">
                  <el-icon><Document /></el-icon>
                  填充模板
                </el-button>
                <el-button type="warning" size="large" @click="exportToExcel" :loading="exporting" :disabled="previewData.length === 0">
                  <el-icon><Download /></el-icon>
                  导出Excel
                </el-button>
              </div>
            </el-card>
          </el-col>
        </el-row>

        <el-row :gutter="20" style="margin-top: 20px;" v-if="previewResult.length > 0">
          <el-col :span="24">
            <el-card shadow="hover" class="result-card">
              <template #header>
                <div class="card-header">
                  <span>数据预览 ({{ previewResult.length }} 条)</span>
                </div>
              </template>
              <el-table :data="previewResult.slice(0, 50)" border size="small" max-height="300">
                <el-table-column 
                  v-for="col in previewColumns" 
                  :key="col" 
                  :prop="col" 
                  :label="col" 
                  min-width="120"
                />
              </el-table>
              <div v-if="previewResult.length > 50" style="margin-top: 10px; color: #999; text-align: center;">
                还有 {{ previewResult.length - 50 }} 条数据，请导出查看全部
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>
    </el-dialog>

    <el-dialog v-model="showTagDialog" title="标签筛选（多选）" width="500px">
      <el-checkbox-group v-model="selectedTags" class="tag-list">
        <el-checkbox 
          v-for="tag in tagList" 
          :key="tag.id" 
          :value="tag.name" 
          class="tag-item"
          style="margin-right: 15px; margin-bottom: 10px;"
        >
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
import { ref, reactive, onMounted, computed } from 'vue'
import { Upload, Search, Document, PriceTag, View, Download } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const uploading = ref(false)
const templates = ref<any[]>([])
const uploadDialogVisible = ref(false)
const uploadRef = ref<any>(null)

const uploadForm = reactive({
  name: '',
  type: '',
  description: '',
  file: null as File | null
})

const dataFillDialogVisible = ref(false)
const selectedTemplateForFill = ref<any>(null)
const tableList = ref<{name: string, label: string}[]>([])
const fieldMappings = ref<any[]>([])

const tagList = ref<{id: number, name: string}[]>([])
const selectedTags = ref<string[]>([])
const showTagDialog = ref(false)

const previewing = ref(false)
const filling = ref(false)
const exporting = ref(false)
const previewResult = ref<any[]>([])

const previewColumns = computed(() => {
  if (previewResult.value.length === 0) return []
  return Object.keys(previewResult.value[0])
})

const loadTemplates = async () => {
  loading.value = true
  try {
    const response = await fetch('/api/templates/list')
    if (response.ok) {
      const result = await response.json()
      if (result.status === 'success') {
        templates.value = result.templates.map((t: any) => ({
          id: t.template_id,
          name: t.template_name,
          type: 'document',
          placeholders: t.fields || [],
          description: t.description,
          created_at: t.created_at,
          file_path: t.file_path
        }))
      }
    }
  } catch (error) {
    console.error('加载模板列表失败:', error)
    ElMessage.error('加载模板列表失败')
  } finally {
    loading.value = false
  }
}

const loadTables = async () => {
  try {
    const response = await fetch('/api/template-data-fill/tables')
    if (response.ok) {
      const result = await response.json()
      if (result.status === 'success') {
        tableList.value = result.tables
      }
    }
  } catch (error) {
    console.error('加载表列表失败:', error)
  }
}

const loadTags = async () => {
  try {
    const response = await fetch('/api/aggregate-query/tags')
    if (response.ok) {
      const result = await response.json()
      if (result.status === 'success') {
        tagList.value = result.tags
      }
    }
  } catch (error) {
    console.error('加载标签列表失败:', error)
  }
}

const showUploadDialog = () => {
  uploadForm.name = ''
  uploadForm.type = ''
  uploadForm.description = ''
  uploadForm.file = null
  uploadDialogVisible.value = true
}

const handleFileChange = (file: any) => {
  uploadForm.file = file.raw
}

const submitUpload = async () => {
  if (!uploadForm.name || !uploadForm.type || !uploadForm.file) {
    ElMessage.warning('请填写完整信息')
    return
  }

  uploading.value = true
  try {
    const formData = new FormData()
    formData.append('file', uploadForm.file)
    formData.append('template_id', 'template_' + Date.now())
    formData.append('template_name', uploadForm.name)
    formData.append('description', uploadForm.description || '')

    const response = await fetch('/api/templates/upload', {
      method: 'POST',
      body: formData
    })

    if (response.ok) {
      const result = await response.json()
      if (result.status === 'success') {
        ElMessage.success('模板上传成功')
        uploadDialogVisible.value = false
        loadTemplates()
      } else {
        ElMessage.error(result.message || '上传失败')
      }
    } else {
      const error = await response.json()
      ElMessage.error(error.detail || '上传失败')
    }
  } catch (error) {
    console.error('上传模板失败:', error)
    ElMessage.error('上传模板失败')
  } finally {
    uploading.value = false
  }
}

const showDataFillDialog = () => {
  if (templates.value.length === 0) {
    ElMessage.warning('请先上传模板')
    return
  }
  selectedTemplateForFill.value = templates.value[0]
  initFieldMappings()
  dataFillDialogVisible.value = true
}

const startDataFill = (template: any) => {
  selectedTemplateForFill.value = template
  initFieldMappings()
  dataFillDialogVisible.value = true
}

const initFieldMappings = () => {
  if (!selectedTemplateForFill.value) return
  
  fieldMappings.value = selectedTemplateForFill.value.placeholders.map((ph: string) => ({
    placeholder: ph,
    source_table: '',
    source_field: '',
    availableFields: [],
    hasDictionary: false,
    dictionaryValues: [],
    dict_values: [],
    aggregate_type: 'direct'
  }))
}

const handleTableChangeForMapping = async (row: any) => {
  row.source_field = ''
  row.availableFields = []
  row.hasDictionary = false
  row.dictionaryValues = []
  row.dict_values = []
  
  if (!row.source_table) return
  
  try {
    const response = await fetch(`/api/template-data-fill/table-fields/${row.source_table}`)
    if (response.ok) {
      const result = await response.json()
      if (result.status === 'success') {
        row.availableFields = result.fields
      }
    }
  } catch (error) {
    console.error('加载字段列表失败:', error)
  }
}

const handleFieldChangeForMapping = async (row: any) => {
  row.hasDictionary = false
  row.dictionaryValues = []
  row.dict_values = []
  
  if (!row.source_table || !row.source_field) return
  
  try {
    const response = await fetch(
      `/api/template-data-fill/field-dictionary/${row.source_table}/${row.source_field}`
    )
    if (response.ok) {
      const result = await response.json()
      if (result.status === 'success' && result.has_dictionary) {
        row.hasDictionary = true
        row.dictionaryValues = result.values
      }
    }
  } catch (error) {
    console.error('检查字段字典失败:', error)
  }
}

const removeTag = (tag: string) => {
  selectedTags.value = selectedTags.value.filter(t => t !== tag)
}

const confirmTags = () => {
  showTagDialog.value = false
}

const previewData = async () => {
  if (fieldMappings.value.length === 0) {
    ElMessage.warning('请先配置字段映射')
    return
  }
  
  const hasValidMapping = fieldMappings.value.some(m => m.source_table && m.source_field)
  if (!hasValidMapping) {
    ElMessage.warning('请至少配置一个有效的字段映射')
    return
  }
  
  previewing.value = true
  try {
    const response = await fetch('/api/template-data-fill/preview', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        template_id: selectedTemplateForFill.value.id,
        tags: selectedTags.value.length > 0 ? selectedTags.value : undefined,
        field_mappings: fieldMappings.value
      })
    })
    
    if (response.ok) {
      const result = await response.json()
      if (result.status === 'success') {
        previewResult.value = result.data
        ElMessage.success(`预览成功，共 ${result.data.length} 条数据`)
      } else {
        ElMessage.error(result.message || '预览失败')
      }
    } else {
      ElMessage.error('预览失败')
    }
  } catch (error) {
    console.error('预览数据失败:', error)
    ElMessage.error('预览数据失败')
  } finally {
    previewing.value = false
  }
}

const fillTemplate = async () => {
  if (previewResult.value.length === 0) {
    ElMessage.warning('请先预览数据')
    return
  }
  
  filling.value = true
  try {
    const response = await fetch('/api/template-data-fill/fill', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        template_id: selectedTemplateForFill.value.id,
        tags: selectedTags.value.length > 0 ? selectedTags.value : undefined,
        field_mappings: fieldMappings.value,
        data: previewResult.value
      })
    })
    
    if (response.ok) {
      const result = await response.json()
      if (result.status === 'success') {
        ElMessage.success('模板填充成功')
        if (result.download_url) {
          window.open(result.download_url, '_blank')
        }
      } else {
        ElMessage.error(result.message || '填充失败')
      }
    } else {
      ElMessage.error('填充失败')
    }
  } catch (error) {
    console.error('填充模板失败:', error)
    ElMessage.error('填充模板失败')
  } finally {
    filling.value = false
  }
}

const exportToExcel = async () => {
  if (previewResult.value.length === 0) {
    ElMessage.warning('没有可导出的数据')
    return
  }
  
  exporting.value = true
  try {
    const response = await fetch('/api/template-data-fill/export', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        data: previewResult.value,
        filename: `${selectedTemplateForFill.value.name}_数据.xlsx`
      })
    })
    
    if (response.ok) {
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${selectedTemplateForFill.value.name}_数据.xlsx`
      a.click()
      window.URL.revokeObjectURL(url)
      ElMessage.success('导出成功')
    } else {
      ElMessage.error('导出失败')
    }
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败')
  } finally {
    exporting.value = false
  }
}

const editTemplate = (template: any) => {
  const filePath = template.file_path || ''
  if (filePath.toLowerCase().endsWith('.pdf')) {
    window.open(`/a3-template-editor/${template.id}`, '_blank')
  } else {
    window.open(`/pdf-template-editor/${template.id}`, '_blank')
  }
}

const previewTemplate = (template: any) => {
  ElMessage.info('预览功能开发中')
}

const downloadTemplate = async (template: any) => {
  try {
    window.open(`/api/templates/${template.id}/download`)
  } catch (error) {
    console.error('下载模板失败:', error)
    ElMessage.error('下载模板失败')
  }
}

const deleteTemplate = async (template: any) => {
  try {
    await ElMessageBox.confirm('确定要删除这个模板吗？', '提示', {
      type: 'warning'
    })

    const response = await fetch(`/api/templates/${template.id}`, {
      method: 'DELETE'
    })

    if (response.ok) {
      ElMessage.success('删除成功')
      loadTemplates()
    } else {
      ElMessage.error('删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除模板失败:', error)
      ElMessage.error('删除模板失败')
    }
  }
}

onMounted(async () => {
  await loadTemplates()
  await loadTables()
  await loadTags()
})
</script>

<style scoped>
.template-management {
  padding: 20px;
}

.page-title {
  margin: 0 0 20px 0;
  font-size: 20px;
  color: #1E40AF;
}

.operation-bar {
  margin-bottom: 20px;
}

.template-list-card {
  margin-bottom: 20px;
}

.placeholder-tag {
  margin-right: 5px;
  margin-bottom: 5px;
}

.data-fill-container {
  padding: 10px;
}

.config-card {
  margin-bottom: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
  font-size: 16px;
}

.tag-filter-section {
  display: flex;
  align-items: center;
  gap: 15px;
}

.selected-tags {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
}

.dict-filter-cell {
  width: 100%;
}

.action-buttons {
  display: flex;
  gap: 15px;
  justify-content: center;
}

.result-card {
  margin-bottom: 0;
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
}

.tag-item {
  margin-right: 15px;
  margin-bottom: 10px;
}
</style>
