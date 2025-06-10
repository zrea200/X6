#!/bin/bash

echo "启动知识库助手项目..."

# 检查Docker是否运行
if ! docker info > /dev/null 2>&1; then
    echo "错误: Docker未运行，请先启动Docker"
    exit 1
fi

# 创建环境变量文件
if [ ! -f .env ]; then
    cp .env.example .env
    echo "已创建 .env 文件"
fi

# 启动数据库和向量数据库
echo "启动数据库服务..."
docker-compose up -d postgres redis etcd minio milvus

# 等待数据库启动
echo "等待数据库启动..."
sleep 10

# 启动后端服务
echo "启动后端服务..."
cd backend
if [ ! -d "venv" ]; then
    echo "创建Python虚拟环境..."
    python -m venv venv
fi

source venv/bin/activate
pip install -r requirements.txt

# 验证设置
echo "验证Milvus向量搜索功能..."
python verify_setup.py

# 初始化向量数据库
echo "初始化向量数据库..."
python init_vector_db.py

# 启动FastAPI服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

cd ..

# 启动前端服务
echo "启动前端服务..."
cd frontend
npm install
npm run dev &
FRONTEND_PID=$!

cd ..

echo "服务启动完成！"
echo "前端地址: http://localhost:5173"
echo "后端API: http://localhost:8000"
echo "API文档: http://localhost:8000/docs"
echo ""
echo "按 Ctrl+C 停止所有服务"

# 等待用户中断
trap "echo '正在停止服务...'; kill $BACKEND_PID $FRONTEND_PID; docker-compose down; exit" INT
wait
