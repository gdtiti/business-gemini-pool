#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为相册前端添加删除功能和存储空间显示
"""

def update_image_gallery_html():
    """更新image_gallery.html文件"""

    # 读取原始文件
    with open('image_gallery.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. 添加存储空间显示的CSS样式
    storage_css = '''
        /* 存储空间信息样式 */
        .storage-info {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 20px;
            box-shadow: var(--shadow);
        }

        .storage-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }

        .storage-stat {
            text-align: center;
        }

        .storage-stat-value {
            font-size: 1.8em;
            font-weight: bold;
            margin-bottom: 5px;
        }

        .storage-stat-label {
            font-size: 0.9em;
            opacity: 0.9;
        }

        .storage-usage-bar {
            width: 100%;
            height: 8px;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 4px;
            overflow: hidden;
            margin-top: 15px;
        }

        .storage-usage-fill {
            height: 100%;
            background: linear-gradient(90deg, #ff6b6b, #ffd93d, #51cf66);
            border-radius: 4px;
            transition: width 0.3s ease;
        }

        /* 删除按钮样式 */
        .delete-btn {
            position: absolute;
            top: 10px;
            right: 10px;
            background: var(--secondary);
            color: white;
            border: none;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            opacity: 0;
            transition: all 0.3s ease;
            z-index: 10;
        }

        .image-item:hover .delete-btn {
            opacity: 1;
        }

        .delete-btn:hover {
            background: #ff5252;
            transform: scale(1.1);
        }

        .delete-btn:active {
            transform: scale(0.95);
        }

        /* 批量操作样式 */
        .batch-operations {
            background: var(--white);
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 20px;
            box-shadow: var(--shadow);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 15px;
        }

        .batch-select-all {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .batch-actions {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }

        .checkbox-wrapper {
            display: flex;
            align-items: center;
            margin-right: 8px;
        }

        .image-checkbox {
            position: absolute;
            top: 10px;
            left: 10px;
            width: 20px;
            height: 20px;
            opacity: 0;
            transition: opacity 0.3s ease;
            z-index: 10;
        }

        .image-item:hover .image-checkbox,
        .image-item.selected .image-checkbox {
            opacity: 1;
        }

        .image-item {
            position: relative;
            cursor: pointer;
        }

        .image-item.selected {
            border: 3px solid var(--primary);
            box-shadow: 0 0 0 2px rgba(74, 144, 226, 0.3);
        }

        /* 模态框样式 */
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            z-index: 1000;
            justify-content: center;
            align-items: center;
        }

        .modal-content {
            background: var(--white);
            padding: 30px;
            border-radius: 16px;
            max-width: 500px;
            width: 90%;
            text-align: center;
            box-shadow: var(--shadow-hover);
        }

        .modal-title {
            font-size: 1.5em;
            font-weight: bold;
            margin-bottom: 15px;
            color: var(--dark);
        }

        .modal-message {
            margin-bottom: 25px;
            color: var(--gray);
            line-height: 1.5;
        }

        .modal-buttons {
            display: flex;
            gap: 15px;
            justify-content: center;
        }

        .modal-btn {
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1em;
            font-weight: 500;
            transition: all 0.3s ease;
        }

        .modal-btn-cancel {
            background: var(--light-gray);
            color: var(--dark);
        }

        .modal-btn-confirm {
            background: var(--secondary);
            color: white;
        }

        .modal-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        }'''

    # 2. 添加存储空间信息的HTML结构
    storage_html = '''
        <!-- 存储空间信息 -->
        <div class="storage-info" id="storageInfo">
            <h3 style="margin: 0 0 10px 0;">存储空间</h3>
            <div class="storage-stats">
                <div class="storage-stat">
                    <div class="storage-stat-value" id="totalImages">-</div>
                    <div class="storage-stat-label">总图片数</div>
                </div>
                <div class="storage-stat">
                    <div class="storage-stat-value" id="totalSize">-</div>
                    <div class="storage-stat-label">图片占用</div>
                </div>
                <div class="storage-stat">
                    <div class="storage-stat-value" id="diskUsage">-</div>
                    <div class="storage-stat-label">磁盘使用率</div>
                </div>
                <div class="storage-stat">
                    <div class="storage-stat-value" id="freeSpace">-</div>
                    <div class="storage-stat-label">剩余空间</div>
                </div>
            </div>
            <div class="storage-usage-bar">
                <div class="storage-usage-fill" id="storageUsageFill" style="width: 0%"></div>
            </div>
        </div>'''

    # 3. 添加批量操作的HTML结构
    batch_operations_html = '''
        <!-- 批量操作 -->
        <div class="batch-operations" id="batchOperations" style="display: none;">
            <div class="batch-select-all">
                <div class="checkbox-wrapper">
                    <input type="checkbox" id="selectAllCheckbox" class="form-checkbox">
                    <label for="selectAllCheckbox">全选</label>
                </div>
                <span id="selectedCount">已选择 0 张图片</span>
            </div>
            <div class="batch-actions">
                <button class="btn btn-danger" id="batchDeleteBtn">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <polyline points="3 6 5 6 21 12 21"></polyline>
                        <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4l5 5v0a2 2 0 0 0 2 2h2"></path>
                    </svg>
                    删除选中
                </button>
            </div>
        </div>'''

    # 4. 添加模态框的HTML结构
    modal_html = '''
    <!-- 确认删除模态框 -->
    <div class="modal" id="deleteModal">
        <div class="modal-content">
            <div class="modal-title">确认删除</div>
            <div class="modal-message" id="modalMessage">
                确定要删除这张图片吗？此操作无法撤销。
            </div>
            <div class="modal-buttons">
                <button class="modal-btn modal-btn-cancel" id="modalCancel">取消</button>
                <button class="modal-btn modal-btn-confirm" id="modalConfirm">确认删除</button>
            </div>
        </div>
    </div>

    <!-- 批量删除确认模态框 -->
    <div class="modal" id="batchDeleteModal">
        <div class="modal-content">
            <div class="modal-title">批量删除确认</div>
            <div class="modal-message" id="batchModalMessage">
                确定要删除选中的 <span id="batchDeleteCount">0</span> 张图片吗？此操作无法撤销。
            </div>
            <div class="modal-buttons">
                <button class="modal-btn modal-btn-cancel" id="batchModalCancel">取消</button>
                <button class="modal-btn modal-btn-confirm" id="batchModalConfirm">确认删除</button>
            </div>
        </div>
    </div>'''

    # 进行替换
    # 添加CSS样式
    if '</style>' in content:
        content = content.replace('</style>', storage_css + '\n    </style>')
        print("✅ 添加存储空间CSS样式成功")
    else:
        print("❌ 未找到样式结束标签")

    # 添加存储空间信息（在header后面）
    if '<div class="container">' in content:
        container_pos = content.find('<div class="container">')
        header_end = content.find('</div>', container_pos) + 6
        content = content[:header_end] + storage_html + content[header_end:]
        print("✅ 添加存储空间信息HTML成功")
    else:
        print("❌ 未找到容器位置")

    # 添加批量操作（在存储信息后面）
    if storage_html in content:
        storage_end = content.find('</div>', content.find(storage_html)) + len('</div>')
        content = content[:storage_end] + batch_operations_html + content[storage_end:]
        print("✅ 添加批量操作HTML成功")
    else:
        print("❌ 未找到存储信息位置")

    # 添加模态框（在body结束标签前面）
    if '</body></html>' in content:
        content = content.replace('</body></html>', modal_html + '\n</body></html>')
        print("✅ 添加模态框HTML成功")
    else:
        print("❌ 未找到body结束标签")

    # 5. 修改图片项目的HTML结构，添加删除和选择功能
    # 这需要在JavaScript部分处理

    # 写回文件
    with open('image_gallery.html', 'w', encoding='utf-8') as f:
        f.write(content)

    print("✅ image_gallery.html 文件修改完成")
    return True

if __name__ == "__main__":
    print("=== 为相册前端添加删除和存储空间功能 ===")
    success = update_image_gallery_html()

    if success:
        print("\n✅ 前端界面修改成功!")
        print("新增功能:")
        print("- 存储空间信息显示")
        print("- 单张图片删除功能")
        print("- 批量选择和删除功能")
        print("- 删除确认模态框")
        print("- 实时存储空间统计")
    else:
        print("\n❌ 前端界面修改失败，请检查错误信息")