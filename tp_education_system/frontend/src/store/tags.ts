import { defineStore } from 'pinia'
import { useRouter } from 'vue-router'

interface Tag {
  path: string
  title: string
  icon: string
}

export const useTagsStore = defineStore('tags', {
  state: () => ({
    tagsList: [
      {
        path: '/',
        title: '首页',
        icon: 'House'
      }
    ] as Tag[],
    activeTag: '/' as string,
    cachedViews: [] as string[]
  }),
  getters: {
    getTagsList: (state) => state.tagsList,
    getActiveTag: (state) => state.activeTag,
    getCachedViews: (state) => state.cachedViews
  },
  actions: {
    addTag(tag: Tag) {
      // 检查标签是否已存在
      const existingTag = this.tagsList.find(t => t.path === tag.path)
      if (!existingTag) {
        this.tagsList.push(tag)
      }
      // 更新当前活跃标签
      this.activeTag = tag.path
      // 更新缓存视图
      this.updateCachedViews()
    },
    removeTag(path: string) {
      // 跳过首页标签的删除
      if (path === '/') return
      
      const tagIndex = this.tagsList.findIndex(t => t.path === path)
      if (tagIndex === -1) return
      
      // 从标签列表中移除标签
      this.tagsList.splice(tagIndex, 1)
      
      // 立即更新缓存视图
      this.updateCachedViews()
      
      // 如果删除的是当前活跃标签，更新活跃标签为最后一个标签
      if (path === this.activeTag && this.tagsList.length > 0) {
        this.activeTag = this.tagsList[this.tagsList.length - 1].path
      }
    },
    closeOtherTags(activePath: string) {
      this.tagsList = this.tagsList.filter(t => t.path === '/' || t.path === activePath)
      this.activeTag = activePath
      
      // 立即更新缓存视图
      this.updateCachedViews()
    },
    closeAllTags() {
      this.tagsList = [{
        path: '/',
        title: '首页',
        icon: 'House'
      }]
      this.activeTag = '/'
      
      // 立即更新缓存视图
      this.updateCachedViews()
    },
    updateCachedViews() {
      this.cachedViews = this.tagsList.map(t => t.path)
    },
    setActiveTag(path: string) {
      this.activeTag = path
    }
  }
})
