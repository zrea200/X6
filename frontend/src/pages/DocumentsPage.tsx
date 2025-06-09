import { useState, useEffect, useRef } from 'react'
import {
  Card,
  CardBody,
  CardHeader,
  Button,
  Input,
  Modal,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
  useDisclosure,
  Table,
  TableHeader,
  TableColumn,
  TableBody,
  TableRow,
  TableCell,
  Chip,
  Dropdown,
  DropdownTrigger,
  DropdownMenu,
  DropdownItem,
  Progress,
  Pagination
} from '@heroui/react'
import {
  Upload,
  Search,
  MoreVertical,
  Eye,
  Edit,
  Trash2,
  RefreshCw,
  FileText,
  Download
} from 'lucide-react'
import { useForm } from 'react-hook-form'
import toast from 'react-hot-toast'
import { documentsApi } from '@/services/api'
import { Document } from '@/types'

interface UploadForm {
  title: string
  file: FileList
}

const DocumentsPage = () => {
  const [documents, setDocuments] = useState<Document[]>([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [uploading, setUploading] = useState(false)
  
  const { isOpen, onOpen, onClose } = useDisclosure()
  const fileInputRef = useRef<HTMLInputElement>(null)
  
  const uploadForm = useForm<UploadForm>()

  useEffect(() => {
    fetchDocuments()
  }, [page])

  const fetchDocuments = async () => {
    try {
      setLoading(true)
      const response = await documentsApi.getDocuments((page - 1) * 10, 10)
      setDocuments(response.data)
      // 这里应该从响应头或响应体中获取总页数，暂时设为1
      setTotalPages(Math.ceil(response.data.length / 10) || 1)
    } catch (error) {
      toast.error('获取文档列表失败')
    } finally {
      setLoading(false)
    }
  }

  const handleUpload = async (data: UploadForm) => {
    if (!data.file || data.file.length === 0) {
      toast.error('请选择文件')
      return
    }

    try {
      setUploading(true)
      const file = data.file[0]
      await documentsApi.uploadDocument(file, data.title)
      toast.success('文档上传成功')
      onClose()
      uploadForm.reset()
      fetchDocuments()
    } catch (error: any) {
      const message = error.response?.data?.detail || '上传失败'
      toast.error(message)
    } finally {
      setUploading(false)
    }
  }

  const handleDelete = async (id: number) => {
    if (!confirm('确定要删除这个文档吗？')) return

    try {
      await documentsApi.deleteDocument(id)
      toast.success('文档删除成功')
      fetchDocuments()
    } catch (error) {
      toast.error('删除失败')
    }
  }

  const handleReprocess = async (id: number) => {
    try {
      await documentsApi.reprocessDocument(id)
      toast.success('重新处理已开始')
      fetchDocuments()
    } catch (error) {
      toast.error('重新处理失败')
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'success'
      case 'processing': return 'warning'
      case 'failed': return 'danger'
      default: return 'default'
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case 'completed': return '已完成'
      case 'processing': return '处理中'
      case 'failed': return '失败'
      case 'pending': return '等待中'
      default: return status
    }
  }

  const filteredDocuments = documents.filter(doc =>
    doc.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    doc.filename.toLowerCase().includes(searchQuery.toLowerCase())
  )

  const formatFileSize = (bytes?: number) => {
    if (!bytes) return '-'
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(1024))
    return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${sizes[i]}`
  }

  return (
    <div className="space-y-6">
      {/* 页面标题和操作 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">文档管理</h1>
          <p className="text-default-500 mt-1">管理您的知识库文档</p>
        </div>
        <Button
          color="primary"
          startContent={<Upload size={16} />}
          onPress={onOpen}
        >
          上传文档
        </Button>
      </div>

      {/* 搜索和筛选 */}
      <Card>
        <CardBody>
          <div className="flex gap-4">
            <Input
              placeholder="搜索文档..."
              startContent={<Search size={16} />}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="flex-1"
            />
            <Button
              variant="bordered"
              startContent={<RefreshCw size={16} />}
              onPress={fetchDocuments}
            >
              刷新
            </Button>
          </div>
        </CardBody>
      </Card>

      {/* 文档列表 */}
      <Card>
        <CardHeader>
          <h3 className="text-lg font-semibold">文档列表</h3>
        </CardHeader>
        <CardBody>
          <Table aria-label="文档列表">
            <TableHeader>
              <TableColumn>文档名称</TableColumn>
              <TableColumn>文件名</TableColumn>
              <TableColumn>大小</TableColumn>
              <TableColumn>状态</TableColumn>
              <TableColumn>上传时间</TableColumn>
              <TableColumn>操作</TableColumn>
            </TableHeader>
            <TableBody
              isLoading={loading}
              emptyContent="暂无文档"
            >
              {filteredDocuments.map((doc) => (
                <TableRow key={doc.id}>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <FileText size={16} className="text-default-400" />
                      <span className="font-medium">{doc.title}</span>
                    </div>
                  </TableCell>
                  <TableCell>{doc.filename}</TableCell>
                  <TableCell>{formatFileSize(doc.file_size)}</TableCell>
                  <TableCell>
                    <Chip
                      color={getStatusColor(doc.status)}
                      variant="flat"
                      size="sm"
                    >
                      {getStatusText(doc.status)}
                    </Chip>
                  </TableCell>
                  <TableCell>
                    {new Date(doc.created_at).toLocaleDateString()}
                  </TableCell>
                  <TableCell>
                    <Dropdown>
                      <DropdownTrigger>
                        <Button
                          isIconOnly
                          variant="light"
                          size="sm"
                        >
                          <MoreVertical size={16} />
                        </Button>
                      </DropdownTrigger>
                      <DropdownMenu>
                        <DropdownItem
                          key="view"
                          startContent={<Eye size={16} />}
                        >
                          查看详情
                        </DropdownItem>
                        <DropdownItem
                          key="edit"
                          startContent={<Edit size={16} />}
                        >
                          编辑
                        </DropdownItem>
                        {doc.status === 'failed' && (
                          <DropdownItem
                            key="reprocess"
                            startContent={<RefreshCw size={16} />}
                            onPress={() => handleReprocess(doc.id)}
                          >
                            重新处理
                          </DropdownItem>
                        )}
                        <DropdownItem
                          key="delete"
                          color="danger"
                          startContent={<Trash2 size={16} />}
                          onPress={() => handleDelete(doc.id)}
                        >
                          删除
                        </DropdownItem>
                      </DropdownMenu>
                    </Dropdown>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
          
          {totalPages > 1 && (
            <div className="flex justify-center mt-4">
              <Pagination
                total={totalPages}
                page={page}
                onChange={setPage}
              />
            </div>
          )}
        </CardBody>
      </Card>

      {/* 上传文档模态框 */}
      <Modal isOpen={isOpen} onClose={onClose}>
        <ModalContent>
          <form onSubmit={uploadForm.handleSubmit(handleUpload)}>
            <ModalHeader>上传文档</ModalHeader>
            <ModalBody>
              <Input
                label="文档标题"
                placeholder="请输入文档标题（可选）"
                {...uploadForm.register('title')}
              />
              <Input
                ref={fileInputRef}
                type="file"
                label="选择文件"
                accept=".pdf,.doc,.docx,.txt,.md"
                {...uploadForm.register('file', { required: '请选择文件' })}
                errorMessage={uploadForm.formState.errors.file?.message}
              />
              <div className="text-sm text-default-500">
                支持的文件格式：PDF、Word、TXT、Markdown
              </div>
            </ModalBody>
            <ModalFooter>
              <Button variant="light" onPress={onClose}>
                取消
              </Button>
              <Button
                color="primary"
                type="submit"
                isLoading={uploading}
              >
                上传
              </Button>
            </ModalFooter>
          </form>
        </ModalContent>
      </Modal>
    </div>
  )
}

export default DocumentsPage
