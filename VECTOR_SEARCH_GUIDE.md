# Milvus向量搜索功能使用指南

## 🎯 功能概述

本项目现已完整集成Milvus向量数据库，实现了智能文档搜索和AI问答功能。

## 🚀 新增功能

### 1. **文档向量化**
- 自动将上传的文档转换为向量表示
- 支持文本分块和重叠处理
- 使用sentence-transformers模型生成高质量嵌入

### 2. **智能搜索**
- 基于语义相似度的文档搜索
- 支持自然语言查询
- 可配置的相似度阈值

### 3. **AI问答增强**
- 聊天时自动搜索相关文档
- 基于文档内容生成回答
- 上下文感知的对话体验

### 4. **重排序优化**
- 使用CrossEncoder模型优化搜索结果
- 提高搜索准确性

## 🛠️ 技术架构

```
用户查询 → 向量化 → Milvus搜索 → 重排序 → AI生成回答
    ↓
文档上传 → 文本提取 → 分块 → 向量化 → 存储到Milvus
```

### 核心组件

1. **VectorService** (`backend/app/services/vector_service.py`)
   - Milvus数据库连接和操作
   - 向量存储、搜索、删除

2. **EmbeddingService** (`backend/app/services/embedding_service.py`)
   - 文本嵌入生成
   - 重排序功能
   - 文本分块处理

3. **DocumentService** (更新)
   - 集成向量化处理
   - 文档搜索功能

4. **ChatService** (更新)
   - 集成文档检索
   - 上下文感知回答

## 📋 使用步骤

### 1. 启动服务

```bash
# Linux/macOS
./start.sh

# Windows
start.bat
```

启动脚本会自动：
- 启动Milvus等数据库服务
- 初始化向量数据库集合
- 启动后端和前端服务

### 2. 上传文档

1. 登录系统
2. 进入"文档管理"页面
3. 上传PDF、Word、TXT或Markdown文件
4. 系统自动提取文本并向量化

### 3. 智能搜索

#### 方式一：直接搜索文档
```bash
# API调用示例
POST /api/v1/documents/search
{
  "query": "Python编程相关内容",
  "limit": 10,
  "threshold": 0.7
}
```

#### 方式二：通过聊天获取答案
1. 进入"聊天"页面
2. 提问相关问题
3. AI会自动搜索相关文档并基于内容回答

## 🔧 配置说明

### 环境变量配置

```env
# Milvus配置
MILVUS_HOST=localhost
MILVUS_PORT=19530
MILVUS_COLLECTION_NAME=documents

# AI模型配置
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
RERANK_MODEL=cross-encoder/ms-marco-MiniLM-L-6-v2
CHUNK_SIZE=512
CHUNK_OVERLAP=50
```

### 模型说明

- **嵌入模型**: `all-MiniLM-L6-v2` (384维)
  - 轻量级、高效
  - 支持多语言
  - 适合文档检索

- **重排序模型**: `ms-marco-MiniLM-L-6-v2`
  - 优化搜索结果排序
  - 提高相关性

## 🧪 测试功能

### 初始化向量数据库
```bash
cd backend
python init_vector_db.py
```

### 测试向量搜索
```bash
cd backend
```

## 📊 API接口

### 文档搜索
```http
POST /api/v1/documents/search
Content-Type: application/json

{
  "query": "搜索关键词",
  "limit": 10,
  "threshold": 0.7
}
```

### 重新向量化文档
```http
POST /api/v1/documents/{document_id}/vectorize
```

### 重新处理文档
```http
POST /api/v1/documents/{document_id}/reprocess
```

## 🔍 工作流程

### 文档处理流程
1. 用户上传文档
2. 提取文本内容
3. 文本分块（512字符，50字符重叠）
4. 生成嵌入向量（384维）
5. 存储到Milvus集合
6. 更新文档状态

### 搜索流程
1. 用户输入查询
2. 查询文本向量化
3. Milvus相似度搜索
4. 结果重排序（可选）
5. 返回相关文档片段

### AI问答流程
1. 用户提问
2. 自动搜索相关文档
3. 构建包含文档上下文的提示
4. AI生成基于文档的回答
5. 返回结果给用户

## 🚨 注意事项

1. **首次启动**：需要下载AI模型，可能需要几分钟
2. **内存需求**：建议至少8GB RAM
3. **存储空间**：向量数据会占用额外存储空间
4. **网络连接**：首次运行需要下载模型文件

## 🔧 故障排除

### Milvus连接失败
```bash
# 检查Milvus服务状态
docker ps | grep milvus

# 重启Milvus服务
docker-compose restart milvus
```

### 模型下载失败
```bash
# 手动下载模型
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"
```

### 向量搜索无结果
1. 确认文档已成功向量化（`is_vectorized=True`）
2. 调整搜索阈值（降低threshold值）
3. 检查查询语言与文档语言是否匹配

## 📈 性能优化

1. **批量处理**：一次处理多个文档
2. **索引优化**：根据数据量调整Milvus索引参数
3. **缓存策略**：缓存常用查询的嵌入向量
4. **异步处理**：文档向量化使用后台任务

## 🎉 功能特色

- ✅ **即插即用**：无需额外配置，开箱即用
- ✅ **多语言支持**：支持中英文文档和查询
- ✅ **实时搜索**：毫秒级向量搜索响应
- ✅ **智能问答**：基于文档内容的AI回答
- ✅ **可扩展性**：支持大规模文档库
- ✅ **高准确性**：重排序模型优化结果

现在您的知识库助手已经具备了真正的智能搜索能力！🚀
