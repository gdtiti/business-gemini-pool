#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查数据库表结构
"""
import sqlite3
import os

def check_database_structure():
    """检查数据库结构和内容"""
    db_path = "conversations.db"

    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        return

    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

            print("=== 数据库表列表 ===")
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()

            for table in tables:
                table_name = table[0]
                print(f"\n表: {table_name}")

                # 获取表结构
                cursor.execute(f"PRAGMA table_info({table_name});")
                columns = cursor.fetchall()
                print("  列:")
                for col in columns:
                    print(f"    {col[1]} {col[2]}")

                # 获取记录数
                cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
                count = cursor.fetchone()[0]
                print(f"  记录数: {count}")

                # 如果是相关表，显示一些示例数据
                if 'usage' in table_name.lower() or 'stats' in table_name.lower():
                    try:
                        cursor.execute(f"SELECT * FROM {table_name} LIMIT 3;")
                        rows = cursor.fetchall()
                        if rows:
                            print("  示例数据:")
                            for row in rows:
                                print(f"    {row}")
                    except Exception as e:
                        print(f"  无法获取示例数据: {e}")

    except Exception as e:
        print(f"数据库连接失败: {e}")

if __name__ == "__main__":
    check_database_structure()