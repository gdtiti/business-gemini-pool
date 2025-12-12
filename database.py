"""Business Gemini Pool 数据库管理器 - 简化版本，Windows兼容"""

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
        """初始化数据库结构 - 简化版本"""
        try:
            logger.info("开始初始化数据库...")

            # 读取schema文件
            schema_path = Path(__file__).parent / "schema.sql"
            if schema_path.exists():
                logger.info(f"读取schema文件: {schema_path}")
                with open(schema_path, 'r', encoding='utf-8') as f:
                    schema_sql = f.read()
                logger.info(f"schema文件大小: {len(schema_sql)} 字符")
            else:
                logger.warning("schema.sql文件不存在，跳过数据库初始化")
                return

            logger.info("开始执行数据库脚本...")

            try:
                with sqlite3.connect(self.db_path, timeout=10.0) as conn:
                    logger.info("数据库连接成功，开始执行脚本...")

                    # 分批执行SQL
                    statements = schema_sql.split(';')
                    executed_count = 0

                    for i, statement in enumerate(statements):
                        statement = statement.strip()
                        if statement:
                            try:
                                conn.execute(statement)
                                executed_count += 1
                                if executed_count % 10 == 0:
                                    conn.commit()
                                    logger.info(f"已执行 {executed_count} 条SQL语句")
                            except sqlite3.Error as e:
                                logger.warning(f"SQL语句执行失败 (语句 {i}): {e}")
                                logger.warning(f"语句内容: {statement[:100]}...")

                    conn.commit()
                    logger.info(f"数据库初始化完成，共执行 {executed_count} 条SQL语句")

            except Exception as e:
                logger.error(f"数据库初始化失败: {e}")
                logger.error("跳过数据库初始化，服务将继续运行")

        except Exception as e:
            logger.error(f"数据库初始化异常: {e}")
            logger.error("跳过数据库初始化，服务将继续运行")

    def get_user_id(self, api_key: str = "", email: str = "") -> str:
        """基于邮箱或API key生成用户ID"""
        # 优先使用邮箱账号
        if email:
            return email
        # 如果没有邮箱，使用默认用户ID
        return "default_user"

    def get_active_conversation(self, user_id: str):
        """获取当前活跃会话"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT session_id, title, created_at, updated_at
                    FROM conversations
                    WHERE user_id = ? AND is_active = 1
                    ORDER BY updated_at DESC
                    LIMIT 1
                """, (user_id,))
                result = cursor.fetchone()
                if result:
                    return {
                        'session_id': result[0],
                        'title': result[1],
                        'created_at': result[2],
                        'updated_at': result[3]
                    }
                return None
        except Exception as e:
            logger.error(f"获取活跃会话失败: {e}")
            return None

    def record_conversation(self, user_id: str, messages: List[Dict[str, Any]]) -> str:
        """记录对话"""
        try:
            conversation_id = f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{user_id[:8]}"

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # 插入对话记录
                cursor.execute("""
                    INSERT INTO conversations
                    (conversation_id, user_id, title, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (conversation_id, user_id, "新对话",
                     datetime.now(), datetime.now()))

                # 插入消息记录
                for i, message in enumerate(messages):
                    cursor.execute("""
                        INSERT INTO messages
                        (conversation_id, role, content, message_order, created_at)
                        VALUES (?, ?, ?, ?, ?)
                    """, (conversation_id, message.get('role'),
                         message.get('content'), i, datetime.now()))

                conn.commit()
                logger.info(f"记录对话成功: {conversation_id}")
                return conversation_id

        except Exception as e:
            logger.error(f"记录对话失败: {e}")
            return ""

    def get_conversations(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """获取用户的对话列表"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT conversation_id, title, created_at, updated_at,
                           (SELECT COUNT(*) FROM messages WHERE conversation_id = c.conversation_id) as message_count
                    FROM conversations c
                    WHERE user_id = ?
                    ORDER BY updated_at DESC
                    LIMIT ?
                """, (user_id, limit))

                columns = [desc[0] for desc in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]

        except Exception as e:
            logger.error(f"获取对话列表失败: {e}")
            return []

    def get_messages(self, conversation_id: str) -> List[Dict[str, Any]]:
        """获取对话的消息"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT role, content, message_order, created_at
                    FROM messages
                    WHERE conversation_id = ?
                    ORDER BY message_order
                """, (conversation_id,))

                columns = [desc[0] for desc in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]

        except Exception as e:
            logger.error(f"获取消息失败: {e}")
            return []

    def delete_conversation(self, conversation_id: str) -> bool:
        """删除对话"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM messages WHERE conversation_id = ?",
                             (conversation_id,))
                cursor.execute("DELETE FROM conversations WHERE conversation_id = ?",
                             (conversation_id,))
                conn.commit()
                logger.info(f"删除对话成功: {conversation_id}")
                return True

        except Exception as e:
            logger.error(f"删除对话失败: {e}")
            return False


# 全局数据库管理器实例
_conversation_manager = None


def get_conversation_manager() -> Optional[ConversationManager]:
    """获取全局对话管理器实例"""
    global _conversation_manager
    if _conversation_manager is None:
        _conversation_manager = ConversationManager()
    return _conversation_manager


# 向后兼容的函数名
init_database = get_conversation_manager