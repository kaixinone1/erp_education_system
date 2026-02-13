<template>
  <div class="dashboard-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>仪表盘</h2>
      <p>欢迎使用太平教育人事工资党建管理系统</p>
    </div>
    
    <!-- 快捷入口区域 -->
    <div class="quick-entry-section">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="stat-card" :body-style="{ padding: '0px' }">
            <div class="stat-card-content" style="background-color: #1890FF;">
              <div class="stat-info">
                <h3 class="stat-value">1,256</h3>
                <p class="stat-label">总人数</p>
              </div>
              <div class="stat-icon">
                <el-icon class="icon-large"><User /></el-icon>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card" :body-style="{ padding: '0px' }">
            <div class="stat-card-content" style="background-color: #52C41A;">
              <div class="stat-info">
                <h3 class="stat-value">23</h3>
                <p class="stat-label">待办工作</p>
              </div>
              <div class="stat-icon">
                <el-icon class="icon-large"><Document /></el-icon>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card" :body-style="{ padding: '0px' }">
            <div class="stat-card-content" style="background-color: #FA8C16;">
              <div class="stat-info">
                <h3 class="stat-value">8</h3>
                <p class="stat-label">合同到期</p>
              </div>
              <div class="stat-icon">
                <el-icon class="icon-large"><Document /></el-icon>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card" :body-style="{ padding: '0px' }">
            <div class="stat-card-content" style="background-color: #F5222D;">
              <div class="stat-info">
                <h3 class="stat-value">5</h3>
                <p class="stat-label">证件过期</p>
              </div>
              <div class="stat-icon">
                <el-icon class="icon-large"><Document /></el-icon>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card" :body-style="{ padding: '0px' }">
            <div class="stat-card-content" style="background-color: #722ED1;">
              <div class="stat-info">
                <h3 class="stat-value">18</h3>
                <p class="stat-label">部门数量</p>
              </div>
              <div class="stat-icon">
                <el-icon class="icon-large"><OfficeBuilding /></el-icon>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card" :body-style="{ padding: '0px' }">
            <div class="stat-card-content" style="background-color: #13C2C2;">
              <div class="stat-info">
                <h3 class="stat-value">85%</h3>
                <p class="stat-label">考核优秀率</p>
              </div>
              <div class="stat-icon">
                <el-icon class="icon-large"><Star /></el-icon>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card" :body-style="{ padding: '0px' }">
            <div class="stat-card-content" style="background-color: #FAAD14;">
              <div class="stat-info">
                <h3 class="stat-value">42</h3>
                <p class="stat-label">使用次数</p>
              </div>
              <div class="stat-icon">
                <el-icon class="icon-large"><View /></el-icon>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card" :body-style="{ padding: '0px' }">
            <div class="stat-card-content" style="background-color: #1890FF;">
              <div class="stat-info">
                <h3 class="stat-value">12</h3>
                <p class="stat-label">党建活动</p>
              </div>
              <div class="stat-icon">
                <el-icon class="icon-large"><Star /></el-icon>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
    
    <!-- 图表分析区域 -->
    <div class="chart-analysis-section">
      <el-row :gutter="20">
        <el-col :span="12">
          <el-card class="chart-card">
            <template #header>
              <div class="chart-header">
                <span>专技岗位分布</span>
              </div>
            </template>
            <div class="chart-container">
              <v-chart class="chart" :option="techPositionOption" />
            </div>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card class="chart-card">
            <template #header>
              <div class="chart-header">
                <span>职级分布</span>
              </div>
            </template>
            <div class="chart-container">
              <v-chart class="chart" :option="rankDistributionOption" />
            </div>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card class="chart-card">
            <template #header>
              <div class="chart-header">
                <span>性别比例</span>
              </div>
            </template>
            <div class="chart-container">
              <v-chart class="chart" :option="genderRatioOption" />
            </div>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card class="chart-card">
            <template #header>
              <div class="chart-header">
                <span>学历结构</span>
              </div>
            </template>
            <div class="chart-container">
              <v-chart class="chart" :option="educationStructureOption" />
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
    
    <!-- 信息流区域 -->
    <div class="info-flow-section">
      <el-card class="info-card">
        <el-tabs v-model="activeTab">
          <el-tab-pane label="待办工作" name="todo">
            <el-table :data="todoList" style="width: 100%">
              <el-table-column prop="title" label="任务名称" />
              <el-table-column prop="type" label="类型" />
              <el-table-column prop="time" label="截止时间" />
              <el-table-column label="操作">
                <template #default="scope">
                  <el-button type="primary" size="small">处理</el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-tab-pane>
          <el-tab-pane label="资讯信息" name="news">
            <el-menu :default-active="activeNewsTab" class="news-menu" mode="horizontal">
              <el-menu-item index="latest">最新</el-menu-item>
              <el-menu-item index="policy">政策法规</el-menu-item>
              <el-menu-item index="notice">通知公告</el-menu-item>
              <el-menu-item index="activity">活动信息</el-menu-item>
            </el-menu>
            <div class="news-list">
              <el-timeline>
                <el-timeline-item v-for="(item, index) in newsList" :key="index" :timestamp="item.time">
                  <el-card>
                    <h4>{{ item.title }}</h4>
                    <p>{{ item.content }}</p>
                  </el-card>
                </el-timeline-item>
              </el-timeline>
            </div>
          </el-tab-pane>
        </el-tabs>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { User, Document, Check, Star, OfficeBuilding, View } from '@element-plus/icons-vue'
