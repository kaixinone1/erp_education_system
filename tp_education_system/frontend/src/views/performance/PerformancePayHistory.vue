<template>
  <div class="performance-pay-history">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>查询历史审批表</span>
          <div class="header-actions">
            <el-select v-model="selectedYear" placeholder="选择年份" clearable style="width: 120px; margin-right: 10px;">
              <el-option
                v-for="year in yearOptions"
                :key="year"
                :label="year + '年'"
                :value="year"
              />
            </el-select>
            <el-button type="primary" @click="loadData">
              <el-icon><Search /></el-icon>查询
            </el-button>
          </div>
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
        <el-table-column prop="total_amount" label="绩效工资合计" width="150">
          <template #default="{ row }">
            {{ formatAmount(row.total_amount) }}
          </template>
        </el-table-column>
        <el-table-column prop="town_subsidy_amount" label="乡镇补贴" width="120">
          <template #default="{ row }">
            {{ formatAmount(row.town_subsidy_amount) }}
          </template>
        </el-table-column>
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
            </el-space>
          </template>
        </el-table-column>
        <el-table-column label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="300" fixed="right">
          <template #default="{ row }">
            <el-space>
              <el-button type="primary" size="small" @click="viewDetail(row)">
                查看
              </el-button>
              <el-button type="success" size="small" @click="downloadFile(row, 'excel')" v-if="row.has_excel">
                Excel
              </el-button>
              <el-button type="warning" size="small" @click="downloadFile(row, 'scanned')" v-if="row.has_scanned">
                扫描件
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

    <!-- 详情对话框 -->
    <el-dialog
      v-model="detailVisible"
      title="审批表详情"
      width="900px"
      destroy-on-close
    >
      <div v-if="currentDetail" class="approval-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="年月">{{ formatYearMonth(currentDetail.year_month) }}</el-descriptions-item>
          <el-descriptions-item label="填报单位">{{ currentDetail.report_unit }}</el-descriptions-item>
          <el-descriptions-item label="绩效人数">{{ currentDetail.total_people }} 人</el-descriptions-item>
          <el-descriptions-item label="绩效工资合计">{{ formatAmount(currentDetail.total_amount) }} 元</el-descriptions-item>
          <el-descriptions-item label="乡镇补贴人数">{{ currentDetail.town_subsidy_people }} 人</el-descriptions-item>
          <el-descriptions-item label="乡镇补贴金额">{{ formatAmount(currentDetail.town_subsidy_amount) }} 元</el-descriptions-item>
          <el-descriptions-item label="退休干部">{{ currentDetail.retired_cadre_count }} 人</el-descriptions-item>
          <el-descriptions-item label="退休工人">{{ currentDetail.retired_worker_count }} 人</el-descriptions-item>
          <el-descriptions-item label="离休干部">{{ currentDetail.retired_cadre_office_count }} 人</el-descriptions-item>
          <el-descriptions-item label="岗位设置遗留问题">{{ currentDetail.legacy_total_people }} 人 / {{ formatAmount(currentDetail.legacy_total_amount) }} 元</el-descriptions-item>
        </el-descriptions>

        <div class="remarks-section" v-if="currentDetail.remarks">
          <h4>备注</h4>
          <pre>{{ currentDetail.remarks }}</pre>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'

const loading = ref(false)
const approvalList = ref([])
const page = ref(1)
const size = ref(20)
const total = ref(0)
const selectedYear = ref('')

const detailVisible = ref(false)
const currentDetail = ref(null)

// 年份选项（最近5年）
const yearOptions = computed(() => {
  const currentYear = new Date().getFullYear()
  const years = []
  for (let i = 0; i < 5; i++) {
    years.push(currentYear - i)
  }
  return years
})

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    let url = `/api/performance-pay/list?page=${page.value}&size=${size.value}`
    if (selectedYear.value) {
      url += `&year=${selectedYear.value}`
    }
    const response = await fetch(url)
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

// 查看详情
const viewDetail = async (row: any) => {
  try {
    const response = await fetch(`/api/performance-pay/${row.id}`)
    const result = await response.json()
    if (result.status === 'success') {
      currentDetail.value = result.data
      detailVisible.value = true
    } else {
      ElMessage.error(result.message || '获取详情失败')
    }
  } catch (error) {
    console.error('获取详情失败:', error)
    ElMessage.error('获取详情失败')
  }
}

// 下载文件
const downloadFile = async (row: any, fileType: string) => {
  try {
    const response = await fetch(`/api/performance-pay/${row.id}/download/${fileType}`)
    if (response.ok) {
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      const suffix = fileType === 'scanned' ? '_扫描件.pdf' : '.xls'
      link.download = `绩效工资审批表_${row.year_month}${suffix}`
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

// 格式化金额
const formatAmount = (amount: number) => {
  if (amount === null || amount === undefined) return '0.00'
  return amount.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

// 格式化日期时间
const formatDateTime = (dateTime: string) => {
  if (!dateTime) return ''
  const date = new Date(dateTime)
  return date.toLocaleString('zh-CN')
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
.performance-pay-history {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  align-items: center;
}

.approval-detail {
  padding: 20px;
}

.remarks-section {
  margin-top: 20px;
}

.remarks-section h4 {
  margin-bottom: 10px;
}

.remarks-section pre {
  background-color: #f5f5f5;
  padding: 15px;
  border-radius: 4px;
  white-space: pre-wrap;
  word-wrap: break-word;
}
</style>
