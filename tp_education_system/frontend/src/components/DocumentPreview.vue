<template>
  <div class="document-preview">
    <el-dialog
      v-model="visible"
      title="文档预览"
      width="900px"
      :close-on-click-modal="false"
      class="preview-dialog"
    >
      <div v-if="loading" class="loading-container">
        <el-skeleton :rows="10" animated />
      </div>

      <div v-else-if="error" class="error-container">
        <el-alert :title="error" type="error" :closable="false" />
      </div>

      <div v-else class="preview-content">
        <!-- 文档信息 -->
        <div class="doc-info">
          <h3>{{ documentTitle }}</h3>
          <p class="doc-meta">模板: {{ templateName }} | 教师: {{ teacherName }}</p>
        </div>

        <!-- 预览内容 -->
        <div class="preview-body" v-html="previewContent"></div>

        <!-- 填充统计 -->
        <div v-if="fillStats" class="fill-stats">
          <el-tag type="success">成功填充 {{ fillStats.filled }} 处</el-tag>
          <el-tag v-if="fillStats.empty > 0" type="warning">空白 {{ fillStats.empty }} 处</el-tag>
        </div>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="visible = false">关闭</el-button>
          <el-dropdown @command="handleExport" split-button type="primary" :loading="exporting">
            导出文档
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="word">导出 Word (.docx)</el-dropdown-item>
                <el-dropdown-item command="pdf">导出 PDF (.pdf)</el-dropdown-item>
                <el-dropdown-item command="excel">导出 Excel (.xlsx)</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps<{
  templateId: number
  templateName: string
  teacherId: number
  teacherName: string
}>()

const emit = defineEmits(['close', 'export'])

const visible = ref(false)
const loading = ref(false)
const error = ref('')
const previewContent = ref('')
const fillStats = ref<{ filled: number; empty: number } | null>(null)
const exporting = ref(false)
const documentTitle = ref('')

// 打开预览
const open = async () => {
  visible.value = true
  loading.value = true
  error.value = ''

  try {
    // 调用预览API
    const response = await fetch(`/api/templates/${props.templateId}/preview?teacher_id=${props.teacherId}`)

    if (!response.ok) {
      throw new Error('预览生成失败')
    }

    const result = await response.json()

    if (result.status === 'success') {
      previewContent.value = result.data.html_content
      fillStats.value = result.data.stats
      documentTitle.value = result.data.document_title || '文档预览'
    } else {
      throw new Error(result.message || '预览生成失败')
    }
  } catch (err: any) {
    error.value = err.message || '预览生成失败'
    ElMessage.error(error.value)
  } finally {
    loading.value = false
  }
}

// 处理导出
const handleExport = async (format: string) => {
  exporting.value = true

  try {
    let url = ''
    let filename = ''

    switch (format) {
      case 'word':
        url = `/api/templates/${props.templateId}/smart-fill-download?teacher_id=${props.teacherId}`
        filename = `${documentTitle.value || '文档'}.docx`
        break
      case 'pdf':
        url = `/api/templates/${props.templateId}/export/pdf?teacher_id=${props.teacherId}`
        filename = `${documentTitle.value || '文档'}.pdf`
        break
      case 'excel':
        url = `/api/templates/${props.templateId}/export/excel?teacher_id=${props.teacherId}`
        filename = `${documentTitle.value || '文档'}.xlsx`
        break
      default:
        throw new Error('不支持的导出格式')
    }

    const response = await fetch(url)

    if (!response.ok) {
      throw new Error('导出失败')
    }

    const blob = await response.blob()
    const downloadUrl = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = downloadUrl
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(downloadUrl)

    ElMessage.success(`已导出 ${format.toUpperCase()} 格式`)
  } catch (err: any) {
    ElMessage.error(err.message || '导出失败')
  } finally {
    exporting.value = false
  }
}

// 关闭
const close = () => {
  visible.value = false
  emit('close')
}

defineExpose({
  open,
  close
})
</script>

<style scoped>
.document-preview {
  :deep(.preview-dialog) {
    .el-dialog__body {
      max-height: 60vh;
      overflow-y: auto;
      padding: 20px;
    }
  }
}

.loading-container,
.error-container {
  padding: 40px;
  text-align: center;
}

.preview-content {
  .doc-info {
    text-align: center;
    margin-bottom: 20px;
    padding-bottom: 15px;
    border-bottom: 1px solid #ebeef5;

    h3 {
      margin: 0 0 10px 0;
      color: #303133;
    }

    .doc-meta {
      color: #909399;
      font-size: 14px;
      margin: 0;
    }
  }

  .preview-body {
    background: #f5f7fa;
    padding: 20px;
    border-radius: 4px;
    min-height: 300px;

    :deep(table) {
      width: 100%;
      border-collapse: collapse;
      margin: 10px 0;
      background: white;

      th, td {
        border: 1px solid #dcdfe6;
        padding: 8px 12px;
        text-align: left;
      }

      th {
        background: #f5f7fa;
        font-weight: 600;
      }
    }

    :deep(p) {
      margin: 10px 0;
      line-height: 1.6;
    }
  }

  .fill-stats {
    margin-top: 15px;
    text-align: center;

    .el-tag {
      margin: 0 5px;
    }
  }
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
