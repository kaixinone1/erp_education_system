<template>
  <div style="padding: 50px; text-align: center;">
    <h2>文件上传测试</h2>
    
    <div style="margin: 30px 0;">
      <input 
        type="file" 
        ref="fileInput" 
        accept=".html,.htm" 
        @change="handleFileChange"
        style="display: none"
      />
      <button 
        @click="fileInput?.click()"
        style="padding: 15px 30px; font-size: 16px; cursor: pointer;"
      >
        选择HTML文件
      </button>
    </div>
    
    <div v-if="fileInfo" style="margin-top: 30px; padding: 20px; background: #f0f0f0; text-align: left;">
      <h3>文件信息：</h3>
      <p>文件名：{{ fileInfo.name }}</p>
      <p>文件类型：{{ fileInfo.type }}</p>
      <p>文件大小：{{ fileInfo.size }} bytes</p>
      <p>内容长度：{{ contentLength }} 字符</p>
    </div>
    
    <div v-if="error" style="margin-top: 30px; padding: 20px; background: #ffcccc; color: red;">
      <h3>错误：</h3>
      <p>{{ error }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const fileInput = ref<HTMLInputElement>()
const fileInfo = ref<{name: string, type: string, size: number} | null>(null)
const contentLength = ref(0)
const error = ref('')

const handleFileChange = (event: Event) => {
  console.log('handleFileChange 被调用')
  error.value = ''
  
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  
  if (!file) {
    error.value = '未选择文件'
    return
  }
  
  console.log('选择的文件:', file)
  
  fileInfo.value = {
    name: file.name,
    type: file.type,
    size: file.size
  }
  
  const reader = new FileReader()
  
  reader.onload = (e) => {
    console.log('FileReader onload')
    const content = e.target?.result as string
    contentLength.value = content.length
    console.log('内容长度:', contentLength.value)
  }
  
  reader.onerror = (e) => {
    console.error('FileReader error:', e)
    error.value = '读取文件失败'
  }
  
  reader.readAsText(file)
  
  // 清空input
  target.value = ''
}
</script>
