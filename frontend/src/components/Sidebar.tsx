import { cn } from '@/utils/cn'
import { Button } from '@heroui/react'
import {
  ChevronLeft,
  ChevronRight,
  Home,
  MessageSquare,
  Plus
} from 'lucide-react'
import { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'

const Sidebar = () => {
  const [collapsed, setCollapsed] = useState(false)
  const location = useLocation()

  const menuItems = [
    {
      icon: Home,
      label: '历史记录',
      path: '/dashboard'
    },
    {
      icon: MessageSquare,
      label: '对话',
      path: '/chat'
    }
  ]

  return (
    <div className={cn(
      "bg-content1 border-r border-divider transition-all duration-300 flex flex-col",
      collapsed ? "w-16" : "w-64"
    )}>
      {/* Logo区域 */}
      <div className="p-4 border-b border-divider">
        <div className="flex items-center justify-between">
          {!collapsed && (
            <h1 className="text-xl font-bold text-foreground">
              知识库助手
            </h1>
          )}
          <Button
            isIconOnly
            variant="ghost"
            size="sm"
            onClick={() => setCollapsed(!collapsed)}
          >
            {collapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
          </Button>
        </div>
      </div>

      {/* 新建对话按钮 */}
      <div className="p-4">
        <Button
          as={Link}
          to="/chat"
          color="primary"
          variant="solid"
          className="w-full"
          startContent={!collapsed ? <Plus size={16} /> : undefined}
        >
          {collapsed ? <Plus size={16} /> : '新建对话'}
        </Button>
      </div>

      {/* 导航菜单 */}
      <nav className="flex-1 px-4">
        <ul className="space-y-2">
          {menuItems.map((item) => {
            const Icon = item.icon
            const isActive = location.pathname === item.path
            
            return (
              <li key={item.path}>
                <Button
                  as={Link}
                  to={item.path}
                  variant={isActive ? "solid" : "ghost"}
                  color={isActive ? "primary" : "default"}
                  className={cn(
                    "w-full justify-start",
                    collapsed && "px-2"
                  )}
                  startContent={<Icon size={16} />}
                >
                  {!collapsed && item.label}
                </Button>
              </li>
            )
          })}
        </ul>
      </nav>

      {/* 底部信息 */}
      {!collapsed && (
        <div className="p-4 border-t border-divider">
          <div className="text-xs text-default-500">
            Knowledge Base Assistant v1.0.0
          </div>
        </div>
      )}
    </div>
  )
}

export default Sidebar
