<template>
  <div class="file-selection-panel">
    <h3>第一步：文件与归属</h3>
    <el-divider></el-divider>
    
    <el-form :model="formData" label-width="120px">
      <!-- 文件上传 -->
      <el-form-item label="选择文件">
        <el-upload
          class="upload-demo"
          action="#"
          :auto-upload="false"
          :on-change="handleFileChange"
          :show-file-list="false"
          accept=".xlsx,.xls,.csv"
        >
          <el-button type="primary">
            <el-icon><Upload /></el-icon>
            选择文件
          </el-button>
          <template #tip>
            <div class="el-upload__tip">
              支持上传 Excel (.xlsx, .xls) 和 CSV 文件
            </div>
          </template>
        </el-upload>
        
        <div v-if="selectedFile" class="file-info">
          <el-tag type="success">{{ selectedFile.name }}</el-tag>
          <el-button size="small" type="danger" @click="clearFile">
            移除
          </el-button>
        </div>
      </el-form-item>
      
      <!-- 目标数据表 -->
      <el-form-item label="目标数据表" required>
        <el-select v-model="formData.targetTable" placeholder="请选择目标数据表" style="width: 100%;">
          <el-option label="教师信息表" value="teachers"></el-option>
          <el-option label="职工信息表" value="staff"></el-option>
          <el-option label="部门信息表" value="departments"></el-option>
          <el-option label="职位信息表" value="positions"></el-option>
        </el-select>
      </el-form-item>
      
      <!-- 导入模式 -->
      <el-form-item label="导入模式">
        <el-radio-group v-model="formData.importMode">
          <el-radio label="insert">新增数据</el-radio>
          <el-radio label="update">更新数据</el-radio>
          <el-radio label="upsert">新增或更新</el-radio>
        </el-radio-group>
      </el-form-item>
      
      <!-- 数据归属 -->
      <el-form-item label="数据归属">
        <el-select v-model="formData.departmentId" placeholder="请选择所属部门（可选）" style="width: 100%;">
          <el-option label="全部部门" value=""></el-option>
          <el-option label="第一中学" value="1"></el-option>
          <el-option label="第二中学" value="2"></el-option>
          <el-option label="中心小学" value="3"></el-option>
        </el-select>
      </el-form-item>
    </el-form>
    
    <div class="panel-tip">
      <el-alert
        title="操作提示"
        type="info"
        :closable="false"
        show-icon
      >
        <ul>
          <li>请确保上传的文件格式正确，包含必要的字段</li>
          <li>选择合适的目标数据表，确保数据结构匹配</li>
          <li>选择适当的导入模式，避免数据冲突</li>
        </ul>
      </el-alert>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { Upload } from '@element-plus/icons-vue'

// 表单数据
const formData = reactive({
  targetTable: '',
  importMode: 'insert',
  departmentId: ''
})

// 选中的文件
const selectedFile = ref<File | null>(null)

// 处理文件选择
const handleFileChange = (file: any) => {
  selectedFile.value = file.raw
  console.log('Selected file:', selectedFile.value)
}

// 清除文件
const clearFile = () => {
  selectedFile.value = null
}

// 导出数据供父组件使用
defineExpose({
  formData,
  selectedFile,
  handleFileChange,
  clearFile
})
</script>

<style scoped>
.file-selection-panel {
  padding: 20px;
}

.file-info {
  margin-top: 10px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.panel-tip {
  margin-top: 30px;
}
</style>
