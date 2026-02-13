// 前端事件总线实现
// 用于组件间通信，特别是标签更新时的事件通知

import type { AnyFunction } from '@vue/shared'

// 预定义事件类型常量
export const EVENT_NAVIGATION_UPDATED = 'navigation_updated'
export const EVENT_TAGS_UPDATED = 'tags_updated'
export const EVENT_ACTIVE_TAG_CHANGED = 'active_tag_changed'
export const EVENT_ROUTE_CHANGED = 'route_changed'

interface EventBus {
  on(event: string, callback: AnyFunction): void
  off(event: string, callback: AnyFunction): void
  emit(event: string, data?: any): void
  once(event: string, callback: AnyFunction): void
  getEvents(): string[]
}

class EventBusImpl implements EventBus {
  private events: Record<string, AnyFunction[]> = {}

  on(event: string, callback: AnyFunction): void {
    if (!this.events[event]) {
      this.events[event] = []
    }
    this.events[event].push(callback)
  }

  off(event: string, callback: AnyFunction): void {
    if (this.events[event]) {
      this.events[event] = this.events[event].filter(cb => cb !== callback)
    }
  }

  emit(event: string, data?: any): void {
    if (this.events[event]) {
      this.events[event].forEach(callback => {
        try {
          callback(data)
        } catch (error) {
          console.error('Error in event callback:', error)
        }
      })
    }
  }

  once(event: string, callback: AnyFunction): void {
    const onceCallback = (data?: any) => {
      callback(data)
      this.off(event, onceCallback)
    }
    this.on(event, onceCallback)
  }

  getEvents(): string[] {
    return Object.keys(this.events)
  }
}

// 创建全局事件总线实例
export const eventBus = new EventBusImpl()

// 导出默认实例
export default eventBus
