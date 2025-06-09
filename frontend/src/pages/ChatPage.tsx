import { chatApi } from '@/services/api'
import { useAuthStore } from '@/stores/authStore'
import { Chat, Message } from '@/types'
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
    MessageSquare,
    Send
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
  const messagesEndRef = useRef<HTMLDivElement>(null)
  
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

    try {
      setSending(true)
      const response = await chatApi.sendMessage({
        message: userMessage,
        chat_id: currentChat?.id,
        use_documents: true
      })

      // 如果是新对话，获取完整的对话信息
      if (!currentChat) {
        await fetchChat(response.data.chat_id)
      } else {
        // 添加AI回复到界面
        const aiMessage: Message = {
          id: Date.now() + 1,
          content: response.data.message,
          role: 'assistant',
          chat_id: response.data.chat_id,
          created_at: new Date().toISOString()
        }
        setMessages(prev => [...prev, aiMessage])
      }
    } catch (error: any) {
      const message = error.response?.data?.detail || '发送消息失败'
      toast.error(message)
      // 移除临时用户消息
      setMessages(prev => prev.filter(msg => msg.id !== tempUserMessage.id))
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
                      message.role === 'user' ? 'justify-end' : 'justify-start'
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
                          : 'bg-content2'
                      } rounded-lg p-3`}
                    >
                      <p className="whitespace-pre-wrap">{message.content}</p>
                      <p className={`text-xs mt-2 ${
                        message.role === 'user'
                          ? 'text-primary-foreground/70'
                          : 'text-default-500'
                      }`}>
                        {formatTime(message.created_at)}
                      </p>
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
            <form
              onSubmit={messageForm.handleSubmit(handleSendMessage)}
              className="flex gap-2"
            >
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
            <div className="text-xs text-default-500 mt-2">
              按 Enter 发送，Shift + Enter 换行
            </div>
          </CardBody>
        </Card>
      </div>
    </div>
  )
}

export default ChatPage
