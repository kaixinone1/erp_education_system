<template>
  <div class="file-selection-panel">
    <el-card class="panel-card">
      <template #header>
        <div class="card-header">
          <span>第一步：文件选择与归属定义</span>
        </div>
      </template>
      
      <div class="panel-content">
        <!-- 文件上传区域 -->
        <div class="upload-section">
          <h3>上传数据文件</h3>
          <el-upload
            ref="uploadRef"
            class="file-uploader"
            drag
            action="#"
            :auto-upload="false"
            :on-change="handleFileChange"
            :on-remove="handleFileRemove"
            :limit="1"
            accept=".xlsx,.xls,.csv"
          >
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">
              拖拽文件到此处或 <em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                支持 Excel (.xlsx, .xls) 和 CSV 格式文件
              </div>
            </template>
          </el-upload>
        </div>

        <!-- 文件名和模块选择区域 -->
        <div class="module-selection-section" v-if="fileSelected">
          <h3>选择数据归属</h3>
          <el-form label-width="120px">
            <!-- 导入文件名和目标文件名 -->
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="导入文件名">
                  <el-input 
                    v-model="importFileName" 
                    readonly
                    placeholder="导入文件名"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="目标文件名">
                  <el-input 
                    v-model="targetTableName" 
                    readonly
                    placeholder="目标文件名"
                  >
                    <template #append>
                      <el-tag type="info" size="small">{{ englishTableName || '待生成' }}</el-tag>
                    </template>
                  </el-input>
                </el-form-item>
              </el-col>
            </el-row>
            
            <!-- 主模块和子模块 -->
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="主模块">
                  <el-select 
                    v-model="selectedMainModule" 
                    placeholder="请选择主模块"
                    @change="handleMainModuleChange"
                    style="width: 100%"
                  >
                    <el-option
                      v-for="module in mainModules"
                      :key="module.id"
                      :label="module.title"
                      :value="module.id"
                    />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="子模块" v-if="selectedMainModule">
                  <el-select 
                    v-model="selectedSubModule" 
                    placeholder="请选择子模块"
                    style="width: 100%"
                  >
                    <el-option
                      v-for="subModule in subModules"
                      :key="subModule.id"
                      :label="subModule.title"
                      :value="subModule.id"
                    />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>
        </div>

        <!-- 解析结果预览区域 -->
        <div class="preview-section" v-if="parsedData">
          <h3>数据预览</h3>
          
          <!-- 字段列表 -->
          <div class="fields-section">
            <h4>提取的字段</h4>
            <el-tag 
              v-for="field in parsedData.fields" 
              :key="field"
              class="field-tag"
            >
              {{ field }}
            </el-tag>
          </div>

          <!-- 数据预览表格 -->
          <div class="data-preview-section">
            <h4>前10行数据预览</h4>
            <el-table 
              :data="parsedData.preview_data" 
              style="width: 100%"
              max-height="300px"
              border
            >
              <el-table-column
                v-for="field in parsedData.fields"
                :key="field"
                :prop="field"
                :label="field"
                min-width="120"
                show-overflow-tooltip
              />
            </el-table>
          </div>

          <!-- 统计信息 -->
          <div class="statistics-section">
            <el-descriptions :column="3" border>
              <el-descriptions-item label="总行数">{{ parsedData.total_rows }}</el-descriptions-item>
              <el-descriptions-item label="总列数">{{ parsedData.fields.length }}</el-descriptions-item>
              <el-descriptions-item label="文件大小">{{ formatFileSize(parsedData.fileSize) }}</el-descriptions-item>
            </el-descriptions>
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="action-section" v-if="canProceed">
          <el-button type="primary" @click="handleNextStep">
            下一步：字段配置
            <el-icon class="el-icon--right"><arrow-right /></el-icon>
          </el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { UploadFilled, ArrowRight } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

// 组件事件
const emit = defineEmits(['next-step', 'data-parsed'])

// 上传组件引用
const uploadRef = ref()

// 文件选择状态
const fileSelected = ref(false)
const currentFile = ref<File | null>(null)

// 文件名显示
const importFileName = ref('')
const targetTableName = ref('')
const englishTableName = ref('')

// 模块选择
const selectedMainModule = ref('')
const selectedSubModule = ref('')

// 导航模块数据
const navigationModules = ref<any[]>([])

// 解析后的数据
const parsedData = ref<{
  fields: string[]
  preview_data: any[]
  total_rows: number
  fileSize: number
} | null>(null)

// 计算属性：主模块列表
const mainModules = computed(() => {
  return navigationModules.value.filter((module: any) => module.type === 'module')
})

// 计算属性：子模块列表
const subModules = computed(() => {
  const mainModule = mainModules.value.find((m: any) => m.id === selectedMainModule.value)
  return mainModule?.children || []
})

// 计算属性：是否可以进行下一步
const canProceed = computed(() => {
  return parsedData.value && selectedMainModule.value && selectedSubModule.value
})

