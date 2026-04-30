<template>
  <div class="todo-template-container">
    <el-card class="page-header">
      <template #header>
        <div class="header-content">
          <div class="title-section">
            <el-icon class="title-icon"><Document /></el-icon>
            <span class="title">清单模板管理</span>
          </div>
          <el-button type="primary" @click="handleCreate">
            <el-icon><Plus /></el-icon>
            新建模板
          </el-button>
        </div>
      </template>

      <!-- 筛选栏 -->
      <div class="filter-bar">
        <el-input
          v-model="filterForm.keyword"
          placeholder="搜索模板名称"
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

        <el-select v-model="filterForm.is_active" placeholder="状态" clearable style="width: 120px">
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

    <!-- 模板列表 -->
    <el-row :gutter="20" class="template-list">
      <el-col :span="8" v-for="template in templateList" :key="template.id">
        <el-card class="template-card" :class="{ 'inactive': !template.is_active }">
          <template #header>
            <div class="template-card-header">
              <div class="template-title">
                <el-icon class="template-icon"><DocumentChecked /></el-icon>
                <span>{{ template.name }}</span>
              </div>
              <el-switch
                v-model="template.is_active"
                @change="(val: boolean) => handleStatusChange(template, val)"
              />
            </div>
          </template>

          <div class="template-content">
            <p class="template-description">{{ template.description || '暂无描述' }}</p>

            <div class="template-meta">
              <el-tag :type="getTypeTag(template.trigger_type)" size="small">
                {{ getTypeText(template.trigger_type) }}
              </el-tag>
              <span class="task-count">
                <el-icon><List /></el-icon>
                {{ template.task_flow?.length || 0 }} 个任务
              </span>
            </div>

            <div class="trigger-info" v-if="template.trigger_conditions?.length">
              <p class="trigger-title">触发条件：</p>
              <ul class="trigger-list">
                <li v-for="(condition, idx) in template.trigger_conditions.slice(0, 2)" :key="idx">
                  {{ condition.field }} {{ condition.operator }} {{ condition.value }}
                </li>
                <li v-if="template.trigger_conditions.length > 2" class="more">
                  还有 {{ template.trigger_conditions.length - 2 }} 个条件...
                </li>
              </ul>
            </div>
          </div>

          <div class="template-actions">
            <el-button type="primary" size="small" @click="handleEdit(template)">
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-button type="success" size="small" @click="handleDesign(template)">
              <el-icon><Connection /></el-icon>
              设计流程
            </el-button>
            <el-button type="danger" size="small" @click="handleDelete(template)">
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 分页 -->
    <div class="pagination-wrapper">
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.page_size"
        :total="pagination.total"
        :page-sizes="[9, 18, 36]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
      />
    </div>

    <!-- 模板编辑对话框 -->
    <el-dialog
      v-model="editDialogVisible"
      :title="isEditing ? '编辑模板' : '新建模板'"
      width="700px"
    >
      <el-form :model="templateForm" label-width="100px" :rules="templateRules" ref="templateFormRef">
        <el-form-item label="模板名称" prop="name">
          <el-input v-model="templateForm.name" placeholder="请输入模板名称" />
        </el-form-item>

        <el-form-item label="触发类型" prop="trigger_type">
          <el-select v-model="templateForm.trigger_type" placeholder="选择触发类型" style="width: 100%">
            <el-option label="退休提醒" value="retirement" />
            <el-option label="死亡登记" value="death" />
            <el-option label="80岁补贴" value="octogenarian" />
            <el-option label="自定义" value="custom" />
          </el-select>
        </el-form-item>

        <el-form-item label="模板描述" prop="description">
          <el-input
            v-model="templateForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入模板描述"
          />
        </el-form-item>

        <el-form-item label="默认截止天数" prop="default_deadline_days">
          <el-input-number v-model="templateForm.default_deadline_days" :min="1" :max="365" />
          <span class="form-hint">天（从创建日期开始计算）</span>
        </el-form-item>

        <el-form-item label="触发条件" prop="trigger_conditions">
          <div class="conditions-section">
            <div
              v-for="(condition, index) in templateForm.trigger_conditions"
              :key="index"
              class="condition-row"
            >
              <el-select v-model="condition.table_name" placeholder="选择表" style="width: 150px">
                <el-option label="教师基本信息" value="teacher_basic_info" />
                <el-option label="退休信息" value="retirement_info" />
              </el-select>
              <el-select v-model="condition.field" placeholder="选择字段" style="width: 150px">
                <el-option label="在职状态" value="employment_status" />
                <el-option label="出生日期" value="birth_date" />
              </el-select>
              <el-select v-model="condition.operator" placeholder="操作符" style="width: 100px">
                <el-option label="等于" value="=" />
                <el-option label="不等于" value="!=" />
                <el-option label="大于" value=">" />
                <el-option label="小于" value="<" />
              </el-select>
              <el-input v-model="condition.value" placeholder="值" style="width: 120px" />
              <el-button type="danger" circle size="small" @click="removeCondition(index)">
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
            <el-button type="primary" plain @click="addCondition">
              <el-icon><Plus /></el-icon>
              添加条件
            </el-button>
          </div>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitTemplate" :loading="submitting">
          确定
        </el-button>
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
                    <el-input v-model="task.name" placeholder="输入任务名称" />
                  </el-form-item>
                  <el-form-item label="任务描述">
                    <el-input v-model="task.description" type="textarea" :rows="2" placeholder="输入任务描述" />
                  </el-form-item>
                  <el-form-item label="负责人">
                    <el-input v-model="task.assignee" placeholder="输入负责人ID或角色" />
                  </el-form-item>
                  <el-form-item label="任务类型">
                    <el-select v-model="task.type" placeholder="选择类型" style="width: 100%">
                      <el-option label="审批" value="approval" />
                      <el-option label="文档" value="document" />
                      <el-option label="通知" value="notification" />
                      <el-option label="完成" value="complete" />
                    </el-select>
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
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import {
  Document,
  Plus,
  Search,
  Refresh,
  DocumentChecked,
  List,
  Edit,
  Delete,
  Connection,
  User,
  Bell,
  Check,
  ArrowUp,
  ArrowDown
} from '@element-plus/icons-vue'
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

