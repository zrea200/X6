import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { 
  Card, 
  CardBody, 
  CardHeader,
  Input, 
  Button, 
  Tabs, 
  Tab,
  Divider
} from '@heroui/react'
import { Eye, EyeOff, Mail, Lock, User } from 'lucide-react'
import { useForm } from 'react-hook-form'
import { useAuthStore } from '@/stores/authStore'

interface LoginForm {
  username: string
  password: string
}

interface RegisterForm {
  username: string
  email: string
  password: string
  confirmPassword: string
  full_name?: string
}

const LoginPage = () => {
  const [isVisible, setIsVisible] = useState(false)
  const [activeTab, setActiveTab] = useState('login')
  const navigate = useNavigate()
  const { login, register, isLoading } = useAuthStore()

  const loginForm = useForm<LoginForm>()
  const registerForm = useForm<RegisterForm>()

  const onLogin = async (data: LoginForm) => {
    const success = await login(data.username, data.password)
    if (success) {
      navigate('/dashboard')
    }
  }

  const onRegister = async (data: RegisterForm) => {
    if (data.password !== data.confirmPassword) {
      registerForm.setError('confirmPassword', {
        message: '密码不匹配'
      })
      return
    }

    const success = await register({
      username: data.username,
      email: data.email,
      password: data.password,
      full_name: data.full_name
    })

    if (success) {
      setActiveTab('login')
      registerForm.reset()
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="flex flex-col gap-3 text-center">
          <h1 className="text-2xl font-bold">知识库助手</h1>
          <p className="text-default-500">智能文档管理与问答系统</p>
        </CardHeader>
        <CardBody>
          <Tabs 
            selectedKey={activeTab} 
            onSelectionChange={(key) => setActiveTab(key as string)}
            className="w-full"
          >
            <Tab key="login" title="登录">
              <form onSubmit={loginForm.handleSubmit(onLogin)} className="space-y-4">
                <Input
                  label="用户名"
                  placeholder="请输入用户名"
                  startContent={<User size={16} />}
                  {...loginForm.register('username', { required: '请输入用户名' })}
                  errorMessage={loginForm.formState.errors.username?.message}
                />
                
                <Input
                  label="密码"
                  placeholder="请输入密码"
                  startContent={<Lock size={16} />}
                  endContent={
                    <button
                      className="focus:outline-none"
                      type="button"
                      onClick={() => setIsVisible(!isVisible)}
                    >
                      {isVisible ? <EyeOff size={16} /> : <Eye size={16} />}
                    </button>
                  }
                  type={isVisible ? "text" : "password"}
                  {...loginForm.register('password', { required: '请输入密码' })}
                  errorMessage={loginForm.formState.errors.password?.message}
                />
                
                <Button 
                  type="submit" 
                  color="primary" 
                  className="w-full"
                  isLoading={isLoading}
                >
                  登录
                </Button>
              </form>
            </Tab>
            
            <Tab key="register" title="注册">
              <form onSubmit={registerForm.handleSubmit(onRegister)} className="space-y-4">
                <Input
                  label="用户名"
                  placeholder="请输入用户名"
                  startContent={<User size={16} />}
                  {...registerForm.register('username', { required: '请输入用户名' })}
                  errorMessage={registerForm.formState.errors.username?.message}
                />
                
                <Input
                  label="邮箱"
                  placeholder="请输入邮箱"
                  type="email"
                  startContent={<Mail size={16} />}
                  {...registerForm.register('email', { 
                    required: '请输入邮箱',
                    pattern: {
                      value: /^\S+@\S+$/i,
                      message: '邮箱格式不正确'
                    }
                  })}
                  errorMessage={registerForm.formState.errors.email?.message}
                />
                
                <Input
                  label="姓名"
                  placeholder="请输入姓名（可选）"
                  {...registerForm.register('full_name')}
                />
                
                <Input
                  label="密码"
                  placeholder="请输入密码"
                  startContent={<Lock size={16} />}
                  type="password"
                  {...registerForm.register('password', { 
                    required: '请输入密码',
                    minLength: {
                      value: 6,
                      message: '密码至少6位'
                    }
                  })}
                  errorMessage={registerForm.formState.errors.password?.message}
                />
                
                <Input
                  label="确认密码"
                  placeholder="请再次输入密码"
                  startContent={<Lock size={16} />}
                  type="password"
                  {...registerForm.register('confirmPassword', { required: '请确认密码' })}
                  errorMessage={registerForm.formState.errors.confirmPassword?.message}
                />
                
                <Button 
                  type="submit" 
                  color="primary" 
                  className="w-full"
                  isLoading={isLoading}
                >
                  注册
                </Button>
              </form>
            </Tab>
          </Tabs>
        </CardBody>
      </Card>
    </div>
  )
}

export default LoginPage
