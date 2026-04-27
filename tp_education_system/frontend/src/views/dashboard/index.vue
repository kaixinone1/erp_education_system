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
            <!-- 使用统一的TodoList组件 -->
            <TodoList 
              ref="todoListRef"
              :showTabs="false" 
              :showCompleted="true"
              @action="handleTodoAction"
            />
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

    <!-- 退回原因对话框 -->
    <el-dialog
      v-model="returnDialogVisible"
      title="退回原因（必填）"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-alert
        title="该待办已完成，退回后需要重新办理"
        type="warning"
        :closable="false"
        style="margin-bottom: 20px"
      />
      <el-form label-width="100px">
        <el-form-item label="退回原因" required>
          <el-input
            v-model="returnReason"
            type="textarea"
            :rows="4"
            placeholder="请详细说明退回原因，以便后续处理"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="returnDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitReturn">确认退回</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { User, Document, Check, Star, OfficeBuilding, View } from '@element-plus/icons-vue'
import VChart from 'vue-echarts'
import ChecklistDrawer from '../../components/ChecklistDrawer.vue'
import TodoList from '../../components/TodoList.vue'
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
const todoListRef = ref<any>(null)

// 原始待办数据
const rawTodoList = ref<any[]>([])

// 计算属性：待办工作列表
const todoList = computed(() => {
  console.log('rawTodoList:', rawTodoList.value)
  
  // 计算每个待办的完成度
  const todosWithProgress = rawTodoList.value.map(todo => {
    const progress = todo.total_tasks > 0 ? Math.round((todo.completed_tasks / todo.total_tasks) * 100) : 0
    // 严格根据状态判断是否已完成（与Header.vue和TodoWork.vue保持一致）
    const isFullyCompleted = todo.status === 'completed'
    return {
      ...todo,
      progress,
      isFullyCompleted
    }
  })
  
  // 分离未完成和已完成的待办（根据状态判断）
  const pendingTodos = todosWithProgress.filter(todo => todo.status !== 'completed')
  const completedTodos = todosWithProgress.filter(todo => todo.status === 'completed')
  
  // 已完成的按完成日期排序
  completedTodos.sort((a, b) => {
    const dateA = new Date(a.completed_at || a.updated_at || a.created_at)
    const dateB = new Date(b.completed_at || b.updated_at || b.created_at)
    return dateB.getTime() - dateA.getTime()
  })
  
  // 映射未完成的待办
  const pendingMapped = pendingTodos.map(todo => {
    const checklistName = todo.checklist_name || '待办任务'
    const teacherName = todo.teacher_name || '未知'
    const baseTitle = todo.title || `${teacherName} - ${checklistName}`
    return {
      id: todo.id,
      teacher_id: todo.teacher_id,
      teacher_name: teacherName,
      title: `${baseTitle}（共${todo.total_tasks}项，已完成${todo.completed_tasks}项，${todo.progress}%）`,
      type: checklistName,
      time: formatDate(todo.created_at),
      status: todo.status,
      isCompleted: false,
      isGray: false,
      progress: todo.progress,
      checklist_id: todo.checklist_id,
      checklist_name: checklistName
    }
  })
  
  // 映射已完成的待办
  const completedMapped = completedTodos.map(todo => {
    const checklistName = todo.checklist_name || '待办任务'
    const teacherName = todo.teacher_name || '未知'
    const baseTitle = todo.title || `${teacherName} - ${checklistName}`
    return {
      id: todo.id,
      teacher_id: todo.teacher_id,
      teacher_name: teacherName,
      title: `✓ ${baseTitle}（共${todo.total_tasks}项，已完成${todo.completed_tasks}项，100%）`,
      type: `${checklistName} - 已完成`,
      time: formatDate(todo.completed_at || todo.updated_at || todo.created_at),
      status: todo.status,
      isCompleted: true,
      isGray: true,
      progress: 100,
      checklist_id: todo.checklist_id,
      checklist_name: checklistName
    }
  })
  
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
    const response = await fetch('/api/todo-system/todo-list')
    console.log('待办列表API响应:', response.status)
    if (response.ok) {
      const result = await response.json()
      console.log('待办列表数据:', result)
      // 转换数据格式以兼容现有代码
      rawTodoList.value = (result.data || []).map((todo: any) => ({
        id: todo.id,
        teacher_id: todo.teacher_id,
        teacher_name: todo.teacher_name,
        title: todo.title,
        task_items: todo.task_items,
        checklist_id: todo.template_id,
        checklist_name: todo.business_type_display || todo.template_name || '待办任务',
        status: todo.status,
        total_tasks: todo.total_tasks || 0,
        completed_tasks: todo.completed_tasks || 0,
        created_at: todo.created_at,
        completed_at: todo.completed_at,
        updated_at: todo.created_at
      }))
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

// 退回对话框
const returnDialogVisible = ref(false)
const returnReason = ref('')
const currentReturnTodo = ref<any>(null)

// 处理待办工作（来自TodoList组件的action事件）
const handleTodoAction = (row: any) => {
  console.log('处理待办:', row)
  if (row.isCompleted) {
    // 已完成，显示退回对话框
    currentReturnTodo.value = row
    returnReason.value = ''
    returnDialogVisible.value = true
  } else {
    // 未完成，打开处理抽屉
    selectedTodo.value = row.rawData
    drawerVisible.value = true
  }
}

// 提交退回
const submitReturn = async () => {
  if (!returnReason.value.trim()) {
    ElMessage.warning('请输入退回原因')
    return
  }
  
  try {
    const response = await fetch(`/api/todo-system/todo/${currentReturnTodo.value.id}/return`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ reason: returnReason.value })
    })
    
    if (response.ok) {
      ElMessage.success('已退回')
      returnDialogVisible.value = false
      // 刷新TodoList组件
      todoListRef.value?.refresh()
    } else {
      ElMessage.error('退回失败')
    }
  } catch (error) {
    console.error('退回失败:', error)
    ElMessage.error('退回失败')
  }
}

