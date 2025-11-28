#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试相册功能
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_gallery_routes():
    """测试相册路由是否正确注册"""
    try:
        from gemini import app

        print("=== Flask应用路由列表 ===")
        routes = []
        for rule in app.url_map.iter_rules():
            if 'image' in rule.rule or 'gallery' in rule.rule:
                methods = ','.join(sorted(rule.methods - {'OPTIONS', 'HEAD'}))
                routes.append(f"{rule.rule:35} [{methods:15}] {rule.endpoint}")
                print(f"✓ {rule.rule:35} [{methods:15}] {rule.endpoint}")

        if not routes:
            print("❌ 未找到任何图片相关路由!")
            return False

        print(f"\n总共找到 {len(routes)} 个图片相关路由")

        # 检查image_gallery路由
        has_gallery_route = any('image_gallery' in route[0] for route in routes)
        if has_gallery_route:
            print("✅ image_gallery.html 路由已注册")
        else:
            print("❌ image_gallery.html 路由未找到")
            return False

        return True

    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_file_exists():
    """测试文件是否存在"""
    gallery_file = "image_gallery.html"
    if os.path.exists(gallery_file):
        print(f"✅ {gallery_file} 文件存在")
        return True
    else:
        print(f"❌ {gallery_file} 文件不存在")
        return False

def test_direct_flask():
    """直接启动Flask应用进行测试"""
    try:
        from gemini import app

        print("\n=== 启动Flask测试服务器 ===")
        print("正在启动测试服务器在 http://127.0.0.1:7862")
        print("请访问 http://127.0.0.1:7862/image_gallery.html 进行测试")
        print("按 Ctrl+C 停止服务器")

        app.run(host='127.0.0.1', port=7862, debug=True)

    except Exception as e:
        print(f"❌ 启动失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=== 相册功能诊断工具 ===\n")

    print("1. 检查文件存在性...")
    file_ok = test_file_exists()

    print("\n2. 检查路由注册...")
    routes_ok = test_gallery_routes()

    if file_ok and routes_ok:
        print("\n✅ 基础检查通过，启动测试服务器...")
        test_direct_flask()
    else:
        print("\n❌ 基础检查失败，请修复上述问题")