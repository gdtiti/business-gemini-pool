#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask路由调试脚本 - 导入并检查应用中注册的所有路由
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from gemini import app

    print("Flask应用路由列表:")
    print("=" * 80)

    for rule in app.url_map.iter_rules():
        methods = ','.join(sorted(rule.methods - {'OPTIONS', 'HEAD'}))
        print(f"{rule.rule:35} [{methods:15}] {rule.endpoint}")

    print("=" * 80)

    # 特别检查image_gallery路由
    image_gallery_rule = None
    for rule in app.url_map.iter_rules():
        if 'image_gallery' in rule.rule or 'image_gallery' in rule.endpoint:
            image_gallery_rule = rule
            break

    if image_gallery_rule:
        print(f"找到image_gallery路由: {image_gallery_rule.rule} -> {image_gallery_rule.endpoint}")
    else:
        print("❌ 未找到image_gallery路由!")

    # 检查chat_history路由作为对比
    chat_history_rule = None
    for rule in app.url_map.iter_rules():
        if 'chat_history' in rule.rule or 'chat_history' in rule.endpoint:
            chat_history_rule = rule
            break

    if chat_history_rule:
        print(f"找到chat_history路由: {chat_history_rule.rule} -> {chat_history_rule.endpoint}")

except ImportError as e:
    print(f"导入gemini模块失败: {e}")
except Exception as e:
    print(f"其他错误: {e}")
    import traceback
    traceback.print_exc()