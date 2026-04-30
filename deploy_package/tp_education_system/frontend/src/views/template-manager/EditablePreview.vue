<template>
  <div class="editable-preview-container">
    <div class="header">
      <h2>{{ pageTitle }}</h2>
      <div class="header-info" v-if="mode === 'fill'">
        <span class="debug-info">教师ID: {{ teacherId }}</span>
      </div>
      <div class="actions">
        <el-button @click="goBack">返回</el-button>
        <el-button type="primary" @click="saveChanges">保存</el-button>
        <el-button type="success" @click="exportDocument">导出</el-button>
      </div>
    </div>

    <div class="content">
      <div ref="editorRef" class="document-editor" contenteditable="true" @input="onContentChange"></div>
    </div>

    <!-- 调试信息面板 -->
    <div class="debug-panel" v-if="showDebug">
      <h3>调试信息</h3>
      <p>模板ID: {{ templateId }}</p>
      <p>教师ID: {{ teacherId }}</p>
      <p>模式: {{ mode }}</p>
      <p>教师姓名: {{ teacherName }}</p>
      <p>API URL: {{ apiUrl }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, computed, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'

const route = useRoute()
const router = useRouter()

const templateId = ref('')
const teacherId = ref(0)
const templateName = ref('')
const teacherName = ref('')
const editorRef = ref<HTMLDivElement | null>(null)
const hasChanges = ref(false)
const mode = ref<'preview' | 'fill'>('fill')
const showDebug = ref(true) // 显示调试信息
const apiUrl = ref('')

// 页面标题
const pageTitle = computed(() => {
  if (mode.value === 'preview') {
    return `预览模板 - ${templateName.value}`
  } else {
    return `填报文档 - ${templateName.value}${teacherName.value ? ' - ' + teacherName.value : ''}`
  }
})

// 返回
const goBack = async () => {
  if (hasChanges.value) {
    try {
      await ElMessageBox.confirm(
        '当前文件没有保存，是否保存？',
        '提示',
        {
          confirmButtonText: '保存',
          cancelButtonText: '取消',
          type: 'warning',
          distinguishCancelAndClose: true
        }
      )
      await saveChanges()
      router.back()
    } catch (action) {
      if (action === 'cancel') {
        router.back()
      }
    }
  } else {
    router.back()
  }
}

// 加载文档
const loadDocument = async () => {
  try {
    const url = `/api/template-field-mapping/preview/${templateId.value}?teacher_id=${teacherId.value}&mode=${mode.value}`
    apiUrl.value = url
    
    console.log('【EditablePreview】加载文档:', {
      templateId: templateId.value,
      teacherId: teacherId.value,
      url: url
    })
    
    const response = await fetch(url)
    if (response.ok) {
      const html = await response.text()
      
      // 检查HTML中是否包含教师姓名
      console.log('【EditablePreview】收到HTML，检查内容...')
      if (html.includes('王军峰')) {
        console.log('【EditablePreview】✓ HTML中包含"王军峰"')
      } else if (html.includes('王德')) {
        console.log('【EditablePreview】✓ HTML中包含"王德"')
      } else {
        console.log('【EditablePreview】✗ HTML中未找到姓名')
      }
      
      if (editorRef.value) {
        editorRef.value.innerHTML = html
      }
    } else {
      ElMessage.error('加载文档失败')
    }
  } catch (error) {
    console.error('加载文档失败:', error)
    ElMessage.error('加载文档失败')
  }
}

// 获取教师姓名
const loadTeacherName = async () => {
  if (!teacherId.value || teacherId.value === 0) {
    teacherName.value = ''
    return
  }
  try {
    const response = await fetch(`/api/teachers/${teacherId.value}`)
    if (response.ok) {
      const data = await response.json()
      teacherName.value = data.name || data.姓名 || ''
      console.log('【EditablePreview】获取教师姓名:', teacherName.value)
    }
  } catch (error) {
    console.error('获取教师姓名失败:', error)
  }
}

// 保存修改
const saveChanges = async () => {
  // TODO: 实现保存逻辑
  ElMessage.success('保存成功')
  hasChanges.value = false
}

// 导出文档
const exportDocument = () => {
  // TODO: 实现导出逻辑
  ElMessage.success('导出成功')
}

// 内容变化
const onContentChange = () => {
  hasChanges.value = true
}

// 页面关闭前提示
const handleBeforeUnload = (e: BeforeUnloadEvent) => {
  if (hasChanges.value) {
    e.preventDefault()
    e.returnValue = ''
  }
}

onMounted(() => {
  // 从查询参数获取参数
  templateId.value = route.query.template_id as string
  mode.value = (route.query.mode as 'preview' | 'fill') || 'fill'
  
  // teacher_id 可以从查询参数或路由参数获取
  const teacherIdFromQuery = parseInt(route.query.teacher_id as string)
  const teacherIdFromParams = parseInt(route.params.id as string)
  teacherId.value = teacherIdFromQuery || teacherIdFromParams || 0
  
  // 获取模板名称
  templateName.value = (route.query.template_name as string) || '文档'
  
  // 调试日志
  console.log('【EditablePreview】页面加载:', {
    templateId: templateId.value,
    teacherId: teacherId.value,
    mode: mode.value,
    query: route.query,
    params: route.params,
    teacherIdFromQuery,
    teacherIdFromParams
  })
  
  // 如果是填报模式，加载教师姓名
  if (mode.value === 'fill' && teacherId.value > 0) {
    loadTeacherName()
  }
  
  // 加载文档
  loadDocument()
  
  // 添加页面关闭前提示
  window.addEventListener('beforeunload', handleBeforeUnload)
})

onBeforeUnmount(() => {
  window.removeEventListener('beforeunload', handleBeforeUnload)
})

// 监听路由参数变化
watch(() => route.query.template_id, (newTemplateId, oldTemplateId) => {
  if (newTemplateId !== oldTemplateId) {
    console.log('【EditablePreview】template_id changed:', newTemplateId)
    templateId.value = newTemplateId as string
    loadDocument()
  }
})

watch(() => route.query.teacher_id, (newTeacherId, oldTeacherId) => {
  if (newTeacherId !== oldTeacherId) {
    console.log('【EditablePreview】teacher_id changed:', newTeacherId)
    teacherId.value = parseInt(newTeacherId as string) || 0
    loadDocument()
    if (mode.value === 'fill' && teacherId.value > 0) {
      loadTeacherName()
    }
  }
})
</script>

<style scoped>
.editable-preview-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  border-bottom: 1px solid #e4e7ed;
  background: #fff;
}

.header-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.debug-info {
  color: #909399;
  font-size: 14px;
}

.content {
  flex: 1;
  overflow: auto;
  padding: 24px;
  background: #f5f7fa;
}

.document-editor {
  max-width: 1200px;
  margin: 0 auto;
  background: #fff;
  padding: 40px;
  min-height: 800px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.debug-panel {
  position: fixed;
  bottom: 20px;
  right: 20px;
  width: 300px;
  background: #fff;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  padding: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  z-index: 1000;
}

.debug-panel h3 {
  margin: 0 0 12px 0;
  font-size: 16px;
  color: #303133;
}

.debug-panel p {
  margin: 8px 0;
  font-size: 13px;
  color: #606266;
  word-break: break-all;
}
</style>
