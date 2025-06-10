import { useAuthStore } from '@/stores/authStore'
import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
  timeout: 10000,
})

// 请求拦截器 - 添加认证token
api.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().token
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器 - 处理认证错误
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      useAuthStore.getState().logout()
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// 认证相关API
export const authApi = {
  login: (username: string, password: string) => {
    const formData = new FormData()
    formData.append('username', username)
    formData.append('password', password)
    return api.post('/auth/login', formData)
  },

  register: (userData: {
    username: string
    email: string
    password: string
    full_name?: string
  }) => api.post('/auth/register', userData),

  getCurrentUser: () => api.get('/users/me'),
}

// 文档相关API
export const documentsApi = {
  getDocuments: (skip = 0, limit = 100) =>
    api.get(`/documents/?skip=${skip}&limit=${limit}`),

  getDocument: (id: number) => api.get(`/documents/${id}`),

  uploadDocument: (file: File, title?: string) => {
    const formData = new FormData()
    formData.append('file', file)
    if (title) {
      formData.append('title', title)
    }
    return api.post('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
  },

  updateDocument: (id: number, data: { title?: string; tags?: string; summary?: string }) =>
    api.put(`/documents/${id}`, data),

  deleteDocument: (id: number) => api.delete(`/documents/${id}`),

  reprocessDocument: (id: number) => api.post(`/documents/${id}/reprocess`),
}

// 聊天相关API
export const chatApi = {
  getChats: (skip = 0, limit = 100) =>
    api.get(`/chat/?skip=${skip}&limit=${limit}`),

  getChat: (id: number) => api.get(`/chat/${id}`),

  createChat: (data: { title: string; description?: string }) =>
    api.post('/chat/', data),

  sendMessage: (data: {
    message: string
    chat_id?: number
    use_documents?: boolean
    document_ids?: number[]
  }) => api.post('/chat/message', data),

  sendMessageStream: async function* (data: {
    message: string
    chat_id?: number
    use_documents?: boolean
    document_ids?: number[]
  }) {
    const token = useAuthStore.getState().token
    const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'}/chat/message/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify(data),
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const reader = response.body?.getReader()
    const decoder = new TextDecoder()

    if (!reader) {
      throw new Error('No response body')
    }

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      const chunk = decoder.decode(value)
      const lines = chunk.split('\n')

      for (const line of lines) {
        if (line.trim().startsWith('data: ')) {
          try {
            const data = JSON.parse(line.trim().substring(6))
            yield data
          } catch (e) {
            console.error('解析流式响应失败:', e)
          }
        }
      }
    }
  },

  deleteChat: (id: number) => api.delete(`/chat/${id}`),

  getChatDocuments: () => api.get('/chat/documents'),
}

export default api
