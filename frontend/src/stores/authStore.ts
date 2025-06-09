import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { authApi } from '@/services/api'
import toast from 'react-hot-toast'

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
          const response = await authApi.login(username, password)
          const { access_token } = response.data
          
          set({ 
            token: access_token,
            isAuthenticated: true,
            isLoading: false 
          })
          
          // 获取用户信息
          await get().fetchUser()
          
          toast.success('登录成功')
          return true
        } catch (error: any) {
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
          const response = await authApi.getCurrentUser()
          set({ user: response.data })
        } catch (error) {
          console.error('Failed to fetch user:', error)
          get().logout()
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
