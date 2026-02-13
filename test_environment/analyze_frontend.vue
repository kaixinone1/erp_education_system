<template>
  <div class="test-page">
    <h1>前端路由参数分析</h1>
    
    <div class="info-box">
      <h2>当前路由信息</h2>
      <p><strong>Path:</strong> {{ route.path }}</p>
      <p><strong>Params:</strong> {{ JSON.stringify(route.params) }}</p>
      <p><strong>Query:</strong> {{ JSON.stringify(route.query) }}</p>
    </div>
    
    <div class="info-box">
      <h2>解析后的参数</h2>
      <p><strong>template_id:</strong> {{ templateId }}</p>
      <p><strong>teacher_id (from query):</strong> {{ teacherIdFromQuery }}</p>
      <p><strong>teacher_id (from params):</strong> {{ teacherIdFromParams }}</p>
      <p><strong>teacher_id (final):</strong> {{ teacherId }}</p>
      <p><strong>mode:</strong> {{ mode }}</p>
    </div>
    
    <div class="info-box">
      <h2>API调用信息</h2>
      <p><strong>API URL:</strong> {{ apiUrl }}</p>
    </div>
    
    <div class="test-buttons">
      <button @click="testAPI">测试API调用</button>
    </div>
    
    <div v-if="apiResult" class="info-box">
      <h2>API返回结果</h2>
      <p><strong>HTML长度:</strong> {{ apiResult.length }}</p>
      <p><strong>包含'王军峰':</strong> {{ apiResult.includes('王军峰') }}</p>
      <p><strong>包含'王德':</strong> {{ apiResult.includes('王德') }}</p>
      <p><strong>剩余{{姓名}}:</strong> {{ (apiResult.match(/\{\{\s*姓名\s*\}\}/g) || []).length }} 个</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

// 模拟 EditablePreview.vue 的参数解析逻辑
const templateId = computed(() => route.query.template_id || '')
const teacherIdFromQuery = computed(() => parseInt(route.query.teacher_id) || 0)
const teacherIdFromParams = computed(() => parseInt(route.params.id) || 0)
const teacherId = computed(() => teacherIdFromQuery.value || teacherIdFromParams.value || 0)
const mode = computed(() => route.query.mode || 'fill')

const apiUrl = computed(() => {
  if (!templateId.value || !teacherId.value) return ''
  return `/api/template-field-mapping/preview/${encodeURIComponent(templateId.value)}?teacher_id=${teacherId.value}&mode=${mode.value}`
})

const apiResult = ref('')

async function testAPI() {
  if (!apiUrl.value) {
    alert('参数不完整，无法调用API')
    return
  }
  
  try {
    const response = await fetch(apiUrl.value)
    apiResult.value = await response.text()
  } catch (error) {
    alert('API调用失败: ' + error.message)
  }
}

onMounted(() => {
  console.log('【TestPage】路由信息:', {
    path: route.path,
    params: route.params,
    query: route.query
  })
})
</script>

<style scoped>
.test-page {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.info-box {
  background: #f5f5f5;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 15px;
  margin: 15px 0;
}

.info-box h2 {
  margin-top: 0;
  color: #333;
}

.info-box p {
  margin: 8px 0;
  font-family: monospace;
}

.test-buttons {
  margin: 20px 0;
}

button {
  padding: 10px 20px;
  font-size: 16px;
  cursor: pointer;
}
</style>
