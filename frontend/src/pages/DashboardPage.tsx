import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { 
  Card, 
  CardBody, 
  CardHeader,
  Button,
  Progress,
  Chip
} from '@heroui/react'
import { 
  FileText, 
  MessageSquare, 
  Upload, 
  TrendingUp,
  Clock,
  CheckCircle,
  AlertCircle
} from 'lucide-react'
import { documentsApi, chatApi } from '@/services/api'
import { Document, Chat } from '@/types'
import { useAuthStore } from '@/stores/authStore'

const DashboardPage = () => {
  const { user } = useAuthStore()
  const [documents, setDocuments] = useState<Document[]>([])
  const [chats, setChats] = useState<Chat[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [docsResponse, chatsResponse] = await Promise.all([
          documentsApi.getDocuments(0, 10),
          chatApi.getChats(0, 10)
        ])
        setDocuments(docsResponse.data)
        setChats(chatsResponse.data)
      } catch (error) {
        console.error('Failed to fetch dashboard data:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'success'
      case 'processing': return 'warning'
      case 'failed': return 'danger'
      default: return 'default'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckCircle size={16} />
      case 'processing': return <Clock size={16} />
      case 'failed': return <AlertCircle size={16} />
      default: return <Clock size={16} />
    }
  }

  const stats = {
    totalDocuments: documents.length,
    completedDocuments: documents.filter(d => d.status === 'completed').length,
    totalChats: chats.length,
    processingDocuments: documents.filter(d => d.status === 'processing').length
  }

  return (
    <div className="space-y-6">
      {/* 欢迎信息 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">
            欢迎回来，{user?.full_name || user?.username}！
          </h1>
          <p className="text-default-500 mt-1">
            这里是您的知识库概览
          </p>
        </div>
        <Button
          as={Link}
          to="/documents"
          color="primary"
          startContent={<Upload size={16} />}
        >
          上传文档
        </Button>
      </div>

      {/* 统计卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardBody className="flex flex-row items-center gap-4">
            <div className="p-3 bg-primary/10 rounded-lg">
              <FileText className="text-primary" size={24} />
            </div>
            <div>
              <p className="text-2xl font-bold">{stats.totalDocuments}</p>
              <p className="text-default-500">总文档数</p>
            </div>
          </CardBody>
        </Card>

        <Card>
          <CardBody className="flex flex-row items-center gap-4">
            <div className="p-3 bg-success/10 rounded-lg">
              <CheckCircle className="text-success" size={24} />
            </div>
            <div>
              <p className="text-2xl font-bold">{stats.completedDocuments}</p>
              <p className="text-default-500">已处理文档</p>
            </div>
          </CardBody>
        </Card>

        <Card>
          <CardBody className="flex flex-row items-center gap-4">
            <div className="p-3 bg-secondary/10 rounded-lg">
              <MessageSquare className="text-secondary" size={24} />
            </div>
            <div>
              <p className="text-2xl font-bold">{stats.totalChats}</p>
              <p className="text-default-500">对话数量</p>
            </div>
          </CardBody>
        </Card>

        <Card>
          <CardBody className="flex flex-row items-center gap-4">
            <div className="p-3 bg-warning/10 rounded-lg">
              <TrendingUp className="text-warning" size={24} />
            </div>
            <div>
              <p className="text-2xl font-bold">{stats.processingDocuments}</p>
              <p className="text-default-500">处理中文档</p>
            </div>
          </CardBody>
        </Card>
      </div>

      {/* 最近文档和对话 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 最近文档 */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <h3 className="text-lg font-semibold">最近文档</h3>
            <Button
              as={Link}
              to="/documents"
              variant="light"
              size="sm"
            >
              查看全部
            </Button>
          </CardHeader>
          <CardBody>
            {loading ? (
              <div className="space-y-3">
                {[...Array(3)].map((_, i) => (
                  <div key={i} className="animate-pulse">
                    <div className="h-4 bg-default-200 rounded w-3/4 mb-2"></div>
                    <div className="h-3 bg-default-100 rounded w-1/2"></div>
                  </div>
                ))}
              </div>
            ) : documents.length > 0 ? (
              <div className="space-y-3">
                {documents.slice(0, 5).map((doc) => (
                  <div key={doc.id} className="flex items-center justify-between p-3 bg-content2 rounded-lg">
                    <div className="flex-1">
                      <p className="font-medium truncate">{doc.title}</p>
                      <p className="text-sm text-default-500">
                        {new Date(doc.created_at).toLocaleDateString()}
                      </p>
                    </div>
                    <Chip
                      color={getStatusColor(doc.status)}
                      variant="flat"
                      size="sm"
                      startContent={getStatusIcon(doc.status)}
                    >
                      {doc.status}
                    </Chip>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <FileText size={48} className="mx-auto text-default-300 mb-4" />
                <p className="text-default-500">还没有上传任何文档</p>
                <Button
                  as={Link}
                  to="/documents"
                  color="primary"
                  variant="light"
                  className="mt-2"
                >
                  立即上传
                </Button>
              </div>
            )}
          </CardBody>
        </Card>

        {/* 最近对话 */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <h3 className="text-lg font-semibold">最近对话</h3>
            <Button
              as={Link}
              to="/chat"
              variant="light"
              size="sm"
            >
              查看全部
            </Button>
          </CardHeader>
          <CardBody>
            {loading ? (
              <div className="space-y-3">
                {[...Array(3)].map((_, i) => (
                  <div key={i} className="animate-pulse">
                    <div className="h-4 bg-default-200 rounded w-3/4 mb-2"></div>
                    <div className="h-3 bg-default-100 rounded w-1/2"></div>
                  </div>
                ))}
              </div>
            ) : chats.length > 0 ? (
              <div className="space-y-3">
                {chats.slice(0, 5).map((chat) => (
                  <div key={chat.id} className="p-3 bg-content2 rounded-lg">
                    <p className="font-medium truncate">{chat.title}</p>
                    <p className="text-sm text-default-500">
                      {new Date(chat.created_at).toLocaleDateString()}
                    </p>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <MessageSquare size={48} className="mx-auto text-default-300 mb-4" />
                <p className="text-default-500">还没有任何对话</p>
                <Button
                  as={Link}
                  to="/chat"
                  color="primary"
                  variant="light"
                  className="mt-2"
                >
                  开始对话
                </Button>
              </div>
            )}
          </CardBody>
        </Card>
      </div>
    </div>
  )
}

export default DashboardPage
