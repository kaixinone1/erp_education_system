<template>
  <div class="template-management">
    <h2 class="page-title">模板管理</h2>

    <!-- 操作栏 -->
    <div class="operation-bar">
      <el-button type="primary" @click="showUploadDialog">
        <el-icon><Upload /></el-icon>
        上传模板
      </el-button>
    </div>

    <!-- 模板列表 -->
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
        <el-table-column label="操作" width="300" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="editTemplate(row)">
              编辑
            </el-button>
            <el-button type="info" size="small" @click="previewTemplate(row)">
              预览
            </el-button>
            <el-button type="success" size="small" @click="downloadTemplate(row)">
              下载
            </el-button>
            <el-button type="danger" size="small" @click="deleteTemplate(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 上传模板对话框 -->
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
            accept=".doc,.docx,.pdf"
          >
            <el-button type="primary">选择文件</el-button>
            <template #tip>
              <div class="el-upload__tip">
                支持 .doc, .docx, .pdf 格式<br>
                Word文件中使用 {{占位符}} 标记需要填充的位置<br>
                PDF文件将使用智能字段提取功能
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

    <!-- 预览对话框 -->
    <el-dialog v-model="previewDialogVisible" title="模板预览" width="800px">
      <div v-if="selectedTemplate" class="preview-content">
        <h3>{{ selectedTemplate.name }}</h3>
        <p><strong>类型：</strong>{{ selectedTemplate.type }}</p>
        <p><strong>描述：</strong>{{ selectedTemplate.description || '无' }}</p>
        <div class="placeholders-section">
          <h4>占位符列表：</h4>
          <el-table :data="placeholderConfigs" border size="small">
            <el-table-column prop="placeholder" label="占位符" width="150" />
            <el-table-column prop="field" label="对应字段">
              <template #default="{ row }">
                <el-select v-model="row.field" placeholder="选择字段" size="small">
                  <el-option label="教师姓名" value="teacher_name" />
                  <el-option label="身份证号" value="id_card" />
                  <el-option label="出生日期" value="birth_date" />
                  <el-option label="性别" value="gender" />
                  <el-option label="职务" value="position" />
                  <el-option label="职称" value="title" />
                  <el-option label="参加工作时间" value="work_start_date" />
                  <el-option label="退休日期" value="retirement_date" />
                </el-select>
              </template>
            </el-table-column>
          </el-table>
        </div>
        <div class="test-section">
          <h4>测试填充：</h4>
          <el-button type="primary" @click="openTeacherSelect" :loading="testing">
            选择教师测试
          </el-button>
        </div>
      </div>
    </el-dialog>

    <!-- 教师选择对话框 -->
    <el-dialog v-model="teacherSelectVisible" title="选择教师" width="600px">
      <el-input
        v-model="teacherSearchKeyword"
        placeholder="输入教师姓名搜索（如：王军峰）"
        clearable
        @keyup.enter="searchTeachers"
        style="margin-bottom: 15px"
      >
        <template #append>
          <el-button @click="searchTeachers">
            <el-icon><Search /></el-icon>
          </el-button>
        </template>
      </el-input>
      
      <el-table :data="teacherList" v-loading="teacherLoading" border height="300">
        <el-table-column prop="name" label="姓名" width="100" />
        <el-table-column prop="id_card_display" label="身份证号" />
        <el-table-column prop="gender" label="性别" width="80" />
        <el-table-column prop="age" label="年龄" width="80" />
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="selectTeacher(row)">
              选择
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <template #footer>
        <el-button @click="teacherSelectVisible = false">取消</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { Upload, Search } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// 状态
const loading = ref(false)
const uploading = ref(false)
const testing = ref(false)
const templates = ref<any[]>([])
const uploadDialogVisible = ref(false)
const previewDialogVisible = ref(false)
const selectedTemplate = ref<any>(null)
const placeholderConfigs = ref<any[]>([])
const uploadRef = ref<any>(null)

// 教师选择相关
const teacherSelectVisible = ref(false)
const teacherSearchKeyword = ref('')
const teacherList = ref<any[]>([])
const teacherLoading = ref(false)

// 上传表单
const uploadForm = reactive({
  name: '',
  type: '',
  description: '',
  file: null as File | null
})

