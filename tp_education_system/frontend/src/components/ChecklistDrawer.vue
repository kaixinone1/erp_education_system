<template>
  <el-drawer
    v-model="visible"
    :title="title"
    size="600px"
    :destroy-on-close="true"
    @close="handleClose"
  >
    <div class="checklist-drawer">
      <!-- 进度统计 -->
      <div class="progress-section">
        <div class="progress-header">
          <span class="progress-title">完成进度</span>
          <span class="progress-count">已完成 {{ completedCount }} / 共 {{ totalCount }} 项</span>
        </div>
        <el-progress :percentage="progressPercentage" :stroke-width="10" :status="progressStatus" />
      </div>
      
      <!-- 任务列表 -->
      <div class="task-list">
        <div
          v-for="(task, index) in taskItems"
          :key="index"
          class="task-item"
          :class="{ completed: task.completed }"
        >
          <!-- 普通任务显示复选框 -->
          <div v-if="!hasOptions(task)" class="task-header">
            <el-checkbox
              v-model="task.completed"
              @change="(val) => handleTaskComplete(index, val)"
            >
              <span class="task-title">{{ task.title }}</span>
              <span v-if="task.step" class="task-step">步骤 {{ task.step }}</span>
            </el-checkbox>
            <el-tag v-if="task.type" size="small" :type="getTaskType(task.type)">
              {{ task.type }}
            </el-tag>
          </div>
          
          <!-- 有选项的任务（如到龄退休提醒）不显示复选框，显示标题 -->
          <div v-else class="task-header-no-checkbox">
            <span class="task-title">{{ task.title }}</span>
            <el-tag v-if="task.type" size="small" :type="getTaskType(task.type)">
              {{ task.type }}
            </el-tag>
          </div>
          
          <div class="task-desc" v-if="task.desc || task.description">{{ task.desc || task.description }}</div>
          <div class="task-meta" v-if="task.days">
            <el-tag size="small" type="info">{{ task.days }} 天内完成</el-tag>
          </div>
          
          <!-- 任务选项（如修改任职状态、已批准延迟退休） -->
          <div class="task-options" v-if="hasOptions(task)">
            <div class="option-items">
              <div 
                v-for="(opt, idx) in getTaskOptions(task)" 
                :key="idx" 
                class="option-item"
                :class="{ selected: task.selectedOption === opt.label, completed: task.completed && task.selectedOption === opt.label }"
                @click="handleOptionClick(index, opt)"
              >
                <div class="option-radio">
                  <el-radio v-model="task.selectedOption" :label="opt.label" @click.stop>
                    {{ opt.name }}
                  </el-radio>
                </div>
                <div class="option-desc">{{ opt.desc }}</div>
              </div>
            </div>
          </div>
          
          <div class="task-actions" v-if="!hasOptions(task)">
            <!-- 内部表类型：填报按钮 -->
            <el-button
              v-if="task.类型 === '内部表'"
              type="primary"
              size="small"
              @click="handleFill(task)"
            >
              填报
            </el-button>
            <!-- 外部链接类型：跳转按钮 -->
            <el-button
              v-else-if="task.类型 === '外部链接'"
              type="info"
              size="small"
              @click="handleRedirect(task)"
            >
              跳转
            </el-button>
            <!-- 自动汇总类型：执行按钮 -->
            <el-button
              v-else-if="task.类型 === '自动汇总'"
              type="warning"
              size="small"
              @click="handleAutoSum(task)"
            >
              执行
            </el-button>
            <!-- 签发证件类型：签发按钮 -->
            <el-button
              v-else-if="task.类型 === '签发证件'"
              type="success"
              size="small"
              @click="handleIssue(task)"
            >
              签发
            </el-button>
            <!-- 原有逻辑保留兼容 -->
            <el-button
              v-else-if="task.action === 'fill' || task.type === '填报'"
              type="primary"
              size="small"
              @click="handleFill(task)"
            >
              填报
            </el-button>
            <el-button
              v-else-if="task.action === 'redirect' || task.type === '跳转'"
              type="info"
              size="small"
              @click="handleRedirect(task)"
            >
              跳转
            </el-button>
          </div>
        </div>
      </div>

      <!-- 办理记录区域 -->
      <div class="notes-section">
        <div class="notes-header">
          <span class="notes-title">
            <el-icon><EditPen /></el-icon>
            办理记录
          </span>
          <el-tag size="small" type="info">{{ notesList.length }} 条记录</el-tag>
        </div>
        
        <!-- 已有记录列表 -->
        <div v-if="notesList.length > 0" class="notes-list">
          <div v-for="(note, idx) in notesList" :key="idx" class="note-item">
            <span class="note-index">{{ idx + 1 }}.</span>
            <span class="note-content">{{ note.content }}</span>
            <span class="note-time">{{ formatNoteTime(note.time) }}</span>
          </div>
        </div>

        <!-- 输入新记录 -->
        <div class="notes-input">
          <el-input
            v-model="newNote"
            type="textarea"
            :rows="3"
            placeholder="输入办理过程记录，按回车或点击添加按钮保存..."
            @keydown.enter.exact.prevent="addNote"
          />
          <el-button 
            type="primary" 
            @click="addNote"
            :disabled="!newNote.trim()"
            style="margin-top: 8px; width: 100%"
          >
            <el-icon><Plus /></el-icon>
            添加记录
          </el-button>
        </div>
      </div>

      <!-- 保存按钮 -->
      <div class="drawer-footer">
        <el-button @click="visible = false">关闭</el-button>
        <el-button type="primary" @click="saveAllNotes" :loading="saving">
          保存所有记录
        </el-button>
      </div>
    </div>
  </el-drawer>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { EditPen, Plus } from '@element-plus/icons-vue'

