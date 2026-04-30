<template>
  <div class="statistics-container">
    <el-card class="statistics-card">
      <template #header>
        <div class="card-header">
          <span>绩效工资数据统计</span>
          <div class="header-actions">
            <el-date-picker
              v-model="selectedYear"
              type="year"
              placeholder="选择年份"
              value-format="YYYY"
              style="width: 120px; margin-right: 10px;"
            />
            <el-select v-model="selectedMonth" placeholder="选择月份" style="width: 120px; margin-right: 10px;">
              <el-option
                v-for="month in 12"
                :key="month"
                :label="month + '月'"
                :value="month"
              />
            </el-select>
            <el-button type="primary" @click="loadStatistics">
              <el-icon><Search /></el-icon>查询统计
            </el-button>
            <el-button type="success" @click="exportStatistics">
              <el-icon><Download /></el-icon>导出统计表
            </el-button>
          </div>
        </div>
      </template>

      <!-- 汇总统计卡片 -->
      <el-row :gutter="20" class="summary-cards">
        <el-col :span="6">
          <el-card class="summary-card" shadow="hover">
            <div class="summary-item">
              <div class="summary-label">总人数</div>
              <div class="summary-value">{{ summaryData.total_count || 0 }}</div>
              <div class="summary-unit">人</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="summary-card" shadow="hover">
            <div class="summary-item">
              <div class="summary-label">绩效工资总额</div>
              <div class="summary-value">{{ formatMoney(summaryData.total_performance_pay) }}</div>
              <div class="summary-unit">元</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="summary-card" shadow="hover">
            <div class="summary-item">
              <div class="summary-label">乡镇补贴总额</div>
              <div class="summary-value">{{ formatMoney(summaryData.total_town_subsidy) }}</div>
              <div class="summary-unit">元</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="summary-card" shadow="hover">
            <div class="summary-item">
              <div class="summary-label">合计金额</div>
              <div class="summary-value">{{ formatMoney(summaryData.total_amount) }}</div>
              <div class="summary-unit">元</div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 按岗位等级统计 -->
      <div class="table-section">
        <h3 class="section-title">按岗位等级统计</h3>
        <el-table :data="levelStatistics" border stripe style="width: 100%">
          <el-table-column prop="level_name" label="岗位等级" min-width="150" />
          <el-table-column prop="count" label="人数" width="100" align="center" />
          <el-table-column prop="performance_pay" label="绩效工资" width="150" align="right">
            <template #default="scope">
              {{ formatMoney(scope.row.performance_pay) }}
            </template>
          </el-table-column>
          <el-table-column prop="town_subsidy" label="乡镇补贴" width="150" align="right">
            <template #default="scope">
              {{ formatMoney(scope.row.town_subsidy) }}
            </template>
          </el-table-column>
          <el-table-column prop="total" label="合计" width="150" align="right">
            <template #default="scope">
              {{ formatMoney(scope.row.total) }}
            </template>
          </el-table-column>
          <el-table-column prop="percentage" label="占比" width="120" align="center">
            <template #default="scope">
              {{ scope.row.percentage }}%
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 按人员类别统计 -->
      <div class="table-section">
        <h3 class="section-title">按人员类别统计</h3>
        <el-table :data="categoryStatistics" border stripe style="width: 100%">
          <el-table-column prop="category" label="人员类别" min-width="150" />
          <el-table-column prop="count" label="人数" width="100" align="center" />
          <el-table-column prop="performance_pay" label="绩效工资" width="150" align="right">
            <template #default="scope">
              {{ formatMoney(scope.row.performance_pay) }}
            </template>
          </el-table-column>
          <el-table-column prop="town_subsidy" label="乡镇补贴" width="150" align="right">
            <template #default="scope">
              {{ formatMoney(scope.row.town_subsidy) }}
            </template>
          </el-table-column>
          <el-table-column prop="total" label="合计" width="150" align="right">
            <template #default="scope">
              {{ formatMoney(scope.row.total) }}
            </template>
          </el-table-column>
          <el-table-column prop="percentage" label="占比" width="120" align="center">
            <template #default="scope">
              {{ scope.row.percentage }}%
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 按乡镇统计 -->
      <div class="table-section">
        <h3 class="section-title">按乡镇统计</h3>
        <el-table :data="townStatistics" border stripe style="width: 100%">
          <el-table-column prop="town" label="乡镇" min-width="150" />
          <el-table-column prop="count" label="人数" width="100" align="center" />
          <el-table-column prop="performance_pay" label="绩效工资" width="150" align="right">
            <template #default="scope">
              {{ formatMoney(scope.row.performance_pay) }}
            </template>
          </el-table-column>
          <el-table-column prop="town_subsidy" label="乡镇补贴" width="150" align="right">
            <template #default="scope">
              {{ formatMoney(scope.row.town_subsidy) }}
            </template>
          </el-table-column>
          <el-table-column prop="total" label="合计" width="150" align="right">
            <template #default="scope">
              {{ formatMoney(scope.row.total) }}
            </template>
          </el-table-column>
          <el-table-column prop="percentage" label="占比" width="120" align="center">
            <template #default="scope">
              {{ scope.row.percentage }}%
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 人员变动统计 -->
      <div class="table-section">
        <h3 class="section-title">人员变动统计</h3>
        <el-table :data="changeStatistics" border stripe style="width: 100%">
          <el-table-column prop="change_type" label="变动类型" min-width="120" />
          <el-table-column prop="count" label="人数" width="100" align="center" />
          <el-table-column prop="cancel_performance_count" label="取消绩效人数" width="120" align="center" />
          <el-table-column prop="cancel_performance_amount" label="取消绩效金额" width="150" align="right">
            <template #default="scope">
              {{ formatMoney(scope.row.cancel_performance_amount) }}
            </template>
          </el-table-column>
          <el-table-column prop="description" label="说明" min-width="200" />
        </el-table>
      </div>

      <!-- 月度对比图表 -->
      <div class="chart-section">
        <h3 class="section-title">月度金额对比</h3>
        <div ref="chartRef" class="chart-container"></div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Download } from '@element-plus/icons-vue'

