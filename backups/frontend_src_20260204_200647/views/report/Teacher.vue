<template>
  <div class="teacher-report-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <el-icon><DataAnalysis /></el-icon>
          <span>教师报表</span>
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
          <el-form-item label="部门">
            <el-select placeholder="请选择部门">
              <el-option label="全部" value="all" />
              <el-option label="教育局" value="education" />
              <el-option label="第一中学" value="school1" />
              <el-option label="第二中学" value="school2" />
            </el-select>
          </el-form-item>
          <el-form-item label="职称">
            <el-select placeholder="请选择职称">
              <el-option label="全部" value="all" />
              <el-option label="教授" value="professor" />
              <el-option label="副教授" value="associate" />
              <el-option label="讲师" value="lecturer" />
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
            <h3 class="chart-title">教师职称分布</h3>
            <el-card class="chart-card">
              <div class="chart-container" style="height: 400px;">
                <!-- 这里将集成ECharts -->
                <div class="placeholder-chart">
                  <el-icon class="chart-icon"><PieChart /></el-icon>
                  <p>教师职称分布图表</p>
                </div>
              </div>
            </el-card>
          </div>
          
          <div class="chart-section">
            <h3 class="chart-title">教师年龄分布</h3>
            <el-card class="chart-card">
              <div class="chart-container" style="height: 400px;">
                <!-- 这里将集成ECharts -->
                <div class="placeholder-chart">
                  <el-icon class="chart-icon"><Histogram /></el-icon>
                  <p>教师年龄分布图表</p>
                </div>
              </div>
            </el-card>
          </div>
          
          <div class="data-table-section">
            <h3 class="table-title">教师详细数据</h3>
            <el-card class="table-card">
              <el-table :data="teacherData" style="width: 100%">
                <el-table-column prop="department" label="部门" width="150" />
                <el-table-column prop="total" label="总人数" width="100" />
                <el-table-column prop="professor" label="教授" width="80" />
                <el-table-column prop="associate" label="副教授" width="100" />
                <el-table-column prop="lecturer" label="讲师" width="80" />
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
import { DataAnalysis, Refresh, Download, Document, Printer, PieChart, Histogram } from '@element-plus/icons-vue'

const teacherData = ref([
  {
    department: '教育局',
    total: 15,
    professor: 2,
    associate: 5,
    lecturer: 8,
    averageAge: 42
  },
  {
    department: '第一中学',
    total: 80,
    professor: 10,
    associate: 30,
    lecturer: 40,
    averageAge: 38
  },
  {
    department: '第二中学',
    total: 65,
    professor: 8,
    associate: 25,
    lecturer: 32,
    averageAge: 40
  }
])
</script>

<style scoped>
.teacher-report-page {
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