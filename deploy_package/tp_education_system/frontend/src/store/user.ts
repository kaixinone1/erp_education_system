import { defineStore } from 'pinia'

interface UserInfo {
  id: string
  name: string
  avatar: string
  role: string
  department: string
}

export const useUserStore = defineStore('user', {
  state: () => ({
    userInfo: {
      id: '',
      name: '管理员',
      avatar: '',
      role: 'admin',
      department: '教育局'
    } as UserInfo,
    isLoggedIn: false,
    token: ''
  }),
  getters: {
    getUserInfo: (state) => state.userInfo,
    getIsLoggedIn: (state) => state.isLoggedIn,
    getToken: (state) => state.token
  },
  actions: {
    setUserInfo(userInfo: UserInfo) {
      this.userInfo = userInfo
      this.isLoggedIn = true
    },
    setToken(token: string) {
      this.token = token
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
    }
  }
})
