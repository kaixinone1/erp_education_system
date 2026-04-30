<template>
  <div class="sidebar-container">
    <el-menu
      :default-active="activeMenu"
      class="sidebar-menu"
      :collapse="isCollapse"
      :collapse-transition="false"
      :unique-opened="true"
      router
    >
      <!-- 首页 - 固定显示 -->
      <el-menu-item index="/">
        <el-icon><House /></el-icon>
        <template #title>首页</template>
      </el-menu-item>

      <!-- 动态导航菜单 -->
      <template v-for="module in navigationModules" :key="module.id">
        <!-- 有子节点的模块 -->
        <el-sub-menu v-if="module.children && module.children.length > 0" :index="module.path">
          <template #title>
            <el-icon>
              <component :is="getIconComponent(module.icon)" />
            </el-icon>
            <span>{{ module.title }}</span>
          </template>

          <!-- 递归渲染子节点 -->
          <template v-for="child in module.children" :key="child.id">
            <!-- 子模块（有children） -->
            <el-sub-menu v-if="child.children && child.children.length > 0" :index="child.path">
              <template #title>
                <span>{{ child.title }}</span>
              </template>
              <el-menu-item
                v-for="grandChild in child.children"
                :key="grandChild.id"
                :index="grandChild.path"
              >
                <span>{{ grandChild.title }}</span>
              </el-menu-item>
            </el-sub-menu>

            <!-- 叶子节点 -->
            <el-menu-item v-else :index="child.path">
              <span>{{ child.title }}</span>
            </el-menu-item>
          </template>
        </el-sub-menu>

        <!-- 无子节点的模块 -->
        <el-menu-item v-else :index="module.path">
          <el-icon>
            <component :is="getIconComponent(module.icon)" />
          </el-icon>
          <template #title>{{ module.title }}</template>
        </el-menu-item>
      </template>
    </el-menu>

    <!-- 折叠按钮 -->
    <el-button
      class="collapse-toggle-btn"
      :icon="isCollapse ? Expand : Fold"
      circle
      size="small"
      @click="toggleCollapse"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import {
  House,
  Setting,
  Grid,
  List,
  Folder,
  Document,
  Bell,
  DocumentCopy,
  DataLine,
  Upload,
  Delete,
  User,
  Fold,
  Expand
} from '@element-plus/icons-vue'

const route = useRoute()

// 菜单折叠状态
const isCollapse = ref(false)

// 当前激活的菜单
const activeMenu = computed(() => route.path)

// 导航模块数据 - 从后端动态加载
const navigationModules = ref<any[]>([])

// 图标映射
const iconMap: Record<string, any> = {
  House,
  Setting,
  Grid,
  List,
  Folder,
  Document,
  Bell,
  DocumentCopy,
  DataLine,
  Upload,
  Delete,
  User
}

// 获取图标组件
const getIconComponent = (iconName: string) => {
  return iconMap[iconName] || Document
}

// 切换折叠状态
const toggleCollapse = () => {
  isCollapse.value = !isCollapse.value
}

// 从后端加载导航数据
const loadNavigation = async () => {
  try {
    const response = await fetch('/api/navigation-admin/tree')
    if (response.ok) {
      const data = await response.json()
      if (data.modules && data.modules.length > 0) {
        navigationModules.value = data.modules
      } else {
        console.error('后端导航数据为空')
      }
    } else {
      console.error('加载导航数据失败:', response.status)
    }
  } catch (error) {
    console.error('加载导航数据出错:', error)
  }
}

// 组件挂载时加载导航数据
onMounted(() => {
  loadNavigation()
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
