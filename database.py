"""Business Gemini Pool 数据库管理器
负责管理历史会话、消息和用户数据
"""

import sqlite3
import json
import uuid
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import threading
import os

# 配置日志
logger = logging.getLogger('gemini_pool.database')

@dataclass
class Conversation:
    """会话数据类"""
    id: Optional[int] = None
    session_id: str = ""
    title: str = ""
    model: str = "gemini-enterprise"
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    message_count: int = 0
    is_active: bool = False
    gemini_session_data: Optional[str] = None
    user_id: str = ""
    metadata: Optional[Dict] = None

@dataclass
class Message:
    """消息数据类"""
    id: Optional[int] = None
    conversation_id: int = 0
    role: str = ""  # 'user' or 'assistant'
    content: str = ""
    timestamp: Optional[str] = None
    message_type: str = "text"  # 'text', 'image', 'file'
    file_metadata: Optional[Dict] = None
    token_count: int = 0
    model: str = ""

@dataclass
class Image:
    """图片数据类"""
    id: Optional[int] = None
    filename: str = ""
    original_filename: Optional[str] = None
    file_path: str = ""
    file_size: int = 0
    image_width: Optional[int] = None
    image_height: Optional[int] = None
    mime_type: str = "image/png"
    title: Optional[str] = None
    description: Optional[str] = None
    prompt: Optional[str] = None
    conversation_id: Optional[int] = None
    message_id: Optional[int] = None
    user_id: str = ""
    tags: Optional[List[str]] = None
    metadata: Optional[Dict] = None
    created_at: Optional[str] = None

