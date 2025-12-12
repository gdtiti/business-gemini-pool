-- Business Gemini Pool 历史会话管理数据库结构
-- 创建时间: 2025-11-28

-- 会话表
CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id VARCHAR(36) UNIQUE NOT NULL,           -- 会话唯一标识
    title VARCHAR(200) NOT NULL,                       -- 会话标题（自动生成或用户修改）
    model VARCHAR(50) NOT NULL DEFAULT 'gemini-enterprise', -- 使用的模型
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,    -- 创建时间
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,    -- 最后更新时间
    message_count INTEGER DEFAULT 0,                  -- 消息数量
    is_active BOOLEAN DEFAULT FALSE,                   -- 是否为当前活跃会话
    gemini_session_data TEXT,                          -- 存储Gemini会话状态（JSON）
    user_id VARCHAR(50),                               -- 用户标识（基于API key）
    metadata JSON                                      -- 额外元数据（标签、设置等）
);

-- 消息表
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id INTEGER NOT NULL,                  -- 关联会话ID
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')), -- 角色
    content TEXT NOT NULL,                             -- 消息内容
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,    -- 消息时间
    message_type VARCHAR(20) DEFAULT 'text' CHECK (message_type IN ('text', 'image', 'file')), -- 消息类型
    file_metadata JSON,                                -- 文件/图片元数据
    token_count INTEGER DEFAULT 0,                    -- Token使用量
    model VARCHAR(50),                                -- 生成消息的模型
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
);

-- 会话标签表（用于分类和搜索）
CREATE TABLE IF NOT EXISTS conversation_tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id INTEGER NOT NULL,
    tag VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,
    UNIQUE(conversation_id, tag)
);

-- 图片表（用于相册功能）
CREATE TABLE IF NOT EXISTS images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename VARCHAR(255) NOT NULL,                      -- 图片文件名
    original_filename VARCHAR(255),                      -- 原始文件名（如果有的话）
    file_path VARCHAR(500) NOT NULL,                     -- 文件存储路径
    file_size INTEGER DEFAULT 0,                        -- 文件大小（字节）
    image_width INTEGER,                                 -- 图片宽度
    image_height INTEGER,                                -- 图片高度
    mime_type VARCHAR(50) DEFAULT 'image/png',          -- MIME类型
    title VARCHAR(200),                                  -- 图片标题
    description TEXT,                                    -- 图片描述
    prompt TEXT,                                         -- 生成提示词
    conversation_id INTEGER,                             -- 关联的会话ID（可选）
    message_id INTEGER,                                  -- 关联的消息ID（可选）
    user_id VARCHAR(50) NOT NULL,                        -- 用户标识
    tags JSON,                                           -- 图片标签
    metadata JSON,                                       -- 其他元数据
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,      -- 创建时间
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE SET NULL,
    FOREIGN KEY (message_id) REFERENCES messages(id) ON DELETE SET NULL
);

-- 系统设置表
CREATE TABLE IF NOT EXISTS settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key VARCHAR(100) UNIQUE NOT NULL,
    value TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引优化
CREATE INDEX IF NOT EXISTS idx_conversations_user_active ON conversations(user_id, is_active);
CREATE INDEX IF NOT EXISTS idx_conversations_updated ON conversations(updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(conversation_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_conversation_tags_tag ON conversation_tags(tag);

-- 图片表索引
CREATE INDEX IF NOT EXISTS idx_images_user_id ON images(user_id);
CREATE INDEX IF NOT EXISTS idx_images_created_at ON images(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_images_conversation ON images(conversation_id);
CREATE INDEX IF NOT EXISTS idx_images_filename ON images(filename);

-- 视图：会话摘要（用于列表显示）
CREATE VIEW IF NOT EXISTS conversation_summary AS
SELECT
    c.id,
    c.session_id,
    c.title,
    c.model,
    c.created_at,
    c.updated_at,
    c.message_count,
    c.is_active,
    c.user_id,
    GROUP_CONCAT(ct.tag, ',') as tags,
    -- 最后一条消息内容作为预览
    (SELECT m.content FROM messages m WHERE m.conversation_id = c.id ORDER BY m.timestamp DESC LIMIT 1) as last_message,
    -- 最后一条消息时间
    (SELECT m.timestamp FROM messages m WHERE m.conversation_id = c.id ORDER BY m.timestamp DESC LIMIT 1) as last_message_time
FROM conversations c
LEFT JOIN conversation_tags ct ON c.id = ct.conversation_id
GROUP BY c.id;

-- 初始化默认设置
INSERT OR IGNORE INTO settings (key, value) VALUES
('db_version', '1.1'),
('max_conversations_per_user', '100'),
('auto_title_generation', 'true'),
('message_retention_days', '365'),
('max_images_per_page', '20'),
('image_retention_days', '365');