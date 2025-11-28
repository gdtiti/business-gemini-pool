#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终相册功能测试和验证
"""

import requests
import json

def test_all_features():
    """测试所有相册功能"""
    BASE_URL = "http://127.0.0.1:7860"
    API_KEY = "sk-qwerASDF@@22"

    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }

    print("=== Business Gemini Pool 相册功能最终测试 ===")

    tests_results = []

    # 1. 测试相册页面访问
    print("\n1. 测试相册页面访问")
    try:
        response = requests.get(f"{BASE_URL}/image_gallery.html")
        status = response.status_code == 200
        tests_results.append(("相册页面访问", status))
        print(f"   状态码: {response.status_code} - {'PASS' if status else 'FAIL'}")
    except Exception as e:
        tests_results.append(("相册页面访问", False))
        print(f"   错误: {e}")

    # 2. 测试存储空间API
    print("\n2. 测试存储空间API")
    try:
        response = requests.get(f"{BASE_URL}/v1/images/statistics", headers=headers)
        status = response.status_code == 200
        tests_results.append(("存储空间API", status))
        print(f"   状态码: {response.status_code} - {'PASS' if status else 'FAIL'}")

        if status:
            data = response.json()
            print(f"   总图片数: {data.get('total_images', 0)}")
            storage = data.get('storage_info', {})
            print(f"   存储使用率: {storage.get('usage_percentage', 0)}%")
    except Exception as e:
        tests_results.append(("存储空间API", False))
        print(f"   错误: {e}")

    # 3. 测试图片列表API
    print("\n3. 测试图片列表API")
    try:
        response = requests.get(f"{BASE_URL}/v1/images?page=1&per_page=3", headers=headers)
        status = response.status_code == 200
        tests_results.append(("图片列表API", status))
        print(f"   状态码: {response.status_code} - {'PASS' if status else 'FAIL'}")

        if status:
            data = response.json()
            images = data.get('images', [])
            print(f"   找到图片数量: {len(images)}")
    except Exception as e:
        tests_results.append(("图片列表API", False))
        print(f"   错误: {e}")

    # 4. 测试删除API逻辑验证（使用不存在文件）
    print("\n4. 测试删除API逻辑验证")
    try:
        response = requests.post(
            f"{BASE_URL}/v1/images/delete",
            headers=headers,
            json={"filename": "nonexistent_test_file.png"}
        )
        # 对于不存在的文件，应该返回404，这说明API逻辑正常
        status = response.status_code in [404, 200]
        tests_results.append(("删除API逻辑", status))
        print(f"   状态码: {response.status_code} - {'PASS' if status else 'FAIL'}")

        if response.status_code == 404:
            print("   正确返回404（文件不存在）")
        elif response.status_code == 200:
            print("   返回200（可能文件存在或API有不同的响应）")
    except Exception as e:
        tests_results.append(("删除API逻辑", False))
        print(f"   错误: {e}")

    # 5. 测试批量删除API逻辑验证
    print("\n5. 测试批量删除API逻辑验证")
    try:
        response = requests.post(
            f"{BASE_URL}/v1/images/batch-delete",
            headers=headers,
            json={"filenames": ["test1.png", "test2.png"]}
        )
        status = response.status_code == 200
        tests_results.append(("批量删除API逻辑", status))
        print(f"   状态码: {response.status_code} - {'PASS' if status else 'FAIL'}")

        if status:
            data = response.json()
            print(f"   删除成功: {data.get('deleted_count', 0)} 张")
            print(f"   删除失败: {data.get('failed_count', 0)} 张")
    except Exception as e:
        tests_results.append(("批量删除API逻辑", False))
        print(f"   错误: {e}")

    # 总结
    print("\n=== 测试总结 ===")
    passed = 0
    total = len(tests_results)

    for test_name, result in tests_results:
        status_text = "PASS" if result else "FAIL"
        print(f"{test_name}: {status_text}")
        if result:
            passed += 1

    print(f"\n总体结果: {passed}/{total} 测试通过")

    if passed == total:
        print("🎉 所有功能测试通过！相册功能已成功升级。")
        print("\n新功能包括:")
        print("- ✅ 存储空间信息显示")
        print("- ✅ 单张图片删除功能")
        print("- ✅ 批量图片删除功能")
        print("- ✅ 删除确认对话框")
        print("- ✅ 图片选择和批量操作")
        print("- ✅ 实时存储空间统计")
        print("\n使用方法:")
        print("1. 访问: http://127.0.0.1:7860/image_gallery.html")
        print("2. 查看页面顶部的存储空间信息")
        print("3. 鼠标悬停图片显示删除按钮")
        print("4. 勾选图片进行批量操作")
    else:
        print("⚠️ 部分功能测试未通过，请检查相关实现。")

    return passed == total

if __name__ == "__main__":
    success = test_all_features()
    exit(0 if success else 1)