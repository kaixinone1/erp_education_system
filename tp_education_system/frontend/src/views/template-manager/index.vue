<template>
  <div class="template-manager">
    <el-card class="page-header">
      <template #header>
        <div class="header-content">
          <span class="title">模板管理</span>
          <div class="header-actions">
            <el-button type="primary" @click="showChecklistDialog = true" v-if="activeTab === 'checklist'">
              <el-icon><Plus /></el-icon>
              新建清单模板
            </el-button>
            <el-button type="primary" @click="showUploadDialog = true" v-else>
              <el-icon><Upload /></el-icon>
              上传模板
            </el-button>
          </div>
        </div>
      </template>
      
      <div class="description">
        统一管理文档模板、清单模板和中间表模板，支持字段映射、智能填报、业务清单推送和动态中间表创建
      </div>
    </el-card>

    <!-- 标签页切换 -->
    <el-tabs v-model="activeTab" class="template-tabs">
      <el-tab-pane label="文档模板" name="document">
        <!-- 文档模板列表 -->
        <el-card class="template-list">
          <el-table :data="templates" v-loading="loading">
            <el-table-column prop="template_name" label="模板名称" min-width="200" />
            <el-table-column prop="file_name" label="文件名" min-width="200" />
            <el-table-column prop="description" label="描述" min-width="250" show-overflow-tooltip />
            <el-table-column prop="created_at" label="创建时间" width="180" />
            <el-table-column label="操作" width="320" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" size="small" @click="editTemplate(row)">
                  标记字段
                </el-button>
                <el-button type="warning" size="small" @click="configFieldMapping(row)">
                  字段映射
                </el-button>
                <el-button type="success" size="small" @click="previewTemplate(row)">
                  预览
                </el-button>
                <el-button type="danger" size="small" @click="deleteTemplate(row)">
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>
      
      <el-tab-pane label="清单模板" name="checklist">
        <!-- 清单模板列表 -->
        <el-card class="template-list">
          <el-table :data="checklistTemplates" v-loading="checklistLoading">
            <el-table-column prop="清单名称" label="清单名称" min-width="200" />
            <el-table-column prop="触发条件" label="触发条件" min-width="200">
              <template #default="{ row }">
                <el-tag v-if="row.触发条件?.target_status">
                  {{ row.触发条件.target_status.join(', ') }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="任务项列表" label="任务数" width="100">
              <template #default="{ row }">
                {{ row.任务项列表?.length || 0 }} 项
              </template>
            </el-table-column>
            <el-table-column prop="是否有效" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.是否有效 ? 'success' : 'danger'">
                  {{ row.是否有效 ? '有效' : '无效' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="250" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" size="small" @click="editChecklistTemplate(row)">
                  编辑
                </el-button>
                <el-button type="success" size="small" @click="previewChecklistTemplate(row)">
                  预览
                </el-button>
                <el-button type="danger" size="small" @click="deleteChecklistTemplate(row)">
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>
      
      <el-tab-pane label="中间表模板" name="intermediate">
        <!-- 中间表模板列表 -->
        <el-card class="template-list">
          <template #header>
            <div class="card-header">
              <span>中间表模板列表</span>
              <el-button type="primary" size="small" @click="createIntermediateTable">
                <el-icon><Plus /></el-icon>
                新建中间表
              </el-button>
            </div>
          </template>
          <el-table :data="intermediateTables" v-loading="intermediateLoading">
            <el-table-column prop="chinese_name" label="表中文名" min-width="200" />
            <el-table-column prop="table_name" label="表英文名" min-width="200" />
            <el-table-column prop="field_count" label="字段数" width="100" />
            <el-table-column prop="created_at" label="创建时间" width="180" />
            <el-table-column label="操作" width="300" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" size="small" @click="editIntermediateTable(row)">
                  设计
                </el-button>
                <el-button type="success" size="small" @click="previewIntermediateTable(row)">
                  预览
                </el-button>
                <el-button type="warning" size="small" @click="manageIntermediateData(row)">
                  数据
                </el-button>
                <el-button type="danger" size="small" @click="deleteIntermediateTable(row)">
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>
    </el-tabs>

    <!-- 上传对话框 -->
    <el-dialog
      v-model="showUploadDialog"
      title="上传文档模板"
      width="600px"
    >
      <el-form :model="uploadForm" label-width="100px">
        <el-form-item label="模板文件" required>
          <el-upload
            ref="uploadRef"
            action="#"
            :auto-upload="false"
            :on-change="handleFileChange"
            :limit="1"
            accept=".docx,.xlsx,.xls,.pdf,.html,.htm"
          >
            <el-button type="primary">选择文件</el-button>
            <template #tip>
              <div class="el-upload__tip">
                支持 .docx (WORD)、.xlsx/.xls (EXCEL)、.pdf (PDF) 和 .html (网页) 格式<br>
                <strong>PDF格式：</strong>上传后可在PDF图片上直接点击标记字段位置<br>
                <strong>HTML格式：</strong>上传后可直接在网页表单中填写数据
              </div>
            </template>
          </el-upload>
        </el-form-item>
        <el-form-item label="模板ID" required>
          <el-input v-model="uploadForm.template_id" placeholder="如：retirement_report" />
        </el-form-item>
        <el-form-item label="模板名称" required>
          <el-input v-model="uploadForm.template_name" placeholder="如：职工退休呈报表" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="uploadForm.description" type="textarea" rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showUploadDialog = false">取消</el-button>
        <el-button type="primary" @click="submitUpload" :loading="uploading">
          上传
        </el-button>
      </template>
    </el-dialog>

    <!-- 字段标记对话框 -->
    <el-dialog
      v-model="showMarkDialog"
      title="标记字段位置"
      width="1200px"
      fullscreen
    >
      <div class="mark-container">
        <!-- 左侧：字段列表 -->
        <div class="field-list">
          <div class="field-list-header">
            <h3>字段列表</h3>
            <el-button type="primary" size="small" @click="addField">
              <el-icon><Plus /></el-icon>
              添加字段
            </el-button>
          </div>
          <el-table :data="fieldList" size="small">
            <el-table-column prop="field_label" label="字段名称" min-width="120">
              <template #default="{ row }">
                <el-input v-model="row.field_label" size="small" />
              </template>
            </el-table-column>
            <el-table-column prop="field_name" label="字段标识" min-width="120">
              <template #default="{ row }">
                <el-input v-model="row.field_name" size="small" />
              </template>
            </el-table-column>
            <el-table-column prop="data_source" label="数据来源" min-width="150">
              <template #default="{ row }">
                <el-select v-model="row.data_source" size="small" placeholder="选择数据来源">
                  <el-option label="教师姓名" value="teacher_basic_info.name" />
                  <el-option label="身份证号" value="teacher_basic_info.id_card" />
                  <el-option label="性别" value="teacher_basic_info.gender" />
                  <el-option label="出生日期" value="teacher_basic_info.archive_birth_date" />
                  <el-option label="民族" value="teacher_basic_info.ethnicity" />
                  <el-option label="籍贯" value="teacher_basic_info.native_place" />
                  <el-option label="参加工作时间" value="teacher_basic_info.work_start_date" />
                  <el-option label="联系电话" value="teacher_basic_info.contact_phone" />
                </el-select>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="80">
              <template #default="{ $index }">
                <el-button type="danger" size="small" @click="removeField($index)">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </template>
            </el-table-column>
          </el-table>
          <div class="field-actions">
            <el-button type="primary" @click="saveFields" :loading="saving">
              保存字段配置
            </el-button>
          </div>
        </div>

        <!-- 右侧：文档预览 -->
        <div class="document-preview">
          <div class="preview-header">
            <h3>文档预览</h3>
            <el-alert
              title="在左侧添加字段后，系统会自动识别文档中的对应位置"
              type="info"
              :closable="false"
            />
          </div>
          <div class="preview-content">
            <iframe
              v-if="currentTemplate"
              :src="previewUrl"
              width="100%"
              height="600px"
              frameborder="0"
            />
            <div v-else class="no-preview">
              请先上传模板
            </div>
          </div>
        </div>
      </div>
    </el-dialog>

    <!-- 清单模板对话框 -->
    <el-dialog
      v-model="showChecklistDialog"
      :title="editingChecklist ? '编辑清单模板' : '新建清单模板'"
      width="800px"
    >
      <el-form :model="checklistForm" label-width="100px">
        <el-form-item label="清单名称" required>
          <el-input v-model="checklistForm.清单名称" placeholder="如：职工退休业务清单" />
        </el-form-item>
        
        <el-form-item label="触发条件" required>
          <el-select 
            v-model="checklistForm.触发条件.target_status" 
            multiple
            placeholder="选择触发状态"
            style="width: 100%"
          >
            <el-option label="退休" value="退休" />
            <el-option label="离职" value="离职" />
            <el-option label="调动" value="调动" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="关联模板">
          <el-select 
            v-model="checklistForm.关联模板ID" 
            placeholder="选择关联的文档模板（可选）"
            style="width: 100%"
            clearable
          >
            <el-option 
              v-for="template in availableTemplates" 
              :key="template.template_id"
              :label="template.template_name"
              :value="template.template_id"
            />
          </el-select>
          <div class="form-tip">关联模板后，清单任务将自动跳转到模板填报页面</div>
        </el-form-item>
        
        <el-form-item label="是否有效">
          <el-switch v-model="checklistForm.是否有效" />
        </el-form-item>
        
        <el-form-item label="任务项列表">
          <div class="task-items">
            <div v-for="(task, index) in checklistForm.任务项列表" :key="index" class="task-item">
              <el-card shadow="hover">
                <template #header>
                  <div class="task-header">
                    <span>任务 {{ index + 1 }}</span>
                    <el-button type="danger" size="small" @click="removeTaskItem(index)">
                      <el-icon><Delete /></el-icon>
                    </el-button>
                  </div>
                </template>
                <el-form :model="task" label-width="80px">
                  <el-form-item label="任务标题">
                    <el-input v-model="task.标题" placeholder="如：填写退休呈报表" />
                  </el-form-item>
                  <el-form-item label="任务目标">
                    <el-input v-model="task.目标" placeholder="如：html_retirement_report" />
                  </el-form-item>
                  <el-form-item label="模板ID">
                    <el-input v-model="task.参数.template_id" placeholder="关联的模板ID（可选）" />
                  </el-form-item>
                </el-form>
              </el-card>
            </div>
            <el-button type="primary" @click="addTaskItem" class="add-task-btn">
              <el-icon><Plus /></el-icon>
              添加任务项
            </el-button>
          </div>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showChecklistDialog = false">取消</el-button>
        <el-button type="primary" @click="saveChecklistTemplate">
          {{ editingChecklist ? '更新' : '创建' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Upload, Plus, Delete } from '@element-plus/icons-vue'

const router = useRouter()

// 标签页
const activeTab = ref('document')

// 中间表模板数据
const intermediateTables = ref([])
const intermediateLoading = ref(false)
const showIntermediateDialog = ref(false)

// 文档模板数据
const templates = ref([])
const loading = ref(false)
const showUploadDialog = ref(false)
const showMarkDialog = ref(false)
const uploading = ref(false)
const saving = ref(false)
const currentTemplate = ref(null)
const fieldList = ref([])
const uploadRef = ref()
const selectedFile = ref<File | null>(null)

const uploadForm = ref({
  template_id: '',
  template_name: '',
  description: ''
})

// 清单模板数据
const checklistTemplates = ref([])
const checklistLoading = ref(false)
const showChecklistDialog = ref(false)
const checklistForm = ref({
  id: null,
  清单名称: '',
  触发条件: { target_status: ['退休'] },
  任务项列表: [],
  是否有效: true,
  关联模板ID: ''
})
const editingChecklist = ref(false)
const availableTemplates = ref([])

const previewUrl = computed(() => {
  if (!currentTemplate.value) return ''
  return `/api/templates/${currentTemplate.value.template_id}/preview?teacher_id=273`
})

// 获取模板列表
const loadTemplates = async () => {
  loading.value = true
  try {
    const response = await fetch('/api/templates/list')
    const result = await response.json()
    if (result.status === 'success') {
      templates.value = result.templates || []
    }
  } catch (error) {
    ElMessage.error('获取模板列表失败')
  } finally {
    loading.value = false
  }
}

// 文件选择 - 自动提取模板ID和模板名称
const handleFileChange = (file: any) => {
  selectedFile.value = file.raw

  // 从文件名自动提取模板信息
  if (file.raw && file.raw.name) {
    const fileName = file.raw.name
    // 支持 .docx, .xlsx, .xls, .pdf 格式
    const nameWithoutExt = fileName.replace(/\.(docx|xlsx|xls|pdf)$/i, '')

    // 自动填写模板名称（直接使用文件名）
    uploadForm.value.template_name = nameWithoutExt

    // 自动生成模板ID（去除特殊字符，用下划线连接）
    const templateId = nameWithoutExt
      .replace(/[\s\-—]+/g, '_')  // 空格、破折号替换为下划线
      .replace(/[^\w\u4e00-\u9fa5]/g, '')  // 去除其他特殊字符
      .toLowerCase()  // 转为小写

    uploadForm.value.template_id = templateId
  }
}

// 提交上传
const submitUpload = async () => {
  if (!uploadForm.value.template_id || !uploadForm.value.template_name) {
    ElMessage.warning('请填写模板ID和名称')
    return
  }
  if (!selectedFile.value) {
    ElMessage.warning('请选择模板文件')
    return
  }

  uploading.value = true
  try {
    const formData = new FormData()
    formData.append('template_id', uploadForm.value.template_id)
    formData.append('template_name', uploadForm.value.template_name)
    formData.append('description', uploadForm.value.description)
    formData.append('file', selectedFile.value)

    const response = await fetch('/api/templates/upload', {
      method: 'POST',
      body: formData
    })

    const result = await response.json()
    if (result.status === 'success') {
      // 显示自动分析结果
      const fieldsCount = result.fields_count || 0
      if (fieldsCount > 0) {
        ElMessage.success(`上传成功！自动识别了 ${fieldsCount} 个可填充字段`)
      } else {
        ElMessage.success('上传成功！未自动识别到字段，请手动标记')
      }

      showUploadDialog.value = false
      loadTemplates()
      // 重置表单
      uploadForm.value = { template_id: '', template_name: '', description: '' }
      selectedFile.value = null
      uploadRef.value?.clearFiles()
    } else {
      ElMessage.error(result.message || '上传失败')
    }
  } catch (error) {
    ElMessage.error('上传失败')
  } finally {
    uploading.value = false
  }
}

// 编辑模板（标记字段）- 根据文件类型跳转到不同编辑器
const editTemplate = (template: any) => {
  const fileName = template.file_name?.toLowerCase() || ''
  if (fileName.endsWith('.pdf')) {
    // PDF文件使用A3四区域编辑器
    router.push(`/a3-template-editor/${template.template_id}`)
  } else if (fileName.endsWith('.xlsx') || fileName.endsWith('.xls')) {
    // Excel文件使用Excel编辑器
    router.push(`/excel-template-editor/${template.template_id}`)
  } else if (fileName.endsWith('.html') || fileName.endsWith('.htm')) {
    // HTML文件使用HTML可视化编辑器
    router.push(`/html-template-editor/${template.template_id}`)
  } else {
    // Word文件使用TemplateMarker编辑器
    router.push(`/template-marker/${template.template_id}`)
  }
}

// 配置字段映射
const configFieldMapping = (template: any) => {
  // 使用数字id而不是template_id字符串
  console.log('跳转字段映射页面，模板对象:', template)
  console.log('模板ID:', template.id)
  router.push(`/template-field-mapping/${template.id}`)
}

// 预览模板 - 使用统一的ReportView
const previewTemplate = (template: any) => {
  // 跳转到统一报表查看页面
  // 使用template_id作为路由参数
  const encodedTemplateId = encodeURIComponent(template.template_id)
  router.push({
    path: `/report-view/${encodedTemplateId}`,  // teacher_id为空表示预览模式
    query: {
      mode: 'preview'
    }
  })
}

// 删除模板
const deleteTemplate = async (template: any) => {
  try {
    await ElMessageBox.confirm('确定要删除这个模板吗？', '提示', {
      type: 'warning'
    })
    
    const response = await fetch(`/api/templates/${template.template_id}`, {
      method: 'DELETE'
    })
    
    const result = await response.json()
    if (result.status === 'success') {
      ElMessage.success('删除成功')
      loadTemplates()
    } else {
      ElMessage.error(result.message || '删除失败')
    }
  } catch (error) {
    // 用户取消
  }
}

// 添加字段
const addField = () => {
  fieldList.value.push({
    field_name: '',
    field_label: '',
    field_type: 'text',
    position_type: 'paragraph',
    position_data: {},
    data_source: '',
    default_value: ''
  })
}

// 移除字段
const removeField = (index: number) => {
  fieldList.value.splice(index, 1)
}

// 保存字段配置
const saveFields = async () => {
  if (!currentTemplate.value) return
  
  saving.value = true
  try {
    const response = await fetch(`/api/templates/${currentTemplate.value.template_id}/fields`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(fieldList.value)
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

// 获取清单模板列表
const loadChecklistTemplates = async () => {
  checklistLoading.value = true
  try {
    const response = await fetch('/api/data/business_checklist')
    const result = await response.json()
    if (result.status === 'success') {
      checklistTemplates.value = result.data || []
    }
  } catch (error) {
    console.error('加载清单模板失败:', error)
    ElMessage.error('加载清单模板失败')
  } finally {
    checklistLoading.value = false
  }
}

// 获取可用模板列表
const loadAvailableTemplates = async () => {
  try {
    const response = await fetch('/api/templates/list')
    const result = await response.json()
    if (result.status === 'success') {
      availableTemplates.value = result.templates || []
    }
  } catch (error) {
    console.error('加载模板列表失败:', error)
  }
}

// 保存清单模板
const saveChecklistTemplate = async () => {
  try {
    const url = editingChecklist.value 
      ? `/api/data/business_checklist/${checklistForm.value.id}`
      : '/api/data/business_checklist'
    const method = editingChecklist.value ? 'PUT' : 'POST'
    
    const response = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(checklistForm.value)
    })
    
    const result = await response.json()
    if (result.status === 'success') {
      ElMessage.success(editingChecklist.value ? '更新成功' : '创建成功')
      showChecklistDialog.value = false
      loadChecklistTemplates()
    } else {
      throw new Error(result.message || '保存失败')
    }
  } catch (error: any) {
    ElMessage.error(error.message || '保存失败')
  }
}

// 编辑清单模板
const editChecklistTemplate = (row: any) => {
  editingChecklist.value = true
  checklistForm.value = {
    id: row.id,
    清单名称: row.清单名称,
    触发条件: row.触发条件 || { target_status: ['退休'] },
    任务项列表: row.任务项列表 || [],
    是否有效: row.是否有效,
    关联模板ID: row.关联模板ID || ''
  }
  loadAvailableTemplates()
  showChecklistDialog.value = true
}

// 删除清单模板
const deleteChecklistTemplate = async (row: any) => {
  try {
    await ElMessageBox.confirm('确定要删除这个清单模板吗？', '确认删除', {
      type: 'warning'
    })
    
    const response = await fetch(`/api/data/business_checklist/${row.id}`, {
      method: 'DELETE'
    })
    
    const result = await response.json()
    if (result.status === 'success') {
      ElMessage.success('删除成功')
      loadChecklistTemplates()
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
    }
  }
}

// 预览清单模板
const previewChecklistTemplate = (row: any) => {
  ElMessage.info(`清单: ${row.清单名称}\n任务数: ${row.任务项列表?.length || 0}项`)
}

// 添加任务项
const addTaskItem = () => {
  checklistForm.value.任务项列表.push({
    标题: '',
    目标: '',
    参数: {}
  })
}

// 删除任务项
const removeTaskItem = (index: number) => {
  checklistForm.value.任务项列表.splice(index, 1)
}

onMounted(() => {
  loadTemplates()
  loadChecklistTemplates()
  loadIntermediateTables()
})

// 创建新中间表（跳转到设计器）
const createIntermediateTable = () => {
  router.push('/intermediate-table-designer')
}

// 加载中间表列表
const loadIntermediateTables = async () => {
  intermediateLoading.value = true
  try {
    const response = await fetch('/api/intermediate-tables/list')
    const result = await response.json()
    if (result.status === 'success') {
      intermediateTables.value = result.data || []
    }
  } catch (error) {
    console.error('加载中间表列表失败:', error)
    ElMessage.error('加载中间表列表失败')
  } finally {
    intermediateLoading.value = false
  }
}

// 编辑中间表（打开设计器）
const editIntermediateTable = (row: any) => {
  router.push(`/intermediate-table-designer/${row.table_name}`)
}

// 预览中间表
const previewIntermediateTable = (row: any) => {
  window.open(`/auto-table/${row.table_name}`, '_blank')
}

// 管理中间表数据
const manageIntermediateData = (row: any) => {
  router.push(`/auto-table/${row.table_name}`)
}

// 删除中间表
const deleteIntermediateTable = async (row: any) => {
  try {
    await ElMessageBox.confirm('确定要删除这个中间表吗？数据将无法恢复！', '确认删除', {
      type: 'warning'
    })
    
    const response = await fetch(`/api/intermediate-tables/${row.table_name}`, {
      method: 'DELETE'
    })
    
    const result = await response.json()
    if (result.status === 'success') {
      ElMessage.success('删除成功')
      loadIntermediateTables()
    } else {
      ElMessage.error(result.message || '删除失败')
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
    }
  }
}
</script>

<style scoped>
.template-manager {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title {
  font-size: 18px;
  font-weight: bold;
}

.description {
  color: #666;
  margin-top: 10px;
}

.template-list {
  margin-top: 20px;
}

.mark-container {
  display: flex;
  gap: 20px;
  height: calc(100vh - 200px);
}

.field-list {
  width: 500px;
  display: flex;
  flex-direction: column;
}

.field-list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.field-list-header h3 {
  margin: 0;
}

.field-actions {
  margin-top: 15px;
  text-align: center;
}

.document-preview {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.preview-header {
  margin-bottom: 15px;
}

.preview-header h3 {
  margin: 0 0 10px 0;
}

.preview-content {
  flex: 1;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  overflow: hidden;
}

.no-preview {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #999;
}

/* 清单模板样式 */
.template-tabs {
  margin-top: 20px;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.task-items {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.task-item {
  margin-bottom: 10px;
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.add-task-btn {
  align-self: flex-start;
}

.form-tip {
  font-size: 12px;
  color: #999;
  margin-top: 5px;
}
</style>
