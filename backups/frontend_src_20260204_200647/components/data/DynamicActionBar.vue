<template>
  <div v-if="hasActions" class="dynamic-action-bar">
    <div class="action-label">专用功能：</div>
    <div class="action-buttons">
      <el-button
        v-for="action in availableActions"
        :key="action.key"
        :type="action.type || 'default'"
        :size="action.size || 'small'"
        :disabled="isActionDisabled(action)"
        @click="handleAction(action)"
      >
        <el-icon v-if="action.icon">
          <component :is="getIconComponent(action.icon)" />
        </el-icon>
        {{ action.label }}
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { 
  MagicStick, 
  CollectionTag, 
  Document, 
  Share,
  Printer,
  Download,
  Upload,
  Refresh,
  Setting
} from '@element-plus/icons-vue'

// 组件属性
const props = defineProps<{
  tableName?: string
  selectedRows?: any[]
}>()

// 组件事件
const emit = defineEmits(['action'])

// 可用操作列表
const availableActions = ref<any[]>([])

// 计算属性：是否有操作
const hasActions = computed(() => {
  return availableActions.value.length > 0
})

// 图标映射
const iconMap: Record<string, any> = {
  'MagicStick': MagicStick,
  'CollectionTag': CollectionTag,
  'Document': Document,
  'Share': Share,
  'Printer': Printer,
  'Download': Download,
  'Upload': Upload,
  'Refresh': Refresh,
  'Setting': Setting
}

// 获取图标组件
const getIconComponent = (iconName: string) => {
  return iconMap[iconName] || Setting
}

// 检查操作是否禁用
const isActionDisabled = (action: any) => {
  if (!action.requireSelection) {
    return false
  }
  return !props.selectedRows || props.selectedRows.length === 0
}

// 处理操作
const handleAction = (action: any) => {
  emit('action', action.key, {
    action: action,
    selectedRows: props.selectedRows
  })
}

// 加载专用操作配置
const loadActionConfig = async () => {
  try {
    // 从后端或配置文件加载
    const response = await fetch(`http://127.0.0.1:8000/api/data/ui-components/${props.tableName}`)
    
    if (response.ok) {
      const config = await response.json()
      availableActions.value = config.actions || []
    } else {
      // 使用默认配置
      availableActions.value = getDefaultActions()
    }
  } catch (error) {
    console.error('加载操作配置失败:', error)
    // 使用默认配置
    availableActions.value = getDefaultActions()
  }
}

// 获取默认操作
const getDefaultActions = () => {
  return [
    {
      key: 'smartFill',
      label: '智能填充',
      icon: 'MagicStick',
      type: 'primary',
      requireSelection: false
    },
    {
      key: 'batchTag',
      label: '批量打标签',
      icon: 'CollectionTag',
      type: 'default',
      requireSelection: true
    },
    {
      key: 'generateReport',
      label: '生成报表',
      icon: 'Document',
      type: 'success',
      requireSelection: false
    },
    {
      key: 'batchExport',
      label: '批量导出',
      icon: 'Download',
      type: 'default',
      requireSelection: true
    }
  ]
}

// 监听表名变化
watch(() => props.tableName, () => {
  if (props.tableName) {
    loadActionConfig()
  }
})

// 组件挂载
onMounted(() => {
  if (props.tableName) {
    loadActionConfig()
  } else {
    availableActions.value = getDefaultActions()
  }
})
</script>

<style scoped>
.dynamic-action-bar {
  display: flex;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #ebeef5;
  gap: 15px;
}

.action-label {
  font-size: 13px;
  color: #909399;
  white-space: nowrap;
}

.action-buttons {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
</style>