const router = useRouter()

// Props
const props = defineProps<{
  modelValue: boolean
  todoData?: any
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
  (e: 'close'): void
  (e: 'status-changed', data: { todoId: number, completedCount: number, totalCount: number, status: string }): void
}>()

// 可见性
const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

// 标题
const title = computed(() => {
  const name = props.todoData?.teacher_name || ''
  const checklist = props.todoData?.checklist_name || props.todoData?.template_name || '业务清单'
  return `${name} - ${checklist}`
})

// 任务项 - 从 todoData 中获取
const taskItems = ref<any[]>([])

// 办理记录
const newNote = ref('')
const notesList = ref<any[]>([])
const saving = ref(false)

// 统计计算
const totalCount = computed(() => taskItems.value.length)
const completedCount = computed(() => taskItems.value.filter(t => t.completed).length)
const progressPercentage = computed(() => {
  if (totalCount.value === 0) return 0
  return Math.round((completedCount.value / totalCount.value) * 100)
})
const progressStatus = computed(() => {
  if (progressPercentage.value === 100) return 'success'
  return ''
})

// 监听 todoData 变化
watch(() => props.todoData, (newTodoData) => {
  // 如果没有todoData，清空任务项
  if (!newTodoData) {
    taskItems.value = []
    notesList.value = []
    return
  }
  
  let items = newTodoData?.task_items || []
  console.log('原始 task_items:', items)
  // 如果 task_items 是 JSON 字符串，解析为数组
  if (typeof items === 'string') {
    try {
      items = JSON.parse(items)
      console.log('解析后的 task_items:', items)
    } catch (e) {
      console.error('解析 task_items 失败:', e)
      items = []
    }
  }
  // 确保至少有一个任务项（如果没有，添加默认的"确认完成"项）
  if (!items || items.length === 0) {
    items = [{
      "title": "确认完成",
      "desc": `请确认${newTodoData?.teacher_name || ''}的"${newTodoData?.checklist_name || '此业务'}"已处理完毕`,
      "type": "确认",
      "completed": false
    }]
  }
  // 转换字段名（兼容中文和英文字段）
  taskItems.value = items.map((item: any) => ({
    ...item,
    title: item.title || item.标题 || '未命名任务',
    type: item.type || item.类型 || '',
    desc: item.desc || item.description || item.说明 || '',
    completed: item.completed || item.完成状态 || false,
    days: item.days || item.天数 || null,
    step: item.step || item.步骤 || null,
    action: item.action || item.动作 || '',
    params: item.params || item.参数 || {}
  }))

  // 加载已有的办理记录
  loadNotes()
}, { immediate: true })

