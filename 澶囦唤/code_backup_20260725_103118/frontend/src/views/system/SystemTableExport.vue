<template>
  <div class="system-table-export-page">
    <el-card class="page-card">
      <template #header>
        <div class="card-header">
          <h2>系统数据表字段导出</h2>
        </div>
      </template>

      <el-alert
        title="使用说明"
        type="info"
        :closable="false"
        style="margin-bottom: 20px;"
      >
        <p>1. 点击"导出字段模板"下载Excel工作簿，每个工作表对应一个数据表</p>
        <p>2. 红色加粗字段为必填字段，请在"填写内容"列中填写数据</p>
        <p>3. 填写完成后，点击"导入数据"上传文件，系统将自动分拣到对应表中</p>
        <p>4. 请勿修改工作表名称和列名</p>
      </el-alert>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-card shadow="hover">
            <template #header>
              <span style="font-weight: bold;">步骤一：导出字段模板</span>
            </template>
            <el-button type="primary" :loading="exporting" @click="handleExport" size="large" style="width: 100%;">
              <el-icon><Download /></el-icon>
              导出字段模板
            </el-button>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card shadow="hover">
            <template #header>
              <span style="font-weight: bold;">步骤二：导入填充数据</span>
            </template>
            <el-upload
              ref="uploadRef"
              :auto-upload="false"
              :limit="1"
              accept=".xlsx"
              :on-change="handleFileChange"
              style="width: 100%;"
            >
              <el-button type="success" :loading="importing" :disabled="!selectedFile" @click="handleImport" size="large" style="width: 100%;">
                <el-icon><Upload /></el-icon>
                导入数据
              </el-button>
              <template #tip>
                <div class="el-upload__tip">
                  {{ selectedFile ? `已选择：${selectedFile.name}` : '请选择填写好的Excel文件' }}
                </div>
              </template>
            </el-upload>
          </el-card>
        </el-col>
      </el-row>

      <el-card v-if="importResults.length > 0" style="margin-top: 20px;">
        <template #header>
          <span>导入结果</span>
        </template>
        <div v-for="(result, index) in importResults" :key="index" style="padding: 4px 0;">
          <el-tag :type="result.includes('成功') ? 'success' : 'danger'" size="small">
            {{ result }}
          </el-tag>
        </div>
      </el-card>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Download, Upload } from '@element-plus/icons-vue'

const exporting = ref(false)
const importing = ref(false)
const selectedFile = ref<File | null>(null)
const importResults = ref<string[]>([])

const handleExport = async () => {
  exporting.value = true
  try {
    const response = await fetch('/api/system-tables/export-fields')
    if (!response.ok) {
      throw new Error('导出失败')
    }
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `系统数据表字段模板_${new Date().toISOString().slice(0, 10)}.xlsx`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (error: any) {
    ElMessage.error(error.message || '导出失败')
  } finally {
    exporting.value = false
  }
}

const handleFileChange = (file: any) => {
  selectedFile.value = file.raw
}

const handleImport = async () => {
  if (!selectedFile.value) {
    ElMessage.warning('请先选择文件')
    return
  }

  importing.value = true
  importResults.value = []
  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value)

    const response = await fetch('/api/system-tables/import-from-workbook', {
      method: 'POST',
      body: formData
    })

    const result = await response.json()
    if (result.status === 'success') {
      ElMessage.success(result.message)
      importResults.value = result.details || []
    } else {
      ElMessage.error(result.message || '导入失败')
    }
  } catch (error: any) {
    ElMessage.error(error.message || '导入失败')
  } finally {
    importing.value = false
  }
}
</script>

<style scoped>
.system-table-export-page {
  padding: 20px;
  background: #f5f5f5;
  min-height: 100vh;
}

.page-card {
  min-height: calc(100vh - 100px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>