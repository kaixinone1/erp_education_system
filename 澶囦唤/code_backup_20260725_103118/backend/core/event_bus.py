from typing import Dict, List, Callable, Any

# 预定义事件类型常量
EVENT_NAVIGATION_UPDATED = 'navigation_updated'
EVENT_SCHEMA_UPDATED = 'schema_updated'
EVENT_UI_COMPONENTS_UPDATED = 'ui_components_updated'
EVENT_REPORT_DEFINITIONS_UPDATED = 'report_definitions_updated'
EVENT_CONFIG_RELOADED = 'config_reloaded'

class EventBus:
    """事件总线 - 系统的神经系统
    
    实现简单的事件发布-订阅模式，用于组件间通信
    """
    
    def __init__(self):
        """初始化事件总线"""
        self._subscribers: Dict[str, List[Callable]] = {}
    
    def subscribe(self, event_type: str, callback: Callable[[Any], None]) -> None:
        """订阅事件
        
        Args:
            event_type: 事件类型
            callback: 回调函数，接收事件数据
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        
        if callback not in self._subscribers[event_type]:
            self._subscribers[event_type].append(callback)
    
    def unsubscribe(self, event_type: str, callback: Callable[[Any], None]) -> None:
        """取消订阅
        
        Args:
            event_type: 事件类型
            callback: 要取消的回调函数
        """
        if event_type in self._subscribers:
            if callback in self._subscribers[event_type]:
                self._subscribers[event_type].remove(callback)
    
    def publish(self, event_type: str, data: Any = None) -> None:
        """发布事件
        
        Args:
            event_type: 事件类型
            data: 事件数据
        """
        if event_type in self._subscribers:
            for callback in self._subscribers[event_type]:
                try:
                    callback(data)
                except Exception as e:
                    print(f"Error in event callback: {e}")
    
    def get_subscribers_count(self, event_type: str) -> int:
        """获取事件订阅者数量
        
        Args:
            event_type: 事件类型
        
        Returns:
            订阅者数量
        """
        if event_type in self._subscribers:
            return len(self._subscribers[event_type])
        return 0
    
    def get_all_event_types(self) -> List[str]:
        """获取所有事件类型
        
        Returns:
            事件类型列表
        """
        return list(self._subscribers.keys())

# 创建全局事件总线实例
event_bus = EventBus()