// 加载办理记录
const loadNotes = async () => {
  if (!props.todoData?.id) return
  try {
    // 使用新的API
    const response = await fetch(`/api/todo-system/todo/${props.todoData.id}/notes`)
    if (response.ok) {
      const result = await response.json()
      if (result.data && result.data.notes) {
        let notes = result.data.notes
        if (typeof notes === 'string') {
          try { notes = JSON.parse(notes) } catch { notes = [] }
        }
        notesList.value = Array.isArray(notes) ? notes : []
      } else {
        notesList.value = []
      }
    }
  } catch (error) {
    console.error('加载办理记录失败:', error)
  }
}

// 格式化记录时间
const formatNoteTime = (timeStr: string): string => {
  if (!timeStr) return ''
  try {
    const date = new Date(timeStr)
    return date.toLocaleString('zh-CN', {
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch {
    return timeStr
  }
}

// 添加记录
const addNote = () => {
  const content = newNote.value.trim()
  if (!content) return
  
  notesList.value.push({
    content: content,
    time: new Date().toISOString()
  })
  
  newNote.value = ''
  ElMessage.success('记录已添加（请点击保存）')
}

// 保存所有记录到后端
const saveAllNotes = async () => {
  if (!props.todoData?.id) {
    ElMessage.error('待办ID无效')
    return
  }
  
  saving.value = true
  try {
    // 使用新的API
    const response = await fetch(`/api/todo-system/todo/${props.todoData.id}/notes`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        notes: notesList.value
      })
    })
    
    if (response.ok) {
      ElMessage.success('保存成功')
    } else {
      const result = await response.json().catch(() => ({}))
      ElMessage.error(result.detail || '保存失败')
    }
  } catch (error) {
    console.error('保存记录失败:', error)
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

// 判断任务是否有选项
const hasOptions = (task: any) => {
  console.log('hasOptions called:', task)
  const params = task.params || task.参数 || {}
  const options = params.选项 || params.options || []
  console.log('params:', params, 'options:', options)
  return options.length > 0
}

// 获取任务选项
const getTaskOptions = (task: any) => {
  const params = task.params || task.参数 || {}
  const options = params.选项 || params.options || []
  return options.map((opt: any) => ({
    label: opt.label || opt.标签,
    name: opt.名称 || opt.name,
    desc: opt.说明 || opt.description,
    targetTable: opt.目标表 || opt.target_table,
    action: opt.操作 || opt.action
  }))
}

// 处理选项点击
const handleOptionClick = async (index: number, opt: any) => {
  const task = taskItems.value[index]
  const teacherId = props.todoData?.teacher_id
  const teacherName = props.todoData?.teacher_name
  
  console.log('handleOptionClick called:', { index, opt, teacherId, teacherName })
  
  // 设置选中状态
  task.selectedOption = opt.label
  
  // 根据选项执行不同操作
  // 支持中英文标签判断
  const label = opt.label || ''
  const name = opt.name || ''
  
  if (label === 'modify_status' || name === '修改任职状态') {
    // 修改任职状态 - 跳转到教师基础信息表
    ElMessage.info(`正在打开教师基础信息表，请修改${teacherName}的任职状态为退休`)
    
    try {
      // 标记任务完成
      await handleTaskComplete(index, true)
      console.log('任务已标记完成，准备跳转')
    } catch (e) {
      console.error('标记任务完成失败:', e)
    }
    
    // 跳转到教师基础信息表（无论标记是否成功都跳转）
    console.log('跳转到教师基础信息表:', `/data/teacher_basic_info?teacher_id=${teacherId}&teacher_name=${teacherName}`)
    router.push({
      path: '/data/teacher_basic_info',
      query: { 
        teacher_id: teacherId,
        teacher_name: teacherName,
        mode: 'edit',
        field: 'employment_status'
      }
    }).then(() => {
      console.log('跳转成功')
      visible.value = false
    }).catch((err: any) => {
      console.error('跳转失败:', err)
      ElMessage.error('跳转失败: ' + (err.message || '未知错误'))
    })
    
  } else if (label === 'delayed_retirement' || name === '已批准延迟退休') {
    // 已批准延迟退休 - 检查延迟退休教师表
    try {
      const response = await fetch(`/api/check-delayed-retirement/${teacherId}`)
      const result = await response.json()
      
      if (result.exists) {
        // 教师在延迟退休表中，直接完成
        ElMessage.success('该教师已在延迟退休教师表中，任务完成')
        await handleTaskComplete(index, true)
      } else {
        // 教师不在延迟退休表中，跳转填写
        ElMessage.info('该教师不在延迟退休教师表中，请填写相关信息')
        
        // 标记任务完成
        await handleTaskComplete(index, true)
        
        // 跳转到延迟退休教师表
        router.push({
          path: '/data/delayed_retirement_records',
          query: { 
            teacher_id: teacherId,
            teacher_name: teacherName,
            mode: 'add'
          }
        })
        visible.value = false
      }
    } catch (error) {
      console.error('检查延迟退休表失败:', error)
      ElMessage.error('检查延迟退休表失败')
    }
  }
}

// 获取任务类型样式
const getTaskType = (type: string) => {
  const typeMap: Record<string, string> = {
    '填报': 'primary',
    '跳转': 'info',
    '收集': 'warning',
    '确认': 'success',
    '内部表': 'primary',
    '外部链接': 'info',
    '自动汇总': 'warning',
    '签发证件': 'success'
  }
  return typeMap[type] || 'info'
}

// 处理任务完成状态
const handleTaskComplete = async (index: number, completed: boolean) => {
  const todoId = props.todoData?.id
  if (!todoId) {
    ElMessage.error('待办ID无效')
    taskItems.value[index].completed = !completed
    return
  }

  try {
    // 使用新的API
    const response = await fetch(`/api/todo-system/todo/${todoId}/update-task-status`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        task_index: index,
        completed: completed
      })
    })

    if (!response.ok) {
      const errorText = await response.text().catch(() => '未知错误')
      console.error('更新状态失败:', response.status, errorText)
      throw new Error(`服务器错误(${response.status})`)
    }

    const result = await response.json().catch(() => null)
    if (result && result.status === 'success') {
      ElMessage.success(completed ? '任务已完成' : '任务已取消')
    } else {
      throw new Error(result?.detail || '响应格式错误')
    }

    // 计算当前完成数量
    const currentCompletedCount = taskItems.value.filter(t => t.completed).length
    const currentStatus = currentCompletedCount >= totalCount.value ? 'completed' : 'pending'

    // 触发状态变更事件，传递更新后的数据
    emit('status-changed', {
      todoId: todoId,
      completedCount: currentCompletedCount,
      totalCount: totalCount.value,
      status: currentStatus
    })
  } catch (error: any) {
    console.error('状态更新失败:', error)
    ElMessage.error(error.message || '状态更新失败')
    // 回滚UI状态
    taskItems.value[index].completed = !completed
  }
}

