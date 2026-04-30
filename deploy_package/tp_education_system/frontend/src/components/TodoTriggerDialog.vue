<template>
  <div>
    <!-- 触发确认对话框 -->
    <el-dialog
      v-model="visible"
      title="待办业务触发确认"
      width="600px"
      :close-on-click-modal="false"
      :show-close="false"
      class="todo-trigger-dialog"
    >
      <div class="trigger-content">
        <div class="trigger-header">
          <el-icon class="trigger-icon"><Bell /></el-icon>
          <div class="trigger-title">
            <h3>{{ currentTrigger?.template_name }}</h3>
            <el-tag :type="getTriggerTypeTag(currentTrigger?.trigger_type)">
              {{ getTriggerTypeText(currentTrigger?.trigger_type) }}
            </el-tag>
          </div>
        </div>

        <el-divider />

        <div class="trigger-info">
          <el-descriptions :column="1" border>
            <el-descriptions-item label="触发原因">
              {{ currentTrigger?.trigger_reason }}
            </el-descriptions-item>
            <el-descriptions-item label="相关人员">
              <div class="teacher-info">
                <span class="teacher-name">{{ currentTrigger?.teacher_name }}</span>
                <span class="teacher-id">({{ currentTrigger?.teacher_id }})</span>
              </div>
            </el-descriptions-item>
            <el-descriptions-item label="触发时间">
              {{ formatDateTime(currentTrigger?.created_at) }}
            </el-descriptions-item>
            <el-descriptions-item label="待办详情" v-if="currentTrigger?.trigger_data?.description">
              {{ currentTrigger.trigger_data.description }}
            </el-descriptions-item>
          </el-descriptions>
        </div>

        <div class="trigger-tasks" v-if="currentTrigger?.trigger_data?.task_flow?.length">
          <h4>任务流程预览</h4>
          <el-timeline>
            <el-timeline-item
              v-for="(task, index) in currentTrigger.trigger_data.task_flow"
              :key="index"
              :type="task.type || 'primary'"
              :icon="getTaskIcon(task.type)"
            >
              <div class="task-item">
                <span class="task-name">{{ task.name }}</span>
                <span class="task-assignee" v-if="task.assignee">
                  负责人：{{ task.assignee }}
                </span>
              </div>
            </el-timeline-item>
          </el-timeline>
        </div>

        <div class="trigger-actions">
          <p class="action-hint">
            <el-icon><InfoFilled /></el-icon>
            确认后将推送该待办业务到待办列表，拒绝后可在"待办工作"页面重新确认
          </p>
        </div>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button 
            type="danger" 
            @click="handleReject"
            :loading="loading"
          >
            <el-icon><CircleClose /></el-icon>
            暂不推送
          </el-button>
          <el-button 
            type="primary" 
            @click="handleConfirm"
            :loading="loading"
          >
            <el-icon><CircleCheck /></el-icon>
            确认推送
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 拒绝原因输入对话框 -->
    <el-dialog
      v-model="rejectVisible"
      title="请输入拒绝原因"
      width="400px"
      append-to-body
    >
      <el-input
        v-model="rejectReason"
        type="textarea"
        :rows="3"
        placeholder="请输入暂不推送的原因（可选）"
      />
      <template #footer>
        <el-button @click="rejectVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmReject" :loading="loading">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Bell,
  InfoFilled,
  CircleCheck,
  CircleClose,
  User,
  Document,
  Check,
  Timer
} from '@element-plus/icons-vue'
import { todoNotificationService, type PendingTrigger } from '@/utils/todoNotification'

const visible = ref(false)
const rejectVisible = ref(false)
const loading = ref(false)
const currentTrigger = ref<PendingTrigger | null>(null)
const rejectReason = ref('')
const pendingTriggers = ref<PendingTrigger[]>([])
const currentIndex = ref(0)

// 获取触发类型标签样式
const getTriggerTypeTag = (type?: string) => {
  const typeMap: Record<string, string> = {
    'retirement': 'warning',
    'death': 'danger',
    'octogenarian': 'success',
    'custom': 'info'
  }
  return typeMap[type || ''] || 'info'
}

// 获取触发类型文本
const getTriggerTypeText = (type?: string) => {
  const textMap: Record<string, string> = {
    'retirement': '退休提醒',
    'death': '死亡登记',
    'octogenarian': '80岁补贴',
    'custom': '自定义待办'
  }
  return textMap[type || ''] || '其他'
}

// 获取任务图标
const getTaskIcon = (type?: string) => {
  const iconMap: Record<string, any> = {
    'approval': User,
    'document': Document,
    'complete': Check,
    'default': Timer
  }
  return iconMap[type || ''] || Timer
}

