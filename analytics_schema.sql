-- Business Gemini Pool 统计分析扩展数据库结构
-- 创建时间: 2025-11-29
-- 功能: 图片生成和使用统计分析

-- 图片生成记录表
CREATE TABLE IF NOT EXISTS image_generation_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    image_id INTEGER NOT NULL,                              -- 关联图片ID
    generation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,    -- 生成时间
    api_key_used VARCHAR(100) NOT NULL,                    -- 使用的API key
    account_team_id VARCHAR(50) NOT NULL,                  -- 账号Team ID
    account_email VARCHAR(100),                            -- 账号邮箱
    model_used VARCHAR(50) NOT NULL DEFAULT 'gemini-enterprise', -- 使用的模型
    prompt_text TEXT NOT NULL,                             -- 生成提示词
    prompt_length INTEGER DEFAULT 0,                       -- 提示词长度
    negative_prompt TEXT,                                  -- 反向提示词（如果有）
    generation_params JSON,                                -- 生成参数（温度、top_p等）
    generation_duration INTEGER DEFAULT 0,                 -- 生成耗时（毫秒）
    success BOOLEAN DEFAULT TRUE,                          -- ��否成功生成
    error_message TEXT,                                    -- 错误信息（如果有）
    request_ip VARCHAR(45),                                -- 请求IP地址
    user_agent TEXT,                                       -- 用户代理
    session_id VARCHAR(36),                               -- 会话ID
    conversation_id INTEGER,                               -- 会话ID
    metadata JSON,                                        -- 其他元数据
    FOREIGN KEY (image_id) REFERENCES images(id) ON DELETE CASCADE,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE SET NULL
);

-- API密钥使用统计表
CREATE TABLE IF NOT EXISTS api_key_usage_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    api_key_hash VARCHAR(64) UNIQUE NOT NULL,              -- API key的哈希值（安全存储）
    api_key_masked VARCHAR(50) NOT NULL,                   -- 遮蔽的API key显示
    account_team_id VARCHAR(50) NOT NULL,                  -- 对应的Team ID
    account_email VARCHAR(100),                            -- 账号邮箱
    total_requests INTEGER DEFAULT 0,                      -- 总请求数
    successful_requests INTEGER DEFAULT 0,                 -- 成功请求数
    failed_requests INTEGER DEFAULT 0,                     -- 失败请求数
    total_tokens_generated INTEGER DEFAULT 0,              -- 生成token总数
    total_images_generated INTEGER DEFAULT 0,              -- 生成图片总数
    first_used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,     -- 首次使用时间
    last_used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,      -- 最后使用时间
    is_active BOOLEAN DEFAULT TRUE,                        -- 是否活跃
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,        -- 创建时间
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP         -- 更新时间
);

-- 模型使用统计表
CREATE TABLE IF NOT EXISTS model_usage_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_name VARCHAR(50) UNIQUE NOT NULL,                -- 模型名称
    total_requests INTEGER DEFAULT 0,                      -- 总请求数
    text_requests INTEGER DEFAULT 0,                       -- 文本请求次数
    image_requests INTEGER DEFAULT 0,                      -- 图片生成请求次数
    successful_requests INTEGER DEFAULT 0,                 -- 成功请求数
    failed_requests INTEGER DEFAULT 0,                     -- 失败请求数
    total_tokens_generated INTEGER DEFAULT 0,              -- 生成token总数
    total_images_generated INTEGER DEFAULT 0,              -- 生成图片总数
    average_tokens_per_request INTEGER DEFAULT 0,          -- 平均每请求token数
    total_usage_time INTEGER DEFAULT 0,                    -- 总使用时间（秒）
    first_used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,     -- 首次使用时间
    last_used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,      -- 最后使用时间
    is_active BOOLEAN DEFAULT TRUE,                        -- 是否活跃
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,        -- 创建时间
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP         -- 更新时间
);

-- 用户使用统计表
CREATE TABLE IF NOT EXISTS user_usage_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id VARCHAR(50) NOT NULL,                          -- 用户标识
    total_requests INTEGER DEFAULT 0,                      -- 总请求数
    successful_requests INTEGER DEFAULT 0,                 -- 成功请求数
    failed_requests INTEGER DEFAULT 0,                     -- 失败请求数
    total_tokens_generated INTEGER DEFAULT 0,              -- 生成token总数
    total_images_generated INTEGER DEFAULT 0,              -- 生成图片总数
    unique_prompts_used INTEGER DEFAULT 0,                 -- 使用的独特提示词数量
    total_generation_time INTEGER DEFAULT 0,               -- 总生成时间（毫秒）
    first_request_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 首次请求时间
    last_request_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,   -- 最后请求时间
    is_active BOOLEAN DEFAULT TRUE,                        -- 是否活跃
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,        -- 创建时间
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP         -- 更新时间
);

