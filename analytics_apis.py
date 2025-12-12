#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Business Gemini Pool 统计分析API (修复版本)
提供详细的使用统计和分析功能，包括API密钥批量操作
"""

from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import json
import sqlite3
import hashlib
import time
import os
from typing import Dict, List, Optional, Any

# 全局变量存储认证装饰器（由主模块设置）
require_api_key = None

def set_auth_decorator(decorator):
    """设置认证装饰器"""
    global require_api_key
    require_api_key = decorator

class AnalyticsManager:
    def __init__(self, db_path: str = "conversations.db"):
        """初始化统计分析管理器"""
        self.db_path = db_path
        self.init_analytics_tables()

    def init_analytics_tables(self):
        """初始化统计分析表"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # 直接创建必要的统计分析表
                tables_sql = [
                    # 图片生成记录表
                    """
                    CREATE TABLE IF NOT EXISTS image_generation_records (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        image_id INTEGER NOT NULL,
                        generation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        api_key_used VARCHAR(100) NOT NULL,
                        account_team_id VARCHAR(50) NOT NULL,
                        account_email VARCHAR(100),
                        model_used VARCHAR(50) NOT NULL DEFAULT 'gemini-enterprise',
                        prompt_text TEXT NOT NULL,
                        prompt_length INTEGER DEFAULT 0,
                        negative_prompt TEXT,
                        generation_params TEXT,
                        generation_duration INTEGER DEFAULT 0,
                        success BOOLEAN DEFAULT TRUE,
                        error_message TEXT,
                        request_ip VARCHAR(45),
                        user_agent TEXT,
                        session_id VARCHAR(36),
                        conversation_id INTEGER,
                        metadata TEXT
                    )
                    """,

                    # API密钥使用统计表
                    """
                    CREATE TABLE IF NOT EXISTS api_key_usage_stats (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        api_key_hash VARCHAR(64) UNIQUE NOT NULL,
                        api_key_masked VARCHAR(50) NOT NULL,
                        account_team_id VARCHAR(50) NOT NULL,
                        account_email VARCHAR(100),
                        total_requests INTEGER DEFAULT 0,
                        successful_requests INTEGER DEFAULT 0,
                        failed_requests INTEGER DEFAULT 0,
                        total_tokens_generated INTEGER DEFAULT 0,
                        total_images_generated INTEGER DEFAULT 0,
                        first_used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        is_active BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """,

                    # 模型使用统计表
                    """
                    CREATE TABLE IF NOT EXISTS model_usage_stats (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        model_name VARCHAR(50) UNIQUE NOT NULL,
                        total_requests INTEGER DEFAULT 0,
                        text_requests INTEGER DEFAULT 0,
                        image_requests INTEGER DEFAULT 0,
                        successful_requests INTEGER DEFAULT 0,
                        failed_requests INTEGER DEFAULT 0,
                        total_tokens_generated INTEGER DEFAULT 0,
                        total_images_generated INTEGER DEFAULT 0,
                        average_tokens_per_request INTEGER DEFAULT 0,
                        total_usage_time INTEGER DEFAULT 0,
                        first_used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        is_active BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """,

                    # 用户使用统计表
                    """
                    CREATE TABLE IF NOT EXISTS user_usage_stats (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id VARCHAR(50) NOT NULL,
                        total_requests INTEGER DEFAULT 0,
                        successful_requests INTEGER DEFAULT 0,
                        failed_requests INTEGER DEFAULT 0,
                        total_tokens_generated INTEGER DEFAULT 0,
                        total_images_generated INTEGER DEFAULT 0,
                        unique_prompts_used INTEGER DEFAULT 0,
                        total_generation_time INTEGER DEFAULT 0,
                        first_request_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_request_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        is_active BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """,

                    # 关键词使用统计表
                    """
                    CREATE TABLE IF NOT EXISTS keyword_usage_stats (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        keyword VARCHAR(100) NOT NULL,
                        keyword_type VARCHAR(20) DEFAULT 'general',
                        usage_count INTEGER DEFAULT 1,
                        unique_users INTEGER DEFAULT 1,
                        total_images_generated INTEGER DEFAULT 0,
                        last_used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                ]

                for sql in tables_sql:
                    try:
                        cursor.execute(sql)
                    except sqlite3.Error as e:
                        if "already exists" not in str(e):
                            print(f"[统计分析] 表创建警告: {e}")

                conn.commit()
                print("[统计分析] 数据库表初始化完成")

        except Exception as e:
            print(f"[统计分析] 数据库初始化失败: {e}")

    def batch_delete_api_keys(self, api_key_hashes: List[str]) -> int:
        """批量删除API密钥统计数据"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # 构建IN子句
                placeholders = ','.join(['?' for _ in api_key_hashes])

                # 删除API密钥使用统计
                cursor.execute(f'''
                    DELETE FROM api_key_usage_stats
                    WHERE api_key_hash IN ({placeholders})
                ''', api_key_hashes)

                deleted_count = cursor.rowcount
                conn.commit()

                print(f"[统计分析] 批量删除 {deleted_count} 个API密钥记录")
                return deleted_count

        except Exception as e:
            print(f"[统计分析] 批量删除失败: {e}")
            return 0

    def clear_all_api_keys(self) -> int:
        """清空所有API密钥统计数据"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # 获取删除前的数量
                cursor.execute("SELECT COUNT(*) FROM api_key_usage_stats")
                before_count = cursor.fetchone()[0]

                # 清空表
                cursor.execute("DELETE FROM api_key_usage_stats")

                # 重置自增ID
                cursor.execute("DELETE FROM sqlite_sequence WHERE name='api_key_usage_stats'")

                conn.commit()

                print(f"[统计分析] 清空 {before_count} 个API密钥记录")
                return before_count

        except Exception as e:
            print(f"[统计分析] 清空操作失败: {e}")
            return 0

    def batch_import_api_keys(self, accounts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """批量导入API密钥统计数据"""
        imported_count = 0
        skipped_count = 0
        error_count = 0
        details = []

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                for i, account in enumerate(accounts):
                    try:
                        # 验证必需字段
                        if not account.get('team_id'):
                            details.append(f"第{i+1}个账号: 缺少team_id字段")
                            error_count += 1
                            continue

                        team_id = account['team_id']
                        email = account.get('email', '')

                        # 生成API key hash (这里用team_id作为标识)
                        api_key_hash = hashlib.sha256(team_id.encode()).hexdigest()
                        api_key_masked = team_id[:8] + '****' + team_id[-4:] if len(team_id) > 12 else team_id

                        # 检查是否已存在
                        cursor.execute('''
                            SELECT id FROM api_key_usage_stats
                            WHERE api_key_hash = ?
                        ''', (api_key_hash,))

                        if cursor.fetchone():
                            details.append(f"第{i+1}个账号: team_id={team_id} 已存在，跳过")
                            skipped_count += 1
                            continue

                        # 插入新记录
                        cursor.execute('''
                            INSERT OR REPLACE INTO api_key_usage_stats (
                                api_key_hash, api_key_masked, account_team_id, account_email,
                                total_requests, successful_requests, failed_requests,
                                total_images_generated, is_active, created_at, updated_at
                            ) VALUES (?, ?, ?, ?, 0, 0, 0, 0, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                        ''', (api_key_hash, api_key_masked, team_id, email))

                        imported_count += 1
                        details.append(f"第{i+1}个账号: team_id={team_id} 导入成功")

                    except Exception as e:
                        error_count += 1
                        details.append(f"第{i+1}个账号: 处理失败 - {str(e)}")

                conn.commit()

        except Exception as e:
            print(f"[统计分析] 批量导入失败: {e}")
            return {
                'imported_count': imported_count,
                'skipped_count': skipped_count,
                'error_count': error_count,
                'details': details + [f"系统错误: {str(e)}"]
            }

        print(f"[统计分析] 批量导入完成: 导入{imported_count}, 跳过{skipped_count}, 错误{error_count}")

        return {
            'imported_count': imported_count,
            'skipped_count': skipped_count,
            'error_count': error_count,
            'details': details
        }

    def export_api_keys(self) -> List[Dict[str, Any]]:
        """导出API密钥统计数据"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute('''
                    SELECT
                        account_team_id as team_id,
                        account_email as email,
                        total_requests,
                        successful_requests,
                        failed_requests,
                        total_images_generated,
                        first_used_at,
                        last_used_at,
                        is_active
                    FROM api_key_usage_stats
                    ORDER BY account_team_id
                ''')

                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()

                return [dict(zip(columns, row)) for row in rows]

        except Exception as e:
            print(f"[统计分析] 导出API密钥失败: {e}")
            return []

    def record_chat_usage(self, usage_data: Dict[str, Any]):
        """记录聊天对话使用事件"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # 准备基础数据
                api_key = usage_data.get('api_key', '')
                api_key_hash = hashlib.sha256(api_key.encode()).hexdigest() if api_key else 'unknown'
                api_key_masked = f"{api_key[:8]}...{api_key[-4:]}" if len(api_key) > 12 else api_key

                model_name = usage_data.get('model', 'gemini-enterprise')
                success = usage_data.get('success', True)
                duration = usage_data.get('duration', 0)
                tokens = usage_data.get('tokens', 0)
                images = usage_data.get('images', 0)

                # 插入或更新API密钥使用统计
                cursor.execute('''
                    INSERT OR REPLACE INTO api_key_usage_stats (
                        api_key_hash, api_key_masked, account_team_id, account_email,
                        total_requests, successful_requests, failed_requests,
                        total_tokens_generated, total_images_generated,
                        first_used_at, last_used_at, is_active, updated_at
                    ) VALUES (
                        ?, ?, ?, ?,
                        COALESCE((SELECT total_requests FROM api_key_usage_stats WHERE api_key_hash = ?), 0) + 1,
                        COALESCE((SELECT successful_requests FROM api_key_usage_stats WHERE api_key_hash = ?), 0) + ?,
                        COALESCE((SELECT failed_requests FROM api_key_usage_stats WHERE api_key_hash = ?), 0) + ?,
                        COALESCE((SELECT total_tokens_generated FROM api_key_usage_stats WHERE api_key_hash = ?), 0) + ?,
                        COALESCE((SELECT total_images_generated FROM api_key_usage_stats WHERE api_key_hash = ?), 0) + ?,
                        COALESCE((SELECT first_used_at FROM api_key_usage_stats WHERE api_key_hash = ?), CURRENT_TIMESTAMP),
                        CURRENT_TIMESTAMP,
                        TRUE,
                        CURRENT_TIMESTAMP
                    )
                ''', (
                    api_key_hash, api_key_masked, usage_data.get('team_id', ''), usage_data.get('email', ''),
                    api_key_hash, api_key_hash, 1 if success else 0, api_key_hash, 0 if success else 1,
                    api_key_hash, tokens, api_key_hash, images, api_key_hash
                ))

                # 更新模型使用统计
                # 首先检查模型是否存在
                cursor.execute('SELECT total_requests FROM model_usage_stats WHERE model_name = ?', (model_name,))
                existing_record = cursor.fetchone()

                if existing_record:
                    # 更新现有记录
                    cursor.execute('''
                        UPDATE model_usage_stats SET
                            total_requests = total_requests + 1,
                            text_requests = text_requests + 1,
                            image_requests = image_requests + ?,
                            successful_requests = successful_requests + ?,
                            failed_requests = failed_requests + ?,
                            total_tokens_generated = total_tokens_generated + ?,
                            total_images_generated = total_images_generated + ?,
                            average_tokens_per_request = ROUND(CAST(total_tokens_generated AS REAL) / GREATEST(total_requests, 1)),
                            total_usage_time = total_usage_time + ?,
                            last_used_at = CURRENT_TIMESTAMP,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE model_name = ?
                    ''', (images, 1 if success else 0, 0 if success else 1, tokens, images, duration, model_name))
                else:
                    # 插入新记录
                    cursor.execute('''
                        INSERT INTO model_usage_stats (
                            model_name, total_requests, text_requests, image_requests,
                            successful_requests, failed_requests, total_tokens_generated,
                            total_images_generated, average_tokens_per_request, total_usage_time,
                            first_used_at, last_used_at, is_active, created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        model_name, 1, 1, images, 1 if success else 0, 0 if success else 1,
                        tokens, images, tokens if tokens > 0 else 0, duration,
                        CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, TRUE,
                        CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                    ))

                # 记录到日志
                print(f"[统计分析] 记录聊天使用: 模型={model_name}, 成功={success}, 耗时={duration:.2f}s")

                conn.commit()

        except Exception as e:
            print(f"[统计分析] 记录聊天使用失败: {e}")

    def record_image_generation(self, image_id: int, generation_data: Dict[str, Any]):
        """记录图片生成事件"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # 准备基础数据
                api_key = generation_data.get('api_key', '')
                api_key_hash = hashlib.sha256(api_key.encode()).hexdigest() if api_key else 'unknown'

                # 插入生成记录
                cursor.execute('''
                    INSERT INTO image_generation_records (
                        image_id, api_key_used, account_team_id, account_email,
                        model_used, prompt_text, prompt_length, generation_duration,
                        success, error_message, request_ip, user_agent,
                        session_id, conversation_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    image_id,
                    api_key_hash,
                    generation_data.get('team_id', ''),
                    generation_data.get('email', ''),
                    generation_data.get('model', 'gemini-enterprise'),
                    generation_data.get('prompt', ''),
                    len(generation_data.get('prompt', '')),
                    generation_data.get('duration', 0),
                    generation_data.get('success', True),
                    generation_data.get('error', ''),
                    generation_data.get('ip', ''),
                    generation_data.get('user_agent', ''),
                    generation_data.get('session_id', ''),
                    generation_data.get('conversation_id')
                ))

                conn.commit()
                print(f"[统计分析] 记录图片生成: image_id={image_id}")

        except Exception as e:
            print(f"[统计分析] 记录生成事件失败: {e}")

    def get_overview_stats(self, days: int = 30) -> Dict[str, Any]:
        """获取总体统计概览"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # 获取指定时间范围内的总体统计
                start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')
                print(f"[统计分析] 概览统计 - 查询时间范围: {start_date} 开始")

                # 从model_usage_stats获取总体统计（包含聊天记录）
                cursor.execute('''
                    SELECT
                        SUM(total_requests) as total_generations,
                        SUM(successful_requests) as successful_generations,
                        SUM(failed_requests) as failed_generations,
                        SUM(total_tokens_generated) as total_tokens,
                        SUM(total_images_generated) as total_images,
                        SUM(total_usage_time) as total_usage_time,
                        COUNT(CASE WHEN total_requests > 0 THEN 1 END) as active_models,
                        ROUND(AVG(average_tokens_per_request), 2) as avg_tokens
                    FROM model_usage_stats
                    WHERE last_used_at >= ? OR (last_used_at < ? AND total_requests > 0)
                ''', (start_date, start_date))

                model_stats = cursor.fetchone()
                print(f"[统计分析] 概览统计 - model_usage_stats查询结果: {model_stats}")

                # 从api_key_usage_stats获取API密钥相关统计
                cursor.execute('''
                    SELECT
                        COUNT(CASE WHEN total_requests > 0 THEN 1 END) as active_keys,
                        SUM(total_requests) as key_total_requests,
                        SUM(successful_requests) as key_successful_requests
                    FROM api_key_usage_stats
                    WHERE last_used_at >= ? OR (last_used_at < ? AND total_requests > 0)
                ''', (start_date, start_date))

                api_stats = cursor.fetchone()

                # 从image_generation_records获取图片生成相关统计（如果有）
                cursor.execute('''
                    SELECT
                        COUNT(*) as image_generations,
                        COUNT(DISTINCT session_id) as unique_sessions,
                        COUNT(DISTINCT user_id) as unique_users,
                        AVG(generation_duration) as avg_duration,
                        COUNT(DISTINCT DATE(generation_time)) as active_days
                    FROM image_generation_records
                    WHERE generation_time >= ?
                ''', (start_date,))

                image_stats = cursor.fetchone()

                # 获取热门模型
                cursor.execute('''
                    SELECT model_name, total_requests, successful_requests
                    FROM model_usage_stats
                    WHERE total_requests > 0
                    ORDER BY total_requests DESC
                    LIMIT 5
                ''')

                top_models_data = cursor.fetchall()

                # 热门关键词
                cursor.execute('''
                    SELECT keyword, usage_count
                    FROM keyword_usage_stats
                    WHERE last_used_at >= ?
                    ORDER BY usage_count DESC
                    LIMIT 10
                ''', (start_date,))

                keyword_stats = cursor.fetchall()

                # 合并计算总统计 - 直接使用model_usage_stats的数据
                total_generations = model_stats[0] or 0
                successful_generations = model_stats[1] or 0

                return {
                    'time_range_days': days,
                    'overall': {
                        'total_generations': total_generations,
                        'successful_generations': successful_generations,
                        'success_rate': round(successful_generations / max(total_generations, 1) * 100, 2),
                        'active_api_keys': api_stats[0] or 0,
                        'unique_sessions': image_stats[1] or 0,
                        'unique_users': image_stats[2] or 0,
                        'avg_generation_duration_ms': round(image_stats[3] or 0, 2),
                        'active_days': image_stats[4] or 0,
                        'total_tokens': model_stats[3] or 0,
                        'total_images': model_stats[4] or 0,
                        'active_models': model_stats[6] or 0
                    },
                    'top_models': [
                        {
                            'model': model,
                            'count': total_requests,
                            'successful': successful_requests,
                            'success_rate': round(successful_requests / max(total_requests, 1) * 100, 2)
                        }
                        for model, total_requests, successful_requests in top_models_data
                    ],
                    'top_keywords': [{'keyword': keyword, 'count': count} for keyword, count in keyword_stats],
                    'generated_at': datetime.now().isoformat()
                }

        except Exception as e:
            print(f"[统计分析] 获取概览统计失败: {e}")
            return {
                'time_range_days': days,
                'overall': {
                    'total_generations': 0,
                    'successful_generations': 0,
                    'success_rate': 0.0,
                    'active_api_keys': 0,
                    'unique_sessions': 0,
                    'unique_users': 0,
                    'avg_generation_duration_ms': 0,
                    'active_days': 0,
                    'total_tokens': 0,
                    'total_images': 0,
                    'active_models': 0
                },
                'top_models': [],
                'top_keywords': [],
                'generated_at': datetime.now().isoformat(),
                'error': str(e)
            }

    def get_api_key_stats(self, limit: int = 20) -> List[Dict[str, Any]]:
        """获取API密钥使用统计"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute('''
                    SELECT
                        api_key_hash,
                        api_key_masked,
                        account_team_id,
                        account_email,
                        total_requests,
                        successful_requests,
                        failed_requests,
                        total_images_generated,
                        first_used_at,
                        last_used_at,
                        is_active
                    FROM api_key_usage_stats
                    ORDER BY total_requests DESC
                    LIMIT ?
                ''', (limit,))

                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()

                # 添加计算字段
                results = []
                for row in rows:
                    data = dict(zip(columns, row))
                    data['success_rate_percent'] = round(
                        (data['successful_requests'] / max(data['total_requests'], 1)) * 100, 2
                    )
                    data['avg_images_per_request'] = round(
                        data['total_images_generated'] / max(data['successful_requests'], 1), 2
                    )
                    results.append(data)

                return results

        except Exception as e:
            print(f"[统计分析] 获取API密钥统计失败: {e}")
            return []

    def get_model_usage_stats(self) -> List[Dict[str, Any]]:
        """获取模型使用统计"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute('SELECT * FROM model_usage_stats ORDER BY total_requests DESC')
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()

                # 添加计算字段
                results = []
                for row in rows:
                    data = dict(zip(columns, row))
                    data['success_rate_percent'] = round(
                        (data['successful_requests'] / max(data['total_requests'], 1)) * 100, 2
                    )
                    data['avg_tokens_per_request'] = round(
                        data['total_tokens_generated'] / max(data['successful_requests'], 1), 2
                    )
                    data['image_request_percent'] = round(
                        (data['image_requests'] / max(data['total_requests'], 1)) * 100, 2
                    )
                    results.append(data)

                return results

        except Exception as e:
            print(f"[统计分析] 获取模型统计失败: {e}")
            return []

    def get_generation_timeline(self, days: int = 7) -> List[Dict[str, Any]]:
        """获取生成时间线数据"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')

                cursor.execute('''
                    SELECT
                        DATE(generation_time) as date,
                        COUNT(*) as total_generations,
                        SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_generations,
                        COUNT(DISTINCT api_key_used) as active_keys,
                        AVG(generation_duration) as avg_duration
                    FROM image_generation_records
                    WHERE generation_time >= ?
                    GROUP BY DATE(generation_time)
                    ORDER BY date DESC
                ''', (start_date,))

                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()

                return [dict(zip(columns, row)) for row in rows]

        except Exception as e:
            print(f"[统计分析] 获取时间线数据失败: {e}")
            return []

    def get_keyword_analysis(self, limit: int = 50) -> List[Dict[str, Any]]:
        """获取关键词分析"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute('''
                    SELECT
                        keyword,
                        usage_count,
                        unique_users,
                        total_images_generated,
                        last_used_at
                    FROM keyword_usage_stats
                    ORDER BY usage_count DESC
                    LIMIT ?
                ''', (limit,))

                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()

                return [dict(zip(columns, row)) for row in rows]

        except Exception as e:
            print(f"[统计分析] 获取关键词分析失败: {e}")
            return []

    def get_user_activity_stats(self, limit: int = 20) -> List[Dict[str, Any]]:
        """获取用户活动统计"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute('''
                    SELECT
                        user_id,
                        total_requests,
                        successful_requests,
                        total_images_generated,
                        total_generation_time,
                        first_request_at,
                        last_request_at
                    FROM user_usage_stats
                    ORDER BY total_requests DESC
                    LIMIT ?
                ''', (limit,))

                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()

                return [dict(zip(columns, row)) for row in rows]

        except Exception as e:
            print(f"[统计分析] 获取用户活动统计失败: {e}")
            return []

# 创建全局分析管理器实例
analytics_manager = None

def get_analytics_manager():
    """获取全局分析管理器实例"""
    global analytics_manager
    if analytics_manager is None:
        analytics_manager = AnalyticsManager()
    return analytics_manager

def check_auth():
    """检查API认证"""
    if require_api_key:
        # 如果设置了认证装饰器，则需要进行认证检查
        # 这里可以手动实现认证逻辑
        required_api_key = os.getenv('DOWNSTREAM_API_KEY', '')
        if required_api_key:
            provided_api_key = request.headers.get('Authorization', '').replace('Bearer ', '').replace('Api-Key ', '')
            if provided_api_key != required_api_key:
                return jsonify({
                    'error': {
                        'message': 'Authentication required',
                        'type': 'authentication_failed'
                    }
                }), 401
    return None

def init_analytics_routes(app):
    """初始化统计分析API路由"""

    @app.route('/v1/analytics/overview', methods=['GET'])
    def get_analytics_overview():
        """获取统计分析概览"""
        # 检查认证
        auth_result = check_auth()
        if auth_result:
            return auth_result

        try:
            days = request.args.get('days', 30, type=int)
            days = min(max(days, 1), 365)  # 限制在1-365天之间

            # 使用真实的分析数据
            print(f"[analytics_apis] 收到统计分析请求，days={days}")
            print(f"[analytics_apis] 开始获取analytics_manager...")
            # 注释掉硬编码测试数据，使用真实数据
            # test_data = {
            #     'time_range_days': days,
            #     'overall': {
            #         'total_generations': 25,
            #         'successful_generations': 23,
            #         'success_rate': 92.0,
            #         'active_api_keys': 1,
            #         'unique_sessions': 3,
            #         'unique_users': 2,
            #         'avg_generation_duration_ms': 1500,
            #         'active_days': 5,
            #         'total_tokens': 5120,
            #         'total_images': 8,
            #         'active_models': 2
            #     },
            #     'top_models': [
            #         {'model': 'gemini-enterprise2', 'count': 20, 'successful': 19, 'success_rate': 95.0},
            #         {'model': 'gemini-1.5-flash', 'count': 5, 'successful': 4, 'success_rate': 80.0}
            #     ],
            #     'top_keywords': [
            #         {'keyword': '编程', 'count': 15},
            #         {'keyword': '设计', 'count': 10}
            #     ],
            #     'generated_at': '2025-12-01T03:30:00.000000'
            # }
            # print(f"[analytics_apis] 返回测试数据: total_generations={test_data['overall']['total_generations']}")
            # return jsonify(test_data)

            manager = get_analytics_manager()
            print(f"[analytics_apis] analytics_manager获取成功: {manager is not None}")
            stats = manager.get_overview_stats(days)
            print(f"[analytics_apis] get_overview_stats返回: {stats}")

            return jsonify(stats)

        except Exception as e:
            return jsonify({'error': f'获取分析概览失败: {str(e)}'}), 500

    @app.route('/v1/analytics/api-keys', methods=['GET'])
    def get_api_key_stats():
        """获取API密钥使用统计"""
        # 检查认证
        auth_result = check_auth()
        if auth_result:
            return auth_result

        try:
            limit = request.args.get('limit', 20, type=int)
            limit = min(max(limit, 1), 100)  # 限制在1-100之间

            manager = get_analytics_manager()
            stats = manager.get_api_key_stats(limit)

            return jsonify({'api_keys': stats})

        except Exception as e:
            return jsonify({'error': f'获取API密钥统计失败: {str(e)}'}), 500

    @app.route('/v1/analytics/models', methods=['GET'])
    def get_model_stats():
        """获取模型使用统计"""
        # 检查认证
        auth_result = check_auth()
        if auth_result:
            return auth_result

        try:
            manager = get_analytics_manager()
            stats = manager.get_model_usage_stats()

            return jsonify({'models': stats})

        except Exception as e:
            return jsonify({'error': f'获取模型统计失败: {str(e)}'}), 500

    @app.route('/v1/analytics/timeline', methods=['GET'])
    def get_generation_timeline():
        """获取生成时间线数据"""
        # 检查认证
        auth_result = check_auth()
        if auth_result:
            return auth_result

        try:
            days = request.args.get('days', 7, type=int)
            days = min(max(days, 1), 30)  # 限制在1-30天之间

            manager = get_analytics_manager()
            timeline = manager.get_generation_timeline(days)

            return jsonify({'timeline': timeline})

        except Exception as e:
            return jsonify({'error': f'获取时间线数据失败: {str(e)}'}), 500

    @app.route('/v1/analytics/keywords', methods=['GET'])
    def get_keyword_analysis():
        """获取关键词分析"""
        # 检查认证
        auth_result = check_auth()
        if auth_result:
            return auth_result

        try:
            limit = request.args.get('limit', 50, type=int)
            limit = min(max(limit, 1), 200)  # 限制在1-200之间

            manager = get_analytics_manager()
            keywords = manager.get_keyword_analysis(limit)

            return jsonify({'keywords': keywords})

        except Exception as e:
            return jsonify({'error': f'获取关键词分析失败: {str(e)}'}), 500

    @app.route('/v1/analytics/users', methods=['GET'])
    def get_user_stats():
        """获取用户活动统计"""
        # 检查认证
        auth_result = check_auth()
        if auth_result:
            return auth_result

        try:
            limit = request.args.get('limit', 20, type=int)
            limit = min(max(limit, 1), 100)  # 限制在1-100之间

            manager = get_analytics_manager()
            stats = manager.get_user_activity_stats(limit)

            return jsonify({'users': stats})

        except Exception as e:
            return jsonify({'error': f'获取用户统计失败: {str(e)}'}), 500

    @app.route('/v1/analytics/dashboard', methods=['GET'])
    def get_analytics_dashboard():
        """获取完整的分析仪表板数据"""
        # 检查认证
        auth_result = check_auth()
        if auth_result:
            return auth_result

        try:
            days = request.args.get('days', 30, type=int)
            days = min(max(days, 1), 365)

            manager = get_analytics_manager()

            dashboard_data = {
                'overview': manager.get_overview_stats(days),
                'timeline': manager.get_generation_timeline(min(days, 7)),  # 时间线最多7天
                'top_models': manager.get_model_usage_stats(),
                'top_keywords': manager.get_keyword_analysis(20),
                'active_users': manager.get_user_activity_stats(10),
                'api_keys': manager.get_api_key_stats(15),
            }

            return jsonify(dashboard_data)

        except Exception as e:
            return jsonify({'error': f'获取仪表板数据失败: {str(e)}'}), 500

    # API密钥批量操作路由
    @app.route('/v1/api-keys/batch-delete', methods=['POST'])
    def batch_delete_api_keys():
        """批量删除API密钥统计数据"""
        try:
            data = request.get_json()
            if not data or 'api_key_hashes' not in data:
                return jsonify({'error': '缺少api_key_hashes参数'}), 400

            api_key_hashes = data['api_key_hashes']
            if not isinstance(api_key_hashes, list):
                return jsonify({'error': 'api_key_hashes必须是数组'}), 400

            manager = get_analytics_manager()
            deleted_count = manager.batch_delete_api_keys(api_key_hashes)

            return jsonify({
                'message': f'成功删除 {deleted_count} 个API密钥记录',
                'deleted_count': deleted_count
            })

        except Exception as e:
            return jsonify({'error': f'批量删除失败: {str(e)}'}), 500

    @app.route('/v1/api-keys/clear-all', methods=['POST'])
    def clear_all_api_keys():
        """清空所有API密钥统计数据"""
        try:
            # 添加安全确认
            data = request.get_json() or {}
            confirmation = data.get('confirmation', '')

            if confirmation != 'CLEAR_ALL_API_KEYS_CONFIRMED':
                return jsonify({'error': '需要提供确认参数 confirmation: CLEAR_ALL_API_KEYS_CONFIRMED'}), 400

            manager = get_analytics_manager()
            deleted_count = manager.clear_all_api_keys()

            return jsonify({
                'message': f'成功清空 {deleted_count} 个API密钥记录',
                'deleted_count': deleted_count,
                'warning': '此操作不可撤销，所有API密钥统计数据已被永久删除'
            })

        except Exception as e:
            return jsonify({'error': f'清空操作失败: {str(e)}'}), 500

    @app.route('/v1/api-keys/batch-import', methods=['POST'])
    def batch_import_api_keys():
        """批量导入API密钥统计数据"""
        try:
            data = request.get_json()
            if not data or 'accounts' not in data:
                return jsonify({'error': '缺少accounts参数'}), 400

            accounts = data['accounts']
            if not isinstance(accounts, list):
                return jsonify({'error': 'accounts必须是数组'}), 400

            if len(accounts) > 1000:
                return jsonify({'error': '单次导入不能超过1000个账号'}), 400

            manager = get_analytics_manager()
            result = manager.batch_import_api_keys(accounts)

            return jsonify({
                'message': f'成功导入 {result["imported_count"]} 个API密钥',
                'imported_count': result['imported_count'],
                'skipped_count': result['skipped_count'],
                'error_count': result['error_count'],
                'details': result['details']
            })

        except Exception as e:
            return jsonify({'error': f'批量导入失败: {str(e)}'}), 500

    @app.route('/v1/api-keys/export', methods=['GET'])
    def export_api_keys():
        """导出API密钥统计数据"""
        try:
            manager = get_analytics_manager()
            keys_data = manager.export_api_keys()

            return jsonify({
                'accounts': keys_data,
                'total_count': len(keys_data),
                'exported_at': datetime.now().isoformat()
            })

        except Exception as e:
            return jsonify({'error': f'导出失败: {str(e)}'}), 500

    print("[统计分析] API路由初始化完成")