const selectedYear = ref(new Date().getFullYear().toString())
const selectedMonth = ref(new Date().getMonth() + 1)

// 汇总数据
const summaryData = ref({
  total_count: 0,
  total_performance_pay: 0,
  total_town_subsidy: 0,
  total_amount: 0
})

// 按岗位等级统计
const levelStatistics = ref([
  { level_name: '九级管理', count: 0, performance_pay: 0, town_subsidy: 0, total: 0, percentage: 0 },
  { level_name: '八级管理', count: 0, performance_pay: 0, town_subsidy: 0, total: 0, percentage: 0 },
  { level_name: '七级管理', count: 0, performance_pay: 0, town_subsidy: 0, total: 0, percentage: 0 },
  { level_name: '六级管理', count: 0, performance_pay: 0, town_subsidy: 0, total: 0, percentage: 0 },
  { level_name: '正高级教师', count: 0, performance_pay: 0, town_subsidy: 0, total: 0, percentage: 0 },
  { level_name: '高级教师', count: 0, performance_pay: 0, town_subsidy: 0, total: 0, percentage: 0 },
  { level_name: '一级教师', count: 0, performance_pay: 0, town_subsidy: 0, total: 0, percentage: 0 },
  { level_name: '二级教师', count: 0, performance_pay: 0, town_subsidy: 0, total: 0, percentage: 0 },
  { level_name: '三级教师', count: 0, performance_pay: 0, town_subsidy: 0, total: 0, percentage: 0 },
  { level_name: '高级工', count: 0, performance_pay: 0, town_subsidy: 0, total: 0, percentage: 0 },
  { level_name: '中级工', count: 0, performance_pay: 0, town_subsidy: 0, total: 0, percentage: 0 },
  { level_name: '初级工', count: 0, performance_pay: 0, town_subsidy: 0, total: 0, percentage: 0 }
])

// 按人员类别统计
const categoryStatistics = ref([
  { category: '专业技术人员', count: 0, performance_pay: 0, town_subsidy: 0, total: 0, percentage: 0 },
  { category: '管理人员', count: 0, performance_pay: 0, town_subsidy: 0, total: 0, percentage: 0 },
  { category: '工勤人员', count: 0, performance_pay: 0, town_subsidy: 0, total: 0, percentage: 0 },
  { category: '退休干部', count: 0, performance_pay: 0, town_subsidy: 0, total: 0, percentage: 0 },
  { category: '退休工人', count: 0, performance_pay: 0, town_subsidy: 0, total: 0, percentage: 0 },
  { category: '离休干部', count: 0, performance_pay: 0, town_subsidy: 0, total: 0, percentage: 0 }
])