-- 关键词使用统计表
CREATE TABLE IF NOT EXISTS keyword_usage_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    keyword VARCHAR(100) NOT NULL,                         -- 关键词
    keyword_type VARCHAR(20) DEFAULT 'general' CHECK (keyword_type IN ('general', 'style', 'subject', 'technical')), -- 关键词类型
    usage_count INTEGER DEFAULT 1,                         -- 使用次数
    unique_users INTEGER DEFAULT 1,                        -- 使用此关键词的唯一用户数
    total_images_generated INTEGER DEFAULT 0,              -- 使用此关键词生成的图片数
    last_used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,      -- 最后使用时间
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,        -- 创建时间
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP         -- 更新时间
);

-- 每日使用汇总表
CREATE TABLE IF NOT EXISTS daily_usage_summary (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    summary_date DATE UNIQUE NOT NULL,                     -- 汇总日期
    total_requests INTEGER DEFAULT 0,                      -- 当日总请求数
    successful_requests INTEGER DEFAULT 0,                 -- 当日成功请求数
    failed_requests INTEGER DEFAULT 0,                     -- 当日失败请求数
    unique_users INTEGER DEFAULT 0,                        -- 当日活跃用户数
    total_images_generated INTEGER DEFAULT 0,              -- 当日生成图片数
    total_tokens_generated INTEGER DEFAULT 0,              -- 当日生成token数
    top_model_used VARCHAR(50),                            -- 当日最常用模型
    top_keyword VARCHAR(100),                              -- 当日最热门关键词
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,        -- 创建时间
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP         -- 更新时间
);

-- 图片生成记录表索引
CREATE INDEX IF NOT EXISTS idx_generation_records_time ON image_generation_records(generation_time DESC);
CREATE INDEX IF NOT EXISTS idx_generation_records_api_key ON image_generation_records(api_key_used);
CREATE INDEX IF NOT EXISTS idx_generation_records_model ON image_generation_records(model_used);
CREATE INDEX IF NOT EXISTS idx_generation_records_success ON image_generation_records(success);
CREATE INDEX IF NOT EXISTS idx_generation_records_user ON image_generation_records(session_id, user_id);

-- API密钥使用统计表索引
CREATE INDEX IF NOT EXISTS idx_api_key_usage_team_id ON api_key_usage_stats(account_team_id);
CREATE INDEX IF NOT EXISTS idx_api_key_usage_active ON api_key_usage_stats(is_active);
CREATE INDEX IF NOT EXISTS idx_api_key_usage_last_used ON api_key_usage_stats(last_used_at DESC);

-- 模型使用统计表索引
CREATE INDEX IF NOT EXISTS idx_model_usage_active ON model_usage_stats(is_active);
CREATE INDEX IF NOT EXISTS idx_model_usage_last_used ON model_usage_stats(last_used_at DESC);

-- 用户使用统计表索引
CREATE INDEX IF NOT EXISTS idx_user_usage_user_id ON user_usage_stats(user_id);
CREATE INDEX IF NOT EXISTS idx_user_usage_active ON user_usage_stats(is_active);
CREATE INDEX IF NOT EXISTS idx_user_usage_last_request ON user_usage_stats(last_request_at DESC);

-- 关键词使用统计表索引
CREATE INDEX IF NOT EXISTS idx_keyword_usage_keyword ON keyword_usage_stats(keyword);
CREATE INDEX IF NOT EXISTS idx_keyword_usage_type ON keyword_usage_stats(keyword_type);
CREATE INDEX IF NOT EXISTS idx_keyword_usage_count ON keyword_usage_stats(usage_count DESC);

-- 每日使用汇总表索引
CREATE INDEX IF NOT EXISTS idx_daily_summary_date ON daily_usage_summary(summary_date DESC);

