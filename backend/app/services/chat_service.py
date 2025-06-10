from typing import Optional, List, AsyncGenerator
from sqlalchemy.orm import Session
from app.models.chat import Chat, Message
from app.schemas.chat import ChatCreate, ChatRequest, ChatResponse
from app.schemas.document import DocumentSearchRequest
# 避免循环导入，在方法内部导入
from app.services.embedding_service import embedding_service
import httpx
import json
import asyncio
import os
import logging

logger = logging.getLogger(__name__)

class AIConfig:
    """AI API配置类"""
    API_URL = "https://api.ai-gaochao.cn/v1/chat/completions"
    API_KEY = os.getenv("AI_API_KEY", "sk-iKe0C3XVddfE5qAF1790FaC14463453e8dFb4c7c1b0bF60b")
    MODEL = "gpt-3.5-turbo"
    MAX_RETRIES = 3
    TIMEOUT = 30.0
    STREAM_TIMEOUT = 60.0

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
        
        # 搜索相关文档
        relevant_docs = await self._search_relevant_documents(chat_request.message, user_id)

        # 生成AI回复（集成真正的AI模型和文档上下文）
        ai_response = await self._generate_ai_response(chat_request.message, relevant_docs)
        
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
    
    async def _generate_ai_response(self, user_message: str, relevant_docs: List[str] = None, max_retries: int = None) -> str:
        """生成AI回复（集成真正的AI模型和文档上下文，带重试机制）"""
        if max_retries is None:
            max_retries = AIConfig.MAX_RETRIES

        # 构建包含文档上下文的提示
        enhanced_message = self._build_context_message(user_message, relevant_docs)

        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient() as client:
                    headers = {
                        'Content-Type': 'application/json',
                        'Authorization': f'Bearer {AIConfig.API_KEY}'
                    }

                    payload = {
                        'model': AIConfig.MODEL,
                        'messages': [{'role': 'user', 'content': enhanced_message}],
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

        # 搜索相关文档
        relevant_docs = await self._search_relevant_documents(chat_request.message, user_id)

        # 流式生成AI回复
        full_response = ""
        async for chunk in self._generate_ai_response_stream(chat_request.message, relevant_docs):
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

    async def _generate_ai_response_stream(self, user_message: str, relevant_docs: List[str] = None, max_retries: int = None) -> AsyncGenerator[str, None]:
        """生成流式AI回复（集成真正的AI模型和文档上下文，带重试机制）"""
        if max_retries is None:
            max_retries = AIConfig.MAX_RETRIES

        # 构建包含文档上下文的提示
        enhanced_message = self._build_context_message(user_message, relevant_docs)

        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient() as client:
                    headers = {
                        'Content-Type': 'application/json',
                        'Authorization': f'Bearer {AIConfig.API_KEY}'
                    }

                    payload = {
                        'model': AIConfig.MODEL,
                        'messages': [{'role': 'user', 'content': enhanced_message}],
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
        full_response = await self._generate_ai_response(user_message, relevant_docs, max_retries=1)

        # 模拟流式输出后备回复
        for i in range(0, len(full_response), 3):
            chunk = full_response[i:i+3]
            yield chunk
            await asyncio.sleep(0.1)  # 模拟网络延迟

    async def _search_relevant_documents(self, query: str, user_id: int, limit: int = 5) -> List[str]:
        """搜索相关文档"""
        try:
            # 动态导入避免循环依赖
            from app.services.document_service import DocumentService

            document_service = DocumentService(self.db)

            search_request = DocumentSearchRequest(
                query=query,
                limit=limit,
                threshold=0.6
            )

            search_results = document_service.search_documents(search_request, user_id)

            # 提取文档内容
            relevant_docs = []
            for result in search_results:
                relevant_docs.append(f"文档《{result.title}》: {result.content}")

            logger.info(f"Found {len(relevant_docs)} relevant documents for query: {query[:50]}...")
            return relevant_docs

        except Exception as e:
            logger.error(f"Failed to search relevant documents: {e}")
            return []

    def _build_context_message(self, user_message: str, relevant_docs: List[str] = None) -> str:
        """构建包含文档上下文的消息"""
        if not relevant_docs:
            return user_message

        context = "\n\n".join(relevant_docs)

        enhanced_message = f"""基于以下文档内容回答用户问题：

相关文档内容：
{context}

用户问题：{user_message}

请基于上述文档内容回答问题。如果文档中没有相关信息，请说明并提供一般性回答。"""

        return enhanced_message
