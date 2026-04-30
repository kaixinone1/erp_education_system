<template>
  <div class="backup-manager">
    <el-dialog
      v-model="visible"
      title="审批表备份管理"
      width="1000px"
      :close-on-click-modal="false"
      destroy-on-close
    >
      <el-tabs v-model="activeTab">
        <!-- 自动备份 -->
        <el-tab-pane label="自动备份" name="auto">
          <div class="backup-section">
            <h3>系统自动备份的Excel和PDF文件</h3>
            <el-table :data="autoBackups" style="width: 100%" v-loading="loading">
              <el-table-column prop="filename" label="文件名" />
              <el-table-column prop="type" label="类型" width="100">
                <template #default="scope">
                  <el-tag :type="scope.row.type === 'excel' ? 'success' : 'warning'">
                    {{ scope.row.type === 'excel' ? 'Excel' : 'PDF' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="createTime" label="创建时间" width="180" />
              <el-table-column prop="size" label="大小" width="100">
                <template #default="scope">
                  {{ formatFileSize(scope.row.size) }}
                </template>
              </el-table-column>
              <el-table-column label="操作" width="150">
                <template #default="scope">
                  <el-button type="primary" size="small" @click="downloadBackup(scope.row)">下载</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-tab-pane>

        <!-- 扫描件管理 -->
        <el-tab-pane label="签字盖章扫描件" name="scan">
          <div class="backup-section">
            <div class="upload-area">
              <el-upload
                drag
                action="/api/performance-pay-approval/upload-scan"
                :data="{ 年月: currentMonth }"
                :on-success="handleUploadSuccess"
                :on-error="handleUploadError"
                accept=".pdf,.jpg,.jpeg,.png"
              >
                <el-icon class="el-icon--upload"><upload-filled /></el-icon>
                <div class="el-upload__text">
                  拖拽文件到此处或 <em>点击上传</em>
                </div>
                <template #tip>
                  <div class="el-upload__tip">
                    支持 PDF、JPG、PNG 格式，文件大小不超过 50MB
                  </div>
                </template>
              </el-upload>
            </div>

            <h3>已上传的扫描件</h3>
            <el-table :data="scanFiles" style="width: 100%" v-loading="loadingScans">
              <el-table-column prop="filename" label="文件名" />
              <el-table-column prop="upload_time" label="上传时间" width="180" />
              <el-table-column prop="size" label="大小" width="100">
                <template #default="scope">
                  {{ formatFileSize(scope.row.size) }}
                </template>
              </el-table-column>
              <el-table-column label="操作" width="200">
                <template #default="scope">
                  <el-button type="primary" size="small" @click="downloadScan(scope.row)">下载</el-button>
                  <el-button type="danger" size="small" @click="deleteScan(scope.row)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-tab-pane>
      </el-tabs>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="visible = false">关闭</el-button>
          <el-button type="primary" @click="refreshData">刷新</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'

const visible = ref(false)
const activeTab = ref('auto')
const loading = ref(false)
const loadingScans = ref(false)
const autoBackups = ref<any[]>([])
const scanFiles = ref<any[]>([])

// 当前月份
const now = new Date()
const currentMonth = computed(() => `${now.getFullYear()}年${now.getMonth() + 1}月`)

// 格式化文件大小
const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 打开对话框
const open = () => {
  visible.value = true
  refreshData()
}

// 刷新数据
const refreshData = async () => {
  await Promise.all([loadAutoBackups(), loadScanFiles()])
}

// 加载自动备份
const loadAutoBackups = async () => {
  loading.value = true
  try {
    const response = await fetch('/api/performance-pay-approval/history')
    if (response.ok) {
      const result = await response.json()
      if (result.status === 'success') {
        // 构建备份文件列表
        const backups = []
        for (const record of result.data) {
          // Excel文件
          backups.push({
            filename: `绩效工资审批表_${record.年月}.xlsx`,
            type: 'excel',
            createTime: record.创建时间,
            size: 0, // 实际大小需要从文件系统获取
            id: record.id
          })
          // PDF文件
          backups.push({
            filename: `绩效工资审批表_${record.年月}.pdf`,
            type: 'pdf',
            createTime: record.创建时间,
            size: 0,
            id: record.id
          })
        }
        autoBackups.value = backups
      }
    }
  } catch (error) {
    console.error('加载备份失败', error)
  } finally {
    loading.value = false
  }
}

// 加载扫描件
const loadScanFiles = async () => {
  loadingScans.value = true
  try {
    const response = await fetch('/api/performance-pay-approval/scans')
    if (response.ok) {
      const result = await response.json()
      if (result.status === 'success') {
        scanFiles.value = result.data
      }
    }
  } catch (error) {
    console.error('加载扫描件失败', error)
  } finally {
    loadingScans.value = false
  }
}

// 下载备份
const downloadBackup = async (row: any) => {
  try {
    const endpoint = row.type === 'excel' 
      ? `/api/performance-pay-approval/download/${row.id}`
      : `/api/performance-pay-approval/download-pdf/${row.id}`
    
    const response = await fetch(endpoint)
    if (response.ok) {
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = row.filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
    }
  } catch (error) {
    ElMessage.error('下载失败')
  }
}

// 下载扫描件
const downloadScan = async (row: any) => {
  try {
    const response = await fetch(`/api/performance-pay-approval/download-scan/${row.filename}`)
    if (response.ok) {
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = row.filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
    }
  } catch (error) {
    ElMessage.error('下载失败')
  }
}

// 删除扫描件
const deleteScan = async (row: any) => {
  try {
    await ElMessageBox.confirm('确定要删除这个扫描件吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    const response = await fetch(`/api/performance-pay-approval/delete-scan/${row.filename}`, {
      method: 'DELETE'
    })
    
    if (response.ok) {
      ElMessage.success('删除成功')
      loadScanFiles()
    } else {
      throw new Error('删除失败')
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
    }
  }
}

// 上传成功
const handleUploadSuccess = () => {
  ElMessage.success('上传成功')
  loadScanFiles()
}

// 上传失败
const handleUploadError = () => {
  ElMessage.error('上传失败')
}

defineExpose({
  open
})
</script>

<style scoped>
.backup-section {
  padding: 20px;
}

.backup-section h3 {
  margin: 20px 0 15px;
  font-size: 16px;
  color: #333;
}

.upload-area {
  margin-bottom: 30px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
