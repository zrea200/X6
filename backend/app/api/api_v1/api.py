from fastapi import APIRouter
from app.api.api_v1.endpoints import auth, users, documents, chat

api_router = APIRouter()

# 包含各个端点路由
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
