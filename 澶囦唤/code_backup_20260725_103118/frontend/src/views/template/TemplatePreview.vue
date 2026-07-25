<template>
  <div class="template-preview">
    <el-card class="preview-card">
      <template #header>
        <div class="card-header">
          <span class="title">{{ title }}</span>
          <div class="header-actions">
            <el-button size="small" @click="refreshPreview">
              <el-icon><Refresh /></el-icon>
              刷新预览
            </el-button>
            <el-button size="small" type="primary" @click="exportExcel">
              <el-icon><Download /></el-icon>
              导出Excel
            </el-button>
          </div>
        </div>
      </template>

      <div v-if="loading" class="loading-container">
        <el-loading :text="'加载中...'" />
      </div>

      <div v-else class="preview-container">
        <!-- Luckysheet预览区域 -->
        <div 
          ref="luckysheetContainer" 
          class="luckysheet-container"
          :style="{ height: containerHeight }"
        ></div>
      </div>

      <!-- 操作按钮 -->
      <div class="action-bar">
        <el-button type="primary" @click="handleSave">
          <el-icon><Save /></el-icon>
          保存配置
        </el-button>
        <el-button @click="handleClose">
          <el-icon><Close /></el-icon>
          关闭
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue'
import { ElMessage, ElLoading } from 'element-plus'
import { Refresh, Download, Save, Close } from '@element-plus/icons-vue'
import axios from 'axios'

const props = defineProps({
  templateId: {
    type: String,
    required: true
  },
  title: {
    type: String,
    default: '模板预览'
  },
  filledData: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['save', 'close'])

const luckysheetContainer = ref(null)
const loading = ref(false)
const containerHeight = ref('600px')

let luckysheetInstance = null

async function loadPreview() {
  loading.value = true
  try {
    let url = `/api/templates/${props.templateId}/preview`
    
    const response = await axios.get(url)
    const luckysheetData = response.data
    
    await nextTick()
    
    if (luckysheetContainer.value) {
      // 销毁旧实例
      if (window.luckysheet && luckysheetInstance) {
        window.luckysheet.destroy(luckysheetContainer.value)
      }
      
      // 创建新实例
      luckysheetInstance = window.luckysheet.create({
        container: luckysheetContainer.value,
        data: [luckysheetData],
        title: props.title,
        lang: 'zh',
        allowEdit: true,
        showSheetBar: false,
        showToolbar: true,
        showFormulaBar: false,
        showGridLines: true,
        enableAddRow: false,
        enableAddCol: false
      })
    }
  } catch (error) {
    ElMessage.error('加载预览失败：' + error.message)
  } finally {
    loading.value = false
  }
}

function refreshPreview() {
  loadPreview()
}

async function exportExcel() {
  try {
    const response = await axios.post(
      `/api/templates/${props.templateId}/export`,
      props.filledData ? { filled_data: props.filledData } : null,
      { responseType: 'blob' }
    )
    
    const blob = new Blob([response.data], { 
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
    })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${props.templateId}.xlsx`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('导出成功')
  } catch (error) {
    ElMessage.error('导出失败：' + error.message)
  }
}

function handleSave() {
  if (luckysheetInstance) {
    const data = luckysheetInstance.getAllSheets()
    emit('save', data)
    ElMessage.success('保存成功')
  }
}

function handleClose() {
  emit('close')
}

onMounted(() => {
  loadPreview()
  
  // 动态调整高度
  const updateHeight = () => {
    const height = window.innerHeight - 200
    containerHeight.value = `${height}px`
  }
  updateHeight()
  window.addEventListener('resize', updateHeight)
})

watch(() => props.templateId, () => {
  loadPreview()
})
</script>

<style scoped>
.template-preview {
  padding: 20px;
  height: calc(100vh - 80px);
  display: flex;
  flex-direction: column;
}

.preview-card {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title {
  font-size: 18px;
  font-weight: bold;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.loading-container {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.preview-container {
  flex: 1;
  overflow: hidden;
}

.luckysheet-container {
  width: 100%;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
}

.action-bar {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
  padding-top: 15px;
  border-top: 1px solid #e4e7ed;
}
</style>
