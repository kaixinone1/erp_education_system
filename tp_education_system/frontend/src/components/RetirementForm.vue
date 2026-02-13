<template>
  <div class="form-container">
    <!-- 工具栏 -->
    <div class="toolbar no-print">
      <input type="file" ref="fileInput" accept="text/html,.html,.htm" @change="importHTML" style="display: none" />
      <button class="btn btn-primary" @click="handleImportClick">导入HTML</button>
      <button class="btn btn-success" @click="printForm" :disabled="!htmlContent">打印</button>
      <button class="btn" @click="resetForm" :disabled="!htmlContent">重置</button>
    </div>

    <!-- 导入的HTML内容 -->
    <div v-if="htmlContent" class="html-wrapper" v-html="htmlContent" ref="htmlContainer"></div>
    
    <!-- 提示 -->
    <div v-else class="empty-tip">
      <el-empty description="请先导入职工退休呈报表HTML文件" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick } from 'vue'
import { ElMessage } from 'element-plus'

const fileInput = ref<HTMLInputElement>()
const htmlContainer = ref<HTMLElement>()
const htmlContent = ref('')

// 处理导入按钮点击
const handleImportClick = () => {
  console.log('导入按钮被点击')
  console.log('fileInput:', fileInput.value)
  if (fileInput.value) {
    fileInput.value.click()
  } else {
    ElMessage.error('文件输入框未找到')
  }
}

// 导入HTML文件
const importHTML = (event: Event) => {
  console.log('importHTML被调用')
  
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  
  if (!file) {
    ElMessage.error('未选择文件')
    return
  }
  
  console.log('选择的文件:', file.name, '类型:', file.type, '大小:', file.size)
  ElMessage.info(`正在读取文件: ${file.name}`)
  
  const reader = new FileReader()
  
  reader.onload = (e) => {
    console.log('FileReader onload触发')
    try {
      const content = e.target?.result as string
      console.log('文件内容长度:', content.length)
      console.log('内容前100字符:', content.substring(0, 100))
      
      htmlContent.value = content
      ElMessage.success('HTML文件导入成功')
      
      // 等待DOM渲染完成后，自动查找所有input并绑定数据
      nextTick(() => {
        bindInputs()
      })
    } catch (err) {
      console.error('读取文件错误:', err)
      ElMessage.error('读取文件失败: ' + err)
    }
  }
  
  reader.onerror = (e) => {
    console.error('FileReader错误:', e)
    ElMessage.error('文件读取错误')
  }
  
  try {
    reader.readAsText(file)
    console.log('readAsText已调用')
  } catch (err) {
    console.error('readAsText错误:', err)
    ElMessage.error('读取文件出错')
  }
  
  // 清空input，允许重复选择同一文件
  target.value = ''
}

// 绑定输入框
const bindInputs = () => {
  if (!htmlContainer.value) return
  
  const inputs = htmlContainer.value.querySelectorAll('input')
  inputs.forEach((input, index) => {
    // 给每个input添加唯一标识
    if (!input.id) {
      input.id = `field_${index}`
    }
    
    // 添加focus样式
    input.addEventListener('focus', () => {
      input.style.backgroundColor = '#fff3cd'
    })
    input.addEventListener('blur', () => {
      input.style.backgroundColor = 'transparent'
    })
  })
  
  console.log(`已绑定 ${inputs.length} 个输入框`)
}

// 打印
const printForm = () => {
  window.print()
}

// 重置
const resetForm = () => {
  if (!htmlContainer.value) return
  
  const inputs = htmlContainer.value.querySelectorAll('input')
  inputs.forEach(input => {
    (input as HTMLInputElement).value = ''
  })
  
  ElMessage.success('已重置')
}
</script>

<style scoped>
.form-container {
  padding: 20px;
  background: #f0f0f0;
  min-height: 100vh;
}

.toolbar {
  margin-bottom: 20px;
  text-align: center;
}

.btn {
  padding: 10px 20px;
  margin: 0 5px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.btn-primary {
  background: #409eff;
  color: white;
}

.btn-success {
  background: #67c23a;
  color: white;
}

.btn:disabled {
  background: #c0c4cc;
  cursor: not-allowed;
}

.html-wrapper {
  background: white;
  margin: 0 auto;
  box-shadow: 0 4px 12px rgba(0,0,0,0.3);
  /* 保持原始HTML的样式 */
}

.empty-tip {
  padding: 100px;
  text-align: center;
}

@media print {
  .no-print {
    display: none !important;
  }
  
  .form-container {
    padding: 0;
    background: white;
  }
  
  .html-wrapper {
    box-shadow: none;
    margin: 0;
  }
}
</style>
