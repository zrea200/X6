import { authApi } from '@/services/api'
import toast from 'react-hot-toast'
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface User {
  id: number
  username: string
  email: string
  full_name?: string
  avatar_url?: string
  is_active: boolean
  is_superuser: boolean
  created_at: string
}

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (username: string, password: string) => Promise<boolean>
  register: (userData: {
    username: string
    email: string
    password: string
    full_name?: string
  }) => Promise<boolean>
  logout: () => void
  fetchUser: () => Promise<void>
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,

      login: async (username: string, password: string) => {
        set({ isLoading: true })
        try {
          console.log('开始登录请求...')
          const response = await authApi.login(username, password)
          console.log('登录响应:', response)

          const { access_token } = response.data
          console.log('获取到token:', access_token ? '成功' : '失败')

          set({
            token: access_token,
            isAuthenticated: true,
            isLoading: false
          })

          // 获取用户信息
          console.log('开始获取用户信息...')
          try {
            await get().fetchUser()
            console.log('用户信息获取成功')
          } catch (userError) {
            console.error('获取用户信息失败:', userError)
            // 即使获取用户信息失败，也不要清除登录状态
            // 因为token是有效的
          }

          toast.success('登录成功')
          return true
        } catch (error: any) {
          console.error('登录失败:', error)
          set({ isLoading: false })
          const message = error.response?.data?.detail || '登录失败'
          toast.error(message)
          return false
        }
      },

      register: async (userData) => {
        set({ isLoading: true })
        try {
          await authApi.register(userData)
          set({ isLoading: false })
          toast.success('注册成功，请登录')
          return true
        } catch (error: any) {
          set({ isLoading: false })
          const message = error.response?.data?.detail || '注册失败'
          toast.error(message)
          return false
        }
      },

      logout: () => {
        set({
          user: null,
          token: null,
          isAuthenticated: false
        })
        toast.success('已退出登录')
      },

      fetchUser: async () => {
        try {
          console.log('正在获取用户信息...')
          const response = await authApi.getCurrentUser()
          console.log('用户信息响应:', response)
          set({ user: response.data })
        } catch (error) {
          console.error('Failed to fetch user:', error)
          // 不要在获取用户信息失败时自动登出
          // 因为这可能只是网络问题或临时错误
          // get().logout()
        }
      }
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        token: state.token,
        isAuthenticated: state.isAuthenticated,
        user: state.user
      })
    }
  )
)