// 处理状态变更
const handleStatusChanged = (data: { todoId: number, completedCount: number, totalCount: number, status: string }) => {
  console.log('状态变更:', data)
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

// 图表配置
const techPositionOption = {
  title: { text: '专技岗位分布', left: 'center' },
  tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
  grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
  xAxis: { type: 'category', data: ['初级', '中级', '高级', '正高级', '特级'] },
  yAxis: { type: 'value', name: '人数' },
  series: [{ data: [300, 350, 250, 100, 50], type: 'bar', itemStyle: { color: '#1890FF' } }]
}

const rankDistributionOption = {
  title: { text: '职级分布', left: 'center' },
  tooltip: { trigger: 'item' },
  legend: { orient: 'vertical', left: 'left' },
  series: [{
    name: '职级',
    type: 'pie',
    radius: '60%',
    data: [
      { value: 400, name: '科员' },
      { value: 300, name: '副科级' },
      { value: 250, name: '正科级' },
      { value: 150, name: '处级' }
    ],
    emphasis: { itemStyle: { shadowBlur: 10, shadowOffsetX: 0, shadowColor: 'rgba(0, 0, 0, 0.5)' } }
  }]
}

const genderRatioOption = {
  title: { text: '性别比例', left: 'center' },
  tooltip: { trigger: 'item' },
  legend: { orient: 'vertical', left: 'left' },
  series: [{
    name: '性别',
    type: 'pie',
    radius: '60%',
    data: [{ value: 250, name: '男' }, { value: 225, name: '女' }],
    emphasis: { itemStyle: { shadowBlur: 10, shadowOffsetX: 0, shadowColor: 'rgba(0, 0, 0, 0.5)' } }
  }]
}

const educationStructureOption = {
  title: { text: '学历结构', left: 'center' },
  tooltip: { trigger: 'item' },
  legend: { orient: 'vertical', left: 'left' },
  series: [{
    name: '学历',
    type: 'pie',
    radius: '60%',
    data: [
      { value: 50, name: '博士' },
      { value: 180, name: '硕士' },
      { value: 220, name: '本科' },
      { value: 25, name: '专科及以下' }
    ],
    emphasis: { itemStyle: { shadowBlur: 10, shadowOffsetX: 0, shadowColor: 'rgba(0, 0, 0, 0.5)' } }
  }]
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

.gray-text {
  color: #909399 !important;
}

:deep(.completed-row) {
  background-color: #f5f7fa !important;
}

:deep(.completed-row:hover) {
  background-color: #e4e7ed !important;
}

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