// 加载模板列表
const loadTemplates = async () => {
  loading.value = true
  try {
    const response = await fetch('/api/templates/list')
    if (response.ok) {
      const result = await response.json()
      if (result.status === 'success') {
        // 转换后端数据格式
        templates.value = result.templates.map((t: any) => ({
          id: t.template_id,
          name: t.template_name,
          type: 'document',
          placeholders: [],
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

// 显示上传对话框
const showUploadDialog = () => {
  uploadForm.name = ''
  uploadForm.type = ''
  uploadForm.description = ''
  uploadForm.file = null
  uploadDialogVisible.value = true
}

// 处理文件选择
const handleFileChange = (file: any) => {
  uploadForm.file = file.raw
}

// 提交上传
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

// 编辑模板
const editTemplate = (template: any) => {
  // 根据文件类型跳转到不同的编辑器
  const filePath = template.file_path || ''
  if (filePath.toLowerCase().endsWith('.pdf')) {
    // PDF文件跳转到A3编辑器
    window.open(`/a3-template-editor/${template.id}`, '_blank')
  } else {
    // Word文件跳转到普通编辑器
    window.open(`/pdf-template-editor/${template.id}`, '_blank')
  }
}

// 预览模板
const previewTemplate = (template: any) => {
  selectedTemplate.value = template
  placeholderConfigs.value = template.placeholders.map((ph: string) => ({
    placeholder: ph,
    field: ''
  }))
  previewDialogVisible.value = true
}

// 下载模板
const downloadTemplate = async (template: any) => {
  try {
    window.open(`/api/templates/${template.id}/download`)
  } catch (error) {
    console.error('下载模板失败:', error)
    ElMessage.error('下载模板失败')
  }
}

// 删除模板
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

// 打开教师选择对话框
const openTeacherSelect = () => {
  teacherSelectVisible.value = true
  teacherSearchKeyword.value = ''
  teacherList.value = []
}

// 搜索教师
const searchTeachers = async () => {
  if (!teacherSearchKeyword.value.trim()) {
    ElMessage.warning('请输入教师姓名')
    return
  }

  teacherLoading.value = true
  try {
    const response = await fetch(`/api/retirement/search-by-name?name=${encodeURIComponent(teacherSearchKeyword.value)}`)
    if (response.ok) {
      const result = await response.json()
      teacherList.value = result.data || []
      if (teacherList.value.length === 0) {
        ElMessage.warning(`未找到名为"${teacherSearchKeyword.value}"的教师，请检查姓名是否正确`)
      } else {
        ElMessage.success(`找到 ${teacherList.value.length} 位教师`)
      }
    } else {
      ElMessage.error('搜索失败')
    }
  } catch (error) {
    console.error('搜索教师失败:', error)
    ElMessage.error('搜索失败')
  } finally {
    teacherLoading.value = false
  }
}

// 选择教师进行测试
const selectTeacher = async (teacher: any) => {
  if (!selectedTemplate.value) return

  testing.value = true
  teacherSelectVisible.value = false

  try {
    // 调用模板填充API
    const response = await fetch(`/api/template-fill/data?template_id=${selectedTemplate.value.id}&teacher_id=${teacher.id}`)
    
    if (response.ok) {
      const result = await response.json()
      
      // 显示填充结果
      ElMessageBox.alert(
        `<div style="max-height: 400px; overflow-y: auto;">
          <h4>模板：${result.template_name}</h4>
          <h4>教师：${teacher.teacher_name}</h4>
          <el-table :data="Object.entries(result.data).map(([key, value]) => ({key, value}))" border>
            <el-table-column prop="key" label="占位符" width="150" />
            <el-table-column prop="value" label="填充值" />
          </el-table>
        </div>`,
        '填充结果预览',
        {
          dangerouslyUseHTMLString: true,
          confirmButtonText: '下载填充后的文档',
          cancelButtonText: '关闭',
          showCancelButton: true
        }
      ).then(() => {
        // 下载填充后的文档
        downloadFilledTemplate(selectedTemplate.value.id, result.data)
      }).catch(() => {})
    } else {
      ElMessage.error('获取填充数据失败')
    }
  } catch (error) {
    console.error('测试填充失败:', error)
    ElMessage.error('测试填充失败')
  } finally {
    testing.value = false
  }
}

// 下载填充后的模板
const downloadFilledTemplate = async (templateId: number, fillData: any) => {
  try {
    const response = await fetch(`/api/templates/${templateId}/fill`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(fillData)
    })

    if (response.ok) {
      const result = await response.json()
      if (result.data && result.data.file_path) {
        // 下载文件
        window.open(`/api/templates/${templateId}/download`, '_blank')
        ElMessage.success('文档生成成功')
      }
    } else {
      ElMessage.error('生成文档失败')
    }
  } catch (error) {
    console.error('下载填充文档失败:', error)
    ElMessage.error('下载失败')
  }
}

// 页面加载
onMounted(() => {
  loadTemplates()
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

.preview-content {
  padding: 20px;
}

.preview-content h3 {
  margin-top: 0;
}

.placeholders-section {
  margin-top: 20px;
}

.test-section {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #e0e0e0;
}
</style>
