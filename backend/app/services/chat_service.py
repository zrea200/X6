from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.chat import Chat, Message
from app.schemas.chat import ChatCreate, ChatRequest, ChatResponse

class ChatService:
    """聊天服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_chat(self, chat_id: int) -> Optional[Chat]:
        """根据ID获取聊天会话"""
        return self.db.query(Chat).filter(Chat.id == chat_id).first()
    
    def get_chats_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Chat]:
        """获取用户的聊天会话列表"""
        return (
            self.db.query(Chat)
            .filter(Chat.user_id == user_id, Chat.is_active == True)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def create_chat(self, chat_create: ChatCreate, user_id: int) -> Chat:
        """创建聊天会话"""
        chat = Chat(
            title=chat_create.title,
            description=chat_create.description,
            user_id=user_id
        )
        
        self.db.add(chat)
        self.db.commit()
        self.db.refresh(chat)
        return chat
    
    def delete_chat(self, chat_id: int) -> bool:
        """删除聊天会话"""
        chat = self.get_chat(chat_id)
        if not chat:
            return False
        
        chat.is_active = False
        self.db.commit()
        return True
    
    async def process_message(self, chat_request: ChatRequest, user_id: int) -> ChatResponse:
        """处理消息"""
        # 如果没有指定chat_id，创建新的聊天会话
        if not chat_request.chat_id:
            chat_create = ChatCreate(title="新对话")
            chat = self.create_chat(chat_create, user_id)
            chat_id = chat.id
        else:
            chat_id = chat_request.chat_id
            chat = self.get_chat(chat_id)
            if not chat or chat.user_id != user_id:
                raise ValueError("Chat not found or access denied")
        
        # 保存用户消息
        user_message = Message(
            content=chat_request.message,
            role="user",
            chat_id=chat_id
        )
        self.db.add(user_message)
        
        # 生成AI回复（这里是简单的回复，后续可以集成真正的AI模型）
        ai_response = self._generate_ai_response(chat_request.message)
        
        # 保存AI回复
        ai_message = Message(
            content=ai_response,
            role="assistant",
            chat_id=chat_id
        )
        self.db.add(ai_message)
        
        self.db.commit()
        
        return ChatResponse(
            message=ai_response,
            chat_id=chat_id,
            sources=[]  # 后续添加文档引用
        )
    
    def _generate_ai_response(self, user_message: str) -> str:
        """生成AI回复（临时实现）"""
        # 这里是一个简单的回复逻辑，后续需要集成真正的AI模型
        if "你好" in user_message or "hello" in user_message.lower():
            return "您好！我是知识库助手，很高兴为您服务。请问有什么可以帮助您的吗？"
        elif "文档" in user_message:
            return "我可以帮您搜索和分析已上传的文档。请告诉我您想了解什么内容？"
        else:
            return f"我收到了您的消息：\"{user_message}\"。这是一个测试回复，后续会集成真正的AI模型来提供更智能的回答。"
