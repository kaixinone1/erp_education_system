<template>
  <div class="tags-view-container">
    <div class="tags-view-wrapper">
      <el-tag
        v-for="tag in tagsList"
        :key="tag.path"
        :closable="tag.path !== '/'"
        :effect="activeTag === tag.path ? 'dark' : 'plain'"
        :class="{'active-tag': activeTag === tag.path}"
        @click="handleTagClick(tag)"
        @close="handleTagClose(tag)"
        class="tag-item"
      >
        <span class="tag-content">
          {{ tag.title }}
        </span>
      </el-tag>
    </div>
    <div class="tags-view-actions">
      <el-dropdown @command="handleDropdownCommand">
        <el-button size="small">
          <el-icon><More /></el-icon>
        </el-button>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="refresh">
              <el-icon><Refresh /></el-icon>
              刷新当前
            </el-dropdown-item>
            <el-dropdown-item command="closeOther">
              <el-icon><Close /></el-icon>
              关闭其他
            </el-dropdown-item>
            <el-dropdown-item command="closeAll">
              <el-icon><Close /></el-icon>
              关闭所有
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </div>
</template>

<script setup lang="ts">
import { watch, ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { More, Refresh, Close } from '@element-plus/icons-vue'
import { storeToRefs } from 'pinia'
import { useTagsStore } from '@/store/tags'
import { eventBus, EVENT_TAGS_UPDATED, EVENT_ACTIVE_TAG_CHANGED } from '@/utils/eventBus'

const route = useRoute()
const router = useRouter()
const tagsStore = useTagsStore()
const { tagsList, activeTag } = storeToRefs(tagsStore)

// 元模块配置 - 仅系统管理和模块管理
const getMetaModules = () => [
  {
    id: "system",
    title: "系统管理",
    icon: "Setting",
    path: "/system",
    type: "module",
    children: [
      {
        id: "system-modules",
        title: "模块管理",
        icon: "Grid",
        path: "/system/module-mgt",
        type: "component",
        component: "Modules",
        api_endpoint: "/api/data/modules"
      }
    ]
  }
]

// 导航模块数据
const navigationModules = ref([])

// 从后端API获取导航数据
const loadNavigationData = async () => {
  try {
    const response = await fetch('http://127.0.0.1:8000/api/navigation-admin/tree')
    if (response.ok) {
      const data = await response.json()
      if (data.modules && data.modules.length > 0) {
        navigationModules.value = data.modules
      }
    } else {
      console.error('获取导航数据失败:', response.status)
      // 使用默认数据
      navigationModules.value = defaultNavigationData
    }
  } catch (error) {
    console.error('加载导航数据失败:', error)
    // 使用默认数据
    // 只有在没有数据时才使用元模块
    if (navigationModules.value.length === 0) {
      navigationModules.value = getMetaModules()
    }
  }
}

// 根据路径查找导航节点标题
const findTitleByPath = (path: string): string => {
  // 首页特殊处理
  if (path === '/') {
    return '首页'
  }
  
  // 递归查找函数
  const search = (modules: any[]): string => {
    for (const module of modules) {
      // 精确匹配
      if (module.path === path) {
        return module.title
      }
      
      // 递归查找子节点
      if (module.children && module.children.length > 0) {
        const found = search(module.children)
        if (found) {
          return found
        }
      }
    }
    return ''
  }
  
  const result = search(navigationModules.value)
  console.log('查找路径标题:', path, '结果:', result)
  return result
}

// 检查路径是否对应数据节点或功能节点
const isFunctionalNode = (path: string): boolean => {
  // 首页总是显示
  if (path === '/') {
    return true
  }
  
  // 递归查找函数
  const search = (modules: any[]): boolean => {
    for (const module of modules) {
      if (module.path === path) {
        // 只返回数据节点和功能节点
        return module.type === 'component' || module.type === 'report'
      }
      if (module.children && module.children.length > 0) {
        const found = search(module.children)
        if (found) {
          return found
        }
      }
    }
    return false
  }
  return search(navigationModules.value)
}

// 监听路由变化，添加标签
watch(
  () => route.fullPath,
  async () => {
    // 确保导航数据已加载
    if (navigationModules.value.length === 0) {
      await loadNavigationData()
    }
    
    // 检查是否为功能节点
    const isFunctionNode = isFunctionalNode(route.path)
    
    // 只添加功能节点到标签行
    if (isFunctionNode || route.path === '/') {
      // 尝试从导航数据中查找标题
      const navTitle = findTitleByPath(route.path)
      
      tagsStore.addTag({
        path: route.path,
        title: navTitle || route.meta.title as string || '页面',
        icon: route.meta.icon as string || ''
      })
    }
  },
  { immediate: true }
)

// 组件挂载时加载导航数据并添加事件监听
onMounted(() => {
  loadNavigationData()
  eventBus.on(EVENT_TAGS_UPDATED, handleTagsUpdated)
  eventBus.on(EVENT_ACTIVE_TAG_CHANGED, handleActiveTagChanged)
})

// 组件卸载时移除事件监听
onUnmounted(() => {
  eventBus.off(EVENT_TAGS_UPDATED, handleTagsUpdated)
  eventBus.off(EVENT_ACTIVE_TAG_CHANGED, handleActiveTagChanged)
})

const handleTagClick = (tag: any) => {
  router.push(tag.path)
}

const handleTagClose = (tag: any) => {
  // 保存当前活跃标签
  const currentActiveTag = activeTag.value
  
  // 移除标签
  tagsStore.removeTag(tag.path)
  
  // 如果关闭的是当前活跃标签
  if (tag.path === currentActiveTag) {
    // 找到新的活跃标签（标签列表的最后一个）
    const newActiveTag = tagsList.value[tagsList.value.length - 1]
    if (newActiveTag) {
      // 立即跳转到新的活跃标签
      router.push(newActiveTag.path)
    }
  }
}

const handleDropdownCommand = (command: string) => {
  switch (command) {
    case 'refresh':
      // 刷新当前页面
      router.go(0)
      break
    case 'closeOther':
      tagsStore.closeOtherTags(activeTag.value)
      break
    case 'closeAll':
      tagsStore.closeAllTags()
      break
  }
}

// 检查并关闭已删除模块的标签
const checkAndCloseDeletedModuleTags = () => {
  // 获取所有有效的路径
  const validPaths = new Set<string>()
  const collectPaths = (modules: any[]) => {
    for (const module of modules) {
      if (module.path) {
        validPaths.add(module.path)
      }
      if (module.children && module.children.length > 0) {
        collectPaths(module.children)
      }
    }
  }
  collectPaths(navigationModules.value)
  
  // 首页总是有效的
  validPaths.add('/')
  
  // 检查每个标签，关闭已删除的
  const tagsToClose = tagsList.value.filter(tag => !validPaths.has(tag.path))
  
  tagsToClose.forEach(tag => {
    console.log('关闭已删除模块的标签:', tag.path)
    tagsStore.removeTag(tag.path)
  })
  
  // 如果当前活跃标签被关闭了，跳转到首页
  if (tagsToClose.some(tag => tag.path === activeTag.value)) {
    router.push('/')
  }
}

// 事件监听器回调
const handleTagsUpdated = (data: any) => {
  console.log('标签已更新:', data)
  // 当导航数据更新时，检查并关闭已删除模块的标签
  if (data && data.type === 'navigation_updated') {
    checkAndCloseDeletedModuleTags()
  }
}

const handleActiveTagChanged = (data: any) => {
  console.log('活跃标签已变更:', data)
}
</script>

<style scoped>
.tags-view-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 40px;
  background-color: #ffffff;
  border-bottom: 1px solid #e6e8eb;
  padding: 0 10px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.tags-view-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
  overflow-x: auto;
  flex: 1;
}

.tags-view-wrapper::-webkit-scrollbar {
  height: 4px;
}

.tags-view-wrapper::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 2px;
}

.tags-view-wrapper::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 2px;
}

.tags-view-wrapper::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

.tag-item {
  cursor: pointer;
  transition: all 0.3s ease;
}

.tag-item:hover {
  border-color: #409eff;
}

.active-tag {
  background-color: #409eff;
  border-color: #409eff;
  color: #ffffff;
}

.tag-content {
  display: flex;
  align-items: center;
  gap: 6px;
}

.tags-view-actions {
  display: flex;
  align-items: center;
  margin-left: 10px;
}
</style>
