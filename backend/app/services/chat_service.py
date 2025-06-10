from typing import Optional, List, AsyncGenerator
from sqlalchemy.orm import Session
from app.models.chat import Chat, Message
from app.schemas.chat import ChatCreate, ChatRequest, ChatResponse, DocumentSource
from app.services.document_search_service import DocumentSearchService
import httpx
import json
import asyncio
import os

class AIConfig:
    """AI API配置类"""
    API_URL = "https://api.bigmodel.org/v1/chat/completions"
    API_KEY = os.getenv("AI_API_KEY", "sk-cmqi8iWV0aS8oNE2OR71OhiWwTUtXV9BsNevqaua2Bdd27NV")
    MODEL = "o1-mini"
    MAX_RETRIES = 3
    TIMEOUT = 30.0
    STREAM_TIMEOUT = 60.0

class ChatService:
    """聊天服务类"""

    def __init__(self, db: Session):
        self.db = db
        self.document_search_service = DocumentSearchService(db)
    
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

        # 获取文档上下文
        document_context = ""
        document_sources = []

        if chat_request.use_documents:
            # 获取文档内容作为上下文
            document_context = self.document_search_service.get_documents_content_for_context(
                user_id=user_id,
                document_ids=chat_request.document_ids
            )

            # 获取文档来源信息
            document_sources = self.document_search_service.search_documents_by_user(
                user_id=user_id,
                query=chat_request.message,
                document_ids=chat_request.document_ids
            )

        # 构建包含文档上下文的消息
        enhanced_message = self._build_enhanced_message(chat_request.message, document_context)

        # 生成AI回复（集成真正的AI模型）
        ai_response = await self._generate_ai_response(enhanced_message)

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
            sources=document_sources if document_sources else None
        )

    def _build_enhanced_message(self, user_message: str, document_context: str) -> str:
        """构建包含文档上下文的增强消息"""
        if not document_context.strip():
            return user_message

        enhanced_message = f"""基于以下文档内容回答用户问题：

{document_context}

用户问题：{user_message}

请基于上述文档内容回答问题。如果文档中没有相关信息，请说明并提供一般性回答。"""

        return enhanced_message

    async def _generate_ai_response(self, user_message: str, max_retries: int = None) -> str:
        """生成AI回复（集成真正的AI模型，带重试机制）"""
        if max_retries is None:
            max_retries = AIConfig.MAX_RETRIES

        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient() as client:
                    headers = {
                        'Content-Type': 'application/json',
                        'Authorization': f'Bearer {AIConfig.API_KEY}'
                    }

                    payload = {
                        'model': AIConfig.MODEL,
                        'messages': [{'role': 'user', 'content': user_message}],
                        'stream': False  # 非流式调用，获取完整回复
                    }

                    response = await client.post(
                        AIConfig.API_URL,
                        headers=headers,
                        json=payload,
                        timeout=AIConfig.TIMEOUT
                    )

                    if response.status_code == 200:
                        data = response.json()
                        if data.get('choices') and len(data['choices']) > 0:
                            return data['choices'][0]['message']['content']

                    # 如果API调用失败但不是最后一次尝试，继续重试
                    if attempt < max_retries - 1:
                        print(f"AI API调用失败，状态码: {response.status_code}，正在重试... (尝试 {attempt + 1}/{max_retries})")
                        await asyncio.sleep(1 * (attempt + 1))  # 指数退避
                        continue

                    # 最后一次尝试失败，返回错误信息
                    return "抱歉，AI服务暂时不可用，请稍后重试。"

            except Exception as e:
                print(f"AI API调用失败: {e}")
                if attempt < max_retries - 1:
                    print(f"正在重试... (尝试 {attempt + 1}/{max_retries})")
                    await asyncio.sleep(1 * (attempt + 1))  # 指数退避
                    continue
                else:
                    # 如果所有重试都失败，使用简单回复作为后备
                    if "你好" in user_message or "hello" in user_message.lower():
                        return "您好！我是知识库助手，很高兴为您服务。请问有什么可以帮助您的吗？（注：AI服务暂时不可用，这是后备回复）"
                    elif "文档" in user_message:
                        return "我可以帮您搜索和分析已上传的文档。请告诉我您想了解什么内容？（注：AI服务暂时不可用，这是后备回复）"
                    else:
                        return f"我收到了您的消息：\"{user_message}\"。抱歉，AI服务暂时不可用，请稍后重试。"

    async def process_message_stream(self, chat_request: ChatRequest, user_id: int) -> AsyncGenerator[str, None]:
        """处理消息并返回流式响应"""
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
        self.db.commit()

        # 获取文档上下文
        document_context = ""
        if chat_request.use_documents:
            document_context = self.document_search_service.get_documents_content_for_context(
                user_id=user_id,
                document_ids=chat_request.document_ids
            )

        # 构建包含文档上下文的消息
        enhanced_message = self._build_enhanced_message(chat_request.message, document_context)

        # 流式生成AI回复
        full_response = ""
        async for chunk in self._generate_ai_response_stream(enhanced_message):
            full_response += chunk
            yield f"data: {json.dumps({'content': chunk, 'chat_id': chat_id})}\n\n"

        # 保存完整的AI回复
        ai_message = Message(
            content=full_response,
            role="assistant",
            chat_id=chat_id
        )
        self.db.add(ai_message)
        self.db.commit()

        # 发送结束信号
        yield f"data: {json.dumps({'done': True, 'chat_id': chat_id})}\n\n"

    async def _generate_ai_response_stream(self, user_message: str, max_retries: int = None) -> AsyncGenerator[str, None]:
        """生成流式AI回复（集成真正的AI模型，带重试机制）"""
        if max_retries is None:
            max_retries = AIConfig.MAX_RETRIES

        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient() as client:
                    headers = {
                        'Content-Type': 'application/json',
                        'Authorization': f'Bearer {AIConfig.API_KEY}'
                    }

                    payload = {
                        'model': AIConfig.MODEL,
                        'messages': [{'role': 'user', 'content': user_message}],
                        'stream': True
                    }

                    async with client.stream(
                        'POST',
                        AIConfig.API_URL,
                        headers=headers,
                        json=payload,
                        timeout=AIConfig.STREAM_TIMEOUT
                    ) as response:
                        if response.status_code == 200:
                            async for line in response.aiter_lines():
                                if line.startswith('data: '):
                                    try:
                                        data_str = line[6:]  # 移除 'data: ' 前缀
                                        if data_str == '[DONE]':
                                            return  # 成功完成，退出函数
                                        data = json.loads(data_str)
                                        if data.get('choices') and len(data['choices']) > 0:
                                            delta = data['choices'][0].get('delta', {})
                                            content = delta.get('content', '')
                                            if content:
                                                yield content
                                    except json.JSONDecodeError:
                                        continue
                            return  # 成功完成，退出函数
                        else:
                            # API调用失败，如果不是最后一次尝试则重试
                            if attempt < max_retries - 1:
                                print(f"AI流式API调用失败，状态码: {response.status_code}，正在重试... (尝试 {attempt + 1}/{max_retries})")
                                await asyncio.sleep(1 * (attempt + 1))
                                continue

            except Exception as e:
                print(f"AI流式API调用失败: {e}")
                if attempt < max_retries - 1:
                    print(f"正在重试... (尝试 {attempt + 1}/{max_retries})")
                    await asyncio.sleep(1 * (attempt + 1))
                    continue

        # 所有重试都失败，使用后备方案
        print("AI流式API所有重试都失败，使用后备方案")
        full_response = await self._generate_ai_response(user_message, max_retries=1)

        # 模拟流式输出后备回复
        for i in range(0, len(full_response), 3):
            chunk = full_response[i:i+3]
            yield chunk
            await asyncio.sleep(0.1)  # 模拟网络延迟