class ConversationManager:
    """会话管理器"""

    def __init__(self, db_path: Optional[str] = None):
        """初始化数据库连接"""
        if db_path is None:
            db_path = Path(__file__).parent / "conversations.db"

        self.db_path = db_path
        self.lock = threading.Lock()
        self._init_database()

    def _init_database(self):
        """初始化数据库结构"""
        try:
            # 读取schema文件
            schema_path = Path(__file__).parent / "schema.sql"
            if schema_path.exists():
                with open(schema_path, 'r', encoding='utf-8') as f:
                    schema_sql = f.read()
            else:
                logger.error("schema.sql文件不存在")
                return

            with sqlite3.connect(self.db_path) as conn:
                conn.executescript(schema_sql)
                conn.commit()
                logger.info("数据库初始化完成")

        except Exception as e:
            logger.error(f"数据库初始化失败: {e}")
            raise

    def get_user_id(self, api_key: str) -> str:
        """基于API key生成用户ID"""
        # 使用API key的hash作为用户ID，保护隐私
        import hashlib
        return hashlib.sha256(api_key.encode()).hexdigest()[:32]

    def create_conversation(self, title: str, model: str = "gemini-enterprise",
                          user_id: str = "", gemini_session_data: Optional[Dict] = None) -> Conversation:
        """创建新会话"""
        session_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        conversation = Conversation(
            session_id=session_id,
            title=title,
            model=model,
            created_at=now,
            updated_at=now,
            is_active=False,
            gemini_session_data=json.dumps(gemini_session_data) if gemini_session_data else None,
            user_id=user_id,
            metadata={}
        )

        with self.lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO conversations
                        (session_id, title, model, created_at, updated_at, is_active,
                         gemini_session_data, user_id, metadata)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        conversation.session_id, conversation.title, conversation.model,
                        conversation.created_at, conversation.updated_at, conversation.is_active,
                        conversation.gemini_session_data, conversation.user_id,
                        json.dumps(conversation.metadata)
                    ))

                    conversation.id = cursor.lastrowid
                    conn.commit()
                    logger.info(f"创建新会话: {conversation.session_id}, 标题: {conversation.title}")

            except Exception as e:
                logger.error(f"创建会话失败: {e}")
                raise

        return conversation

    def get_conversation(self, conversation_id: int, user_id: str) -> Optional[Conversation]:
        """获取指定会话"""
        with self.lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    conn.row_factory = sqlite3.Row
                    cursor = conn.cursor()

                    cursor.execute('''
                        SELECT * FROM conversations
                        WHERE id = ? AND user_id = ?
                    ''', (conversation_id, user_id))

                    row = cursor.fetchone()
                    if row:
                        return Conversation(
                            id=row['id'],
                            session_id=row['session_id'],
                            title=row['title'],
                            model=row['model'],
                            created_at=row['created_at'],
                            updated_at=row['updated_at'],
                            message_count=row['message_count'],
                            is_active=bool(row['is_active']),
                            gemini_session_data=row['gemini_session_data'],
                            user_id=row['user_id'],
                            metadata=json.loads(row['metadata']) if row['metadata'] else {}
                        )
                    return None

            except Exception as e:
                logger.error(f"获取会话失败: {e}")
                return None

    def get_conversations(self, user_id: str, limit: int = 50, offset: int = 0) -> List[Conversation]:
        """获取用户的会话列表"""
        with self.lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    conn.row_factory = sqlite3.Row
                    cursor = conn.cursor()

                    cursor.execute('''
                        SELECT c.* FROM conversation_summary c
                        WHERE c.user_id = ?
                        ORDER BY c.updated_at DESC
                        LIMIT ? OFFSET ?
                    ''', (user_id, limit, offset))

                    conversations = []
                    for row in cursor.fetchall():
                        conversations.append(Conversation(
                            id=row['id'],
                            session_id=row['session_id'],
                            title=row['title'],
                            model=row['model'],
                            created_at=row['created_at'],
                            updated_at=row['updated_at'],
                            message_count=row['message_count'],
                            is_active=bool(row['is_active']),
                            user_id=row['user_id']
                        ))

                    return conversations

            except Exception as e:
                logger.error(f"获取会话列表失败: {e}")
                return []

    def get_active_conversation(self, user_id: str) -> Optional[Conversation]:
        """获取当前活跃会话"""
        with self.lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    conn.row_factory = sqlite3.Row
                    cursor = conn.cursor()

                    cursor.execute('''
                        SELECT * FROM conversations
                        WHERE user_id = ? AND is_active = 1
                        ORDER BY updated_at DESC
                        LIMIT 1
                    ''', (user_id,))

                    row = cursor.fetchone()
                    if row:
                        return Conversation(
                            id=row['id'],
                            session_id=row['session_id'],
                            title=row['title'],
                            model=row['model'],
                            created_at=row['created_at'],
                            updated_at=row['updated_at'],
                            message_count=row['message_count'],
                            is_active=True,
                            gemini_session_data=row['gemini_session_data'],
                            user_id=row['user_id'],
                            metadata=json.loads(row['metadata']) if row['metadata'] else {}
                        )
                    return None

            except Exception as e:
                logger.error(f"获取活跃会话失败: {e}")
                return None

    def set_active_conversation(self, conversation_id: int, user_id: str) -> bool:
        """设置活跃会话"""
        with self.lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()

                    # 先清除该用户的所有活跃状态
                    cursor.execute('''
                        UPDATE conversations SET is_active = 0
                        WHERE user_id = ?
                    ''', (user_id,))

                    # 设置新的活跃会话
                    cursor.execute('''
                        UPDATE conversations SET is_active = 1, updated_at = ?
                        WHERE id = ? AND user_id = ?
                    ''', (datetime.now().isoformat(), conversation_id, user_id))

                    conn.commit()
                    return cursor.rowcount > 0

            except Exception as e:
                logger.error(f"设置活跃会话失败: {e}")
                return False

    def update_conversation(self, conversation_id: int, user_id: str, **updates) -> bool:
        """更新会话信息"""
        allowed_fields = ['title', 'model', 'gemini_session_data', 'metadata']
        update_fields = []
        update_values = []

        for field, value in updates.items():
            if field in allowed_fields:
                update_fields.append(f"{field} = ?")
                if field in ['metadata', 'gemini_session_data'] and value:
                    update_values.append(json.dumps(value))
                else:
                    update_values.append(value)

        if not update_fields:
            return False

        update_fields.append("updated_at = ?")
        update_values.append(datetime.now().isoformat())
        update_values.extend([conversation_id, user_id])

        with self.lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute(f'''
                        UPDATE conversations
                        SET {', '.join(update_fields)}
                        WHERE id = ? AND user_id = ?
                    ''', update_values)

                    conn.commit()
                    return cursor.rowcount > 0

            except Exception as e:
                logger.error(f"更新会话失败: {e}")
                return False

    def delete_conversation(self, conversation_id: int, user_id: str) -> bool:
        """删除会话及其所有消息"""
        with self.lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()

                    # 删除会话（级联删除消息）
                    cursor.execute('''
                        DELETE FROM conversations
                        WHERE id = ? AND user_id = ?
                    ''', (conversation_id, user_id))

                    conn.commit()
                    return cursor.rowcount > 0

            except Exception as e:
                logger.error(f"删除会话失败: {e}")
                return False

    def add_message(self, conversation_id: int, role: str, content: str,
                   message_type: str = "text", file_metadata: Optional[Dict] = None,
                   token_count: int = 0, model: str = "") -> int:
        """添加消息到会话"""
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            timestamp=datetime.now().isoformat(),
            message_type=message_type,
            file_metadata=file_metadata,
            token_count=token_count,
            model=model
        )

        with self.lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()

                    # 插入消息
                    cursor.execute('''
                        INSERT INTO messages
                        (conversation_id, role, content, timestamp, message_type,
                         file_metadata, token_count, model)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        message.conversation_id, message.role, message.content,
                        message.timestamp, message.message_type,
                        json.dumps(file_metadata) if file_metadata else None,
                        message.token_count, message.model
                    ))

                    message_id = cursor.lastrowid

                    # 更新会话的消息数量和更新时间
                    cursor.execute('''
                        UPDATE conversations
                        SET message_count = message_count + 1, updated_at = ?
                        WHERE id = ?
                    ''', (message.timestamp, conversation_id))

                    conn.commit()
                    logger.debug(f"添加消息到会话 {conversation_id}: {role}")

                    return message_id

            except Exception as e:
                logger.error(f"添加消息失败: {e}")
                raise

    def get_messages(self, conversation_id: int, user_id: str, limit: int = 100) -> List[Message]:
        """获取会话的消息"""
        with self.lock:
            try:
                # 验证会话属于该用户
                if not self._verify_conversation_ownership(conversation_id, user_id):
                    return []

                with sqlite3.connect(self.db_path) as conn:
                    conn.row_factory = sqlite3.Row
                    cursor = conn.cursor()

                    cursor.execute('''
                        SELECT * FROM messages
                        WHERE conversation_id = ?
                        ORDER BY timestamp ASC
                        LIMIT ?
                    ''', (conversation_id, limit))

                    messages = []
                    for row in cursor.fetchall():
                        messages.append(Message(
                            id=row['id'],
                            conversation_id=row['conversation_id'],
                            role=row['role'],
                            content=row['content'],
                            timestamp=row['timestamp'],
                            message_type=row['message_type'],
                            file_metadata=json.loads(row['file_metadata']) if row['file_metadata'] else None,
                            token_count=row['token_count'],
                            model=row['model']
                        ))

                    return messages

            except Exception as e:
                logger.error(f"获取消息失败: {e}")
                return []

    def clear_conversation_messages(self, conversation_id: int, user_id: str) -> bool:
        """清除会话的所有消息"""
        with self.lock:
            try:
                # 验证会话属于该用户
                if not self._verify_conversation_ownership(conversation_id, user_id):
                    logger.warning(f"用户 {user_id} 尝试清除不属于自己的会话 {conversation_id} 的消息")
                    return False

                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()

                    # 删除会话的所有消息
                    cursor.execute('''
                        DELETE FROM messages
                        WHERE conversation_id = ?
                    ''', (conversation_id,))

                    # 更新会话的消息数量为0
                    cursor.execute('''
                        UPDATE conversations
                        SET message_count = 0, updated_at = ?
                        WHERE id = ?
                    ''', (datetime.now().isoformat(), conversation_id))

                    conn.commit()
                    deleted_count = cursor.rowcount
                    logger.info(f"清除会话 {conversation_id} 的 {deleted_count} 条消息")
                    return True

            except Exception as e:
                logger.error(f"清除会话消息失败: {e}")
                return False

    def _verify_conversation_ownership(self, conversation_id: int, user_id: str) -> bool:
        """验证会话是否属于指定用户"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT COUNT(*) FROM conversations
                    WHERE id = ? AND user_id = ?
                ''', (conversation_id, user_id))

                return cursor.fetchone()[0] > 0
        except:
            return False

    def search_conversations(self, user_id: str, query: str, limit: int = 20) -> List[Conversation]:
        """搜索会话（基于标题和消息内容）"""
        with self.lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    conn.row_factory = sqlite3.Row
                    cursor = conn.cursor()

                    cursor.execute('''
                        SELECT DISTINCT c.* FROM conversations c
                        LEFT JOIN messages m ON c.id = m.conversation_id
                        WHERE c.user_id = ? AND (
                            c.title LIKE ? OR
                            m.content LIKE ?
                        )
                        ORDER BY c.updated_at DESC
                        LIMIT ?
                    ''', (user_id, f"%{query}%", f"%{query}%", limit))

                    conversations = []
                    for row in cursor.fetchall():
                        conversations.append(Conversation(
                            id=row['id'],
                            session_id=row['session_id'],
                            title=row['title'],
                            model=row['model'],
                            created_at=row['created_at'],
                            updated_at=row['updated_at'],
                            message_count=row['message_count'],
                            is_active=bool(row['is_active']),
                            user_id=row['user_id']
                        ))

                    return conversations

            except Exception as e:
                logger.error(f"搜索会话失败: {e}")
                return []

    def get_statistics(self, user_id: str) -> Dict[str, Any]:
        """获取用户统计信息"""
        with self.lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()

                    # 总会话数
                    cursor.execute('''
                        SELECT COUNT(*) FROM conversations WHERE user_id = ?
                    ''', (user_id,))
                    total_conversations = cursor.fetchone()[0]

                    # 总消息数
                    cursor.execute('''
                        SELECT COUNT(*) FROM conversation_summary WHERE user_id = ?
                    ''', (user_id,))
                    result = cursor.fetchone()
                    total_messages = result[0] if result else 0

                    # 今日活跃会话
                    today = datetime.now().date()
                    cursor.execute('''
                        SELECT COUNT(*) FROM conversations
                        WHERE user_id = ? AND DATE(updated_at) = ?
                    ''', (user_id, today))
                    active_today = cursor.fetchone()[0]

                    return {
                        'total_conversations': total_conversations,
                        'total_messages': total_messages,
                        'active_today': active_today,
                        'last_updated': datetime.now().isoformat()
                    }

            except Exception as e:
                logger.error(f"获取统计信息失败: {e}")
                return {}

    # ==================== 图片管理方法 ====================

    def add_image(self, filename: str, file_path: str, user_id: str, **kwargs) -> int:
        """添加图片记录"""
        with self.lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()

                    cursor.execute('''
                        INSERT INTO images (
                            filename, original_filename, file_path, file_size,
                            image_width, image_height, mime_type, title, description,
                            prompt, conversation_id, message_id, user_id, tags, metadata
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        filename,
                        kwargs.get('original_filename'),
                        file_path,
                        kwargs.get('file_size', 0),
                        kwargs.get('image_width'),
                        kwargs.get('image_height'),
                        kwargs.get('mime_type', 'image/png'),
                        kwargs.get('title'),
                        kwargs.get('description'),
                        kwargs.get('prompt'),
                        kwargs.get('conversation_id'),
                        kwargs.get('message_id'),
                        user_id,
                        json.dumps(kwargs.get('tags', [])) if kwargs.get('tags') else None,
                        json.dumps(kwargs.get('metadata', {})) if kwargs.get('metadata') else None
                    ))

                    image_id = cursor.lastrowid
                    conn.commit()
                    logger.info(f"添加图片记录: {filename} (ID: {image_id})")
                    return image_id or 0

            except Exception as e:
                logger.error(f"添加图片记录失败: {e}")
                return 0

    def get_images(self, user_id: str, page: int = 1, per_page: int = 20,
                   search_query: Optional[str] = None, conversation_id: Optional[int] = None) -> List[Image]:
        """获取用户的图片列表（分页）"""
        with self.lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    conn.row_factory = sqlite3.Row
                    cursor = conn.cursor()

                    # 构建查询条件
                    where_conditions = ["user_id = ?"]
                    params = [user_id]

                    if search_query:
                        where_conditions.append("(title LIKE ? OR description LIKE ? OR prompt LIKE ?)")
                        search_term = f"%{search_query}%"
                        params.extend([search_term, search_term, search_term])

                    if conversation_id:
                        where_conditions.append("conversation_id = ?")
                        params.append(conversation_id)

                    where_clause = " AND ".join(where_conditions)
                    offset = (page - 1) * per_page

                    cursor.execute(f'''
                        SELECT * FROM images
                        WHERE {where_clause}
                        ORDER BY created_at DESC
                        LIMIT ? OFFSET ?
                    ''', params + [per_page, offset])

                    images = []
                    for row in cursor.fetchall():
                        images.append(Image(
                            id=row['id'],
                            filename=row['filename'],
                            original_filename=row['original_filename'],
                            file_path=row['file_path'],
                            file_size=row['file_size'],
                            image_width=row['image_width'],
                            image_height=row['image_height'],
                            mime_type=row['mime_type'],
                            title=row['title'],
                            description=row['description'],
                            prompt=row['prompt'],
                            conversation_id=row['conversation_id'],
                            message_id=row['message_id'],
                            user_id=row['user_id'],
                            tags=json.loads(row['tags']) if row['tags'] else None,
                            metadata=json.loads(row['metadata']) if row['metadata'] else None,
                            created_at=row['created_at']
                        ))

                    return images

            except Exception as e:
                logger.error(f"获取图片列表失败: {e}")
                return []

    def get_image_count(self, user_id: str, search_query: Optional[str] = None,
                       conversation_id: Optional[int] = None) -> int:
        """获取用���图片总数"""
        with self.lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()

                    # 构建查询条件
                    where_conditions = ["user_id = ?"]
                    params = [user_id]

                    if search_query:
                        where_conditions.append("(title LIKE ? OR description LIKE ? OR prompt LIKE ?)")
                        search_term = f"%{search_query}%"
                        params.extend([search_term, search_term, search_term])

                    if conversation_id:
                        where_conditions.append("conversation_id = ?")
                        params.append(conversation_id)

                    where_clause = " AND ".join(where_conditions)

                    cursor.execute(f'''
                        SELECT COUNT(*) FROM images
                        WHERE {where_clause}
                    ''', params)

                    return cursor.fetchone()[0]

            except Exception as e:
                logger.error(f"获取图片数量失败: {e}")
                return 0

    def get_image_by_id(self, image_id: int, user_id: str) -> Optional[Image]:
        """根据ID获取图片信息"""
        with self.lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    conn.row_factory = sqlite3.Row
                    cursor = conn.cursor()

                    cursor.execute('''
                        SELECT * FROM images
                        WHERE id = ? AND user_id = ?
                    ''', (image_id, user_id))

                    row = cursor.fetchone()
                    if row:
                        return Image(
                            id=row['id'],
                            filename=row['filename'],
                            original_filename=row['original_filename'],
                            file_path=row['file_path'],
                            file_size=row['file_size'],
                            image_width=row['image_width'],
                            image_height=row['image_height'],
                            mime_type=row['mime_type'],
                            title=row['title'],
                            description=row['description'],
                            prompt=row['prompt'],
                            conversation_id=row['conversation_id'],
                            message_id=row['message_id'],
                            user_id=row['user_id'],
                            tags=json.loads(row['tags']) if row['tags'] else None,
                            metadata=json.loads(row['metadata']) if row['metadata'] else None,
                            created_at=row['created_at']
                        )
                    return None

            except Exception as e:
                logger.error(f"获取图片信息失败: {e}")
                return None

    def update_image(self, image_id: int, user_id: str, **kwargs) -> bool:
        """更新图片信息"""
        with self.lock:
            try:
                # 验证图片属于该用户
                if not self.get_image_by_id(image_id, user_id):
                    return False

                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()

                    # 动态构建更新语句
                    update_fields = []
                    params = []

                    for field in ['title', 'description', 'prompt', 'tags', 'metadata']:
                        if field in kwargs:
                            update_fields.append(f"{field} = ?")
                            if field in ['tags', 'metadata']:
                                params.append(json.dumps(kwargs[field]))
                            else:
                                params.append(kwargs[field])

                if update_fields:
                    cursor.execute(f'''
                        UPDATE images
                        SET {', '.join(update_fields)}, created_at = ?
                        WHERE id = ?
                    ''', params + [datetime.now().isoformat(), image_id])

                    conn.commit()
                    logger.info(f"更新图片信息: ID {image_id}")
                    return True

                return False

            except Exception as e:
                logger.error(f"更新图片信息失败: {e}")
                return False

    def delete_image(self, image_id: int, user_id: str) -> bool:
        """删除图片记录"""
        with self.lock:
            try:
                # 获取图片信息（用于删除文件）
                image = self.get_image_by_id(image_id, user_id)
                if not image:
                    return False

                # 删除数据库记录
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()

                    cursor.execute('''
                        DELETE FROM images
                        WHERE id = ? AND user_id = ?
                    ''', (image_id, user_id))

                    conn.commit()
                    deleted_count = cursor.rowcount

                    # 尝试删除物理文件（可选）
                    try:
                        import os
                        if os.path.exists(image.file_path):
                            os.remove(image.file_path)
                            logger.info(f"删除图片文件: {image.file_path}")
                    except Exception as file_error:
                        logger.warning(f"删除图片文件失败: {file_error}")

                    logger.info(f"删除图片记录: ID {image_id}")
                    return deleted_count > 0

            except Exception as e:
                logger.error(f"删除图片失败: {e}")
                return False

# 全局数据库管理器实例
conversation_manager = None

def get_conversation_manager() -> ConversationManager:
    """获取全局会话管理器实例"""
    global conversation_manager
    if conversation_manager is None:
        conversation_manager = ConversationManager()
    return conversation_manager