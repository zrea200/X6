export interface User {
  id: number
  username: string
  email: string
  full_name?: string
  bio?: string
  avatar_url?: string
  is_active: boolean
  is_superuser: boolean
  created_at: string
  updated_at?: string
  last_login?: string
}

export interface Document {
  id: number
  title: string
  filename: string
  file_path: string
  file_size?: number
  file_type?: string
  mime_type?: string
  content?: string
  summary?: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  error_message?: string
  is_vectorized: boolean
  vector_count: number
  metadata?: string
  tags?: string
  owner_id: number
  created_at: string
  updated_at?: string
  processed_at?: string
}

export interface Chat {
  id: number
  title: string
  description?: string
  user_id: number
  is_active: boolean
  created_at: string
  updated_at?: string
  messages: Message[]
}

export interface Message {
  id: number
  content: string
  role: 'user' | 'assistant' | 'system'
  chat_id: number
  msg_metadata?: string
  token_count?: number
  created_at: string
}

export interface ChatRequest {
  message: string
  chat_id?: number
  use_documents?: boolean
  document_ids?: number[]
}

export interface DocumentSource {
  document_id: number
  title: string
  filename: string
  content_snippet: string
}

export interface ChatResponse {
  message: string
  chat_id: number
  sources?: DocumentSource[]
}

export interface DocumentUploadResponse {
  message: string
  document_id: number
  filename: string
  status: string
}

export interface ApiError {
  detail: string
}
