<template>
  <div v-if="item.children && Array.isArray(item.children) && item.children.length > 0">
    <el-sub-menu :index="item.id">
      <template #title>
        <span v-if="!isCollapse">{{ item.title }}</span>
      </template>
      <SidebarItem
        v-for="child in item.children"
        :key="child.id"
        :item="child"
        :is-collapse="isCollapse"
      />
    </el-sub-menu>
  </div>
  <div v-else>
    <el-menu-item :index="item.path || item.id" @click="handleMenuClick">
      <span v-if="!isCollapse">{{ item.title }}</span>
    </el-menu-item>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

interface MenuItem {
  id: string
  title: string
  path?: string
  children?: MenuItem[]
}

const props = defineProps<{
  item: MenuItem
  isCollapse: boolean
}>()

const router = useRouter()

const handleMenuClick = () => {
  console.log('菜单点击:', props.item.title, '路径:', props.item.path)
  if (props.item.path) {
    console.log('正在导航到:', props.item.path)
    router.push(props.item.path).then(() => {
      console.log('导航成功')
    }).catch((err) => {
      console.error('导航失败:', err)
    })
  } else {
    console.warn('没有路径:', props.item)
  }
}
</script>

<style scoped>
/* 组件样式可以在这里添加 */
</style>
