import { defineStore } from 'pinia'

interface UserInfo {
  id: string
  name: string
  avatar: string
  role: string
  department: string
}

interface UnitItem {
  id: number
  unit_name: string
  unit_level: string
  parent_id: number | null
  full_path: string
  depth: number
}

export const useUserStore = defineStore('user', {
  state: () => {
    // 从 localStorage 恢复登录状态
    const saved = localStorage.getItem('user_auth')
    const parsed = saved ? JSON.parse(saved) : {}
    return {
      userInfo: {
        id: '',
        name: parsed.用户名 || '管理员',
        avatar: '',
        role: parsed.角色 || 'admin',
        department: parsed.已选单位名称 || ''
      } as UserInfo,
      isLoggedIn: parsed.token ? true : false,
      token: parsed.token || '',
      角色: parsed.角色 || '',
      权限: parsed.权限 || [],
      已选单位ID: parsed.已选单位ID || null,
      已选单位名称: parsed.已选单位名称 || '',
      可选单位: (parsed.可选单位 || []) as UnitItem[]
    }
  },
  getters: {
    getUserInfo: (state) => state.userInfo,
    getIsLoggedIn: (state) => state.isLoggedIn,
    getToken: (state) => state.token,
    当前单位ID: (state) => state.已选单位ID,
    当前单位名称: (state) => state.已选单位名称,
    是县级管理员: (state) => state.角色 === 'county',
    /** 系统名称：已选单位名称 + "教育人事管理系统"，未选单位时使用中性名称 */
    系统名称: (state) => {
      if (state.已选单位名称) {
        return state.已选单位名称 + '教育人事管理系统'
      }
      return '教育人事管理系统'
    }
  },
  actions: {
    setLoginInfo(info: { token: string; 用户名: string; 角色: string; 权限: string[] }) {
      this.token = info.token
      this.角色 = info.角色
      this.权限 = info.权限
      this.isLoggedIn = true
      this.userInfo.name = info.用户名
      this.userInfo.role = info.角色
      this._saveToStorage()
    },
    setAvailableUnits(units: UnitItem[]) {
      this.可选单位 = units
    },
    selectUnit(unitId: number, unitName: string) {
      this.已选单位ID = unitId
      this.已选单位名称 = unitName
      this.userInfo.department = unitName
      this._saveToStorage()
    },
    setToken(token: string) {
      this.token = token
      this._saveToStorage()
    },
    logout() {
      this.userInfo = {
        id: '',
        name: '',
        avatar: '',
        role: '',
        department: ''
      }
      this.isLoggedIn = false
      this.token = ''
      this.角色 = ''
      this.权限 = []
      this.已选单位ID = null
      this.已选单位名称 = ''
      this.可选单位 = []
      localStorage.removeItem('user_auth')
      sessionStorage.removeItem('token_verified')
    },
    _saveToStorage() {
      localStorage.setItem('user_auth', JSON.stringify({
        token: this.token,
        用户名: this.userInfo.name,
        角色: this.角色,
        权限: this.权限,
        已选单位ID: this.已选单位ID,
        已选单位名称: this.已选单位名称,
        可选单位: this.可选单位
      }))
    }
  }
})