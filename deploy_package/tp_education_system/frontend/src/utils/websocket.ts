/**
 * WebSocket服务 - 实时通知
 * 用于接收待办业务触发通知
 */

import { ElNotification } from 'element-plus'
import type { NotificationHandle } from 'element-plus'

interface TriggerNotification {
  id: number
  template_name: string
  trigger_reason: string
  teacher_name: string
  teacher_id: string
  created_at: string
}

interface WebSocketMessage {
  type: 'trigger_notification' | 'connection' | 'error'
  data?: TriggerNotification
  message?: string
}

class WebSocketService {
  private ws: WebSocket | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 3000
  private notificationHandlers: ((notification: TriggerNotification) => void)[] = []
  private activeNotifications: Map<number, NotificationHandle> = new Map()
  private isManualClose = false

  // WebSocket服务器地址
  private get wsUrl(): string {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = window.location.host
    return `${protocol}//${host}/api/ws/todo-notifications`
  }

  /**
   * 连接WebSocket
   */
  connect(): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      console.log('[WebSocket] 已连接')
      return
    }

    this.isManualClose = false

    try {
      this.ws = new WebSocket(this.wsUrl)

      this.ws.onopen = () => {
        console.log('[WebSocket] 连接成功')
        this.reconnectAttempts = 0
      }

      this.ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data)
          this.handleMessage(message)
        } catch (error) {
          console.error('[WebSocket] 消息解析失败:', error)
        }
      }

      this.ws.onclose = () => {
        console.log('[WebSocket] 连接关闭')
        if (!this.isManualClose) {
          this.attemptReconnect()
        }
      }

      this.ws.onerror = (error) => {
        console.error('[WebSocket] 连接错误:', error)
      }
    } catch (error) {
      console.error('[WebSocket] 连接失败:', error)
      this.attemptReconnect()
    }
  }

  /**
   * 断开连接
   */
  disconnect(): void {
    this.isManualClose = true
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }

  /**
   * 尝试重连
   */
  private attemptReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.log('[WebSocket] 达到最大重连次数，停止重连')
      return
    }

    this.reconnectAttempts++
    console.log(`[WebSocket] ${this.reconnectDelay}ms后尝试第${this.reconnectAttempts}次重连`)

    setTimeout(() => {
      this.connect()
    }, this.reconnectDelay)
  }

  /**
   * 处理接收到的消息
   */
  private handleMessage(message: WebSocketMessage): void {
    switch (message.type) {
      case 'trigger_notification':
        if (message.data) {
          this.showTriggerNotification(message.data)
          this.notifyHandlers(message.data)
        }
        break
      case 'connection':
        console.log('[WebSocket]', message.message)
        break
      case 'error':
        console.error('[WebSocket] 错误:', message.message)
        break
    }
  }

  /**
   * 显示触发通知弹窗
   */
  private showTriggerNotification(data: TriggerNotification): void {
    // 如果已存在该通知，先关闭
    if (this.activeNotifications.has(data.id)) {
      const existing = this.activeNotifications.get(data.id)
      existing?.close()
    }

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
        <div style="margin-top: 10px; display: flex; gap: 10px;">
          <button 
            onclick="window.dispatchEvent(new CustomEvent('confirm-todo-trigger', {detail: ${data.id}}))"
            style="padding: 5px 15px; background: #67C23A; color: white; border: none; border-radius: 4px; cursor: pointer;"
          >确认推送</button>
          <button 
            onclick="window.dispatchEvent(new CustomEvent('reject-todo-trigger', {detail: ${data.id}}))"
            style="padding: 5px 15px; background: #F56C6C; color: white; border: none; border-radius: 4px; cursor: pointer;"
          >暂不推送</button>
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
        console.error('[WebSocket] 通知处理器执行失败:', error)
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
}

// 单例导出
export const websocketService = new WebSocketService()
export type { TriggerNotification, WebSocketMessage }