// 处理填报 - 支持通用模板
const handleFill = (task: any) => {
  const teacherIdRaw = props.todoData?.teacher_id
  const teacherId = typeof teacherIdRaw === 'string' ? parseInt(teacherIdRaw) : teacherIdRaw
  
  const tableName = task.target || task.目标
  const taskParams = task.params || task.参数 || {}
  
  const templateId = taskParams.template_id || task.template_id
  const templateType = taskParams.template_type || task.template_type || 'old'
  
  if (!templateId) {
    ElMessage.error('任务未配置模板ID')
    return
  }
  
  if (!teacherId) {
    ElMessage.error('教师ID无效')
    return
  }
  
  if (templateType === 'universal') {
    const encodedTemplateId = encodeURIComponent(templateId)
    router.push({
      path: `/universal-report/${encodedTemplateId}/${teacherId}`,
      query: { 
        teacher_name: props.todoData?.teacher_name || ''
      }
    })
  } else {
    const encodedTemplateId = encodeURIComponent(templateId)
    router.push({
      path: `/report-view/${encodedTemplateId}/${teacherId}`,
      query: { 
        mode: 'fill',
        table: tableName 
      }
    })
  }
  
  visible.value = false
}

// 处理跳转
const handleRedirect = (task: any) => {
  const url = task.url || task.target || task.目标 || task.link
  if (url) {
    window.open(url, '_blank')
  }
}

