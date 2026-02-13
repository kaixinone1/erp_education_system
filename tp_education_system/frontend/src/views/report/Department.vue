<template>
  <div class="department-report-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <el-icon><PieChart /></el-icon>
          <span>部门报表</span>
        </div>
      </template>
      <div class="card-content">
        <el-form :inline="true" class="filter-form">
          <el-form-item label="年份">
            <el-select placeholder="请选择年份">
              <el-option label="2026" value="2026" />
              <el-option label="2025" value="2025" />
              <el-option label="2024" value="2024" />
            </el-select>
          </el-form-item>
          <el-form-item label="部门类型">
            <el-select placeholder="请选择部门类型">
              <el-option label="全部" value="all" />
              <el-option label="教育局" value="bureau" />
              <el-option label="学校" value="school" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary">
              <el-icon><Refresh /></el-icon>
              刷新数据
            </el-button>
          </el-form-item>
        </el-form>
        
        <el-divider />
        
        <div class="report-content">
          <div class="chart-section">
            <h3 class="chart-title">部门人员分布</h3>
            <el-card class="chart-card">
              <div class="chart-container" style="height: 400px;">
                <!-- 这里将集成ECharts -->
                <div class="placeholder-chart">
                  <el-icon class="chart-icon"><PieChart /></el-icon>
                  <p>部门人员分布图表</p>
                </div>
              </div>
            </el-card>
          </div>
          
          <div class="chart-section">
            <h3 class="chart-title">部门职位分布</h3>
            <el-card class="chart-card">
              <div class="chart-container" style="height: 400px;">
                <!-- 这里将集成ECharts -->
                <div class="placeholder-chart">
                  <el-icon class="chart-icon"><Histogram /></el-icon>
                  <p>部门职位分布图表</p>
                </div>
              </div>
            </el-card>
          </div>
          
          <div class="data-table-section">
            <h3 class="table-title">部门详细数据</h3>
            <el-card class="table-card">
              <el-table :data="departmentData" style="width: 100%">
                <el-table-column prop="name" label="部门名称" width="150" />
                <el-table-column prop="type" label="部门类型" width="100" />
                <el-table-column prop="totalStaff" label="总人数" width="100" />
                <el-table-column prop="leaders" label="领导人数" width="100" />
                <el-table-column prop="staff" label="普通职工数" width="100" />
                <el-table-column prop="averageAge" label="平均年龄" width="100" />
              </el-table>
            </el-card>
          </div>
          
          <div class="export-section">
            <el-button type="success" class="export-excel">
              <el-icon><Download /></el-icon>
              导出Excel
            </el-button>
            <el-button type="warning" class="export-pdf">
              <el-icon><Document /></el-icon>
              导出PDF
            </el-button>
            <el-button type="info" class="print-report">
              <el-icon><Printer /></el-icon>
              打印报表
            </el-button>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { PieChart, Refresh, Download, Document, Printer, Histogram } from '@element-plus/icons-vue'

const departmentData = ref([
  {
    name: '教育局',
    type: '教育局',
    totalStaff: 15,
    leaders: 3,
    staff: 12,
    averageAge: 42
  },
  {
    name: '第一中学',
    type: '学校',
    totalStaff: 80,
    leaders: 5,
    staff: 75,
    averageAge: 38
  },
  {
    name: '第二中学',
    type: '学校',
    totalStaff: 65,
    leaders: 4,
    staff: 61,
    averageAge: 40
  }
])
</script>

<style scoped>
.department-report-page {
  padding: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: bold;
}

.card-content {
  padding-top: 20px;
}

.filter-form {
  margin-bottom: 20px;
}

.report-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.chart-section {
  margin-bottom: 20px;
}

.chart-title,
.table-title {
  font-size: 14px;
  font-weight: bold;
  margin-bottom: 10px;
  color: #303133;
}

.chart-card {
  margin-bottom: 15px;
}

.chart-container {
  position: relative;
}

.placeholder-chart {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.chart-icon {
  font-size: 48px;
  color: #409eff;
  margin-bottom: 10px;
}

.data-table-section {
  margin-bottom: 20px;
}

.table-card {
  margin-bottom: 15px;
}

.export-section {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}

.export-excel,
.export-pdf,
.print-report {
  margin-right: 10px;
}
</style>