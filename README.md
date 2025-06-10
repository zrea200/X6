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
- 📄 文档上传与处理（PDF、Word、TXT、Markdown等）
- 🔍 **智能向量搜索** - 基于Milvus的语义搜索
- 🤖 **AI问答助手** - 集成文档上下文的智能回答
- 📊 文档管理界面
- 🚀 **Rerank模型优化搜索结果** - 提高搜索准确性
- 🧠 **文本嵌入** - sentence-transformers模型
- ⚡ **实时向量搜索** - 毫秒级响应

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
# 初始化向量数据库（首次运行）
python init_vector_db.py
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
- 前端: http://localhost:5173
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs
- Milvus管理: http://localhost:9091/healthz

### 默认账户
- 用户名: `admin`
- 密码: `admin123`

## 项目结构

```
├── backend/                 # FastAPI后端
│   ├── app/
│   │   ├── api/            # API路由层
│   │   │   └── api_v1/     # v1版本API
│   │   │       └── endpoints/ # 具体端点
│   │   ├── core/           # 核心配置
│   │   ├── models/         # 数据模型（SQLAlchemy）
│   │   ├── schemas/        # Pydantic模式
│   │   ├── services/       # 业务逻辑层
│   │   └── utils/          # 工具函数
│   ├── requirements.txt    # Python依赖
│   └── Dockerfile         # 后端容器化
├── frontend/               # React前端
│   ├── src/
│   │   ├── components/     # 可复用组件
│   │   ├── pages/          # 页面组件
│   │   ├── services/       # API服务
│   │   ├── stores/         # 状态管理
│   │   ├── types/          # TypeScript类型
│   │   └── utils/          # 工具函数
│   ├── package.json       # Node.js依赖
│   └── Dockerfile         # 前端容器化
├── docker-compose.yml     # 容器编排
└── 启动脚本
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

## 🔍 向量搜索功能

### 智能文档搜索
1. 上传文档后，系统自动进行向量化处理
2. 支持自然语言查询，如"Python编程相关内容"
3. 基于语义相似度返回最相关的文档片段

### AI问答增强
1. 聊天时自动搜索相关文档
2. 基于文档内容生成准确回答
3. 支持上下文感知的多轮对话

### 测试向量搜索
```bash
cd backend
python test_vector_search.py
```

## API文档

启动后端服务后，访问 http://localhost:8000/docs 查看完整的API文档。

### 新增API端点
- `POST /api/v1/documents/search` - 搜索文档
- `POST /api/v1/documents/{id}/vectorize` - 重新向量化文档

## 贡献

欢迎提交Issue和Pull Request！

## 许可证

MIT License
