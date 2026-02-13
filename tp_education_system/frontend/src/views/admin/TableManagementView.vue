<template>
  <div class="table-management-view">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>数据表管理</span>
          <el-button type="primary" @click="loadTables" :loading="loading">
            <el-icon><Refresh /></el-icon>
            刷新列表
          </el-button>
        </div>
      </template>

      <el-alert
        title="警告：删除表将永久删除该表的所有数据，包括数据库表、表结构配置、导航菜单等。此操作不可恢复！"
        type="warning"
        show-icon
        :closable="false"
        style="margin-bottom: 20px;"
      />

      <el-table
        :data="tables"
        style="width: 100%"
        border
        v-loading="loading"
      >
        <el-table-column prop="chinese_name" label="中文表名" min-width="150">
          <template #default="{ row }">
            <span>{{ row.chinese_name }}</span>
            <el-tag v-if="row.is_orphan" type="danger" size="small" style="margin-left: 5px;">残留</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="english_name" label="英文表名" min-width="150" />
        <el-table-column prop="table_type" label="表类型" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.table_type === 'master'" type="primary">主表</el-tag>
            <el-tag v-else-if="row.table_type === 'child'" type="warning">子表</el-tag>
            <el-tag v-else-if="row.table_type === 'dictionary'" type="success">字典表</el-tag>
            <el-tag v-else type="info">{{ row.table_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="field_count" label="字段数" width="80" />
        <el-table-column prop="created_at" label="创建时间" min-width="150">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button
              type="danger"
              size="small"
              @click="confirmDelete(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="!loading && tables.length === 0" description="暂无数据表" />
    </el-card>

    <!-- 删除确认对话框 -->
    <el-dialog
      v-model="deleteDialogVisible"
      title="确认删除"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-alert
        title="此操作将永久删除以下表及其所有数据："
        type="error"
        show-icon
        :closable="false"
        style="margin-bottom: 15px;"
      />
      <p><strong>中文表名：</strong>{{ selectedTable?.chinese_name }}</p>
      <p><strong>英文表名：</strong>{{ selectedTable?.english_name }}</p>
      <p><strong>表类型：</strong>{{ selectedTable?.table_type }}</p>
      <p style="color: red; margin-top: 15px;">删除内容包括：</p>
      <ul style="color: red;">
        <li>数据库表及所有数据</li>
        <li>表名映射配置</li>
        <li>表结构配置</li>
        <li>导航菜单</li>
        <li>字段配置文件</li>
      </ul>

      <template #footer>
        <el-button @click="deleteDialogVisible = false">取消</el-button>
        <el-button
          type="danger"
          @click="handleDelete"
          :loading="deleting"
        >
          确认删除
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Refresh } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// 表格数据
const tables = ref<any[]>([])
const loading = ref(false)
const deleteDialogVisible = ref(false)
const selectedTable = ref<any>(null)
const deleting = ref(false)

// 加载表列表
const loadTables = async () => {
  loading.value = true
  try {
    const response = await fetch('/api/admin/tables')
    if (response.ok) {
      const result = await response.json()
      tables.value = result.tables || []
    } else {
      ElMessage.error('获取表列表失败')
    }
  } catch (error) {
    console.error('获取表列表失败:', error)
    ElMessage.error('获取表列表失败')
  } finally {
    loading.value = false
  }
}

// 格式化日期
const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

// 确认删除
const confirmDelete = (row: any) => {
  selectedTable.value = row
  deleteDialogVisible.value = true
}

// 执行删除
const handleDelete = async () => {
  if (!selectedTable.value) return

  deleting.value = true
  try {
    const response = await fetch('/api/admin/cleanup-table', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        chinese_name: selectedTable.value.chinese_name,
        english_name: selectedTable.value.english_name
      })
    })

    if (response.ok) {
      const result = await response.json()
      ElMessage.success(result.message)
      deleteDialogVisible.value = false
      // 刷新列表
      loadTables()
    } else {
      const error = await response.json()
      ElMessage.error(error.detail || '删除失败')
    }
  } catch (error) {
    console.error('删除失败:', error)
    ElMessage.error('删除失败')
  } finally {
    deleting.value = false
  }
}

// 页面加载时获取数据
onMounted(() => {
  loadTables()
})
</script>

<style scoped>
.table-management-view {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
