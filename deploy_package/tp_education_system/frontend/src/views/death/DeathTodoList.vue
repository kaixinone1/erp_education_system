<template>
  <div class="death-todo-list">
    <el-card class="page-card">
      <template #header>
        <div class="card-header">
          <span class="title">教师去世后待办工作业务清单</span>
          <div class="header-actions">
            <el-input
              v-model="searchKeyword"
              placeholder="搜索教师姓名"
              style="width: 200px; margin-right: 10px;"
              clearable
              @clear="handleSearch"
              @keyup.enter="handleSearch"
            >
              <template #append>
                <el-button @click="handleSearch">
                  <el-icon><Search /></el-icon>
                </el-button>
              </template>
            </el-input>
            <el-select
              v-model="filterStatus"
              placeholder="状态筛选"
              style="width: 120px; margin-right: 10px;"
              clearable
              @change="handleSearch"
            >
              <el-option label="全部" value="" />
              <el-option label="待处理" value="待处理" />
              <el-option label="已完成" value="已完成" />
            </el-select>
          </div>
        </div>
      </template>

      <el-table
        v-loading="loading"
        :data="tableData"
        border
        style="width: 100%"
        :row-class-name="tableRowClassName"
      >
        <el-table-column type="index" label="序号" width="60" align="center" />
        <el-table-column prop="教师姓名" label="教师姓名" width="100" />
        <el-table-column prop="身份证号码" label="身份证号码" width="180" />
        <el-table-column prop="死亡日期" label="死亡日期" width="120" />
        <el-table-column prop="状态" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.状态 === '已完成' ? 'success' : 'warning'">
              {{ row.状态 }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="完成进度" width="280" align="center">
          <template #default="{ row }">
            <div class="progress-wrapper">
              <el-progress
                :percentage="row.完成进度"
                :status="row.完成进度 === 100 ? 'success' : ''"
                :stroke-width="16"
              />
              <span class="progress-text">（共{{ row.总任务数 }}项，已完成{{ row.已完成任务数 }}项，{{ row.完成进度 }}%）</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="创建时间" label="创建时间" width="150" />
        <el-table-column prop="完成时间" label="完成时间" width="150" />
        <el-table-column prop="备注" label="备注" min-width="150" show-overflow-tooltip />
        <el-table-column label="操作" width="200" fixed="right" align="center">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleProcess(row)">
              {{ row.状态 === '已完成' ? '查看' : '处理' }}
            </el-button>
            <el-button
              v-if="row.状态 === '已完成'"
              type="warning"
              size="small"
              @click="handleRevert(row)"
            >
              退回
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 处理/查看对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="currentRow ? `${currentRow.教师姓名}教师去世后待办工作` : '教师去世后待办工作'"
      width="700px"
      :close-on-click-modal="false"
    >
      <div v-if="currentRow" class="todo-detail">
        <el-descriptions :column="2" border class="mb-4">
          <el-descriptions-item label="教师姓名">{{ currentRow.教师姓名 }}</el-descriptions-item>
          <el-descriptions-item label="身份证号码">{{ currentRow.身份证号码 }}</el-descriptions-item>
          <el-descriptions-item label="死亡日期">
            <el-date-picker
              v-if="currentRow.状态 !== '已完成'"
              v-model="currentRow.死亡日期"
              type="date"
              placeholder="选择死亡日期"
              format="YYYY年M月D日"
              value-format="YYYY-MM-DD"
              style="width: 100%"
              @change="handleDeathDateChange"
            />
            <span v-else>{{ currentRow.死亡日期 || '-' }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="当前状态">
            <el-tag :type="currentRow.状态 === '已完成' ? 'success' : 'warning'">
              {{ currentRow.状态 }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>

        <div class="task-list">
          <h4 class="task-title">待办任务清单（共{{ taskList.length }}项，已完成{{ currentRow?.已完成任务数 || 0 }}项，{{ currentRow?.完成进度 || 0 }}%）</h4>
          <el-checkbox-group v-model="checkedTasks" class="task-checkbox-group">
            <div
              v-for="(task, index) in taskList"
              :key="index"
              class="task-item"
              :class="{ 'is-completed': task.completed }"
            >
              <el-checkbox
                :label="task.field"
                :disabled="currentRow.状态 === '已完成'"
                @change="(val) => handleTaskChange(index, val)"
              >
                <span class="task-number">{{ index + 1 }}.</span>
                <span class="task-name">{{ task.name }}</span>
              </el-checkbox>
            </div>
          </el-checkbox-group>
        </div>

        <div class="progress-summary">
          <div class="progress-header">
            <span class="progress-title">完成进度</span>
            <span class="progress-count">（共{{ taskList.length }}项，已完成{{ currentRow?.已完成任务数 || 0 }}项，{{ currentRow?.完成进度 || 0 }}%）</span>
          </div>
          <el-progress
            :percentage="currentRow?.完成进度 || 0"
            :status="currentRow?.完成进度 === 100 ? 'success' : ''"
            :stroke-width="20"
            :text-inside="true"
          />
        </div>
      </div>

      <template #footer>
        <el-button @click="dialogVisible = false">关闭</el-button>
        <el-button
          v-if="currentRow && currentRow.状态 !== '已完成'"
          type="primary"
          :loading="submitting"
          @click="handleSubmit"
        >
          保存进度
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search } from '@element-plus/icons-vue'

// 表格数据
const loading = ref(false)
const tableData = ref([])
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const searchKeyword = ref('')
const filterStatus = ref('')

// 对话框
const dialogVisible = ref(false)
const dialogTitle = ref('')
const submitting = ref(false)
const currentRow = ref<any>(null)
const checkedTasks = ref<string[]>([])

// 任务列表定义
const taskDefinitions = [
  { field: '任务1_收集死亡证明', name: '收集死亡医学证明、火化证' },
  { field: '任务2_打印终保承诺书', name: '登录养老系统打印终保承诺书' },
  { field: '任务3_扫描上传材料', name: '扫描死亡医学证明、火化证、终保承诺书并上传养老系统' },
  { field: '任务4_填报抚恤金审批表', name: '填报抚恤金、安葬费审批表' },
  { field: '任务5_送审材料', name: '复印工资报复、死亡医学证明、火化证，与终保承诺书、抚恤金安葬费审批表一并送审' },
  { field: '任务6_机关中心签批', name: '报到机关中心在火化证上签批未超领工资' },
  { field: '任务7_工资科预审核', name: '报工资科预审核算结果' },
  { field: '任务8_教育局审批', name: '报教育局审批签章' },
  { field: '任务9_人社局审批', name: '报人社局工资科审批' },
  { field: '任务10_财政局备案', name: '报财政局备案' },
  { field: '任务11_处理绩效工资', name: '在绩效工资审批表中处理绩效，标明死亡信息' }
]

const taskList = reactive(
  taskDefinitions.map(t => ({ ...t, completed: false }))
)

// 计算属性
const completedCount = computed(() => {
  return checkedTasks.value.length
})

const currentProgress = computed(() => {
  return Math.round((completedCount.value / taskList.length) * 100)
})

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    const params = new URLSearchParams({
      page: currentPage.value.toString(),
      size: pageSize.value.toString()
    })
    if (searchKeyword.value) {
      params.append('teacher_name', searchKeyword.value)
    }
    if (filterStatus.value) {
      params.append('status', filterStatus.value)
    }

    const response = await fetch(`/api/death-todo/list?${params}`)
    const result = await response.json()

    if (result.status === 'success') {
      // 直接使用后端返回的数据，不再重新计算
      tableData.value = result.data
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

// 搜索
const handleSearch = () => {
  currentPage.value = 1
  loadData()
}

// 分页
const handleSizeChange = (val: number) => {
  pageSize.value = val
  loadData()
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  loadData()
}

// 处理/查看
const handleProcess = async (row: any) => {
  currentRow.value = row
  dialogTitle.value = row.状态 === '已完成' ? '查看死亡待办工作' : '处理死亡待办工作'
  
  // 重置任务列表
  taskList.forEach(task => {
    task.completed = false
  })
  checkedTasks.value = []
  
  // 加载详情
  try {
    const response = await fetch(`/api/death-todo/${row.id}/detail`)
    const result = await response.json()
    
    if (result.status === 'success' && result.data.任务进度) {
      const progress = result.data.任务进度
      
      // 更新任务完成状态
      taskList.forEach(task => {
        task.completed = progress[task.field] || false
        if (task.completed) {
          checkedTasks.value.push(task.field)
        }
      })
    }
  } catch (error) {
    console.error('加载详情失败:', error)
  }
  
  dialogVisible.value = true
}

// 任务变更
const handleTaskChange = (index: number, val: boolean) => {
  taskList[index].completed = val
}

// 提交进度
const handleSubmit = async () => {
  if (!currentRow.value) return
  
  submitting.value = true
  try {
    // 构建任务数据
    const taskData: any = {}
    taskList.forEach(task => {
      taskData[task.field] = task.completed
    })
    taskData['操作人'] = '系统用户'
    
    const response = await fetch(`/api/death-todo/${currentRow.value.id}/update-progress`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(taskData)
    })
    
    const result = await response.json()
    
    if (result.status === 'success') {
      ElMessage.success('进度保存成功')
      dialogVisible.value = false
      loadData()
    } else {
      ElMessage.error(result.detail || result.message || '保存失败')
    }
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error('保存失败')
  } finally {
    submitting.value = false
  }
}

// 退回
const handleRevert = async (row: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要退回"${row.教师姓名}"的死亡待办工作吗？退回后所有任务将重置为未完成状态。`,
      '确认退回',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const response = await fetch(`/api/death-todo/revert/${row.id}`, {
      method: 'POST'
    })
    
    const result = await response.json()
    
    if (result.status === 'success') {
      ElMessage.success('退回成功')
      loadData()
    } else {
      ElMessage.error(result.detail || result.message || '退回失败')
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('退回失败:', error)
      ElMessage.error('退回失败')
    }
  }
}

// 死亡日期变更处理
const handleDeathDateChange = async (date: string) => {
  if (!currentRow.value || !date) return
  
  try {
    const response = await fetch(`/api/death-todo/${currentRow.value.id}/update-death-date`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        death_date: date
      })
    })
    
    const result = await response.json()
    
    if (result.status === 'success') {
      ElMessage.success('死亡日期已更新')
      loadData()
    } else {
      ElMessage.error(result.detail || result.message || '更新失败')
    }
  } catch (error) {
    console.error('更新死亡日期失败:', error)
    ElMessage.error('更新死亡日期失败')
  }
}

// 表格行样式
const tableRowClassName = ({ row }: { row: any }) => {
  if (row.状态 === '已完成') {
    return 'completed-row'
  }
  return ''
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.death-todo-list {
  padding: 20px;
}

.page-card {
  min-height: calc(100vh - 120px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
}

.progress-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
}

.progress-text {
  font-size: 12px;
  color: #606266;
  white-space: nowrap;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.todo-detail {
  padding: 10px 0;
}

.mb-4 {
  margin-bottom: 20px;
}

.task-list {
  margin-bottom: 20px;
}

.task-title {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 15px;
  color: #303133;
}

.task-checkbox-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.task-item {
  padding: 10px 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
  transition: all 0.3s;
}

.task-item:hover {
  background-color: #e4e7ed;
}

.task-item.is-completed {
  background-color: #f0f9eb;
}

.task-number {
  font-weight: bold;
  margin-right: 8px;
  color: #409eff;
}

.task-name {
  color: #606266;
}

.progress-summary {
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.progress-title {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
}

.progress-count {
  font-size: 14px;
  color: #606266;
}

.progress-info {
  margin-top: 10px;
  text-align: center;
  color: #606266;
  font-size: 14px;
}

:deep(.completed-row) {
  background-color: #f0f9eb;
}

:deep(.el-checkbox__label) {
  white-space: normal;
  line-height: 1.5;
}
</style>
