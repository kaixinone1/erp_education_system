<template>
  <div class="checklist-template-container">
    <!-- 搜索筛选栏 -->
    <el-card class="filter-card">
      <div class="filter-bar">
        <el-input
          v-model="filterForm.keyword"
          placeholder="搜索清单名称"
          clearable
          style="width: 250px"
          @keyup.enter="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>

        <el-select v-model="filterForm.trigger_type" placeholder="触发类型" clearable style="width: 150px">
          <el-option label="退休提醒" value="retirement" />
          <el-option label="死亡登记" value="death" />
          <el-option label="80岁补贴" value="octogenarian" />
          <el-option label="自定义" value="custom" />
        </el-select>

        <el-select v-model="filterForm.status" placeholder="状态" clearable style="width: 120px">
          <el-option label="启用" :value="true" />
          <el-option label="禁用" :value="false" />
        </el-select>

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

    <!-- 标题和新增按钮 -->
    <div class="header">
      <h2>清单模板管理</h2>
      <el-button type="primary" @click="handleAdd">
        <el-icon><Plus /></el-icon>新增清单模板
      </el-button>
    </div>

    <el-table :data="filteredTableData" v-loading="loading" border stripe>
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="清单名称" label="清单名称" min-width="150" />
      <el-table-column label="触发条件" min-width="150">
        <template #default="{ row }">
          <span v-if="row.触发条件 && row.触发条件.target_status">
            状态: {{ row.触发条件.target_status.join(', ') }}
          </span>
          <span v-else class="text-gray">未设置</span>
        </template>
      </el-table-column>
      <el-table-column label="任务项" min-width="250">
        <template #default="{ row }">
          <div v-if="row.任务项列表 && row.任务项列表.length > 0" class="task-list">
            <div v-for="(item, idx) in row.任务项列表.slice(0, 3)" :key="idx" class="task-item-preview">
              <span class="task-num">{{ item.序号 || idx + 1 }}.</span>
              <span class="task-title">{{ item.标题 }}</span>
              <span class="task-options" v-if="item.参数 && item.参数.选项 && item.参数.选项.length">
                <span v-for="(opt, oi) in item.参数.选项" :key="oi">{{ opt.名称 }}<span v-if="oi < item.参数.选项.length - 1"> / </span></span>
              </span>
              <span class="task-target" v-else-if="item.目标">({{ getTargetDisplayName(item.目标) }})</span>
            </div>
            <div v-if="row.任务项列表.length > 3" class="more-tasks">
              + 还有 {{ row.任务项列表.length - 3 }} 项...
            </div>
          </div>
          <span v-else class="text-gray">暂无任务</span>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="80" align="center">
        <template #default="{ row }">
          <el-tag :type="row.是否有效 ? 'success' : 'danger'">
            {{ row.是否有效 ? '有效' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="280" fixed="right">
        <template #default="{ row }">
          <el-button size="small" type="primary" @click="handleEdit(row)">编辑</el-button>
          <el-button size="small" type="success" @click="handleDesign(row)">设计流程</el-button>
          <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
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

    <!-- 编辑/新增对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑清单模板' : '新增清单模板'"
      width="800px"
      destroy-on-close
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="清单名称" prop="清单名称">
          <el-input v-model="form.清单名称" placeholder="请输入清单名称" />
        </el-form-item>

        <el-form-item label="触发条件" prop="触发条件">
          <div class="trigger-condition">
            <span>当教师任职状态变更为：</span>
            <el-select
              v-model="form.触发条件.target_status"
              multiple
              placeholder="选择触发状态"
              style="width: 300px"
            >
              <el-option
                v-for="opt in employmentStatusOptions"
                :key="opt.value"
                :label="opt.label"
                :value="opt.value"
              />
            </el-select>
            <span style="margin-left: 10px; color: #909399; font-size: 12px">（根据教师基础信息表中任职状态字段）</span>
          </div>
        </el-form-item>

        <el-form-item label="任务项列表" prop="任务项列表">
          <div class="task-items">
            <div v-for="(item, index) in form.任务项列表" :key="index" class="task-item">
              <el-card shadow="never">
                <template #header>
                  <div class="task-header">
                    <span>任务项 {{ index + 1 }}</span>
                    <el-button type="danger" size="small" text @click="removeTaskItem(index)">
                      删除
                    </el-button>
                  </div>
                </template>
                <el-form-item label="标题">
                  <el-input v-model="item.标题" placeholder="任务标题" />
                </el-form-item>
                <el-form-item label="类型">
                  <el-select v-model="item.类型" placeholder="选择类型">
                    <el-option label="内部表" value="内部表" />
                    <el-option label="外部链接" value="外部链接" />
                    <el-option label="自动汇总" value="自动汇总" />
                    <el-option label="签发证件" value="签发证件" />
                  </el-select>
                </el-form-item>
                <el-form-item label="目标">
                  <el-select 
                    v-model="item.目标" 
                    placeholder="选择目标"
                    filterable
                    allow-create
                    default-first-option
                    style="width: 100%"
                  >
                    <el-option
                      v-for="opt in targetOptions"
                      :key="opt.value"
                      :label="opt.label"
                      :value="opt.value"
                    >
                      <span>{{ opt.label }}</span>
                      <span style="float: right; color: #8492a6; font-size: 12px">{{ opt.type }}</span>
                    </el-option>
                  </el-select>
                </el-form-item>
                <el-form-item label="说明">
                  <el-input v-model="item.参数.说明" type="textarea" rows="2" placeholder="任务说明" />
                </el-form-item>
                <el-form-item label="选项" v-if="item.参数 && item.参数.选项">
                  <div v-for="(opt, idx) in item.参数.选项" :key="idx" style="margin-bottom: 5px">
                    <el-tag>{{ opt.名称 }}</el-tag>
                  </div>
                </el-form-item>
                <el-form-item v-if="item.类型 === '内部表'" label="关联模板">
                  <el-select v-model="item.参数.template_id" placeholder="选择模板" clearable>
                    <el-option-group label="通用模板">
                      <el-option
                        v-for="tpl in universalTemplateList"
                        :key="tpl.template_id"
                        :label="tpl.template_name"
                        :value="tpl.template_id"
                      />
                    </el-option-group>
                    <el-option-group label="旧模板">
                      <el-option
                        v-for="tpl in templateList"
                        :key="tpl.template_id"
                        :label="tpl.template_id"
                        :value="tpl.template_id"
                      />
                    </el-option-group>
                  </el-select>
                </el-form-item>
              </el-card>
            </div>
            <el-button type="primary" text @click="addTaskItem">+ 添加任务项</el-button>
          </div>
        </el-form-item>

        <el-form-item label="是否有效">
          <el-switch v-model="form.是否有效" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>

    <!-- 流程设计器对话框 -->
    <el-dialog
      v-model="designDialogVisible"
      title="任务流程设计器"
      width="900px"
      class="designer-dialog"
    >
      <div class="workflow-designer" v-if="currentTemplate">
        <div class="designer-toolbar">
          <el-button-group>
            <el-button @click="addTaskNode('approval')">
              <el-icon><User /></el-icon>
              审批节点
            </el-button>
            <el-button @click="addTaskNode('document')">
              <el-icon><Document /></el-icon>
              文档节点
            </el-button>
            <el-button @click="addTaskNode('notification')">
              <el-icon><Bell /></el-icon>
              通知节点
            </el-button>
            <el-button @click="addTaskNode('complete')">
              <el-icon><Check /></el-icon>
              完成节点
            </el-button>
          </el-button-group>
          <el-button type="primary" @click="saveTaskFlow" :loading="savingFlow">
            <el-icon><Check /></el-icon>
            保存流程
          </el-button>
        </div>

        <div class="designer-canvas">
          <el-timeline>
            <el-timeline-item
              v-for="(task, index) in taskFlow"
              :key="index"
              :type="task.type"
              :icon="getTaskIcon(task.type)"
            >
              <el-card class="task-node-card">
                <template #header>
                  <div class="task-node-header">
                    <span>步骤 {{ index + 1 }}</span>
                    <div class="task-actions">
                      <el-button circle size="small" @click="moveTaskUp(index)" :disabled="index === 0">
                        <el-icon><ArrowUp /></el-icon>
                      </el-button>
                      <el-button circle size="small" @click="moveTaskDown(index)" :disabled="index === taskFlow.length - 1">
                        <el-icon><ArrowDown /></el-icon>
                      </el-button>
                      <el-button type="danger" circle size="small" @click="removeTask(index)">
                        <el-icon><Delete /></el-icon>
                      </el-button>
                    </div>
                  </div>
                </template>

                <el-form :model="task" label-width="80px" size="small">
                  <el-form-item label="任务名称">
                    <el-input :model-value="task.标题 || task.name" @update:model-value="val => task.标题 = val || task.name" placeholder="输入任务名称" />
                  </el-form-item>
                  <el-form-item label="任务描述">
                    <el-input :model-value="task.说明 || task.description" @update:model-value="val => task.说明 = val || task.description" type="textarea" :rows="2" placeholder="输入任务描述" />
                  </el-form-item>
                  <el-form-item label="负责人" v-if="task.assignee !== undefined">
                    <el-input v-model="task.assignee" placeholder="输入负责人ID或角色" />
                  </el-form-item>
                  <el-form-item label="任务类型">
                    <el-input :model-value="task.类型 || task.type" @update:model-value="val => task.类型 = val || task.type" placeholder="输入任务类型" />
                  </el-form-item>
                  <el-form-item label="选项" v-if="task.参数 && task.参数.选项">
                    <div v-for="(opt, idx) in task.参数.选项" :key="idx" style="margin-bottom: 5px">
                      <el-tag>{{ opt.名称 }}</el-tag>
                    </div>
                  </el-form-item>
                </el-form>
              </el-card>
            </el-timeline-item>
          </el-timeline>

          <el-empty v-if="!taskFlow.length" description="点击上方按钮添加任务节点" />
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus,
  Search,
  Refresh,
  User,
  Document,
  Bell,
  Check,
  ArrowUp,
  ArrowDown,
  Delete
} from '@element-plus/icons-vue'

const API_BASE = '/api/checklist-template'

// 筛选表单
const filterForm = ref({
  keyword: '',
  trigger_type: '',
  status: null as boolean | null
})

// 分页
const pagination = ref({
  page: 1,
  page_size: 10,
  total: 0
})

const loading = ref(false)
const submitting = ref(false)
const tableData = ref<any[]>([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref()
const templateList = ref<any[]>([])
const universalTemplateList = ref<any[]>([])
const targetOptions = ref<any[]>([])
const employmentStatusOptions = ref<any[]>([])

// 设计器相关
const designDialogVisible = ref(false)
const currentTemplate = ref<any>(null)
const taskFlow = ref<any[]>([])
const savingFlow = ref(false)

const form = ref({
  id: null,
  清单名称: '',
  触发条件: { target_status: [] as string[] },
  任务项列表: [] as any[],
  是否有效: true,
  关联模板ID: null
})

const rules = {
  清单名称: [{ required: true, message: '请输入清单名称', trigger: 'blur' }]
}

// 过滤后的数据
const filteredTableData = computed(() => {
  let result = tableData.value

  // 关键字筛选
  if (filterForm.value.keyword) {
    const keyword = filterForm.value.keyword.toLowerCase()
    result = result.filter(item =>
      item.清单名称 && item.清单名称.toLowerCase().includes(keyword)
    )
  }

  // 状态筛选
  if (filterForm.value.status !== null) {
    result = result.filter(item => item.是否有效 === filterForm.value.status)
  }

  return result
})

const loadData = async () => {
  loading.value = true
  try {
    const res = await fetch(`${API_BASE}/list`)
    const result = await res.json()
    if (result.status === 'success') {
      tableData.value = result.data
      pagination.value.total = result.data.length
    }
  } catch (e: any) {
    ElMessage.error('加载数据失败: ' + e.message)
  } finally {
    loading.value = false
  }
}

const loadTemplates = async () => {
  try {
    // 加载旧模板
    const res = await fetch('/api/document-templates/list')
    const result = await res.json()
    if (result.status === 'success') {
      templateList.value = result.data || []
    }

    // 加载通用模板
    const res2 = await fetch('/api/universal-templates/list')
    const result2 = await res2.json()
    if (result2.status === 'success') {
      universalTemplateList.value = result2.data || []
    }
  } catch (e) {
    console.error('加载模板列表失败', e)
  }
}

const loadTargetOptions = async () => {
  try {
    const res = await fetch('/api/checklist-template/target-options')
    const result = await res.json()
    if (result.status === 'success') {
      targetOptions.value = result.data || []
    }
  } catch (e) {
    console.error('加载目标选项失败', e)
  }
}

const loadEmploymentStatusOptions = async () => {
  try {
    const res = await fetch('/api/checklist-template/employment-status-options')
    const result = await res.json()
    if (result.status === 'success') {
      employmentStatusOptions.value = result.data || []
    }
  } catch (e) {
    console.error('加载任职状态选项失败', e)
  }
}

const getTargetDisplayName = (target: string) => {
  if (!target) return ''
  // 如果是网址，直接显示
  if (target.startsWith('http://') || target.startsWith('https://')) {
    return target
  }
  // 从选项中查找
  const found = targetOptions.value.find(opt => opt.value === target)
  return found ? found.label : target
}

// 搜索和重置
const handleSearch = () => {
  pagination.value.page = 1
  // 数据已经在computed中过滤
}

const handleReset = () => {
  filterForm.value.keyword = ''
  filterForm.value.trigger_type = ''
  filterForm.value.status = null
  handleSearch()
}

// 分页
const handleSizeChange = (size: number) => {
  pagination.value.page_size = size
}

const handlePageChange = (page: number) => {
  pagination.value.page = page
}

const handleAdd = () => {
  isEdit.value = false
  form.value = {
    id: null,
    清单名称: '',
    触发条件: { target_status: [] },
    任务项列表: [],
    是否有效: true,
    关联模板ID: null
  }
  dialogVisible.value = true
}

const handleEdit = (row: any) => {
  isEdit.value = true
  form.value = {
    id: row.id,
    清单名称: row.清单名称,
    触发条件: row.触发条件 || { target_status: [] },
    任务项列表: row.任务项列表 || [],
    是否有效: row.是否有效,
    关联模板ID: row.关联模板ID
  }
  dialogVisible.value = true
}

const handleDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm(`确定要删除清单模板 "${row.清单名称}" 吗？`, '提示', {
      type: 'warning'
    })
    await fetch(`${API_BASE}/${row.id}`, { method: 'DELETE' })
    ElMessage.success('删除成功')
    loadData()
  } catch (e: any) {
    if (e !== 'cancel') {
      ElMessage.error('删除失败: ' + e.message)
    }
  }
}

const addTaskItem = () => {
  form.value.任务项列表.push({
    序号: form.value.任务项列表.length + 1,
    标题: '',
    类型: '内部表',
    目标: '',
    参数: {
      说明: '',
      template_id: ''
    },
    完成状态: false
  })
}

const removeTaskItem = (index: number) => {
  form.value.任务项列表.splice(index, 1)
  form.value.任务项列表.forEach((item, i) => {
    item.序号 = i + 1
  })
}

const handleSubmit = async () => {
  await formRef.value?.validate()
  submitting.value = true
  try {
    const data = { ...form.value }
    let result
    if (isEdit.value) {
      const res = await fetch(`${API_BASE}/${data.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      })
      result = await res.json()
      ElMessage.success('更新成功')
    } else {
      const res = await fetch(`${API_BASE}/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      })
      result = await res.json()
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    loadData()
  } catch (e: any) {
    ElMessage.error('操作失败: ' + e.message)
  } finally {
    submitting.value = false
  }
}

// 设计流程
const handleDesign = (row: any) => {
  currentTemplate.value = row
  const tasks = row.任务项列表 ? [...row.任务项列表] : []
  taskFlow.value = tasks.map((t: any) => ({
    name: t.标题 || t.name,
    description: t.说明 || t.description,
    type: t.类型 || t.type,
    参数: t.参数
  }))
  designDialogVisible.value = true
}

// 获取任务图标
const getTaskIcon = (type?: string) => {
  const map: Record<string, any> = {
    'approval': User,
    'document': Document,
    'notification': Bell,
    'complete': Check
  }
  return map[type || ''] || Check
}

// 添加任务节点
const addTaskNode = (type: string) => {
  const typeNames: Record<string, string> = {
    'approval': '审批任务',
    'document': '文档处理',
    'notification': '发送通知',
    'complete': '完成确认'
  }

  taskFlow.value.push({
    name: typeNames[type] || '新任务',
    description: '',
    type: type,
    assignee: '',
    status: 'pending'
  })
}

// 移除任务
const removeTask = (index: number) => {
  taskFlow.value.splice(index, 1)
}

// 上移任务
const moveTaskUp = (index: number) => {
  if (index === 0) return
  const temp = taskFlow.value[index]
  taskFlow.value[index] = taskFlow.value[index - 1]
  taskFlow.value[index - 1] = temp
}

// 下移任务
const moveTaskDown = (index: number) => {
  if (index === taskFlow.value.length - 1) return
  const temp = taskFlow.value[index]
  taskFlow.value[index] = taskFlow.value[index + 1]
  taskFlow.value[index + 1] = temp
}

// 保存任务流程
const saveTaskFlow = async () => {
  if (!currentTemplate.value) return

  savingFlow.value = true
  try {
    await fetch(`${API_BASE}/${currentTemplate.value.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        ...currentTemplate.value,
        task_flow: taskFlow.value
      })
    })
    ElMessage.success('流程保存成功')
    designDialogVisible.value = false
    loadData()
  } catch (error: any) {
    ElMessage.error('保存流程失败: ' + error.message)
  } finally {
    savingFlow.value = false
  }
}

onMounted(() => {
  loadData()
  loadTemplates()
  loadTargetOptions()
  loadEmploymentStatusOptions()
})
</script>

<style scoped>
.checklist-template-container {
  padding: 20px;
}

.filter-card {
  margin-bottom: 20px;
}

.filter-bar {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
  align-items: center;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header h2 {
  margin: 0;
}

.trigger-condition {
  display: flex;
  align-items: center;
  gap: 10px;
}

.task-items {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.task-item {
  margin-bottom: 10px;
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.text-gray {
  color: #999;
}

.task-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.task-item-preview {
  font-size: 12px;
  line-height: 1.4;
}

.task-num {
  color: #409eff;
  font-weight: bold;
  margin-right: 4px;
}

.task-title {
  color: #303133;
}

.task-target {
  color: #909399;
  font-size: 11px;
  margin-left: 4px;
}

.more-tasks {
  color: #909399;
  font-size: 12px;
  margin-top: 4px;
}

.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

/* 设计器样式 */
.designer-dialog :deep(.el-dialog__body) {
  padding: 0;
}

.workflow-designer {
  display: flex;
  flex-direction: column;
  height: 600px;
}

.designer-toolbar {
  display: flex;
  justify-content: space-between;
  padding: 15px 20px;
  border-bottom: 1px solid #ebeef5;
  background: #f5f7fa;
}

.designer-canvas {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.task-node-card {
  width: 400px;
}

.task-node-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.task-actions {
  display: flex;
  gap: 5px;
}
</style>
