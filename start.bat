@echo off
echo 启动知识库助手项目...

REM 检查Docker是否运行
docker info >nul 2>&1
if errorlevel 1 (
    echo 错误: Docker未运行，请先启动Docker
    pause
    exit /b 1
)

REM 创建环境变量文件
if not exist .env (
    copy .env.example .env
    echo 已创建 .env 文件
)

REM 启动数据库和向量数据库
echo 启动数据库服务...
docker-compose up -d postgres redis etcd minio milvus

REM 等待数据库启动
echo 等待数据库启动...
timeout /t 10 /nobreak >nul

echo 服务启动完成！
echo 前端地址: http://localhost:5173
echo 后端API: http://localhost:8000
echo API文档: http://localhost:8000/docs
echo.
echo 请在新的终端窗口中运行以下命令启动后端：
echo cd backend
echo pip install -r requirements.txt
echo python init_vector_db.py
echo uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
echo.
echo 请在另一个新的终端窗口中运行以下命令启动前端：
echo cd frontend
echo npm install
echo npm run dev
echo.
pause
