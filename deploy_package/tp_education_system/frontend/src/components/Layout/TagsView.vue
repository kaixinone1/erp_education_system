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
import { watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { More, Refresh, Close } from '@element-plus/icons-vue'
import { storeToRefs } from 'pinia'
import { useTagsStore } from '@/store/tags'

const route = useRoute()
const router = useRouter()
const tagsStore = useTagsStore()
const { tagsList, activeTag } = storeToRefs(tagsStore)

// 监听路由变化，添加标签
watch(
  () => route.fullPath,
  () => {
    // 添加标签到标签列表
    tagsStore.addTag({
      path: route.path,
      title: route.meta.title as string || '页面',
      icon: route.meta.icon as string || ''
    })
  },
  { immediate: true }
)

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
