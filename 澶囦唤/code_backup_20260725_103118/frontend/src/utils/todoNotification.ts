/**
 * 待办业务通知服务
 * 支持WebSocket和HTTP轮询两种方式
 */

import { ElNotification } from 'element-plus'
import type { NotificationHandle } from 'element-plus'
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

interface TriggerNotification {
  id: number
  template_name: string
  trigger_reason: string
  teacher_name: string
  teacher_id: string
  created_at: string
}

interface PendingTrigger {
  id: number
  template_id: number
  template_name: string
  trigger_type: string
  trigger_reason: string
  teacher_id: string
  teacher_name: string
  trigger_data: Record<string, any>
  status: 'pending' | 'confirmed' | 'rejected'
  created_at: string
}

class TodoNotificationService {
  private pollingInterval: number | null = null
  private pollingDelay = 5000 // 5秒轮询一次
  private notificationHandlers: ((notification: TriggerNotification) => void)[] = []
  private activeNotifications: Map<number, NotificationHandle> = new Map()
  private isPolling = false

  /**
   * 启动通知服务（HTTP轮询方式）
   */
  start(): void {
    if (this.isPolling) return

    this.isPolling = true
    this.pollPendingTriggers()
    console.log('[TodoNotification] 通知服务已启动')
  }

  /**
   * 停止通知服务
   */
  stop(): void {
    this.isPolling = false
    if (this.pollingInterval) {
      clearTimeout(this.pollingInterval)
      this.pollingInterval = null
    }
    console.log('[TodoNotification] 通知服务已停止')
  }

  /**
   * 轮询待处理的触发器
   */
  private async pollPendingTriggers(): Promise<void> {
    if (!this.isPolling) return

    try {
      const response = await axios.get(`${API_BASE_URL}/api/todo-system/pending-triggers`)
      const triggers: PendingTrigger[] = response.data.triggers || []

      // 显示新的触发通知
      triggers.forEach(trigger => {
        if (!this.activeNotifications.has(trigger.id)) {
          this.showTriggerNotification({
            id: trigger.id,
            template_name: trigger.template_name,
            trigger_reason: trigger.trigger_reason,
            teacher_name: trigger.teacher_name,
            teacher_id: trigger.teacher_id,
            created_at: trigger.created_at
          })
        }
      })
    } catch (error) {
      console.error('[TodoNotification] 轮询失败:', error)
    }

    // 继续下一轮轮询
    if (this.isPolling) {
      this.pollingInterval = window.setTimeout(() => {
        this.pollPendingTriggers()
      }, this.pollingDelay)
    }
  }

  /**
   * 显示触发通知弹窗
   */
  private showTriggerNotification(data: TriggerNotification): void {
    const notification = ElNotification({
      title: '待办业务触发提醒',
      dangerouslyUseHTMLString: true,
      message: `
        <div style="padding: 10px 0;">
          <p style="margin: 5px 0; font-weight: bold; color: #409EFF;">${data.template_name}</p>
          <p style="margin: 5px 0; color: #606266;">触发原因：${data.trigger_reason}</p>
          <p style="margin: 5px 0; color: #606266;">相关人员：${data.teacher_name} (${data.teacher_id})</p>
          <p style="margin: 5px 0; color: #909399; font-size: 12px;">触发时间：${new Date(data.created_at).toLocaleString('zh-CN')}</p>
        </div>
      `,
      type: 'info',
      duration: 0,
      position: 'top-right',
      showClose: true,
      onClose: () => {
        this.activeNotifications.delete(data.id)
      }
    })

    this.activeNotifications.set(data.id, notification)
    this.notifyHandlers(data)

    // 触发全局事件，供组件监听
    window.dispatchEvent(new CustomEvent('todo-trigger-detected', { detail: data }))
  }

  /**
   * 确认触发（推送待办）
   */
  async confirmTrigger(triggerId: number, operatorId?: string): Promise<boolean> {
    try {
      await axios.post(`${API_BASE_URL}/api/todo-system/confirm-trigger`, {
        trigger_id: triggerId,
        operator_id: operatorId || 'system'
      })

      // 关闭对应的通知
      this.closeNotification(triggerId)
      console.log('[TodoNotification] 触发已确认:', triggerId)
      return true
    } catch (error) {
      console.error('[TodoNotification] 确认触发失败:', error)
      return false
    }
  }

  /**
   * 拒绝触发（暂不推送）
   */
  async rejectTrigger(triggerId: number, reason?: string): Promise<boolean> {
    try {
      await axios.post(`${API_BASE_URL}/api/todo-system/reject-trigger`, {
        trigger_id: triggerId,
        reject_reason: reason || '用户暂不处理'
      })

      // 关闭对应的通知
      this.closeNotification(triggerId)
      console.log('[TodoNotification] 触发已拒绝:', triggerId)
      return true
    } catch (error) {
      console.error('[TodoNotification] 拒绝触发失败:', error)
      return false
    }
  }

  /**
   * 注册通知处理器
   */
  onNotification(handler: (notification: TriggerNotification) => void): void {
    this.notificationHandlers.push(handler)
  }

  /**
   * 移除通知处理器
   */
  offNotification(handler: (notification: TriggerNotification) => void): void {
    const index = this.notificationHandlers.indexOf(handler)
    if (index > -1) {
      this.notificationHandlers.splice(index, 1)
    }
  }

  /**
   * 通知所有处理器
   */
  private notifyHandlers(notification: TriggerNotification): void {
    this.notificationHandlers.forEach(handler => {
      try {
        handler(notification)
      } catch (error) {
        console.error('[TodoNotification] 通知处理器执行失败:', error)
      }
    })
  }

  /**
   * 关闭指定通知
   */
  closeNotification(triggerId: number): void {
    const notification = this.activeNotifications.get(triggerId)
    if (notification) {
      notification.close()
      this.activeNotifications.delete(triggerId)
    }
  }

  /**
   * 关闭所有通知
   */
  closeAllNotifications(): void {
    this.activeNotifications.forEach(notification => {
      notification.close()
    })
    this.activeNotifications.clear()
  }

  /**
   * 获取待处理的触发列表
   */
  async getPendingTriggers(): Promise<PendingTrigger[]> {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/todo-system/pending-triggers`)
      return response.data.triggers || []
    } catch (error) {
      console.error('[TodoNotification] 获取待处理触发失败:', error)
      return []
    }
  }

  /**
   * 获取待办列表
   */
  async getTodoList(params?: {
    status?: string
    template_id?: number
    page?: number
    page_size?: number
  }): Promise<{ todos: any[]; total: number }> {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/todo-system/todo-list`, { params })
      return {
        todos: response.data.todos || [],
        total: response.data.total || 0
      }
    } catch (error) {
      console.error('[TodoNotification] 获取待办列表失败:', error)
      return { todos: [], total: 0 }
    }
  }

  /**
   * 创建自定义待办
   */
  async createCustomTodo(data: {
    title: string
    description?: string
    deadline?: string
    operator_id?: string
  }): Promise<boolean> {
    try {
      await axios.post(`${API_BASE_URL}/api/todo-system/custom-todo`, data)
      return true
    } catch (error) {
      console.error('[TodoNotification] 创建自定义待办失败:', error)
      return false
    }
  }
}

// 单例导出
export const todoNotificationService = new TodoNotificationService()
export type { TriggerNotification, PendingTrigger }