// 筛选表单
const filterForm = reactive({
  keyword: '',
  trigger_type: '',
  is_active: null as boolean | null
})

// 分页
const pagination = reactive({
  page: 1,
  page_size: 9,
  total: 0
})

// 模板列表
const templateList = ref<any[]>([])
const loading = ref(false)

// 编辑对话框
const editDialogVisible = ref(false)
const isEditing = ref(false)
const templateFormRef = ref<FormInstance>()
const submitting = ref(false)

const templateForm = reactive({
  id: null as number | null,
  name: '',
  trigger_type: '',
  description: '',
  default_deadline_days: 7,
  trigger_conditions: [] as any[]
})

const templateRules: FormRules = {
  name: [{ required: true, message: '请输入模板名称', trigger: 'blur' }],
  trigger_type: [{ required: true, message: '请选择触发类型', trigger: 'change' }]
}

// 设计器对话框
const designDialogVisible = ref(false)
const currentTemplate = ref<any>(null)
const taskFlow = ref<any[]>([])
const savingFlow = ref(false)

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

// 获取类型文本
const getTypeText = (type?: string) => {
  const map: Record<string, string> = {
    'retirement': '退休提醒',
    'death': '死亡登记',
    'octogenarian': '80岁补贴',
    'custom': '自定义'
  }
  return map[type || ''] || type
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

// 加载模板列表
const loadTemplates = async () => {
  loading.value = true
  try {
    const params: any = {
      page: pagination.page,
      page_size: pagination.page_size,
      ...filterForm
    }
    const response = await axios.get(`${API_BASE_URL}/api/todo-system/templates`, { params })
    templateList.value = response.data.templates || []
    pagination.total = response.data.total || 0
  } catch (error) {
    console.error('加载模板列表失败:', error)
    ElMessage.error('加载模板列表失败')
  } finally {
    loading.value = false
  }
}

// 处理搜索
const handleSearch = () => {
  pagination.page = 1
  loadTemplates()
}

// 处理重置
const handleReset = () => {
  filterForm.keyword = ''
  filterForm.trigger_type = ''
  filterForm.is_active = null
  handleSearch()
}

// 处理分页
const handleSizeChange = (size: number) => {
  pagination.page_size = size
  loadTemplates()
}

const handlePageChange = (page: number) => {
  pagination.page = page
  loadTemplates()
}

// 处理状态变更
const handleStatusChange = async (template: any, isActive: boolean) => {
  try {
    await axios.put(`${API_BASE_URL}/api/todo-system/templates/${template.id}`, {
      is_active: isActive
    })
    ElMessage.success(isActive ? '已启用' : '已禁用')
  } catch (error) {
    console.error('状态变更失败:', error)
    ElMessage.error('状态变更失败')
    template.is_active = !isActive
  }
}

// 处理创建
const handleCreate = () => {
  isEditing.value = false
  templateForm.id = null
  templateForm.name = ''
  templateForm.trigger_type = ''
  templateForm.description = ''
  templateForm.default_deadline_days = 7
  templateForm.trigger_conditions = []
  editDialogVisible.value = true
}

// 处理编辑
const handleEdit = (template: any) => {
  isEditing.value = true
  templateForm.id = template.id
  templateForm.name = template.name
  templateForm.trigger_type = template.trigger_type
  templateForm.description = template.description || ''
  templateForm.default_deadline_days = template.default_deadline_days || 7
  templateForm.trigger_conditions = template.trigger_conditions || []
  editDialogVisible.value = true
}

// 添加条件
const addCondition = () => {
  templateForm.trigger_conditions.push({
    table_name: 'teacher_basic_info',
    field: '',
    operator: '=',
    value: ''
  })
}

// 移除条件
const removeCondition = (index: number) => {
  templateForm.trigger_conditions.splice(index, 1)
}

// 提交模板
const submitTemplate = async () => {
  if (!templateFormRef.value) return

  await templateFormRef.value.validate(async (valid) => {
    if (!valid) return

    submitting.value = true
    try {
      if (isEditing.value && templateForm.id) {
        await axios.put(`${API_BASE_URL}/api/todo-system/templates/${templateForm.id}`, templateForm)
        ElMessage.success('更新成功')
      } else {
        await axios.post(`${API_BASE_URL}/api/todo-system/templates`, templateForm)
        ElMessage.success('创建成功')
      }
      editDialogVisible.value = false
      loadTemplates()
    } catch (error) {
      console.error('保存模板失败:', error)
      ElMessage.error('保存失败')
    } finally {
      submitting.value = false
    }
  })
}

// 处理设计流程
const handleDesign = (template: any) => {
  currentTemplate.value = template
  taskFlow.value = template.task_flow ? [...template.task_flow] : []
  designDialogVisible.value = true
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
    await axios.put(`${API_BASE_URL}/api/todo-system/templates/${currentTemplate.value.id}`, {
      task_flow: taskFlow.value
    })
    ElMessage.success('流程保存成功')
    designDialogVisible.value = false
    loadTemplates()
  } catch (error) {
    console.error('保存流程失败:', error)
    ElMessage.error('保存流程失败')
  } finally {
    savingFlow.value = false
  }
}

