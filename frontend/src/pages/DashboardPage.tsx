import { chatApi } from '@/services/api'
import { useAuthStore } from '@/stores/authStore'
import { Chat } from '@/types'
import {
    Button,
    Card,
    CardBody,
    CardHeader
} from '@heroui/react'
import {
    MessageSquare,
    Plus
} from 'lucide-react'
import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

const DashboardPage = () => {
  const { user } = useAuthStore()
  const [chats, setChats] = useState<Chat[]>([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')

  useEffect(() => {
    const fetchChats = async () => {
      try {
        const response = await chatApi.getChats(0, 100)
        setChats(response.data)
      } catch (error) {
        console.error('Failed to fetch chats:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchChats()
  }, [])

  const filteredChats = chats.filter(chat =>
    chat.title.toLowerCase().includes(searchQuery.toLowerCase())
  )

  const handleDeleteChat = async (chatId: number) => {
    try {
      // TODO: 实现删除对话的API调用
      setChats(prev => prev.filter(chat => chat.id !== chatId))
    } catch (error) {
      console.error('Failed to delete chat:', error)
    }
  }

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">
            对话历史
          </h1>
          <p className="text-default-500 mt-1">
            查看和管理您的所有对话记录
          </p>
        </div>
        <Button
          as={Link}
          to="/chat"
          color="primary"
          startContent={<Plus size={16} />}
        >
          新建对话
        </Button>
      </div>

      {/* 搜索栏 */}
      <div className="flex gap-4">
        <Input
          placeholder="搜索对话..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          startContent={<Search size={16} />}
          className="flex-1"
        />
      </div>

      {/* 对话列表 */}
      <Card>
        <CardHeader>
          <h3 className="text-lg font-semibold">
            对话列表 ({filteredChats.length})
          </h3>
        </CardHeader>
        <CardBody>
          {loading ? (
            <div className="space-y-3">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="animate-pulse">
                  <div className="h-4 bg-default-200 rounded w-3/4 mb-2"></div>
                  <div className="h-3 bg-default-100 rounded w-1/2"></div>
                </div>
              ))}
            </div>
          ) : filteredChats.length > 0 ? (
            <div className="space-y-3">
              {filteredChats.map((chat) => (
                <div key={chat.id} className="flex items-center justify-between p-4 bg-content2 rounded-lg hover:bg-content3 transition-colors">
                  <div className="flex-1">
                    <Link
                      to={`/chat/${chat.id}`}
                      className="block"
                    >
                      <p className="font-medium truncate hover:text-primary">
                        {chat.title}
                      </p>
                      <div className="flex items-center gap-2 mt-1">
                        <Clock size={12} className="text-default-400" />
                        <p className="text-sm text-default-500">
                          {new Date(chat.created_at).toLocaleDateString('zh-CN', {
                            year: 'numeric',
                            month: 'short',
                            day: 'numeric',
                            hour: '2-digit',
                            minute: '2-digit'
                          })}
                        </p>
                      </div>
                    </Link>
                  </div>
                  <Button
                    isIconOnly
                    variant="light"
                    size="sm"
                    color="danger"
                    onPress={() => handleDeleteChat(chat.id)}
                  >
                    <Trash2 size={16} />
                  </Button>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <MessageSquare size={64} className="mx-auto text-default-300 mb-4" />
              <p className="text-default-500 mb-4">
                {searchQuery ? '没有找到匹配的对话' : '还没有任何对话'}
              </p>
              <Button
                as={Link}
                to="/chat"
                color="primary"
                startContent={<Plus size={16} />}
              >
                开始新对话
              </Button>
            </div>
          )}
        </CardBody>
      </Card>
    </div>
  )
}

export default DashboardPage
