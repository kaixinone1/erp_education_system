<template>
  <div class="todo-business-container">
    <el-card class="page-header">
      <template #header>
        <div class="header-content">
          <div class="title-section">
            <el-icon class="title-icon"><List /></el-icon>
            <span class="title">待办业务管理</span>
          </div>
          <div class="stats-section">
            <el-statistic title="待处理" :value="stats.pending" class="stat-item" />
            <el-statistic title="进行中" :value="stats.in_progress" class="stat-item" />
            <el-statistic title="已完成" :value="stats.completed" class="stat-item" />
            <el-statistic title="已退回" :value="stats.returned" class="stat-item" />
          </div>
        </div>
      </template>

      <!-- 筛选栏 -->
      <div class="filter-bar">
        <el-input
          v-model="filterForm.keyword"
          placeholder="搜索待办标题/相关人员"
          clearable
          style="width: 250px"
          @keyup.enter="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>

        <el-select v-model="filterForm.status" placeholder="状态" clearable style="width: 120px">
          <el-option label="待处理" value="pending" />
          <el-option label="进行中" value="in_progress" />
          <el-option label="已完成" value="completed" />
          <el-option label="已退回" value="returned" />
        </el-select>

        <el-select v-model="filterForm.template_id" placeholder="业务类型" clearable style="width: 150px">
          <el-option
            v-for="template in templateOptions"
            :key="template.id"
            :label="template.name"
            :value="template.id"
          />
        </el-select>

        <el-date-picker
          v-model="filterForm.date_range"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          value-format="YYYY-MM-DD"
          style="width: 280px"
        />

        <el-button type="primary" @click="handleSearch">
          <el-icon><Search /></el-icon>
          查询
        </el-button>
        <el-button @click="handleReset">
          <el-icon><Refresh /></el-icon>
          重置
        </el-button>
      </div>
    </el-card>

    <!-- 数据表格 -->
    <el-card class="data-table-card">
      <template #header>
        <div class="table-header">
          <span>待办业务列表</span>
          <div class="table-actions">
            <el-button type="success" @click="handleCreateCustom">
              <el-icon><Plus /></el-icon>
              新建自定义待办
            </el-button>
            <el-button type="warning" @click="handleBatchReturn" :disabled="!selectedRows.length">
              <el-icon><RefreshLeft /></el-icon>
              批量退回
            </el-button>
          </div>
        </div>
      </template>

      <el-table
        :data="todoList"
        v-loading="loading"
        @selection-change="handleSelectionChange"
        stripe
        border
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="template_name" label="业务类型" width="150">
          <template #default="{ row }">
            <el-tag :type="getTypeTag(row.trigger_type)">
              {{ row.template_name }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="title" label="待办标题" min-width="200" show-overflow-tooltip />
        <el-table-column prop="teacher_name" label="相关人员" width="150">
          <template #default="{ row }">
            <div class="teacher-cell">
              <span>{{ row.teacher_name }}</span>
              <span class="teacher-id">({{ row.teacher_id }})</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="operator_name" label="负责人" width="120" />
        <el-table-column prop="deadline" label="截止日期" width="120">
          <template #default="{ row }">
            <span :class="{ 'deadline-warning': isDeadlineWarning(row.deadline) }">
              {{ formatDate(row.deadline) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTag(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button-group>
              <el-button size="small" @click="handleView(row)">查看</el-button>
              <el-button size="small" type="primary" @click="handleEdit(row)" v-if="row.status !== 'completed'">
                编辑
              </el-button>
              <el-button size="small" type="warning" @click="handleReturn(row)" v-if="row.status === 'completed'">
                退回
              </el-button>
            </el-button-group>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.page_size"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- 新建自定义待办对话框 -->
    <el-dialog
      v-model="customDialogVisible"
      title="新建自定义待办"
      width="600px"
    >
      <el-form :model="customForm" label-width="100px" :rules="customRules" ref="customFormRef">
        <el-form-item label="待办标题" prop="title">
          <el-input v-model="customForm.title" placeholder="请输入待办标题" />
        </el-form-item>
        <el-form-item label="详细描述" prop="description">
          <el-input
            v-model="customForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入详细描述"
          />
        </el-form-item>
        <el-form-item label="相关人员" prop="teacher_id">
          <el-select
            v-model="customForm.teacher_id"
            filterable
            remote
            :remote-method="searchTeachers"
            placeholder="搜索教师"
            style="width: 100%"
          >
            <el-option
              v-for="teacher in teacherOptions"
              :key="teacher.id"
              :label="teacher.name + ' (' + teacher.id + ')'"
              :value="teacher.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="负责人" prop="operator_id">
          <el-input v-model="customForm.operator_id" placeholder="请输入负责人ID" />
        </el-form-item>
        <el-form-item label="截止日期" prop="deadline">
          <el-date-picker
            v-model="customForm.deadline"
            type="date"
            placeholder="选择截止日期"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="customDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitCustomTodo" :loading="submitting">
          确定
        </el-button>
      </template>
    </el-dialog>

    <!-- 查看详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="待办详情"
      width="700px"
    >
      <el-descriptions :column="2" border v-if="currentTodo">
        <el-descriptions-item label="业务类型" :span="2">
          <el-tag :type="getTypeTag(currentTodo.trigger_type)">
            {{ currentTodo.template_name }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="待办标题" :span="2">
          {{ currentTodo.title }}
        </el-descriptions-item>
        <el-descriptions-item label="相关人员">
          {{ currentTodo.teacher_name }} ({{ currentTodo.teacher_id }})
        </el-descriptions-item>
        <el-descriptions-item label="负责人">
          {{ currentTodo.operator_name }}
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusTag(currentTodo.status)">
            {{ getStatusText(currentTodo.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="截止日期">
          {{ formatDate(currentTodo.deadline) }}
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">
          {{ formatDateTime(currentTodo.created_at) }}
        </el-descriptions-item>
        <el-descriptions-item label="完成时间" v-if="currentTodo.completed_at">
          {{ formatDateTime(currentTodo.completed_at) }}
        </el-descriptions-item>
        <el-descriptions-item label="详细描述" :span="2">
          {{ currentTodo.description || '无' }}
        </el-descriptions-item>
      </el-descriptions>

      <!-- 任务流程 -->
      <div class="task-flow-section" v-if="currentTodo?.task_flow?.length">
        <h4>任务流程</h4>
        <el-timeline>
          <el-timeline-item
            v-for="(task, index) in currentTodo.task_flow"
            :key="index"
            :type="getTaskStatusType(task.status)"
          >
            <div class="task-flow-item">
              <span class="task-name">{{ task.name }}</span>
              <el-tag size="small" :type="getTaskStatusType(task.status)">
                {{ getTaskStatusText(task.status) }}
              </el-tag>
              <span v-if="task.completed_at" class="task-time">
                {{ formatDateTime(task.completed_at) }}
              </span>
            </div>
          </el-timeline-item>
        </el-timeline>
      </div>
    </el-dialog>

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
      <el-form :model="returnForm" :rules="returnRules" ref="returnFormRef" label-width="100px">
        <el-form-item label="退回原因" prop="reason">
          <el-input
            v-model="returnForm.reason"
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

    <!-- 批量退回原因对话框 -->
    <el-dialog
      v-model="batchReturnDialogVisible"
      title="批量退回原因（必填）"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-alert
        title="批量退回操作"
        type="warning"
        :closable="false"
        style="margin-bottom: 20px"
      >
        <template #default>
          共选中 {{ selectedRows.length }} 项待办业务，其中 {{ selectedRows.filter(r => r.status === 'completed').length }} 项已完成
        </template>
      </el-alert>
      <el-form :model="batchReturnForm" :rules="batchReturnRules" ref="batchReturnFormRef" label-width="100px">
        <el-form-item label="退回原因" prop="reason">
          <el-input
            v-model="batchReturnForm.reason"
            type="textarea"
            :rows="4"
            placeholder="请详细说明批量退回原因"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="batchReturnDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitBatchReturn">确认批量退回</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import {
  List,
  Search,
  Refresh,
  Plus,
  RefreshLeft
} from '@element-plus/icons-vue'
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

// 筛选表单
const filterForm = reactive({
  keyword: '',
  status: '',
  template_id: null as number | null,
  date_range: [] as string[]
})

// 分页
const pagination = reactive({
  page: 1,
  page_size: 20,
  total: 0
})

// 统计数据
const stats = reactive({
  pending: 0,
  in_progress: 0,
  completed: 0,
  returned: 0
})

// 表格数据
const todoList = ref<any[]>([])
const loading = ref(false)
const selectedRows = ref<any[]>([])

// 模板选项
const templateOptions = ref<any[]>([])

// 自定义待办对话框
const customDialogVisible = ref(false)
const customFormRef = ref<FormInstance>()
const customForm = reactive({
  title: '',
  description: '',
  teacher_id: '',
  operator_id: '',
  deadline: ''
})
const customRules: FormRules = {
  title: [{ required: true, message: '请输入待办标题', trigger: 'blur' }],
  teacher_id: [{ required: true, message: '请选择相关人员', trigger: 'change' }],
  operator_id: [{ required: true, message: '请输入负责人', trigger: 'blur' }]
}
const submitting = ref(false)
const teacherOptions = ref<any[]>([])

// 详情对话框
const detailDialogVisible = ref(false)
const currentTodo = ref<any>(null)

// 获取类型标签
const getTypeTag = (type?: string) => {
  const map: Record<string, string> = {
    'retirement': 'warning',
    'death': 'danger',
    'octogenarian': 'success',
    'custom': 'info'
  }
  return map[type || ''] || 'info'
}

// 获取状态标签
const getStatusTag = (status?: string) => {
  const map: Record<string, string> = {
    'pending': 'info',
    'in_progress': 'primary',
    'completed': 'success',
    'returned': 'danger'
  }
  return map[status || ''] || 'info'
}

// 获取状态文本
const getStatusText = (status?: string) => {
  const map: Record<string, string> = {
    'pending': '待处理',
    'in_progress': '进行中',
    'completed': '已完成',
    'returned': '已退回'
  }
  return map[status || ''] || status
}

// 获取任务状态标签
const getTaskStatusType = (status?: string) => {
  const map: Record<string, string> = {
    'pending': 'info',
    'in_progress': 'primary',
    'completed': 'success'
  }
  return map[status || ''] || 'info'
}

// 获取任务状态文本
const getTaskStatusText = (status?: string) => {
  const map: Record<string, string> = {
    'pending': '待处理',
    'in_progress': '进行中',
    'completed': '已完成'
  }
  return map[status || ''] || status
}

// 格式化日期
const formatDate = (dateStr?: string) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN')
}

// 格式化日期时间
const formatDateTime = (dateStr?: string) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

// 检查截止日期是否临近
const isDeadlineWarning = (deadline?: string) => {
  if (!deadline) return false
  const deadlineDate = new Date(deadline)
  const today = new Date()
  const diffDays = Math.ceil((deadlineDate.getTime() - today.getTime()) / (1000 * 60 * 60 * 24))
  return diffDays <= 7 && diffDays >= 0
}

// 加载待办列表
const loadTodoList = async () => {
  loading.value = true
  try {
    const params: any = {
      page: pagination.page,
      page_size: pagination.page_size,
      ...filterForm
    }
    if (filterForm.date_range?.length === 2) {
      params.start_date = filterForm.date_range[0]
      params.end_date = filterForm.date_range[1]
    }

    const response = await axios.get(`${API_BASE_URL}/api/todo-system/todo-list`, { params })
    todoList.value = response.data.todos || []
    pagination.total = response.data.total || 0
  } catch (error) {
    console.error('加载待办列表失败:', error)
    ElMessage.error('加载待办列表失败')
  } finally {
    loading.value = false
  }
}

// 加载统计数据
const loadStats = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/todo-system/stats`)
    Object.assign(stats, response.data)
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

// 加载模板选项
const loadTemplates = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/todo-system/templates`)
    templateOptions.value = response.data.templates || []
  } catch (error) {
    console.error('加载模板失败:', error)
  }
}

// 搜索教师
const searchTeachers = async (query: string) => {
  if (query.length < 2) return
  try {
    const response = await axios.get(`${API_BASE_URL}/api/data/teacher_basic_info`, {
      params: { search: query, page_size: 20 }
    })
    teacherOptions.value = (response.data.data || []).map((t: any) => ({
      id: t.职工编号 || t.id,
      name: t.姓名 || t.name
    }))
  } catch (error) {
    console.error('搜索教师失败:', error)
  }
}

// 处理搜索
const handleSearch = () => {
  pagination.page = 1
  loadTodoList()
}

// 处理重置
const handleReset = () => {
  filterForm.keyword = ''
  filterForm.status = ''
  filterForm.template_id = null
  filterForm.date_range = []
  handleSearch()
}

// 处理分页大小变化
const handleSizeChange = (size: number) => {
  pagination.page_size = size
  loadTodoList()
}

// 处理页码变化
const handlePageChange = (page: number) => {
  pagination.page = page
  loadTodoList()
}

// 处理选择变化
const handleSelectionChange = (selection: any[]) => {
  selectedRows.value = selection
}

// 处理查看
const handleView = (row: any) => {
  currentTodo.value = row
  detailDialogVisible.value = true
}

// 处理编辑
const handleEdit = (row: any) => {
  ElMessage.info('编辑功能开发中...')
}

// 退回原因对话框
const returnDialogVisible = ref(false)
const returnForm = reactive({
  todo_id: null as number | null,
  reason: ''
})
const returnFormRef = ref<FormInstance>()
const returnRules: FormRules = {
  reason: [{ required: true, message: '请输入退回原因', trigger: 'blur' }]
}

// 处理退回
const handleReturn = async (row: any) => {
  // 先显示警告确认
  try {
    await ElMessageBox.confirm(
      `<div style="color: #F56C6C; font-weight: bold; margin-bottom: 10px;">⚠️ 警告：该待办已完成</div>
       <div>退回后，该待办将重新变为"待处理"状态，需要重新办理。</div>
       <div style="margin-top: 10px; color: #909399;">请确认是否需要退回？</div>`,
      '确认退回已完成待办',
      {
        type: 'warning',
        dangerouslyUseHTMLString: true,
        confirmButtonText: '确认退回',
        cancelButtonText: '取消'
      }
    )

    // 显示退回原因输入对话框
    returnForm.todo_id = row.id
    returnForm.reason = ''
    returnDialogVisible.value = true

  } catch (error) {
    // 用户取消
  }
}

// 提交退回
const submitReturn = async () => {
  if (!returnFormRef.value) return

  await returnFormRef.value.validate(async (valid) => {
    if (!valid) return

    try {
      await axios.post(`${API_BASE_URL}/api/todo-system/return-todo`, {
        todo_id: returnForm.todo_id,
        reason: returnForm.reason
      })
      ElMessage.success('已退回')
      returnDialogVisible.value = false
      loadTodoList()
      loadStats()
    } catch (error) {
      console.error('退回失败:', error)
      ElMessage.error('退回失败')
    }
  })
}

// 批量退回对话框
const batchReturnDialogVisible = ref(false)
const batchReturnForm = reactive({
  reason: ''
})
const batchReturnFormRef = ref<FormInstance>()
const batchReturnRules: FormRules = {
  reason: [{ required: true, message: '请输入批量退回原因', trigger: 'blur' }]
}

// 处理批量退回
const handleBatchReturn = async () => {
  if (!selectedRows.value.length) return

  // 检查是否选中了已完成的待办
  const completedCount = selectedRows.value.filter(row => row.status === 'completed').length

  try {
    let confirmMessage = `确定要退回选中的 ${selectedRows.value.length} 项待办业务吗？`
    if (completedCount > 0) {
      confirmMessage = `<div style="color: #F56C6C; font-weight: bold; margin-bottom: 10px;">⚠️ 警告：选中了 ${completedCount} 项已完成待办</div>
                        <div>其中 ${completedCount} 项已完成，退回后需要重新办理。</div>
                        <div style="margin-top: 10px;">共选中 ${selectedRows.value.length} 项待办业务</div>`
    }

    await ElMessageBox.confirm(
      confirmMessage,
      '确认批量退回',
      {
        type: 'warning',
        dangerouslyUseHTMLString: completedCount > 0,
        confirmButtonText: '确认退回',
        cancelButtonText: '取消'
      }
    )

    // 显示批量退回原因输入对话框
    batchReturnForm.reason = ''
    batchReturnDialogVisible.value = true

  } catch (error) {
    // 用户取消
  }
}

// 提交批量退回
const submitBatchReturn = async () => {
  if (!batchReturnFormRef.value) return

  await batchReturnFormRef.value.validate(async (valid) => {
    if (!valid) return

    try {
      // 批量退回逻辑
      for (const row of selectedRows.value) {
        await axios.post(`${API_BASE_URL}/api/todo-system/return-todo`, {
          todo_id: row.id,
          reason: batchReturnForm.reason
        })
      }
      ElMessage.success('批量退回成功')
      batchReturnDialogVisible.value = false
      loadTodoList()
      loadStats()
    } catch (error) {
      console.error('批量退回失败:', error)
      ElMessage.error('批量退回失败')
    }
  })
}

// 处理新建自定义待办
const handleCreateCustom = () => {
  customForm.title = ''
  customForm.description = ''
  customForm.teacher_id = ''
  customForm.operator_id = ''
  customForm.deadline = ''
  customDialogVisible.value = true
}

// 提交自定义待办
const submitCustomTodo = async () => {
  if (!customFormRef.value) return

  await customFormRef.value.validate(async (valid) => {
    if (!valid) return

    submitting.value = true
    try {
      await axios.post(`${API_BASE_URL}/api/todo-system/custom-todo`, customForm)
      ElMessage.success('创建成功')
      customDialogVisible.value = false
      loadTodoList()
      loadStats()
    } catch (error) {
      console.error('创建自定义待办失败:', error)
      ElMessage.error('创建失败')
    } finally {
      submitting.value = false
    }
  })
}

onMounted(() => {
  loadTodoList()
  loadStats()
  loadTemplates()
})
</script>

<style scoped>
.todo-business-container {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title-section {
  display: flex;
  align-items: center;
  gap: 10px;
}

.title-icon {
  font-size: 24px;
  color: #409EFF;
}

.title {
  font-size: 20px;
  font-weight: bold;
}

.stats-section {
  display: flex;
  gap: 40px;
}

.stat-item :deep(.el-statistic__content) {
  font-size: 24px;
  font-weight: bold;
  color: #409EFF;
}

.filter-bar {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
  align-items: center;
}

.data-table-card {
  margin-top: 20px;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.table-actions {
  display: flex;
  gap: 10px;
}

.teacher-cell {
  display: flex;
  flex-direction: column;
}

.teacher-id {
  font-size: 12px;
  color: #909399;
}

.deadline-warning {
  color: #F56C6C;
  font-weight: bold;
}

.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.task-flow-section {
  margin-top: 20px;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.task-flow-section h4 {
  margin: 0 0 15px 0;
  color: #303133;
}

.task-flow-item {
  display: flex;
  align-items: center;
  gap: 15px;
}

.task-name {
  font-weight: bold;
}

.task-time {
  color: #909399;
  font-size: 12px;
}
</style>
