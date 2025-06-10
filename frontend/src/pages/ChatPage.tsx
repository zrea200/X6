import { chatApi, documentsApi } from '@/services/api'
import { useAuthStore } from '@/stores/authStore'
import { Chat, Document, Message } from '@/types'
import {
    Avatar,
    Button,
    Card,
    CardBody,
    CardHeader,
    Input,
    ScrollShadow,
    Spinner
} from '@heroui/react'
import {
    Bot,
    Check,
    Copy,
    FileText,
    MessageSquare,
    Paperclip,
    RotateCcw,
    Send,
    X
} from 'lucide-react'
import { useEffect, useRef, useState } from 'react'
import { useForm } from 'react-hook-form'
import toast from 'react-hot-toast'
import { useParams } from 'react-router-dom'

interface MessageForm {
  message: string
}

const ChatPage = () => {
  const { chatId } = useParams()
  const { user } = useAuthStore()
  const [currentChat, setCurrentChat] = useState<Chat | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [loading, setLoading] = useState(false)
  const [sending, setSending] = useState(false)
  const [copiedMessageId, setCopiedMessageId] = useState<number | null>(null)
  const [uploadedDocuments, setUploadedDocuments] = useState<Document[]>([])
  const [uploading, setUploading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  
  const messageForm = useForm<MessageForm>()

  useEffect(() => {
    if (chatId) {
      fetchChat(parseInt(chatId))
    } else {
      // 如果没有chatId，显示新对话界面
      setCurrentChat(null)
      setMessages([])
    }
  }, [chatId])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const fetchChat = async (id: number) => {
    try {
      setLoading(true)
      const response = await chatApi.getChat(id)
      setCurrentChat(response.data)
      setMessages(response.data.messages || [])
    } catch (error: any) {
      console.error('获取对话失败:', error)
      if (error.response?.status === 404) {
        toast.error('对话不存在，已重定向到新对话')
        // 重定向到新对话页面
        window.location.href = '/chat'
      } else {
        toast.error('获取对话失败')
      }
    } finally {
      setLoading(false)
    }
  }

  const handleSendMessage = async (data: MessageForm) => {
    if (!data.message.trim()) return

    const userMessage = data.message.trim()
    messageForm.reset()

    // 添加用户消息到界面
    const tempUserMessage: Message = {
      id: Date.now(),
      content: userMessage,
      role: 'user',
      chat_id: currentChat?.id || 0,
      created_at: new Date().toISOString()
    }
    setMessages(prev => [...prev, tempUserMessage])

    // 添加空的AI消息占位
    const tempAiMessage: Message = {
      id: Date.now() + 1,
      content: '',
      role: 'assistant',
      chat_id: currentChat?.id || 0,
      created_at: new Date().toISOString()
    }
    setMessages(prev => [...prev, tempAiMessage])

    try {
      setSending(true)
      let fullResponse = ''
      let chatId = currentChat?.id

      // 使用流式API
      const documentIds = uploadedDocuments.map(doc => doc.id)
      const useDocuments = documentIds.length > 0
      for await (const chunk of chatApi.sendMessageStream({
        message: userMessage,
        chat_id: currentChat?.id,
        use_documents: useDocuments,
        document_ids: useDocuments ? documentIds : undefined
      })) {
        if (chunk.content) {
          fullResponse += chunk.content
          // 更新AI消息内容
          setMessages(prev => {
            const newMessages = [...prev]
            const lastMessage = newMessages[newMessages.length - 1]
            if (lastMessage.role === 'assistant') {
              lastMessage.content = fullResponse
            }
            return newMessages
          })
        }

        if (chunk.chat_id) {
          chatId = chunk.chat_id
        }

        if (chunk.done) {
          // 如果是新对话，更新当前聊天信息
          if (!currentChat && chatId) {
            await fetchChat(chatId)
          }
          break
        }
      }
    } catch (error: any) {
      console.error('发送消息失败:', error)
      const message = error.message || '发送消息失败'
      toast.error(message)
      // 移除临时消息
      setMessages(prev => prev.filter(msg =>
        msg.id !== tempUserMessage.id && msg.id !== tempAiMessage.id
      ))
    } finally {
      setSending(false)
    }
  }

  const formatTime = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleTimeString('zh-CN', {
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const handleCopyMessage = async (messageId: number, content: string) => {
    try {
      await navigator.clipboard.writeText(content)
      setCopiedMessageId(messageId)
      toast.success('已复制到剪贴板')
      setTimeout(() => setCopiedMessageId(null), 2000)
    } catch (error) {
      toast.error('复制失败')
    }
  }

  const handleRetryMessage = async (messageIndex: number) => {
    if (messageIndex < 1) return // 确保有前一条用户消息

    const userMessage = messages[messageIndex - 1]
    if (userMessage.role !== 'user') return

    // 移除当前AI消息及之后的所有消息
    const newMessages = messages.slice(0, messageIndex)
    setMessages(newMessages)

    // 重新发送用户消息
    const tempAiMessage: Message = {
      id: Date.now(),
      content: '',
      role: 'assistant',
      chat_id: currentChat?.id || 0,
      created_at: new Date().toISOString()
    }
    setMessages(prev => [...prev, tempAiMessage])

    try {
      setSending(true)
      let fullResponse = ''
      // 使用流式API重新生成回复
      const documentIds = uploadedDocuments.map(doc => doc.id)
      const useDocuments = documentIds.length > 0
      for await (const chunk of chatApi.sendMessageStream({
        message: userMessage.content,
        chat_id: currentChat?.id,
        use_documents: useDocuments,
        document_ids: useDocuments ? documentIds : undefined
      })) {
        if (chunk.content) {
          fullResponse += chunk.content
          // 更新AI消息内容
          setMessages(prev => {
            const newMessages = [...prev]
            const lastMessage = newMessages[newMessages.length - 1]
            if (lastMessage.role === 'assistant') {
              lastMessage.content = fullResponse
            }
            return newMessages
          })
        }

        if (chunk.done) {
          break
        }
      }
    } catch (error: any) {
      console.error('重新生成失败:', error)
      toast.error('重新生成失败')
      // 移除临时消息
      setMessages(prev => prev.filter(msg => msg.id !== tempAiMessage.id))
    } finally {
      setSending(false)
    }
  }

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files
    if (!files || files.length === 0) return

    const file = files[0]

    // 验证文件类型
    const allowedTypes = ['.pdf', '.doc', '.docx', '.txt', '.md']
    const fileExtension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'))
    if (!allowedTypes.includes(fileExtension)) {
      toast.error('不支持的文件格式。支持：PDF、Word、TXT、Markdown')
      return
    }

    // 验证文件大小 (10MB)
    if (file.size > 10 * 1024 * 1024) {
      toast.error('文件大小不能超过10MB')
      return
    }

    try {
      setUploading(true)
      const response = await documentsApi.uploadDocument(file, file.name)

      // 添加到已上传文档列表
      const uploadedDoc: Document = {
        id: response.data.document_id,
        title: file.name,
        filename: response.data.filename,
        file_path: '',
        status: response.data.status as 'pending' | 'processing' | 'completed' | 'failed',
        is_vectorized: false,
        vector_count: 0,
        owner_id: 0,
        created_at: new Date().toISOString()
      }
      setUploadedDocuments(prev => [...prev, uploadedDoc])

      // 添加文档上传消息到聊天
      const documentMessage: Message = {
        id: Date.now(),
        content: `📄 已上传文档：${file.name}`,
        role: 'system',
        chat_id: currentChat?.id || 0,
        created_at: new Date().toISOString()
      }
      setMessages(prev => [...prev, documentMessage])

      toast.success('文档上传成功，正在处理中...')

    } catch (error: any) {
      console.error('文档上传失败:', error)
      toast.error(error.response?.data?.detail || '文档上传失败')
    } finally {
      setUploading(false)
      // 清空文件输入
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
    }
  }

  const handleFileButtonClick = () => {
    fileInputRef.current?.click()
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <Spinner size="lg" />
      </div>
    )
  }

  return (
    <div className="flex h-full">
      {/* 主聊天区域 */}
      <div className="flex-1 flex flex-col">
        {/* 聊天头部 */}
        <Card className="rounded-none border-b">
          <CardHeader className="flex items-center gap-3">
            <div className="p-2 bg-primary/10 rounded-lg">
              <MessageSquare className="text-primary" size={20} />
            </div>
            <div>
              <h2 className="text-lg font-semibold">
                {currentChat?.title || '新对话'}
              </h2>
              <p className="text-sm text-default-500">
                智能知识库助手
              </p>
            </div>
          </CardHeader>
        </Card>

        {/* 消息列表 */}
        <div className="flex-1 overflow-hidden">
          <ScrollShadow className="h-full p-4">
            {messages.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full text-center">
                <div className="p-4 bg-primary/10 rounded-full mb-4">
                  <Bot size={48} className="text-primary" />
                </div>
                <h3 className="text-xl font-semibold mb-2">开始新对话</h3>
                <p className="text-default-500 max-w-md">
                  我是您的智能知识库助手，可以帮您搜索和分析已上传的文档。请输入您的问题开始对话。
                </p>
              </div>
            ) : (
              <div className="space-y-4">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex gap-3 ${
                      message.role === 'user' ? 'justify-end' :
                      message.role === 'system' ? 'justify-center' : 'justify-start'
                    }`}
                  >
                    {message.role === 'assistant' && (
                      <Avatar
                        icon={<Bot size={16} />}
                        className="bg-primary/10 text-primary"
                        size="sm"
                      />
                    )}

                    <div
                      className={`max-w-[70%] ${
                        message.role === 'user'
                          ? 'bg-primary text-primary-foreground'
                          : message.role === 'system'
                          ? 'bg-warning/10 text-warning-600 border border-warning/20'
                          : 'bg-content2'
                      } rounded-lg p-3`}
                    >
                      <p className={`whitespace-pre-wrap ${
                        message.role === 'user'
                          ? 'text-primary-foreground'
                          : 'text-black dark:text-white'
                      }`}>
                        {message.content}
                      </p>
                      {/* <p className={`text-xs mt-2 ${
                        message.role === 'user'
                          ? 'text-primary-foreground/70'
                          : 'text-default-500'
                      }`}>
                        {formatTime(message.created_at)}
                      </p> */}

                      {/* 消息操作按钮 */}
                      {message.content && message.role !== 'system' && (
                        <div className="flex gap-1 mt-2">
                          <Button
                            size="sm"
                            variant="light"
                            isIconOnly
                            className="h-6 w-6 min-w-6"
                            onPress={() => handleCopyMessage(message.id, message.content)}
                          >
                            {copiedMessageId === message.id ? (
                              <Check size={12} className="text-success" />
                            ) : (
                              <Copy size={12} />
                            )}
                          </Button>

                          {message.role === 'assistant' && (
                            <Button
                              size="sm"
                              variant="light"
                              isIconOnly
                              className="h-6 w-6 min-w-6"
                              onPress={() => {
                                const messageIndex = messages.findIndex(m => m.id === message.id)
                                handleRetryMessage(messageIndex)
                              }}
                              isDisabled={sending}
                            >
                              <RotateCcw size={12} />
                            </Button>
                          )}
                        </div>
                      )}
                    </div>

                    {message.role === 'user' && (
                      <Avatar
                        name={user?.username}
                        src={user?.avatar_url}
                        size="sm"
                      />
                    )}
                  </div>
                ))}
                
                {sending && (
                  <div className="flex gap-3 justify-start">
                    <Avatar
                      icon={<Bot size={16} />}
                      className="bg-primary/10 text-primary"
                      size="sm"
                    />
                    <div className="bg-content2 rounded-lg p-3">
                      <div className="flex items-center gap-2">
                        <Spinner size="sm" />
                        <span className="text-sm text-default-500">正在思考...</span>
                      </div>
                    </div>
                  </div>
                )}
                
                <div ref={messagesEndRef} />
              </div>
            )}
          </ScrollShadow>
        </div>

        {/* 消息输入区域 */}
        <Card className="rounded-none border-t">
          <CardBody>
            {/* 已上传文档显示 */}
            {uploadedDocuments.length > 0 && (
              <div className="mb-3">
                <div className="text-xs text-default-500 mb-2">已上传文档：</div>
                <div className="flex flex-wrap gap-2">
                  {uploadedDocuments.map((doc) => (
                    <div
                      key={doc.id}
                      className="flex items-center gap-2 bg-content2 rounded-lg px-3 py-1 text-sm"
                    >
                      <FileText size={14} />
                      <span>{doc.title}</span>
                      <Button
                        size="sm"
                        variant="light"
                        isIconOnly
                        className="h-4 w-4 min-w-4"
                        onPress={() => {
                          setUploadedDocuments(prev => prev.filter(d => d.id !== doc.id))
                        }}
                      >
                        <X size={10} />
                      </Button>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <form
              onSubmit={messageForm.handleSubmit(handleSendMessage)}
              className="flex gap-2"
            >
              <Button
                type="button"
                variant="light"
                isIconOnly
                onPress={handleFileButtonClick}
                isLoading={uploading}
                className="shrink-0"
              >
                <Paperclip size={16} />
              </Button>

              <Input
                placeholder="输入您的问题..."
                {...messageForm.register('message', { required: true })}
                disabled={sending}
                className="flex-1"
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault()
                    messageForm.handleSubmit(handleSendMessage)()
                  }
                }}
              />

              <Button
                type="submit"
                color="primary"
                isIconOnly
                isLoading={sending}
                disabled={!messageForm.watch('message')?.trim()}
              >
                <Send size={16} />
              </Button>
            </form>

            {/* 隐藏的文件输入 */}
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.doc,.docx,.txt,.md"
              onChange={handleFileUpload}
              className="hidden"
              aria-label="上传文档"
            />

            <div className="text-xs text-default-500 mt-2">
              按 Enter 发送，Shift + Enter 换行 • 支持上传 PDF、Word、TXT、Markdown 文档
            </div>
          </CardBody>
        </Card>
      </div>
    </div>
  )
}

export default ChatPage
