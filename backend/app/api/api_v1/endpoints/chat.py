from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user
from app.schemas.chat import Chat, ChatCreate, ChatRequest, ChatResponse
from app.services.chat_service import ChatService
from app.services.document_search_service import DocumentSearchService
from app.models.user import User

router = APIRouter()

@router.post("/", response_model=Chat)
async def create_chat(
    chat_create: ChatCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建新的聊天会话"""
    chat_service = ChatService(db)
    chat = chat_service.create_chat(chat_create, current_user.id)
    return chat

@router.get("/", response_model=List[Chat])
async def get_chats(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户的聊天会话列表"""
    chat_service = ChatService(db)
    chats = chat_service.get_chats_by_user(current_user.id, skip, limit)
    return chats

@router.get("/{chat_id}", response_model=Chat)
async def get_chat(
    chat_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取指定聊天会话"""
    chat_service = ChatService(db)
    chat = chat_service.get_chat(chat_id)
    
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )
    
    # 检查权限
    if chat.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return chat

@router.post("/message", response_model=ChatResponse)
async def send_message(
    chat_request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """发送消息"""
    chat_service = ChatService(db)

    try:
        response = await chat_service.process_message(chat_request, current_user.id)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process message: {str(e)}"
        )

@router.post("/message/stream")
async def send_message_stream(
    chat_request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """发送消息（流式响应）"""
    chat_service = ChatService(db)

    try:
        return StreamingResponse(
            chat_service.process_message_stream(chat_request, current_user.id),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*",
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process message: {str(e)}"
        )

@router.delete("/{chat_id}")
async def delete_chat(
    chat_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除聊天会话"""
    chat_service = ChatService(db)
    chat = chat_service.get_chat(chat_id)
    
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )
    
    # 检查权限
    if chat.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    success = chat_service.delete_chat(chat_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete chat"
        )
    
    return {"message": "Chat deleted successfully"}

@router.get("/documents")
async def get_chat_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户可用于聊天的文档列表"""
    document_search_service = DocumentSearchService(db)
    documents = document_search_service.get_user_documents_summary(current_user.id)
    return {"documents": documents}
