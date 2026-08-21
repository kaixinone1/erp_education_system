<template>
  <div class="snapshot-history">
    <div class="page-header">
      <h2>历史快照管理</h2>
      <p class="description">创建数据快照，实现"时光倒流" — 查看历史数据状态</p>
    </div>

    <!-- 操作栏 -->
    <div class="toolbar">
      <el-button type="primary" @click="showCreateDialog = true" :loading="creating">
        <el-icon><Camera /></el-icon> 创建快照
      </el-button>
      <el-select v-model="filterType" placeholder="快照类型" clearable style="width: 150px; margin-left: 12px" @change="loadSnapshots">
        <el-option label="手动快照" value="manual" />
        <el-option label="月度快照" value="monthly" />
        <el-option label="年度快照" value="yearly" />
      </el-select>
      <el-button @click="loadSnapshots" :loading="loading" style="margin-left: 12px">
        <el-icon><Refresh /></el-icon> 刷新
      </el-button>
    </div>

    <!-- 快照列表 -->
    <el-table :data="snapshots" v-loading="loading" stripe style="margin-top: 16px" max-height="calc(100vh - 280px)">
      <el-table-column prop="快照日期" label="快照日期" width="140" sortable />
      <el-table-column prop="快照类型" label="快照类型" width="120">
        <template #default="{ row }">
          <el-tag :type="row['快照类型'] === 'manual' ? 'primary' : row['快照类型'] === 'monthly' ? 'success' : 'warning'" size="small">
            {{ row['快照类型'] === 'manual' ? '手动' : row['快照类型'] === 'monthly' ? '月度' : '年度' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="涉及表数" label="涉及表数" width="100" />
      <el-table-column prop="总记录数" label="总记录数" width="100" />
      <el-table-column prop="首次创建" label="首次创建" width="180" />
      <el-table-column prop="最后创建" label="最后创建" width="180" />
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" size="small" link @click="viewDetail(row)">时光倒流</el-button>
          <el-button type="danger" size="small" link @click="confirmDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <el-pagination
      v-model:current-page="page"
      v-model:page-size="pageSize"
      :total="total"
      :page-sizes="[10, 20, 50]"
      layout="total, sizes, prev, pager, next"
      style="margin-top: 16px; justify-content: flex-end"
      @change="loadSnapshots"
    />

    <!-- 创建快照对话框 -->
    <el-dialog v-model="showCreateDialog" title="创建数据快照" width="500px">
      <el-form label-width="100px">
        <el-form-item label="快照类型">
          <el-radio-group v-model="createForm.snapshot_type">
            <el-radio value="manual">手动快照</el-radio>
            <el-radio value="monthly">月度快照</el-radio>
            <el-radio value="yearly">年度快照</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="指定表">
          <el-select v-model="createForm.table_name" placeholder="不选则全部表" clearable filterable style="width: 100%">
            <el-option v-for="t in tableList" :key="t" :label="t" :value="t" />
          </el-select>
          <div class="form-tip">留空则对所有业务表创建快照</div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="createSnapshot" :loading="creating">开始创建</el-button>
      </template>
    </el-dialog>

    <!-- 详情对话框 -->
    <el-dialog v-model="showDetailDialog" :title="`快照详情 — ${detailDate}`" width="900px" top="5vh">
      <el-tabs v-model="detailTab" type="border-card">
        <el-tab-pane label="按表查看" name="tables">
          <el-select v-model="selectedTable" placeholder="选择表" filterable style="width: 300px; margin-bottom: 12px" @change="loadDetail">
            <el-option v-for="t in detailTables" :key="t" :label="t" :value="t" />
          </el-select>
          <el-table :data="detailData" v-loading="detailLoading" stripe max-height="500px" border>
            <el-table-column type="index" label="序号" width="60" />
            <el-table-column prop="记录ID" label="记录ID" width="80" />
            <el-table-column v-for="col in detailColumns" :key="col" :prop="col" :label="col" min-width="120" show-overflow-tooltip>
              <template #default="{ row }">
                <span v-if="row['快照数据']">{{ formatValue(row['快照数据'][col]) }}</span>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Camera, Refresh } from '@element-plus/icons-vue'

const loading = ref(false)
const creating = ref(false)
const snapshots = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const filterType = ref('')

// 创建对话框
const showCreateDialog = ref(false)
const createForm = ref({ snapshot_type: 'manual', table_name: '' })
const tableList = ref<string[]>([])

// 详情对话框
const showDetailDialog = ref(false)
const detailLoading = ref(false)
const detailDate = ref('')
const detailTab = ref('tables')
const detailData = ref<any[]>([])
const detailTables = ref<string[]>([])
const selectedTable = ref('')
const detailColumns = ref<string[]>([])

const loadSnapshots = async () => {
  loading.value = true
  try {
    const params = new URLSearchParams()
    params.set('page', String(page.value))
    params.set('page_size', String(pageSize.value))
    if (filterType.value) params.set('snapshot_type', filterType.value)

    const res = await fetch(`/api/snapshots/list?${params}`)
    const data = await res.json()
    if (data.status === 'success') {
      snapshots.value = data.data || []
      total.value = data.data?.length || 0
    }
  } catch (e) {
    console.error('加载快照列表失败:', e)
  } finally {
    loading.value = false
  }
}

const loadTableList = async () => {
  try {
    const res = await fetch('/api/snapshots/tables')
    const data = await res.json()
    if (data.status === 'success') {
      tableList.value = data.data || []
    }
  } catch (e) {
    console.error('加载表列表失败:', e)
  }
}

const createSnapshot = async () => {
  creating.value = true
  try {
    const res = await fetch('/api/snapshots/create', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        table_name: createForm.value.table_name || null,
        snapshot_type: createForm.value.snapshot_type
      })
    })
    const data = await res.json()
    if (data.status === 'success') {
      ElMessage.success(data.message || '快照创建成功')
      showCreateDialog.value = false
      loadSnapshots()
    } else {
      ElMessage.error(data.detail || '创建失败')
    }
  } catch (e: any) {
    ElMessage.error('创建快照失败: ' + (e.message || '未知错误'))
  } finally {
    creating.value = false
  }
}