// 格式化日期时间
const formatDateTime = (dateStr?: string) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 显示触发对话框
const showTrigger = (trigger: PendingTrigger) => {
  currentTrigger.value = trigger
  visible.value = true
}

// 处理确认
const handleConfirm = async () => {
  if (!currentTrigger.value) return

  loading.value = true
  try {
    const success = await todoNotificationService.confirmTrigger(
      currentTrigger.value.id,
      'current_user'
    )
    if (success) {
      ElMessage.success('已确认推送待办业务')
      visible.value = false
      // 检查是否还有更多待处理触发
      checkNextTrigger()
    } else {
      ElMessage.error('推送失败，请重试')
    }
  } catch (error) {
    ElMessage.error('操作失败：' + error)
  } finally {
    loading.value = false
  }
}

// 处理拒绝
const handleReject = () => {
  rejectReason.value = ''
  rejectVisible.value = true
}

// 确认拒绝
const confirmReject = async () => {
  if (!currentTrigger.value) return

  loading.value = true
  try {
    const success = await todoNotificationService.rejectTrigger(
      currentTrigger.value.id,
      rejectReason.value
    )
    if (success) {
      ElMessage.info('已暂不推送该待办业务')
      rejectVisible.value = false
      visible.value = false
      // 检查是否还有更多待处理触发
      checkNextTrigger()
    } else {
      ElMessage.error('操作失败，请重试')
    }
  } catch (error) {
    ElMessage.error('操作失败：' + error)
  } finally {
    loading.value = false
  }
}

// 检查下一个触发
const checkNextTrigger = async () => {
  // 从列表中移除当前处理完的触发
  pendingTriggers.value = pendingTriggers.value.filter(
    t => t.id !== currentTrigger.value?.id
  )

  if (pendingTriggers.value.length > 0) {
    // 显示下一个触发
    currentIndex.value = 0
    showTrigger(pendingTriggers.value[0])
  } else {
    // 重新获取待处理触发列表
    const triggers = await todoNotificationService.getPendingTriggers()
    if (triggers.length > 0) {
      pendingTriggers.value = triggers
      currentIndex.value = 0
      showTrigger(triggers[0])
    }
  }
}

// 监听全局触发事件
const handleTriggerEvent = (event: CustomEvent<PendingTrigger>) => {
  const trigger = event.detail
  // 添加到待处理列表
  if (!pendingTriggers.value.find(t => t.id === trigger.id)) {
    pendingTriggers.value.push(trigger)
  }
  // 如果当前没有显示对话框，则显示
  if (!visible.value) {
    showTrigger(trigger)
  }
}

onMounted(() => {
  // 监听全局触发事件
  window.addEventListener('todo-trigger-detected', handleTriggerEvent as EventListener)

  // 启动通知服务
  todoNotificationService.start()

  // 立即检查一次待处理触发
  todoNotificationService.getPendingTriggers().then(triggers => {
    if (triggers.length > 0) {
      pendingTriggers.value = triggers
      showTrigger(triggers[0])
    }
  })
})

onUnmounted(() => {
  window.removeEventListener('todo-trigger-detected', handleTriggerEvent as EventListener)
  todoNotificationService.stop()
})
</script>

<style scoped>
.todo-trigger-dialog :deep(.el-dialog__header) {
  background: linear-gradient(135deg, #409EFF 0%, #66b1ff 100%);
  margin-right: 0;
  padding: 20px;
}

.todo-trigger-dialog :deep(.el-dialog__title) {
  color: white;
  font-weight: bold;
}

.trigger-content {
  padding: 10px 0;
}

.trigger-header {
  display: flex;
  align-items: center;
  gap: 15px;
}

.trigger-icon {
  font-size: 40px;
  color: #409EFF;
}

.trigger-title {
  flex: 1;
}

.trigger-title h3 {
  margin: 0 0 8px 0;
  font-size: 18px;
  color: #303133;
}

.trigger-info {
  margin: 20px 0;
}

.teacher-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.teacher-name {
  font-weight: bold;
  color: #409EFF;
}

.teacher-id {
  color: #909399;
  font-size: 12px;
}

.trigger-tasks {
  margin: 20px 0;
  padding: 15px;
  background: #f5f7fa;
  border-radius: 8px;
}

.trigger-tasks h4 {
  margin: 0 0 15px 0;
  color: #303133;
}

.task-item {
  display: flex;
  flex-direction: column;
}

.task-name {
  font-weight: bold;
  color: #303133;
}

.task-assignee {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.trigger-actions {
  margin-top: 20px;
  padding: 15px;
  background: #fdf6ec;
  border-radius: 8px;
  border-left: 4px solid #e6a23c;
}

.action-hint {
  margin: 0;
  color: #e6a23c;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 15px;
}
</style>
