import { 
  Navbar, 
  NavbarContent, 
  NavbarItem,
  Dropdown,
  DropdownTrigger,
  DropdownMenu,
  DropdownItem,
  Avatar,
  Button
} from '@heroui/react'
import { LogOut, User, Settings } from 'lucide-react'
import { useAuthStore } from '@/stores/authStore'

const Header = () => {
  const { user, logout } = useAuthStore()

  const handleLogout = () => {
    logout()
  }

  return (
    <Navbar 
      className="border-b border-divider bg-content1"
      maxWidth="full"
      height="64px"
    >
      <NavbarContent justify="end">
        <NavbarItem>
          <Dropdown placement="bottom-end">
            <DropdownTrigger>
              <Avatar
                as="button"
                className="transition-transform"
                color="primary"
                name={user?.full_name || user?.username}
                size="sm"
                src={user?.avatar_url}
              />
            </DropdownTrigger>
            <DropdownMenu aria-label="Profile Actions" variant="flat">
              <DropdownItem key="profile" className="h-14 gap-2">
                <p className="font-semibold">登录身份</p>
                <p className="font-semibold">{user?.username}</p>
              </DropdownItem>
              <DropdownItem 
                key="settings" 
                startContent={<Settings size={16} />}
              >
                设置
              </DropdownItem>
              <DropdownItem 
                key="logout" 
                color="danger" 
                startContent={<LogOut size={16} />}
                onClick={handleLogout}
              >
                退出登录
              </DropdownItem>
            </DropdownMenu>
          </Dropdown>
        </NavbarItem>
      </NavbarContent>
    </Navbar>
  )
}

export default Header