// 处理自动汇总
const handleAutoSum = (task: any) => {
  const params = task.参数 || task.params || {}
  ElMessage.info('自动汇总功能：' + (params.说明 || ''))
  // TODO: 实现自动汇总逻辑
}

// 处理签发证件
const handleIssue = (task: any) => {
  const params = task.参数 || task.params || {}
  const fields = params.字段 || []
  ElMessage.info('签发证件功能：' + (params.说明 || ''))
  // TODO: 实现签发证件逻辑
}

// 关闭处理
const handleClose = () => {
  emit('close')
}
</script>

<style scoped>
.checklist-drawer {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.task-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.task-item {
  padding: 16px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  background: #fff;
}

.task-item.completed {
  background: #e6f7ff;
  border-color: #91d5ff;
}

.task-item.completed .task-header {
  color: #1890ff;
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.task-title {
  font-weight: 500;
  margin-right: 8px;
}

.task-step {
  font-size: 12px;
  color: #909399;
  background: #f0f2f5;
  padding: 2px 8px;
  border-radius: 4px;
}

.task-desc {
  color: #606266;
  font-size: 14px;
  margin-bottom: 12px;
  line-height: 1.5;
}

.task-meta {
  margin-bottom: 12px;
}

.task-actions {
  display: flex;
  gap: 8px;
}

.progress-section {
  padding: 16px;
  background: #f5f7fa;
  border-radius: 8px;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.progress-title {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}

.progress-count {
  font-size: 13px;
  color: #606266;
}

/* 办理记录样式 */
.notes-section {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 16px;
  background: #fafafa;
}

.notes-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.notes-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}

.notes-list {
  max-height: 200px;
  overflow-y: auto;
  margin-bottom: 12px;
}

.note-item {
  display: flex;
  gap: 8px;
  padding: 8px 0;
  border-bottom: 1px dashed #eee;
  font-size: 13px;
}

.note-item:last-child {
  border-bottom: none;
}

.note-index {
  color: #909399;
  font-weight: 500;
  min-width: 20px;
}

.note-content {
  flex: 1;
  color: #303133;
  word-break: break-all;
}

.note-time {
  color: #c0c4cc;
  font-size: 12px;
  white-space: nowrap;
}

.notes-input {
  margin-top: 8px;
}

.drawer-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding-top: 16px;
  border-top: 1px solid #eee;
}

/* 任务头部（无复选框） */
.task-header-no-checkbox {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

/* 任务选项样式 */
.task-options {
  margin: 12px 0;
}

.option-items {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.option-item {
  padding: 16px;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  background: #fff;
}

.option-item:hover {
  border-color: #409eff;
  box-shadow: 0 2px 12px 0 rgba(64, 158, 255, 0.1);
}

.option-item.selected {
  border-color: #409eff;
  background: #ecf5ff;
}

.option-item.completed {
  border-color: #67c23a;
  background: #f0f9eb;
}

.option-radio {
  margin-bottom: 8px;
}

.option-radio :deep(.el-radio__label) {
  font-size: 14px;
  font-weight: 500;
}

.option-desc {
  font-size: 13px;
  color: #606266;
  padding-left: 24px;
  line-height: 1.5;
}
</style>