// 按乡镇统计
const townStatistics = ref([
  { town: '县城', count: 0, performance_pay: 0, town_subsidy: 0, total: 0, percentage: 0 },
  { town: '城关镇', count: 0, performance_pay: 0, town_subsidy: 0, total: 0, percentage: 0 },
  { town: '东乡镇', count: 0, performance_pay: 0, town_subsidy: 0, total: 0, percentage: 0 },
  { town: '西乡镇', count: 0, performance_pay: 0, town_subsidy: 0, total: 0, percentage: 0 },
  { town: '南乡镇', count: 0, performance_pay: 0, town_subsidy: 0, total: 0, percentage: 0 },
  { town: '北乡镇', count: 0, performance_pay: 0, town_subsidy: 0, total: 0, percentage: 0 }
])

// 人员变动统计
const changeStatistics = ref([
  { change_type: '退休', count: 0, cancel_performance_count: 0, cancel_performance_amount: 0, description: '达到退休年龄办理退休手续' },
  { change_type: '调动', count: 0, cancel_performance_count: 0, cancel_performance_amount: 0, description: '调离本单位' },
  { change_type: '辞职', count: 0, cancel_performance_count: 0, cancel_performance_amount: 0, description: '主动辞职' },
  { change_type: '死亡', count: 0, cancel_performance_count: 0, cancel_performance_amount: 0, description: '因病或意外死亡' }
])

const chartRef = ref<HTMLElement | null>(null)

// 格式化金额
const formatMoney = (value: number) => {
  if (value === null || value === undefined) return '0.00'
  return value.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

// 加载统计数据
const loadStatistics = async () => {
  try {
    const response = await fetch(`/api/performance-pay/statistics?year=${selectedYear.value}&month=${selectedMonth.value}`)
    const result = await response.json()
    if (result.status === 'success') {
      const data = result.data
      // 更新汇总数据
      summaryData.value = data.summary || summaryData.value
      // 更新各维度统计数据
      if (data.level_statistics) levelStatistics.value = data.level_statistics
      if (data.category_statistics) categoryStatistics.value = data.category_statistics
      if (data.town_statistics) townStatistics.value = data.town_statistics
      if (data.change_statistics) changeStatistics.value = data.change_statistics
      ElMessage.success('统计数据加载成功')
    } else {
      ElMessage.error(result.message || '加载统计数据失败')
    }
  } catch (error) {
    console.error('加载统计数据失败:', error)
    ElMessage.error('加载统计数据失败')
  }
}

// 导出统计表
const exportStatistics = async () => {
  try {
    const response = await fetch(`/api/performance-pay/statistics/export?year=${selectedYear.value}&month=${selectedMonth.value}`)
    if (response.ok) {
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `绩效工资统计表_${selectedYear.value}年${selectedMonth.value}月.xlsx`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
      ElMessage.success('导出成功')
    } else {
      ElMessage.error('导出失败')
    }
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败')
  }
}

onMounted(() => {
  loadStatistics()
})
</script>

<style scoped>
.statistics-container {
  padding: 20px;
}

.statistics-card {
  min-height: calc(100vh - 100px);
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

.summary-cards {
  margin-bottom: 30px;
}

.summary-card {
  text-align: center;
}

.summary-item {
  padding: 20px;
}

.summary-label {
  font-size: 14px;
  color: #666;
  margin-bottom: 10px;
}

.summary-value {
  font-size: 32px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 5px;
}

.summary-unit {
  font-size: 14px;
  color: #999;
}

.table-section {
  margin-bottom: 30px;
}

.section-title {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 15px;
  padding-left: 10px;
  border-left: 4px solid #409eff;
}

.chart-section {
  margin-top: 30px;
}

.chart-container {
  width: 100%;
  height: 400px;
  background-color: #f5f5f5;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
}
</style>
