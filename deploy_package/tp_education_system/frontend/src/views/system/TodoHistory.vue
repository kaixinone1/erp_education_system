<template>
  <div class="todo-history-container">
    <el-card>
      <template #header>
        <div class="header-content">
          <div class="title-section">
            <el-icon class="title-icon"><Clock /></el-icon>
            <span class="title">待办历史记录</span>
          </div>
          <div class="header-actions">
            <el-button @click="loadData">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </div>
      </template>

      <!-- 筛选条件 -->
      <div class="filter-section">
        <el-form inline>
          <el-form-item label="教师姓名">
            <el-input v-model="filters.teacherName" placeholder="请输入教师姓名" clearable @keyup.enter="loadData" />
          </el-form-item>
          <el-form-item label="业务类型">
            <el-select v-model="filters.businessType" placeholder="请选择" clearable>
              <el-option label="退休" value="RETIREMENT" />
              <el-option label="去世" value="DEATH" />
              <el-option label="高龄补贴" value="OCTOGENARIAN" />
            </el-select>
          </el-form-item>
          <el-form-item label="状态">
            <el-select v-model="filters.status" placeholder="请选择" clearable>
              <el-option label="已完成" value="completed" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="loadData">查询</el-button>
            <el-button @click="resetFilters">重置</el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 列表 -->
      <el-table :data="tableData" v-loading="loading" stripe>
        <el-table-column prop="teacher_name" label="教师姓名" width="120" />
        <el-table-column prop="business_type" label="业务类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getBusinessTypeTag(row.business_type)" size="small">
              {{ getBusinessTypeName(row.business_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="title" label="标题" min-width="200" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'completed' ? 'success' : row.status === 'pending' ? 'warning' : 'info'" size="small">
              {{ row.status === 'completed' ? '已完成' : row.status === 'pending' ? '待处理' : row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160">
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="completed_at" label="完成时间" width="160">
          <template #default="{ row }">
            {{ formatTime(row.completed_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="archived_at" label="归档时间" width="160">
          <template #default="{ row }">
            {{ formatTime(row.archived_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="return_count" label="退回次数" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.return_count > 0" type="warning" size="small">{{ row.return_count }}次</el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="viewDetail(row)">查看详情</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.size"
          :total="pagination.total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          @size-change="loadData"
          @current-change="loadData"
        />
      </div>
    </el-card>

    <!-- 详情对话框 -->
    <el-dialog v-model="detailVisible" title="办理详情" width="900px">
      <el-descriptions :column="2" border v-if="currentRow">
        <el-descriptions-item label="教师姓名">{{ currentRow.teacher_name }}</el-descriptions-item>
        <el-descriptions-item label="业务类型">{{ getBusinessTypeName(currentRow.business_type) }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ formatTime(currentRow.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="完成时间">{{ formatTime(currentRow.completed_at) }}</el-descriptions-item>
        <el-descriptions-item label="归档时间">{{ formatTime(currentRow.archived_at) }}</el-descriptions-item>
        <el-descriptions-item label="退回次数">{{ currentRow.return_count }}次</el-descriptions-item>
        <el-descriptions-item label="标题" :span="2">{{ currentRow.title }}</el-descriptions-item>
        <el-descriptions-item label="描述" :span="2">{{ currentRow.description || '-' }}</el-descriptions-item>
        <el-descriptions-item label="退回原因" :span="2">{{ currentRow.return_reason || '-' }}</el-descriptions-item>
      </el-descriptions>
      
      <!-- 任务项完成情况 -->
      <div v-if="currentRow.task_items && currentRow.task_items.length" style="margin-top: 20px">
        <h4>任务项完成情况</h4>
        <el-table :data="currentRow.task_items" size="small" border>
          <el-table-column type="index" label="序号" width="60" />
          <el-table-column label="任务内容">
            <template #default="{ row }">
              {{ row.标题 || row.name || row.title || '-' }}
            </template>
          </el-table-column>
          <el-table-column label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="(row.完成状态 || row.completed) ? 'success' : 'info'" size="small">
                {{ (row.完成状态 || row.completed) ? '已完成' : '待处理' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="完成时间" width="180">
            <template #default="{ row }">
              {{ row.完成时间 || row.completed_at || '-' }}
            </template>
          </el-table-column>
        </el-table>
      </div>
      
      <!-- 办理记录 -->
      <div v-if="currentRow.notes && currentRow.notes.length" style="margin-top: 20px">
        <h4>办理记录</h4>
        <el-table :data="currentRow.notes" size="small" border>
          <el-table-column prop="时间" label="办理时间" width="180" />
          <el-table-column prop="事项" label="办理事项" />
        </el-table>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Clock, Refresh } from '@element-plus/icons-vue'

const API_BASE_URL = ''

const loading = ref(false)
const tableData = ref<any[]>([])
const detailVisible = ref(false)
const currentRow = ref<any>(null)

const filters = reactive({
  teacherName: '',
  businessType: '',
  status: ''
})

const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

const loadData = async () => {
  loading.value = true
  try {
    const params = new URLSearchParams()
    if (filters.teacherName) params.append('teacher_name', filters.teacherName)
    if (filters.businessType) params.append('business_type', filters.businessType)
    if (filters.status) params.append('status', filters.status)
    params.append('page', pagination.page.toString())
    params.append('size', pagination.size.toString())

    const res = await fetch(`${API_BASE_URL}/api/todo-system/todo-history?${params}`)
    const result = await res.json()
    
    if (result.success) {
      tableData.value = result.data
      pagination.total = result.total
    } else {
      ElMessage.error(result.message || '加载失败')
    }
  } catch (error) {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

const resetFilters = () => {
  filters.teacherName = ''
  filters.businessType = ''
  filters.status = ''
  pagination.page = 1
  loadData()
}

const viewDetail = (row: any) => {
  currentRow.value = row
  detailVisible.value = true
}

const formatTime = (time: string) => {
  if (!time) return '-'
  return time.replace('T', ' ').substring(0, 19)
}

const getBusinessTypeName = (type: string) => {
  const map: Record<string, string> = {
    'RETIREMENT': '退休',
    'RETIREMENT_REMIND': '退休提醒',
    'retirement_reminder': '退休提醒',
    'DEATH': '死亡登记',
    'death': '死亡登记',
    'DEATH_001': '死亡登记',
    'death_001': '死亡登记',
    'death_registration': '死亡登记',
    'OCTOGENARIAN': '高龄补贴',
    'octogenarian': '高龄补贴',
    'OCTOGENARIAN_001': '高龄补贴',
    'octogenarian_subsidy': '高龄补贴',
    'MIGRATED': '退休'
  }
  return map[type] || type || '-'
}

const getBusinessTypeTag = (type: string) => {
  const map: Record<string, string> = {
    'RETIREMENT': 'warning',
    'DEATH': 'danger',
    'OCTOGENARIAN': 'success'
  }
  return map[type] || ''
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.todo-history-container {
  padding: 20px;
}
.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.title-section {
  display: flex;
  align-items: center;
  gap: 8px;
}
.title-icon {
  font-size: 20px;
  color: #409eff;
}
.title {
  font-size: 18px;
  font-weight: bold;
}
.filter-section {
  margin-bottom: 20px;
}
.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
