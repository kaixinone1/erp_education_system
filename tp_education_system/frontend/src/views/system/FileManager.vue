<template>
  <div class="file-manager">
    <el-card class="header-card">
      <div class="header-row">
        <div>
          <h2>文件管理</h2>
          <p class="subtitle">管理系统生成的导出文件（退休呈报表、职务升降表、绩效工资审批表等）</p>
        </div>
        <div class="stats">
          <el-tag type="info" size="large">共 {{ totalCount }} 个文件</el-tag>
          <el-tag type="warning" size="large" v-if="totalSize">总大小 {{ totalSize }}</el-tag>
        </div>
      </div>
    </el-card>

    <el-card class="table-card">
      <!-- 工具栏 -->
      <div class="toolbar">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索文件名..."
          clearable
          style="width: 300px"
          @input="filterFiles"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-select v-model="filterType" placeholder="文件类型" clearable style="width: 140px" @change="filterFiles">
          <el-option label="全部类型" value="" />
          <el-option label="Word (.docx)" value=".docx" />
          <el-option label="PDF (.pdf)" value=".pdf" />
          <el-option label="Excel (.xlsx)" value=".xlsx" />
          <el-option label="HTML (.html)" value=".html" />
        </el-select>
        <el-select v-model="filterCategory" placeholder="文件分类" clearable style="width: 160px" @change="filterFiles">
          <el-option label="全部分类" value="" />
          <el-option label="退休呈报表" value="退休" />
          <el-option label="职务升降表" value="职务升降" />
          <el-option label="绩效工资审批表" value="绩效" />
        </el-select>
        <el-button type="danger" @click="batchDelete" :disabled="selectedFiles.length === 0">
          <el-icon><Delete /></el-icon> 批量删除 ({{ selectedFiles.length }})
        </el-button>
        <el-button type="primary" @click="refreshList" :loading="loading">
          <el-icon><Refresh /></el-icon> 刷新
        </el-button>
      </div>

      <!-- 表格 -->
      <el-table :data="displayFiles" v-loading="loading" stripe style="width: 100%" max-height="600"
        @selection-change="handleSelectionChange" ref="tableRef">
        <el-table-column type="selection" width="50" />
        <el-table-column prop="文件名" label="文件名" min-width="350" show-overflow-tooltip>
          <template #default="{ row }">
            <span :class="['file-icon', row.类型.replace('.', '')]"></span>
            <span style="margin-left: 6px">{{ row.文件名 }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="类型" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="typeTagColor(row.类型)" size="small">{{ row.类型 }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="大小显示" label="大小" width="100" align="right" />
        <el-table-column prop="修改时间" label="修改时间" width="170" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.类型 === '.pdf' || row.类型 === '.html'"
              type="primary"
              size="small"
              link
              @click="previewFile(row)"
            >
              <el-icon><View /></el-icon> 预览
            </el-button>
            <el-button
              v-else
              type="primary"
              size="small"
              link
              @click="downloadFile(row)"
            >
              <el-icon><Download /></el-icon> 下载查看
            </el-button>
            <el-button type="danger" size="small" link @click="confirmDelete(row)">
              <el-icon><Delete /></el-icon> 删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div v-if="displayFiles.length === 0 && !loading" class="empty-state">
        <el-empty description="暂无文件" />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, View, Download, Delete } from '@element-plus/icons-vue'
import axios from 'axios'

const loading = ref(false)
const allFiles = ref([])
const searchKeyword = ref('')
const filterType = ref('')
const filterCategory = ref('')
const selectedFiles = ref([])
const tableRef = ref(null)

const displayFiles = ref([])
const totalCount = computed(() => allFiles.value.length)
const totalSize = computed(() => {
  const total = allFiles.value.reduce((sum, f) => sum + (f.大小 || 0), 0)
  if (total < 1024) return total + ' B'
  if (total < 1024 * 1024) return (total / 1024).toFixed(1) + ' KB'
  return (total / (1024 * 1024)).toFixed(1) + ' MB'
})

function typeTagColor(type) {
  const map = { '.pdf': 'danger', '.docx': 'primary', '.xlsx': 'success', '.html': 'warning' }
  return map[type] || 'info'
}

function handleSelectionChange(selection) {
  selectedFiles.value = selection
}

function filterFiles() {
  let result = allFiles.value
  if (searchKeyword.value) {
    const kw = searchKeyword.value.toLowerCase()
    result = result.filter(f => f.文件名.toLowerCase().includes(kw))
  }
  if (filterType.value) {
    result = result.filter(f => f.类型 === filterType.value)
  }
  if (filterCategory.value) {
    result = result.filter(f => {
      const name = f.文件名
      if (filterCategory.value === '退休') return name.includes('退休')
      if (filterCategory.value === '职务升降') return name.includes('职务升降')
      if (filterCategory.value === '绩效') return name.includes('绩效')
      return true
    })
  }
  displayFiles.value = result
}

async function refreshList() {
  loading.value = true
  try {
    const res = await axios.get('/api/file-manager/list')
    if (res.data.成功) {
      allFiles.value = res.data.数据 || []
      filterFiles()
    } else {
      ElMessage.error('获取文件列表失败：' + (res.data.错误 || '未知错误'))
    }
  } catch (e) {
    ElMessage.error('获取文件列表失败：' + e.message)
  } finally {
    loading.value = false
  }
}

function previewFile(row) {
  const url = `/api/file-manager/preview/${encodeURI(row.路径)}`
  window.open(url, '_blank')
}

function downloadFile(row) {
  const url = `/api/file-manager/preview/${encodeURI(row.路径)}`
  const a = document.createElement('a')
  a.href = url
  a.download = row.文件名
  a.click()
}

async function confirmDelete(row) {
  try {
    await ElMessageBox.confirm(
      `确定要删除文件 "${row.文件名}" 吗？此操作不可恢复。`,
      '确认删除',
      { confirmButtonText: '确认删除', cancelButtonText: '取消', type: 'warning' }
    )
    await axios.post('/api/file-manager/delete', { 路径: row.路径 })
    ElMessage.success('文件已删除')
    await refreshList()
  } catch (e) {
    if (e !== 'cancel' && e !== 'close') {
      ElMessage.error('删除失败：' + (e.response?.data?.detail || e.message))
    }
  }
}

async function batchDelete() {
  const count = selectedFiles.value.length
  if (count === 0) return
  try {
    await ElMessageBox.confirm(
      `确定要批量删除选中的 ${count} 个文件吗？此操作不可恢复。`,
      '批量删除确认',
      { confirmButtonText: '确认删除', cancelButtonText: '取消', type: 'warning' }
    )
    const paths = selectedFiles.value.map(f => f.路径)
    const res = await axios.post('/api/file-manager/batch-delete', { 路径列表: paths })
    if (res.data.成功) {
      ElMessage.success(res.data.消息)
    } else {
      ElMessage.error('删除失败：' + (res.data.错误 || '未知错误'))
    }
    await refreshList()
  } catch (e) {
    if (e !== 'cancel' && e !== 'close') {
      ElMessage.error('批量删除失败：' + (e.response?.data?.detail || e.message))
    }
  }
}

onMounted(() => {
  refreshList()
})
</script>

<style scoped>
.file-manager {
  padding: 20px;
}

.header-card {
  margin-bottom: 16px;
}

.header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-row h2 {
  margin: 0 0 4px 0;
  font-size: 20px;
}

.subtitle {
  margin: 0;
  color: #909399;
  font-size: 13px;
}

.stats {
  display: flex;
  gap: 10px;
}

.table-card {
  margin-bottom: 16px;
}

.toolbar {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  align-items: center;
}

.empty-state {
  padding: 40px 0;
}

.file-icon {
  display: inline-block;
  width: 16px;
  height: 16px;
  vertical-align: middle;
  border-radius: 2px;
  margin-right: 4px;
}
.file-icon.docx { background: #409eff; }
.file-icon.pdf { background: #f56c6c; }
.file-icon.xlsx { background: #67c23a; }
.file-icon.html { background: #e6a23c; }
</style>