// 处理删除
const handleDelete = async (template: any) => {
  try {
    await ElMessageBox.confirm(`确定要删除模板 "${template.name}" 吗？`, '确认删除', {
      type: 'warning'
    })
    await axios.delete(`${API_BASE_URL}/api/todo-system/templates/${template.id}`)
    ElMessage.success('删除成功')
    loadTemplates()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

onMounted(() => {
  loadTemplates()
})
</script>

<style scoped>
.todo-template-container {
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

.filter-bar {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
  align-items: center;
}

.template-list {
  margin-top: 20px;
}

.template-card {
  margin-bottom: 20px;
  transition: all 0.3s;
}

.template-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.template-card.inactive {
  opacity: 0.6;
}

.template-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.template-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: bold;
}

.template-icon {
  color: #409EFF;
}

.template-content {
  min-height: 120px;
}

.template-description {
  color: #606266;
  margin: 0 0 15px 0;
  min-height: 40px;
}

.template-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.task-count {
  color: #909399;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 5px;
}

.trigger-info {
  background: #f5f7fa;
  padding: 10px;
  border-radius: 4px;
}

.trigger-title {
  margin: 0 0 8px 0;
  font-weight: bold;
  font-size: 13px;
  color: #606266;
}

.trigger-list {
  margin: 0;
  padding-left: 20px;
  font-size: 13px;
  color: #606266;
}

.trigger-list li {
  margin-bottom: 4px;
}

.trigger-list li.more {
  color: #909399;
  font-style: italic;
}

.template-actions {
  display: flex;
  justify-content: space-between;
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #ebeef5;
}

.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.conditions-section {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.condition-row {
  display: flex;
  gap: 10px;
  align-items: center;
}

.form-hint {
  margin-left: 10px;
  color: #909399;
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
