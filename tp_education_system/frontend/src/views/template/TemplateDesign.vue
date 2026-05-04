<template>
  <div class="template-design">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>模板设计器</span>
          <el-button type="primary" @click="saveTemplate">保存模板</el-button>
        </div>
      </template>

      <el-row :gutter="20">
        <!-- 左侧：模板上传和字段配置 -->
        <el-col :span="8">
          <el-card shadow="never">
            <template #header>
              <span>模板上传</span>
            </template>
            
            <el-upload
              ref="uploadRef"
              :auto-upload="false"
              :on-change="handleFileChange"
              :show-file-list="false"
              accept=".xlsx,.xls,.docx"
            >
              <template #trigger>
                <el-button type="primary">上传模板文件</el-button>
              </template>
            </el-upload>
            
            <div v-if="templateFile" style="margin-top: 10px;">
              <el-tag>{{ templateFile.name }}</el-tag>
            </div>
          </el-card>

          <!-- 字段配置 -->
          <el-card shadow="never" style="margin-top: 20px;">
            <template #header>
              <span>字段配置</span>
            </template>
            
            <el-table :data="templateConfig.fields" border max-height="400">
              <el-table-column prop="chinese_name" label="中文名" width="100" />
              <el-table-column prop="english_name" label="英文名" width="100" />
              <el-table-column label="操作" width="80">
                <template #default="{ row, $index }">
                  <el-button
                    type="text"
                    size="small"
                    @click="editField($index)"
                  >
                    编辑
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-col>

        <!-- 右侧：模板预览 -->
        <el-col :span="16">
          <el-card shadow="never">
            <template #header>
              <span>模板预览</span>
            </template>
            
            <div v-if="templateConfig.fields.length > 0">
              <el-form
                :model="previewData"
                label-width="120px"
                :label-position="templateConfig.display_config?.form_layout || 'right'"
              >
                <el-row :gutter="20">
                  <el-col
                    v-for="(field, index) in templateConfig.fields"
                    :key="index"
                    :span="24 / (templateConfig.display_config?.columns_per_row || 3)"
                  >
                    <el-form-item :label="field.chinese_name">
                      <el-input
                        v-model="previewData[field.english_name]"
                        :placeholder="`请输入${field.chinese_name}`"
                      />
                    </el-form-item>
                  </el-col>
                </el-row>
              </el-form>
            </div>
            
            <el-empty v-else description="请先上传模板文件" />
          </el-card>

          <!-- 数据源配置 -->
          <el-card shadow="never" style="margin-top: 20px;">
            <template #header>
              <span>数据源配置</span>
            </template>
            
            <el-form label-width="120px">
              <el-form-item label="数据表">
                <el-select v-model="templateConfig.data_source.table" placeholder="选择数据表">
                  <el-option label="教师基础信息表" value="teacher_basic_info" />
                  <el-option label="退休信息表" value="retirement_info" />
                </el-select>
              </el-form-item>
              
              <el-form-item label="统计方式">
                <el-select v-model="templateConfig.data_source.aggregation" placeholder="选择统计方式">
                  <el-option label="求和" value="sum" />
                  <el-option label="计数" value="count" />
                  <el-option label="平均" value="avg" />
                </el-select>
              </el-form-item>
            </el-form>
          </el-card>
        </el-col>
      </el-row>
    </el-card>

    <!-- 字段编辑对话框 -->
    <el-dialog v-model="fieldDialogVisible" title="编辑字段" width="500px">
      <el-form :model="currentField" label-width="100px">
        <el-form-item label="中文名称">
          <el-input v-model="currentField.chinese_name" />
        </el-form-item>
        
        <el-form-item label="英文名称">
          <el-input v-model="currentField.english_name" />
        </el-form-item>
        
        <el-form-item label="数据类型">
          <el-select v-model="currentField.data_type">
            <el-option label="文本" value="VARCHAR" />
            <el-option label="数字" value="INTEGER" />
            <el-option label="日期" value="DATE" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="是否必填">
          <el-switch v-model="currentField.required" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="fieldDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveField">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const uploadRef = ref()
const templateFile = ref(null)
const templateConfig = reactive({
  template_id: '',
  chinese_name: '',
  english_name: '',
  fields: [],
  display_config: {
    form_layout: 'right',
    columns_per_row: 3
  },
  data_source: {
    table: '',
    aggregation: ''
  }
})

const previewData = reactive({})
const fieldDialogVisible = ref(false)
const currentField = reactive({
  index: -1,
  chinese_name: '',
  english_name: '',
  data_type: 'VARCHAR',
  required: false
})

const handleFileChange = async (file) => {
  templateFile.value = file.raw
  
  // 上传并解析模板
  const formData = new FormData()
  formData.append('file', file.raw)
  
  try {
    const response = await axios.post('http://127.0.0.1:8000/api/template/parse', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    
    if (response.data.success) {
      Object.assign(templateConfig, response.data.template_config)
      ElMessage.success('模板解析成功')
    }
  } catch (error) {
    ElMessage.error('模板解析失败：' + error.message)
  }
}

const editField = (index) => {
  currentField.index = index
  Object.assign(currentField, templateConfig.fields[index])
  fieldDialogVisible.value = true
}

const saveField = () => {
  if (currentField.index >= 0) {
    templateConfig.fields[currentField.index] = { ...currentField }
  }
  fieldDialogVisible.value = false
  ElMessage.success('字段已更新')
}

const saveTemplate = async () => {
  try {
    const response = await axios.post('http://127.0.0.1:8000/api/template/save', templateConfig)
    
    if (response.data.success) {
      ElMessage.success('模板保存成功')
    }
  } catch (error) {
    ElMessage.error('模板保存失败：' + error.message)
  }
}
</script>

<style scoped>
.template-design {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
