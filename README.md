# Knowledge Base Assistant

一个基于FastAPI和React的智能知识库助手系统。

## 技术栈

### 后端
- **FastAPI**: 现代、快速的Web框架
- **PostgreSQL**: 关系数据库
- **Milvus**: 向量数据库
- **SQLAlchemy**: ORM
- **Alembic**: 数据库迁移
- **JWT**: 身份认证

### 前端
- **React**: 用户界面库
- **Vite**: 构建工具
- **HeroUI**: 组件库
- **Axios**: HTTP客户端

## 功能特性

- 🔐 用户身份验证与授权
- 📄 文档上传与处理（PDF、Word、TXT等）
- 🔍 智能向量搜索
- 🤖 AI问答助手
- 📊 文档管理界面
- 🚀 Rerank模型优化搜索结果

## 快速开始

### 环境要求
- Docker & Docker Compose
- Node.js 18+
- Python 3.9+

### 一键启动（推荐）

#### Linux/macOS
```bash
chmod +x start.sh
./start.sh
```

#### Windows
```bash
start.bat
```

### 手动启动

1. 启动数据库服务
```bash
docker-compose up -d postgres redis etcd minio milvus
```

2. 启动后端服务
```bash
cd backend
pip install -r requirements.txt
# 创建超级用户（首次运行）
python create_superuser.py
# 启动API服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

3. 启动前端服务
```bash
cd frontend
npm install
npm run dev
```

4. 访问应用
- 前端: http://localhost:3000
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs

### 默认账户
- 用户名: `admin`
- 密码: `admin123`

## 项目结构

```
├── backend/                 # FastAPI后端
│   ├── app/
│   │   ├── api/            # API路由
│   │   ├── core/           # 核心配置
│   │   ├── models/         # 数据模型
│   │   ├── services/       # 业务逻辑
│   │   └── utils/          # 工具函数
│   └── requirements.txt
├── frontend/               # React前端
│   ├── src/
│   │   ├── components/     # 组件
│   │   ├── pages/          # 页面
│   │   └── services/       # API服务
│   └── package.json
├── docker-compose.yml      # 容器编排
└── README.md
```

## 环境变量

创建 `.env` 文件：

```env
# 数据库配置
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=knowledge_base
DATABASE_URL=postgresql://postgres:password@localhost:5432/knowledge_base

# Milvus配置
MILVUS_HOST=localhost
MILVUS_PORT=19530

# JWT配置
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 其他配置
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=10485760  # 10MB
```

## API文档

启动后端服务后，访问 http://localhost:8000/docs 查看完整的API文档。

## 贡献

欢迎提交Issue和Pull Request！

## 许可证

MIT License
