<template>
  <div class="performance-pay-upload">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>上传审批表扫描件</span>
        </div>
      </template>

      <!-- 审批表列表 -->
      <el-table :data="approvalList" v-loading="loading" style="width: 100%">
        <el-table-column type="index" label="序号" width="60" />
        <el-table-column prop="year_month" label="年月" width="120">
          <template #default="{ row }">
            {{ formatYearMonth(row.year_month) }}
          </template>
        </el-table-column>
        <el-table-column prop="report_unit" label="填报单位" width="150" />
        <el-table-column prop="total_people" label="绩效人数" width="100" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="文件状态" width="200">
          <template #default="{ row }">
            <el-space>
              <el-tag v-if="row.has_excel" type="success" size="small">Excel</el-tag>
              <el-tag v-if="row.has_pdf" type="success" size="small">PDF</el-tag>
              <el-tag v-if="row.has_scanned" type="success" size="small">扫描件</el-tag>
              <el-tag v-if="!row.has_scanned" type="info" size="small">未上传</el-tag>
            </el-space>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="300" fixed="right">
          <template #default="{ row }">
            <el-space>
              <el-upload
                :action="`/api/performance-pay/${row.id}/upload-scanned`"
                :headers="uploadHeaders"
                :show-file-list="false"
                :before-upload="beforeUpload"
                :on-success="handleUploadSuccess"
                :on-error="handleUploadError"
                accept=".pdf"
              >
                <el-button type="primary" size="small">
                  <el-icon><Upload /></el-icon>上传扫描件
                </el-button>
              </el-upload>
              <el-button
                v-if="row.has_scanned"
                type="success"
                size="small"
                @click="downloadFile(row)"
              >
                下载扫描件
              </el-button>
            </el-space>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="page"
        v-model:page-size="size"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next"
        @size-change="loadData"
        @current-change="loadData"
        style="margin-top: 20px; justify-content: flex-end;"
      />
    </el-card>

    <!-- 上传说明 -->
    <el-card class="upload-tips" style="margin-top: 20px;">
      <template #header>
        <span>上传说明</span>
      </template>
      <el-alert
        title="扫描件上传要求"
        type="info"
        :closable="false"
      >
        <template #default>
          <ol>
            <li>请上传PDF格式的扫描件</li>
            <li>文件大小不超过10MB</li>
            <li>扫描件应包含完整的审批表内容和签章</li>
            <li>建议扫描分辨率300dpi以上，确保清晰可读</li>
            <li>如需重新上传，直接选择新文件即可覆盖原文件</li>
          </ol>
        </template>
      </el-alert>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Upload } from '@element-plus/icons-vue'

const loading = ref(false)
const approvalList = ref([])
const page = ref(1)
const size = ref(20)
const total = ref(0)

// 上传请求头
const uploadHeaders = {
  // 可以添加认证token等
}

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    const response = await fetch(`/api/performance-pay/list?page=${page.value}&size=${size.value}`)
    const result = await response.json()
    if (result.status === 'success') {
      approvalList.value = result.data
      total.value = result.total
    } else {
      ElMessage.error(result.message || '加载数据失败')
    }
  } catch (error) {
    console.error('加载数据失败:', error)
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

// 上传前验证
const beforeUpload = (file: File) => {
  const isPDF = file.type === 'application/pdf' || file.name.endsWith('.pdf')
  if (!isPDF) {
    ElMessage.error('只能上传PDF格式的文件！')
    return false
  }
  const isLt10M = file.size / 1024 / 1024 < 10
  if (!isLt10M) {
    ElMessage.error('文件大小不能超过10MB！')
    return false
  }
  return true
}

// 上传成功
const handleUploadSuccess = (response: any) => {
  if (response.status === 'success') {
    ElMessage.success('扫描件上传成功')
    loadData()
  } else {
    ElMessage.error(response.message || '上传失败')
  }
}

// 上传失败
const handleUploadError = (error: any) => {
  console.error('上传失败:', error)
  ElMessage.error('上传失败，请重试')
}

// 下载扫描件
const downloadFile = async (row: any) => {
  try {
    const response = await fetch(`/api/performance-pay/${row.id}/download/scanned`)
    if (response.ok) {
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `绩效工资审批表_${row.year_month}_扫描件.pdf`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
    } else {
      ElMessage.error('下载失败')
    }
  } catch (error) {
    console.error('下载失败:', error)
    ElMessage.error('下载失败')
  }
}

// 格式化年月
const formatYearMonth = (yearMonth: string) => {
  if (!yearMonth) return ''
  const [year, month] = yearMonth.split('-')
  return `${year}年${parseInt(month)}月`
}

// 获取状态类型
const getStatusType = (status: string) => {
  const typeMap: Record<string, string> = {
    'draft': 'info',
    'generated': 'primary',
    'exported': 'success',
    'uploaded': 'warning'
  }
  return typeMap[status] || 'info'
}

// 获取状态文本
const getStatusText = (status: string) => {
  const textMap: Record<string, string> = {
    'draft': '草稿',
    'generated': '已生成',
    'exported': '已导出',
    'uploaded': '已上传扫描件'
  }
  return textMap[status] || status
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.performance-pay-upload {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.upload-tips ol {
  margin: 10px 0;
  padding-left: 20px;
}

.upload-tips li {
  margin: 5px 0;
}
</style>
