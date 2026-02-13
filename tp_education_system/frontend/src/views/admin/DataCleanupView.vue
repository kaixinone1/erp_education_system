<template>
  <div class="data-cleanup-view">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>数据清理工具</span>
          <el-tag type="warning">开发工具</el-tag>
        </div>
      </template>

      <el-alert
        title="警告：此功能用于开发阶段清理测试数据"
        type="warning"
        description="删除后数据无法恢复，请谨慎操作！"
        show-icon
        :closable="false"
        style="margin-bottom: 20px;"
      />

      <!-- 可删除表列表 -->
      <div class="table-list">
        <h3>可清理的表（显示中文表名）</h3>
        <el-table
          :data="tableList"
          style="width: 100%"
          border
          v-loading="loading"
        >
          <el-table-column
            prop="chinese_name"
            label="中文表名"
            min-width="150"
          />
          <el-table-column
            prop="english_name"
            label="英文表名"
            min-width="200"
          />
          <el-table-column
            prop="table_type"
            label="表类型"
            width="100"
          >
            <template #default="{ row }">
              <el-tag v-if="row.table_type === 'dictionary'" type="success">字典表</el-tag>
              <el-tag v-else type="primary">子表</el-tag>
            </template>
          </el-table-column>
          <el-table-column
            label="状态"
            width="100"
            align="center"
          >
            <template #default="{ row }">
              <el-tag v-if="row.exists_in_db" type="success">存在</el-tag>
              <el-tag v-else type="info">不存在</el-tag>
            </template>
          </el-table-column>
          <el-table-column
            label="操作"
            width="120"
            align="center"
          >
            <template #default="{ row }">
              <el-button
                type="danger"
                size="small"
                @click="confirmCleanup(row)"
                :disabled="!row.exists_in_db"
              >
                清理
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 清理结果 -->
      <el-dialog
        v-model="resultDialogVisible"
        title="清理结果"
        width="500px"
      >
        <div v-if="cleanupResult">
          <el-alert
            :title="cleanupResult.success ? '清理成功' : '清理失败'"
            :type="cleanupResult.success ? 'success' : 'error'"
            show-icon
            :closable="false"
            style="margin-bottom: 15px;"
          />
          
          <div v-if="cleanupResult.details && cleanupResult.details.length > 0">
            <p>清理详情：</p>
            <ul>
              <li v-for="(detail, index) in cleanupResult.details" :key="index">
                {{ detail }}
              </li>
            </ul>
          </div>
          
          <div v-if="cleanupResult.errors && cleanupResult.errors.length > 0">
            <p style="color: red;">错误信息：</p>
            <ul>
              <li v-for="(error, index) in cleanupResult.errors" :key="index" style="color: red;">
                {{ error }}
              </li>
            </ul>
          </div>
        </div>
      </el-dialog>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// 可删除表列表
const tableList = ref<any[]>([])
const loading = ref(false)

// 清理结果
const resultDialogVisible = ref(false)
const cleanupResult = ref<any>(null)

// 获取可删除表列表
const fetchTableList = async () => {
  loading.value = true
  try {
    const response = await fetch('/api/admin/list-deletable-tables')
    if (response.ok) {
      const result = await response.json()
      tableList.value = result.tables || []
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

// 确认清理
const confirmCleanup = (row: any) => {
  ElMessageBox.confirm(
    `确定要清理表 "${row.chinese_name}" 吗？\n这将删除数据库表、表名映射、字段配置和导航配置。`,
    '确认清理',
    {
      confirmButtonText: '确定清理',
      cancelButtonText: '取消',
      type: 'warning',
    }
  )
    .then(() => {
      doCleanup(row.chinese_name)
    })
    .catch(() => {
      // 取消操作
    })
}

// 执行清理
const doCleanup = async (chineseName: string) => {
  try {
    const response = await fetch('/api/admin/cleanup-table', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ chinese_name: chineseName })
    })
    
    const result = await response.json()
    cleanupResult.value = result
    resultDialogVisible.value = true
    
    if (result.success) {
      ElMessage.success(`表 "${chineseName}" 清理成功`)
      // 刷新列表
      fetchTableList()
    } else {
      ElMessage.error(`表 "${chineseName}" 清理失败`)
    }
  } catch (error) {
    console.error('清理失败:', error)
    ElMessage.error('清理失败')
  }
}

// 页面加载时获取列表
onMounted(() => {
  fetchTableList()
})
</script>

<style scoped>
.data-cleanup-view {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.table-list {
  margin-top: 20px;
}

.table-list h3 {
  margin-bottom: 15px;
  font-size: 16px;
  font-weight: 600;
}
</style>