import VChart from 'vue-echarts'
import * as echarts from 'echarts/core'
import { BarChart, PieChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  GridComponent,
  LegendComponent
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

// 注册必须的组件
echarts.use([
  TitleComponent,
  TooltipComponent,
  GridComponent,
  LegendComponent,
  BarChart,
  PieChart,
  CanvasRenderer
])

// 状态管理
const activeTab = ref('todo')
const activeNewsTab = ref('latest')

// 待办工作列表
const todoList = ref([
  {
    title: '教师职称评审',
    type: '审批',
    time: '2026-02-01'
  },
  {
    title: '部门预算审核',
    type: '审核',
    time: '2026-02-03'
  }
])

// 资讯信息列表
const newsList = ref([
  {
    title: '关于做好2026年教师招聘工作的通知',
    content: '根据上级部门要求，现将2026年教师招聘工作有关事项通知如下...',
    time: '2026-01-30'
  },
  {
    title: '2026年春季学期开学工作安排',
    content: '2026年春季学期将于2月20日正式开学，请各学校做好开学准备工作...',
    time: '2026-01-28'
  },
  {
    title: '关于加强师德师风建设的实施意见',
    content: '为进一步加强教师队伍建设，提高教师职业道德水平...',
    time: '2026-01-25'
  }
])

// 专技岗位分布图表配置
const techPositionOption = {
  title: {
    text: '专技岗位分布',
    left: 'center'
  },
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      type: 'shadow'
    }
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    containLabel: true
  },
  xAxis: {
    type: 'category',
    data: ['初级', '中级', '高级', '正高级', '特级']
  },
  yAxis: {
    type: 'value',
    name: '人数'
  },
  series: [
    {
      data: [300, 350, 250, 100, 50],
      type: 'bar',
      itemStyle: {
        color: '#1890FF'
      }
    }
  ]
}

// 职级分布图表配置
const rankDistributionOption = {
  title: {
    text: '职级分布',
    left: 'center'
  },
  tooltip: {
    trigger: 'item'
  },
  legend: {
    orient: 'vertical',
    left: 'left'
  },
  series: [
    {
      name: '职级',
      type: 'pie',
      radius: '60%',
      data: [
        { value: 400, name: '科员' },
        { value: 300, name: '副科级' },
        { value: 250, name: '正科级' },
        { value: 150, name: '处级' }
      ],
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowOffsetX: 0,
          shadowColor: 'rgba(0, 0, 0, 0.5)'
        }
      }
    }
  ]
}

// 性别比例图表配置
const genderRatioOption = {
  title: {
    text: '性别比例',
    left: 'center'
  },
  tooltip: {
    trigger: 'item'
  },
  legend: {
    orient: 'vertical',
    left: 'left'
  },
  series: [
    {
      name: '性别',
      type: 'pie',
      radius: '60%',
      data: [
        { value: 250, name: '男' },
        { value: 225, name: '女' }
      ],
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowOffsetX: 0,
          shadowColor: 'rgba(0, 0, 0, 0.5)'
        }
      }
    }
  ]
}

// 学历结构图表配置
const educationStructureOption = {
  title: {
    text: '学历结构',
    left: 'center'
  },
  tooltip: {
    trigger: 'item'
  },
  legend: {
    orient: 'vertical',
    left: 'left'
  },
  series: [
    {
      name: '学历',
      type: 'pie',
      radius: '60%',
      data: [
        { value: 50, name: '博士' },
        { value: 180, name: '硕士' },
        { value: 220, name: '本科' },
        { value: 25, name: '专科及以下' }
      ],
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowOffsetX: 0,
          shadowColor: 'rgba(0, 0, 0, 0.5)'
        }
      }
    }
  ]
}
</script>

<style scoped>
.dashboard-page {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100%;
}

.page-header {
  margin-bottom: 30px;
}

.page-header h2 {
  margin: 0;
  font-size: 24px;
  color: #1E40AF;
}

.page-header p {
  margin: 5px 0 0 0;
  color: #606266;
}

/* 快捷入口区域 */
.quick-entry-section {
  margin-bottom: 30px;
}

.stat-card {
  height: 140px;
}

.stat-card-content {
  height: 140px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  color: #ffffff;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  margin: 0;
}

.stat-label {
  font-size: 14px;
  margin: 5px 0 0 0;
  opacity: 0.9;
}

.stat-icon {
  margin-left: 20px;
}

.icon-large {
  font-size: 40px;
  opacity: 0.8;
}

/* 图表分析区域 */
.chart-analysis-section {
  margin-bottom: 30px;
}

.chart-card {
  height: 300px;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-container {
  height: 240px;
}

.chart {
  width: 100%;
  height: 100%;
}

/* 信息流区域 */
.info-flow-section {
  margin-bottom: 30px;
}

.info-card {
  min-height: 400px;
}

.news-menu {
  border-bottom: 1px solid #e6e8eb;
  margin-bottom: 20px;
}

.news-list {
  max-height: 300px;
  overflow-y: auto;
}

/* 响应式设计 */
@media screen and (max-width: 1200px) {
  .el-col {
    margin-bottom: 20px;
  }
  
  .el-col:nth-child(1),
  .el-col:nth-child(2),
  .el-col:nth-child(3),
  .el-col:nth-child(4) {
    flex: 1;
    max-width: calc(50% - 10px);
  }
}

@media screen and (max-width: 768px) {
  .el-col:nth-child(1),
  .el-col:nth-child(2),
  .el-col:nth-child(3),
  .el-col:nth-child(4) {
    flex: 1;
    max-width: 100%;
  }
  
  .chart-card {
    height: 250px;
  }
  
  .chart-container {
    height: 190px;
  }
}
</style>