const viewDetail = async (row: any) => {
  detailDate.value = row['快照日期']
  showDetailDialog.value = true
  detailLoading.value = true
  try {
    const res = await fetch(`/api/snapshots/detail/${detailDate.value}`)
    const data = await res.json()
    if (data.status === 'success') {
      detailData.value = data.data || []
      // 提取所有表名
      const tables = [...new Set(data.data.map((d: any) => d['表名']))]
      detailTables.value = tables as string[]
      if (tables.length > 0) {
        selectedTable.value = tables[0] as string
        updateColumns()
      }
    }
  } catch (e) {
    console.error('加载详情失败:', e)
  } finally {
    detailLoading.value = false
  }
}

const updateColumns = () => {
  if (!selectedTable.value) {
    detailColumns.value = []
    return
  }
  const firstRow = detailData.value.find((d: any) => d['表名'] === selectedTable.value)
  if (firstRow && firstRow['快照数据']) {
    detailColumns.value = Object.keys(firstRow['快照数据']).slice(0, 15)
  }
}

const loadDetail = () => {
  updateColumns()
}

const formatValue = (val: any) => {
  if (val === null || val === undefined) return ''
  if (typeof val === 'object') return JSON.stringify(val)
  return String(val)
}

const confirmDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除 ${row['快照日期']} 的所有快照数据吗？此操作不可恢复。`,
      '确认删除',
      { type: 'warning' }
    )
    const res = await fetch(`/api/snapshots/${row['快照日期']}`, { method: 'DELETE' })
    const data = await res.json()
    if (data.status === 'success') {
      ElMessage.success(data.message)
      loadSnapshots()
    }
  } catch (e: any) {
    if (e !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

onMounted(() => {
  loadSnapshots()
  loadTableList()
})
</script>

<style scoped>
.snapshot-history {
  padding: 20px;
  background: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0 0 8px 0;
  font-size: 22px;
  color: #303133;
}

.description {
  color: #909399;
  font-size: 14px;
  margin: 0;
}

.toolbar {
  display: flex;
  align-items: center;
  background: #fff;
  padding: 16px;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
}

.form-tip {
  color: #909399;
  font-size: 12px;
  margin-top: 4px;
}
</style>