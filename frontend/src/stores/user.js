import { defineStore } from 'pinia'
import axios from 'axios'

export const useUserStore = defineStore('user', {
  state: () => {
    // 从 localStorage 恢复用户状态
    const userStr = localStorage.getItem('user')
    const user = userStr ? JSON.parse(userStr) : null
    
    return {
      token: localStorage.getItem('token') || '',
      id: user?.id || null,
      username: user?.username || '',
      fullName: user?.full_name || '',
      isAdmin: user?.is_admin || false
    }
  },

  actions: {
    async login(username, password) {
      try {
        // 创建 FormData 对象
        const formData = new FormData()
        formData.append('username', username)
        formData.append('password', password)
        
        // 发送登录请求
        const response = await axios.post('/api/v1/auth/login', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          },
          withCredentials: true
        })
        const { access_token, user } = response.data
        
        // 保存 token
        this.token = access_token
        localStorage.setItem('token', access_token)
        
        // 设置 axios 默认 header
        axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
        
        // 保存用户信息
        this.id = user.id
        this.username = user.username
        this.fullName = user.full_name
        this.isAdmin = user.is_admin
        
        // 保存完整的用户信息到 localStorage
        localStorage.setItem('user', JSON.stringify(user))
        
        return true
      } catch (error) {
        console.error('Login failed:', error)
        return false
      }
    },
    
    logout() {
      this.token = ''
      this.id = null
      this.username = ''
      this.fullName = ''
      this.isAdmin = false
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      delete axios.defaults.headers.common['Authorization']
    },

    // 初始化 axios 请求头
    initAxiosHeader() {
      const token = localStorage.getItem('token')
      if (token) {
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
      }
    }
  }
}) 