<template>
  <div class="data-import-workbench">
    <el-card class="box-card" style="height: calc(100vh - 120px);">
      <template #header>
        <div class="card-header">
          <span>数据导入工作台</span>
        </div>
      </template>
      
      <div class="card-body">
        <!-- 步骤导航 -->
        <el-steps :active="currentStep" align-center style="margin-bottom: 30px;">
          <el-step title="1. 文件与归属" />
          <el-step title="2. 字段配置" />
          <el-step title="3. 数据预览" />
          <el-step title="4. 确认导入" />
        </el-steps>
        
        <!-- 主内容区域 -->
        <div class="main-content">
          <FileSelectionPanel 
            v-if="currentStep === 0"
            @next-step="handleStep1Complete"
            @data-parsed="handleDataParsed"
          />
          <FieldConfigPanel
            v-else-if="currentStep === 1 && importData.parsedData"
            :parsed-data="importData.parsedData"
            @previous-step="handlePreviousStep"
            @next-step="handleStep2Complete"
            @field-configs-updated="handleFieldConfigsUpdated"
          />
          <div v-else-if="currentStep === 1" class="loading-placeholder">
            <el-empty description="请先上传文件" />
          </div>
          <DataPreviewPanel
            v-else-if="currentStep === 2 && importData.parsedData"
            :parsed-data="importData.parsedData"
            :field-configs="importData.fieldConfigs"
            @previous-step="handlePreviousStep"
            @next-step="handleStep3Complete"
            @validation-complete="handleValidationComplete"
          />
          <div v-else-if="currentStep === 2" class="loading-placeholder">
            <el-empty description="请先完成字段配置" />
          </div>
          <ConfirmImportPanel
            v-else-if="currentStep === 3"
            :validated-data="importData.validatedData"
            :field-configs="importData.fieldConfigs"
            :module-id="importData.mainModule"
            :module-name="importData.moduleName"
            :table-name="importData.tableName"
            :file-name="importData.fileName"
            :chinese-title="importData.chineseTitle"
            :sub-module-id="importData.subModule"
            :sub-module-name="importData.subModuleName"
            :table-type="importData.tableType"
            :parent-table="importData.parentTable"
            @previous-step="handlePreviousStep"
            @import-complete="handleImportComplete"
          />
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import FileSelectionPanel from '@/components/import/FileSelectionPanel.vue'
import FieldConfigPanel from '@/components/import/FieldConfigPanel.vue'
import DataPreviewPanel from '@/components/import/DataPreviewPanel.vue'
import ConfirmImportPanel from '@/components/import/ConfirmImportPanel.vue'

// 当前步骤索引
const currentStep = ref(0)

// 导入数据存储
const importData = ref<{
  file: File | null
  fileName: string
  chineseTitle: string
  parsedData: any
  mainModule: string
  subModule: string
  subModuleName: string
  moduleName: string
  fieldConfigs: any[]
  validatedData: any[]
  validationReport: any
  tableName: string
  tableType: string
  parentTable: string
}>({
  file: null,
  fileName: '',
  chineseTitle: '',
  parsedData: null,
  mainModule: '',
  subModule: '',
  subModuleName: '',
  moduleName: '',
  fieldConfigs: [],
  validatedData: [],
  validationReport: null,
  tableName: '',
  tableType: 'master',
  parentTable: ''
})

// 异步生成表名 - 调用后端翻译API
const generateTableNameAsync = async (chineseTitle: string, moduleName: string): Promise<string> => {
  try {
    // 调用后端翻译API
    const response = await fetch('/api/import/translate-table-name', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        chinese_name: chineseTitle,
        module_name: moduleName
      })
    })
    
    if (response.ok) {
      const result = await response.json()
      return result.english_name
    }
  } catch (error) {
    console.error('表名翻译失败:', error)
  }
  
  // 如果翻译失败，使用备用方案（时间戳）
  const timestamp = new Date().getTime().toString().slice(-6)
  const modulePrefix = importData.value.mainModule || 'data'
  return `${modulePrefix}_${timestamp}`
}

// 从文件名提取中文标题
const extractChineseTitle = (fileName: string): string => {
  if (!fileName) return ''
  // 移除扩展名
  const nameWithoutExt = fileName.replace(/\.[^/.]+$/, '')
  // 清理文件名，移除常见的无意义后缀
  return nameWithoutExt
    .replace(/\s+/g, '')  // 移除空格
    .replace(/\(\d+\)$/, '')  // 移除括号内的数字
    .replace(/_\d+$/, '')  // 移除下划线后的数字
    .replace(/-\d+$/, '')  // 移除横线后的数字
}

// 处理第一步完成
const handleStep1Complete = async (data: any) => {
  const fileName = data.file?.name || ''
  const chineseTitle = extractChineseTitle(fileName)
  
  // 获取子模块名称
  const subModuleName = getSubModuleName(data.mainModule, data.subModule)
  
  // 异步生成表名（调用后端翻译API）
  const tableName = await generateTableNameAsync(chineseTitle, data.moduleName || '')
  
  importData.value = { 
    ...importData.value, 
    ...data,
    fileName: fileName,
    chineseTitle: chineseTitle,
    subModuleName: subModuleName,
    tableName: tableName
  }
  currentStep.value = 1
}

// 获取子模块名称
const getSubModuleName = (_mainModuleId: string, subModuleId: string): string => {
  // 这里需要从导航数据中获取子模块名称
  // 简化处理，返回子模块ID作为名称
  return subModuleId
}

// 处理数据解析完成
const handleDataParsed = (data: any) => {
  importData.value = { ...importData.value, ...data }
}

// 处理上一步
const handlePreviousStep = () => {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}

// 处理第二步完成
const handleStep2Complete = (data: any) => {
  importData.value = { ...importData.value, ...data }
  currentStep.value = 2
}

// 处理字段配置更新
const handleFieldConfigsUpdated = (configs: any[]) => {
  importData.value.fieldConfigs = configs || []
}

// 处理第三步完成
const handleStep3Complete = (data: any) => {
  importData.value = { 
    ...importData.value, 
    ...data,
    validatedData: data.validatedData || []
  }
  currentStep.value = 3
}

// 处理验证完成
const handleValidationComplete = (report: any) => {
  importData.value.validationReport = report
}

// 处理导入完成
const handleImportComplete = (result: any) => {
  // 导入完成后可以重置或跳转到其他页面
  console.log('导入完成:', result)
}
</script>

<style scoped>
.data-import-workbench {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 16px;
  font-weight: 600;
}

.card-body {
  height: calc(100% - 60px);
  display: flex;
  flex-direction: column;
}

.main-content {
  flex: 1;
  overflow: auto;
}
</style>
