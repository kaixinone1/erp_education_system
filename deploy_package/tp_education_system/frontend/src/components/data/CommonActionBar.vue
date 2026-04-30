<template>
  <div class="common-action-bar">
    <div class="action-group">
      <el-button type="primary" size="small" @click="handleCreate">
        <el-icon><Plus /></el-icon>
        新增
      </el-button>
      <el-button 
        type="primary" 
        size="small" 
        plain
        :disabled="!canEdit"
        @click="handleEdit"
      >
        <el-icon><Edit /></el-icon>
        编辑
      </el-button>
      <el-button 
        type="danger" 
        size="small" 
        plain
        :disabled="!canDelete"
        @click="handleDelete"
      >
        <el-icon><Delete /></el-icon>
        删除
      </el-button>
    </div>
    
    <div class="action-group">
      <el-button size="small" @click="handleImport">
        <el-icon><Download /></el-icon>
        导入
      </el-button>
      <el-button size="small" @click="handleExport">
        <el-icon><Upload /></el-icon>
        导出
      </el-button>
    </div>
    
    <div class="action-group">
      <el-button size="small" @click="handleRefresh">
        <el-icon><Refresh /></el-icon>
        刷新
      </el-button>
      <el-button 
        size="small" 
        :type="isFilterActive ? 'primary' : 'default'"
        @click="handleFilter"
      >
        <el-icon><Filter /></el-icon>
        筛选
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Plus, Edit, Delete, Upload, Download, Refresh, Filter } from '@element-plus/icons-vue'

// 组件属性
const props = defineProps<{
  selectedRows?: any[]
}>()

// 组件事件
const emit = defineEmits([
  'create', 'edit', 'delete', 'import', 'export', 'refresh', 'filter'
])

// 计算属性：是否可以编辑
const canEdit = computed(() => {
  return props.selectedRows && props.selectedRows.length === 1
})

// 计算属性：是否可以删除
const canDelete = computed(() => {
  return props.selectedRows && props.selectedRows.length > 0
})

// 计算属性：筛选是否激活
const isFilterActive = computed(() => {
  return false // 由父组件控制
})

// 事件处理
const handleCreate = () => {
  emit('create')
}

const handleEdit = () => {
  if (canEdit.value) {
    emit('edit')
  }
}

const handleDelete = () => {
  if (canDelete.value) {
    emit('delete')
  }
}

const handleImport = () => {
  emit('import')
}

const handleExport = () => {
  emit('export')
}

const handleRefresh = () => {
  emit('refresh')
}

const handleFilter = () => {
  emit('filter')
}
</script>

<style scoped>
.common-action-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #ebeef5;
}

.action-group {
  display: flex;
  gap: 8px;
}
</style>
