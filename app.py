#!/usr/bin/env python3
"""
HuggingFace Space 入口文件
"""

if __name__ == "__main__":
    from gemini import print_startup_info, account_manager, app

    # 打印启动��息
    print_startup_info()

    # 检查是否有配置
    if not account_manager.accounts:
        print("\n" + "="*60)
        print("❌ 配置错误: 未检测到任何账号配置")
        print("请在 HuggingFace Space 设置中配置 ACCOUNTS_CONFIG 环境变量")
        print("="*60)
        import sys
        sys.exit(1)

    # 启动 Flask 应用
    print("✅ 配置验证通过，启动服务...")
    app.run(host='0.0.0.0', port=8000, debug=False)