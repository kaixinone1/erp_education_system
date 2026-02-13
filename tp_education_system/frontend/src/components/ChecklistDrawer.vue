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
          :class="{ completed: task.完成状态 }"
        >
          <div class="task-header">
            <el-checkbox
              v-model="task.完成状态"
              @change="(val) => handleTaskComplete(index, val)"
            >
              {{ task.标题 }}
            </el-checkbox>
            <el-tag v-if="task.类型" size="small" :type="getTaskType(task.类型)">
              {{ task.类型 }}
            </el-tag>
          </div>
          <div class="task-desc" v-if="task.说明">{{ task.说明 }}</div>
          <div class="task-actions">
            <el-button
              v-if="task.类型 === '内部表'"
              type="primary"
              size="small"
              @click="handleFill(task)"
            >
              填报
            </el-button>
            <el-button
              v-else-if="task.类型 === '外部链接'"
              type="info"
              size="small"
              @click="handleRedirect(task)"
            >
              打开
            </el-button>
          </div>
          </div>
      </div>
    </div>
  </el-drawer>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()

// Props
const props = defineProps<{
  modelValue: boolean
  todoData?: any
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
  (e: 'close'): void
}>()

// 可见性
const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

// 标题
const title = computed(() => props.todoData?.checklist_name || '业务清单')

// 任务项 - 从 todoData 中获取
const taskItems = ref<any[]>([])

// 统计计算
const totalCount = computed(() => taskItems.value.length)
const completedCount = computed(() => taskItems.value.filter(t => t.完成状态).length)
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
  let items = newTodoData?.task_items || []
  // 如果 task_items 是 JSON 字符串，解析为数组
  if (typeof items === 'string') {
    try {
      items = JSON.parse(items)
    } catch (e) {
      console.error('解析 task_items 失败:', e)
      items = []
    }
  }
  taskItems.value = items
}, { immediate: true })

// 获取任务类型样式
const getTaskType = (type: string) => {
  const typeMap: Record<string, string> = {
    '内部表': 'primary',
    '外部链接': 'info',
    '自动汇总': 'warning',
    '签发证件': 'success'
  }
  return typeMap[type] || 'info'
}

// 处理任务完成状态
const handleTaskComplete = async (index: number, completed: boolean) => {
  try {
    const response = await fetch(`/api/todo-work/update-status`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        todo_id: props.todoData?.id,
        task_index: index,
        completed: completed
      })
    })
    if (!response.ok) throw new Error('更新失败')
    ElMessage.success(completed ? '任务已完成' : '任务已取消')
  } catch (error) {
    ElMessage.error('状态更新失败')
    taskItems.value[index].完成状态 = !completed
  }
}

// 处理填报 - 直接使用 task 中的 template_id
const handleFill = (task: any) => {
  const teacherId = props.todoData?.teacher_id
  const tableName = task.目标
  const taskParams = task.参数 || {}
  
  // 直接从任务参数获取 template_id
  const templateId = taskParams.template_id
  
  if (!templateId) {
    ElMessage.error('任务未配置模板ID')
    return
  }
  
  if (!teacherId) {
    ElMessage.error('教师ID无效')
    return
  }
  
  // 跳转到报表页面
  const encodedTemplateId = encodeURIComponent(templateId)
  router.push({
    path: `/report-view/${encodedTemplateId}/${teacherId}`,
    query: { 
      mode: 'fill',
      table: tableName 
    }
  })
  
  visible.value = false
}

// 处理跳转
const handleRedirect = (task: any) => {
  const url = task.目标
  if (url) {
    window.open(url, '_blank')
  }
}

// 关闭处理
const handleClose = () => {
  emit('close')
}
</script>

<style scoped>
.checklist-drawer {
  padding: 20px;
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

.task-desc {
  color: #606266;
  font-size: 14px;
  margin-bottom: 12px;
  line-height: 1.5;
}

.task-actions {
  display: flex;
  gap: 8px;
}

.progress-section {
  margin-bottom: 20px;
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
</style>
