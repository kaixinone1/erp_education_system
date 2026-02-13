<template>
  <div class="sidebar-container" :style="{ width: isCollapse ? '64px' : '200px' }">
    <el-menu
      ref="menu"
      :default-active="activeMenu"
      class="sidebar-menu"
      :collapse="isCollapse"
      :router="false"
      :unique-opened="true"
      @select="handleMenuSelect"
      @collapse="handleCollapse"
      @expand="handleExpand"
    >
      <!-- 首页 -->
      <el-menu-item index="/" @click="handleHomeClick">
        <span v-if="!isCollapse">首页</span>
      </el-menu-item>
      
      <!-- 动态渲染导航菜单 -->
      <SidebarItem
        v-for="module in navigationModules"
        :key="module.id"
        :item="module"
        :is-collapse="isCollapse"
      />
    </el-menu>
    <el-button
      circle
      class="collapse-toggle-btn"
      @click="toggleCollapse"
    >
      <el-icon><ArrowLeft v-if="!isCollapse" /><ArrowRight v-else /></el-icon>
    </el-button>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { School, ArrowLeft, ArrowRight } from '@element-plus/icons-vue'
import { useAppStore } from '@/store/app'
import SidebarItem from './SidebarItem.vue'

interface MenuModule {
  id: string
  title: string
  path?: string
  children?: MenuModule[]
}

const route = useRoute()
const router = useRouter()
const appStore = useAppStore()
// 导航模块数据 - 从后端API加载
const navigationModules = ref<MenuModule[]>([])
const loadError = ref<string>('')

const isCollapse = computed(() => appStore.sidebarCollapse)

const activeMenu = computed(() => {
  const path = route.path
  return path || '/'
})

const toggleCollapse = () => {
  appStore.setSidebarCollapse(!isCollapse.value)
}

const menu = ref()

const handleMenuSelect = (key: string, keyPath: string[]) => {
  console.log('菜单选择:', key, keyPath)
}

const handleCollapse = (collapse: boolean) => {
  appStore.setSidebarCollapse(collapse)
}

const handleExpand = (key: string, keyPath: string[]) => {
  console.log('菜单展开:', key, keyPath)
  // 展开一个菜单时，折叠其他菜单
  if (menu.value) {
    // 使用Element Plus的API获取已展开的菜单
    const openedMenus = menu.value.store?.openedMenus || []
    // 如果有多个已展开的菜单，只保留当前展开的
    if (openedMenus.length > 1) {
      // 折叠其他所有菜单
      openedMenus.forEach((menuKey: string) => {
        if (menuKey !== key) {
          // 使用Element Plus的API折叠菜单
          menu.value?.collapse(menuKey)
        }
      })
    }
  }
}

const handleHomeClick = () => {
  router.push('/')
}

// 存储上次导航数据的哈希值，用于检测变化
let lastNavigationHash = ''

// 获取元模块配置（仅用于首次启动或文件损坏时）
const getMetaModules = (): MenuModule[] => [
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

const loadNavigationData = async () => {
  try {
    loadError.value = ''
    // 从后端API获取导航数据
    const response = await fetch('/api/navigation-admin/tree')
    if (response.ok) {
      const data = await response.json()
      const currentModules = data.modules || []
      
      // 如果后端返回空数据，使用元模块
      if (currentModules.length === 0) {
        navigationModules.value = getMetaModules()
        loadError.value = '导航数据为空，已加载默认元模块'
      } else {
        // 计算当前导航数据的哈希值
        const currentHash = JSON.stringify(currentModules)
        
        // 检查数据是否有变化
        if (currentHash !== lastNavigationHash) {
          navigationModules.value = currentModules
          lastNavigationHash = currentHash
          console.log('导航数据已更新')
        }
      }
    } else {
      console.error('获取导航数据失败:', response.status)
      loadError.value = `获取导航数据失败: ${response.status}`
      // 只有在没有数据时才使用元模块
      if (navigationModules.value.length === 0) {
        navigationModules.value = getMetaModules()
      }
    }
  } catch (error) {
    console.error('加载导航数据失败:', error)
    loadError.value = `加载导航数据失败: ${error.message}`
    // 只有在没有数据时才使用元模块
    if (navigationModules.value.length === 0) {
      navigationModules.value = getMetaModules()
    }
  }
}

// 轮询检查导航数据更新
const startPolling = () => {
  // 每3秒检查一次导航数据
  setInterval(() => {
    loadNavigationData()
  }, 3000)
}

// 组件挂载时加载导航数据并启动轮询
onMounted(() => {
  // 首先从后端加载导航数据
  loadNavigationData()
  // 启动轮询，定期获取最新导航数据
  startPolling()
})
</script>

<style scoped>
.sidebar-container {
  height: 100%;
  background-color: #1890FF;
  border-right: 1px solid rgba(255, 255, 255, 0.2);
  position: relative;
  overflow-y: auto;
  margin: 0;
  padding: 0;
}

.sidebar-menu {
  border-right: none;
  height: calc(100% - 80px);
  background-color: #1890FF;
  --el-menu-bg-color: #1890FF;
  --el-menu-text-color: #ffffff;
  --el-menu-active-color: #ffffff;
  --el-menu-hover-bg-color: rgba(255, 255, 255, 0.1);
  --el-menu-border-color: rgba(255, 255, 255, 0.2);
}

.collapse-toggle-btn {
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  background-color: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: #ffffff;
}
</style>