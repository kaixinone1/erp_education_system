import { defineStore } from 'pinia'

export const useAppStore = defineStore('app', {
  state: () => ({
    sidebarCollapse: false,
    device: 'desktop',
    theme: 'light',
    language: 'zh-CN'
  }),
  getters: {
    getSidebarCollapse: (state) => state.sidebarCollapse,
    getDevice: (state) => state.device,
    getTheme: (state) => state.theme,
    getLanguage: (state) => state.language
  },
  actions: {
    setSidebarCollapse(collapse: boolean) {
      this.sidebarCollapse = collapse
    },
    toggleSidebar() {
      this.sidebarCollapse = !this.sidebarCollapse
    },
    setDevice(device: string) {
      this.device = device
    },
    setTheme(theme: string) {
      this.theme = theme
    },
    setLanguage(language: string) {
      this.language = language
    }
  }
})