// 加载导航数据
const loadNavigationData = async () => {
  try {
    const response = await fetch('http://127.0.0.1:8000/api/navigation-admin/tree')
    if (response.ok) {
      const data = await response.json()
      navigationModules.value = data.modules || []
    }
  } catch (error) {
    console.error('加载导航数据失败:', error)
    ElMessage.error('加载导航数据失败')
  }
}

// 处理文件选择
const handleFileChange = (uploadFile: any) => {
  currentFile.value = uploadFile.raw
  fileSelected.value = true
  
  // 自动解析文件
  parseFile(uploadFile.raw)
}

// 处理文件移除
const handleFileRemove = () => {
  currentFile.value = null
  fileSelected.value = false
  parsedData.value = null
  selectedMainModule.value = ''
  selectedSubModule.value = ''
  importFileName.value = ''
  targetTableName.value = ''
  englishTableName.value = ''
}

// 解析文件
const parseFile = async (file: File) => {
  try {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await fetch('http://127.0.0.1:8000/api/import/parse-file?preview_only=false', {
      method: 'POST',
      body: formData
    })
    
    if (response.ok) {
      const data = await response.json()
      parsedData.value = {
        fields: data.fields || [],
        preview_data: data.preview_data || [],
        total_rows: data.total_rows || 0,
        fileSize: file.size
      }
      
      // 设置文件名显示
      importFileName.value = file.name
      // 生成目标表名（从文件名提取中文名）
      const chineseTitle = extractChineseTitle(file.name)
      targetTableName.value = chineseTitle
      
      // 调用API获取英文表名
      await fetchEnglishTableName(chineseTitle)
      
      // 发送解析完成事件
      emit('data-parsed', {
        file: file,
        parsedData: parsedData.value,
        mainModule: selectedMainModule.value,
        subModule: selectedSubModule.value,
        chineseTitle: chineseTitle,
        englishTableName: englishTableName.value
      })
      
      ElMessage.success('文件解析成功')
    } else {
      const error = await response.json()
      ElMessage.error(error.detail || '文件解析失败')
    }
  } catch (error) {
    console.error('解析文件失败:', error)
    ElMessage.error('解析文件失败')
  }
}

// 从文件名提取中文标题
const extractChineseTitle = (fileName: string): string => {
  // 移除扩展名
  const nameWithoutExt = fileName.replace(/\.[^/.]+$/, '')
  // 移除数字和特殊字符，保留中文字符
  const chinesePart = nameWithoutExt.replace(/[^\u4e00-\u9fa5]/g, '')
  return chinesePart || nameWithoutExt
}

// 获取英文表名
const fetchEnglishTableName = async (chineseTitle: string) => {
  try {
    const response = await fetch('http://127.0.0.1:8000/api/import/translate-table-name', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        chinese_name: chineseTitle,
        module_name: selectedMainModule.value
      })
    })
    
    if (response.ok) {
      const data = await response.json()
      englishTableName.value = data.english_name
      console.log('获取到英文表名:', data.english_name)
    } else {
      console.error('获取英文表名失败')
      englishTableName.value = ''
    }
  } catch (error) {
    console.error('获取英文表名失败:', error)
    englishTableName.value = ''
  }
}

// 处理主模块选择变化
const handleMainModuleChange = () => {
  selectedSubModule.value = ''
}

// 格式化文件大小
const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 处理下一步
const handleNextStep = () => {
  if (!canProceed.value) {
    ElMessage.warning('请完成文件上传和模块选择')
    return
  }
  
  emit('next-step', {
    file: currentFile.value,
    parsedData: parsedData.value,
    mainModule: selectedMainModule.value,
    subModule: selectedSubModule.value
  })
}

// 组件挂载时加载导航数据
onMounted(() => {
  loadNavigationData()
})
</script>

<style scoped>
.file-selection-panel {
  padding: 20px;
}

.panel-card {
  min-height: 600px;
}

.card-header {
  font-size: 16px;
  font-weight: 600;
}

.panel-content {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.upload-section,
.module-selection-section,
.preview-section,
.action-section {
  width: 100%;
}

.upload-section h3,
.module-selection-section h3,
.preview-section h3 {
  margin: 0 0 15px 0;
  font-size: 14px;
  font-weight: 600;
  color: #606266;
}

.file-uploader {
  width: 100%;
}

.fields-section {
  margin-bottom: 20px;
}

.fields-section h4 {
  margin: 0 0 10px 0;
  font-size: 13px;
  color: #909399;
}

.field-tag {
  margin: 0 8px 8px 0;
}

.data-preview-section {
  margin-bottom: 20px;
}

.data-preview-section h4 {
  margin: 0 0 10px 0;
  font-size: 13px;
  color: #909399;
}

.statistics-section {
  margin-bottom: 20px;
}

.action-section {
  display: flex;
  justify-content: flex-end;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}
</style>