-- 视图：API密钥使用详情
CREATE VIEW IF NOT EXISTS api_key_usage_details AS
SELECT
    akus.*,
    -- 计算成功率
    CASE
        WHEN akus.total_requests > 0 THEN
            ROUND((CAST(akus.successful_requests AS REAL) / akus.total_requests) * 100, 2)
        ELSE 0
    END as success_rate_percent,
    -- 计算平均每请求生成图片数
    CASE
        WHEN akus.successful_requests > 0 THEN
            ROUND(CAST(akus.total_images_generated AS REAL) / akus.successful_requests, 2)
        ELSE 0
    END as avg_images_per_request,
    -- 计算使用天数
    (julianday('now') - julianday(akus.first_used_at)) as days_in_use
FROM api_key_usage_stats akus;

-- 视图：模型使用详情
CREATE VIEW IF NOT EXISTS model_usage_details AS
SELECT
    mus.*,
    -- 计算成功率
    CASE
        WHEN mus.total_requests > 0 THEN
            ROUND((CAST(mus.successful_requests AS REAL) / mus.total_requests) * 100, 2)
        ELSE 0
    END as success_rate_percent,
    -- 计算平均每请求token数
    CASE
        WHEN mus.successful_requests > 0 THEN
            ROUND(CAST(mus.total_tokens_generated AS REAL) / mus.successful_requests, 2)
        ELSE 0
    END as avg_tokens_per_request,
    -- 计算图片请求占比
    CASE
        WHEN mus.total_requests > 0 THEN
            ROUND((CAST(mus.image_requests AS REAL) / mus.total_requests) * 100, 2)
        ELSE 0
    END as image_request_percent
FROM model_usage_stats mus;

-- 视图：生成记录统计汇总
CREATE VIEW IF NOT EXISTS generation_summary_stats AS
SELECT
    DATE(igr.generation_time) as generation_date,
    igr.model_used,
    igr.account_team_id,
    COUNT(*) as total_generations,
    SUM(CASE WHEN igr.success = 1 THEN 1 ELSE 0 END) as successful_generations,
    AVG(igr.generation_duration) as avg_generation_duration,
    COUNT(DISTINCT igr.session_id) as unique_sessions,
    COUNT(DISTINCT igr.user_id) as unique_users
FROM image_generation_records igr
GROUP BY DATE(igr.generation_time), igr.model_used, igr.account_team_id
ORDER BY generation_date DESC;

-- 触发器：更新API密钥使用统计
CREATE TRIGGER IF NOT EXISTS update_api_key_usage_after_generation
AFTER INSERT ON image_generation_records
FOR EACH ROW
BEGIN
    INSERT OR REPLACE INTO api_key_usage_stats (
        api_key_hash,
        api_key_masked,
        account_team_id,
        account_email,
        total_requests,
        successful_requests,
        failed_requests,
        total_images_generated,
        last_used_at,
        updated_at
    ) VALUES (
        NEW.api_key_used,
        SUBSTR(NEW.api_key_used, 1, 8) || '****' || SUBSTR(NEW.api_key_used, -4),
        NEW.account_team_id,
        NEW.account_email,
        COALESCE((SELECT total_requests FROM api_key_usage_stats WHERE api_key_hash = NEW.api_key_used), 0) + 1,
        COALESCE((SELECT successful_requests FROM api_key_usage_stats WHERE api_key_hash = NEW.api_key_used), 0) + CASE WHEN NEW.success = 1 THEN 1 ELSE 0 END,
        COALESCE((SELECT failed_requests FROM api_key_usage_stats WHERE api_key_hash = NEW.api_key_used), 0) + CASE WHEN NEW.success = 0 THEN 1 ELSE 0 END,
        COALESCE((SELECT total_images_generated FROM api_key_usage_stats WHERE api_key_hash = NEW.api_key_used), 0) + 1,
        NEW.generation_time,
        CURRENT_TIMESTAMP
    );
END;

-- 初始化统计数据
INSERT OR IGNORE INTO model_usage_stats (model_name, total_requests) VALUES
('gemini-enterprise', 0),
('gemini-1.5-flash', 0),
('gemini-1.5-pro', 0),
('claude-3-sonnet', 0),
('claude-3-opus', 0);

-- 初始化设置
INSERT OR IGNORE INTO settings (key, value) VALUES
('analytics_db_version', '1.0'),
('enable_generation_tracking', 'true'),
('retention_days_records', '90'),
('auto_cleanup_old_records', 'false');