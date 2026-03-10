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
            <div v-if="loading" class="loading-wrapper">
              <el-skeleton :rows="3" animated />
            </div>
            <div v-else-if="rawTodoList.length === 0" class="empty-wrapper">
              <el-empty description="暂无待办工作" :image-size="80" />
            </div>
            <el-table v-else :data="todoList" style="width: 100%" :row-class-name="rowClassName">
              <el-table-column prop="title" label="任务名称" min-width="250">
                <template #default="{ row }">
                  <span :class="{ 'gray-text': row.isGray }">{{ row.title }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="type" label="类型" width="120">
                <template #default="{ row }">
                  <el-tag :type="row.isGray ? 'info' : 'warning'">{{ row.type }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="status" label="状态" width="100">
                <template #default="{ row }">
                  <el-tag :type="row.isGray ? 'info' : (row.status === 'pending' ? 'danger' : 'success')">
                    {{ row.isGray ? '已完成' : (row.status === 'pending' ? '待处理' : '处理中') }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="time" label="时间" width="120">
                <template #default="{ row }">
                  <span :class="{ 'gray-text': row.isGray }">{{ row.time }}</span>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="100" fixed="right">
                <template #default="{ row }">
                  <el-button 
                    :type="row.isGray ? 'info' : 'primary'" 
                    size="small" 
                    @click="handleTodo(row)"
                    :disabled="row.isGray"
                  >
                    {{ row.isGray ? '已完成' : '处理' }}
                  </el-button>
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

    <!-- 清单详情抽屉 -->
    <ChecklistDrawer
      v-model="drawerVisible"
      :todo-data="selectedTodo"
      @close="drawerVisible = false"
      @status-changed="handleStatusChanged"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { User, Document, Check, Star, OfficeBuilding, View } from '@element-plus/icons-vue'
import VChart from 'vue-echarts'
import ChecklistDrawer from '../../components/ChecklistDrawer.vue'
import * as echarts from 'echarts/core'
import { BarChart, PieChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  GridComponent,
  LegendComponent
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { ElMessage } from 'element-plus'

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
const loading = ref(false)
const drawerVisible = ref(false)
const selectedTodo = ref<any>(null)

// 原始待办数据
const rawTodoList = ref<any[]>([])

// 计算属性：待办工作列表
// 1. 完成度100%的显示灰色字体
// 2. 已完成的排在未完成后面
// 3. 已完成的按完成日期排序
const todoList = computed(() => {
  console.log('rawTodoList:', rawTodoList.value)
  
  // 计算每个待办的完成度
  const todosWithProgress = rawTodoList.value.map(todo => {
    const progress = todo.total_tasks > 0 ? Math.round((todo.completed_tasks / todo.total_tasks) * 100) : 0
    return {
      ...todo,
      progress,
      isFullyCompleted: progress >= 100
    }
  })
  
  // 分离未完成和已完成的待办
  const pendingTodos = todosWithProgress.filter(todo => !todo.isFullyCompleted)
  const completedTodos = todosWithProgress.filter(todo => todo.isFullyCompleted)
  
  // 已完成的按完成日期排序（如果有completed_at字段，否则按created_at排序）
  completedTodos.sort((a, b) => {
    const dateA = new Date(a.completed_at || a.updated_at || a.created_at)
    const dateB = new Date(b.completed_at || b.updated_at || b.created_at)
    return dateB.getTime() - dateA.getTime() // 降序，最新的在前
  })
  
  // 映射未完成的待办
  const pendingMapped = pendingTodos.map(todo => ({
    id: todo.id,
    teacher_id: todo.teacher_id,
    teacher_name: todo.teacher_name,
    title: `新增${todo.teacher_name}退休业务清单（共${todo.total_tasks}项，已完成${todo.completed_tasks}项，${todo.progress}%）`,
    type: `${todo.teacher_name}退休呈报`,
    time: formatDate(todo.created_at),
    status: todo.status,
    isCompleted: false,
    isGray: false,
    progress: todo.progress
  }))
  
  // 映射已完成的待办（显示灰色）
  const completedMapped = completedTodos.map(todo => ({
    id: todo.id,
    teacher_id: todo.teacher_id,
    teacher_name: todo.teacher_name,
    title: `✓ ${todo.teacher_name}退休业务清单（共${todo.total_tasks}项，已完成${todo.completed_tasks}项，100%）`,
    type: `${todo.teacher_name}退休呈报 - 已完成`,
    time: formatDate(todo.completed_at || todo.updated_at || todo.created_at),
    status: todo.status,
    isCompleted: true,
    isGray: true,
    progress: 100
  }))
  
  // 合并：未完成的在前，已完成的在后
  const mapped = [...pendingMapped, ...completedMapped]
  console.log('mapped todoList:', mapped)
  return mapped
})

// 格式化日期
const formatDate = (dateStr: string): string => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  })
}

// 表格行样式类名
const rowClassName = ({ row }: { row: any }) => {
  return row.isGray ? 'completed-row' : ''
}

// 加载待办列表
const loadTodoList = async () => {
  loading.value = true
  try {
    console.log('开始加载待办列表...')
    const response = await fetch('/api/todo-work/list')
    console.log('待办列表API响应:', response.status)
    if (response.ok) {
      const result = await response.json()
      console.log('待办列表数据:', result)
      rawTodoList.value = result.data || []
      console.log('rawTodoList:', rawTodoList.value)
      console.log('todoList:', todoList.value)
    } else {
      console.error('API响应错误:', response.status, response.statusText)
      ElMessage.error(`加载待办列表失败: ${response.status}`)
    }
  } catch (error) {
    console.error('加载待办列表失败:', error)
    ElMessage.error('加载待办列表失败')
  } finally {
    loading.value = false
  }
}

// 处理待办工作 - 打开清单抽屉
const handleTodo = (row: any) => {
  console.log('处理待办:', row)
  // 从rawTodoList中找到完整的待办数据
  const originalTodo = rawTodoList.value.find(todo => todo.id === row.id)
  if (originalTodo) {
    // 直接传递完整的原始数据，与PushedChecklistView保持一致
    selectedTodo.value = originalTodo
    drawerVisible.value = true
  }
}

// 处理状态变更 - 只更新当前待办的数据，不刷新整个列表
const handleStatusChanged = (data: { todoId: number, completedCount: number, totalCount: number, status: string }) => {
  console.log('状态变更:', data)
  
  // 在 rawTodoList 中找到对应的待办并更新
  const todoIndex = rawTodoList.value.findIndex(todo => todo.id === data.todoId)
  if (todoIndex !== -1) {
    rawTodoList.value[todoIndex].completed_tasks = data.completedCount
    rawTodoList.value[todoIndex].status = data.status
    console.log('已更新待办数据:', rawTodoList.value[todoIndex])
  }
}

// 页面加载时获取数据
onMounted(() => {
  loadTodoList()
})

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

.loading-wrapper {
  padding: 20px;
}

.empty-wrapper {
  padding: 40px 0;
}

/* 已完成任务的灰色样式 */
.gray-text {
  color: #909399 !important;
}

:deep(.completed-row) {
  background-color: #f5f7fa !important;
}

:deep(.completed-row:hover) {
  background-color: #e4e7ed !important;
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