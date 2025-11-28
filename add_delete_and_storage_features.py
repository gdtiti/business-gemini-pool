#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为相册添加删除照片和存储空间功能
"""

import os
import shutil

def modify_gemini_file():
    """修改gemini.py文件添加新功能"""

    # 读取原始文件
    with open('gemini.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. 修改统计API以包含存储空间信息
    old_stats_function = '''@app.route('/v1/images/statistics', methods=['GET'])
@require_api_key
def get_image_statistics():
    """获取用户图片统计信息"""
    try:
        user_id = get_user_id_from_request()
        if not user_id:
            return jsonify({"error": "无法识别用户"}), 401

        conversation_manager = get_conversation_manager()
        total_count = conversation_manager.get_image_count(user_id)

        return jsonify({
            'total_images': total_count,
            'storage_info': {
                'image_directory': str(IMAGE_CACHE_DIR),
                'max_file_size': '10MB'
            },
            'last_updated': datetime.now().isoformat()
        })

    except Exception as e:
        logger = logging.getLogger('gemini_pool.api')
        logger.error(f"获取图片统计失败: {e}")
        return jsonify({"error": "获取图片统计失败"}), 500'''

    new_stats_function = '''@app.route('/v1/images/statistics', methods=['GET'])
@require_api_key
def get_image_statistics():
    """获取用户图片统计信息"""
    try:
        user_id = get_user_id_from_request()
        if not user_id:
            return jsonify({"error": "无法识别用户"}), 401

        # 计算存储空间使用情况
        total_size = 0
        total_count = 0

        try:
            for filename in os.listdir(IMAGE_CACHE_DIR):
                file_path = IMAGE_CACHE_DIR / filename
                if file_path.is_file() and filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp')):
                    stat = file_path.stat()
                    total_size += stat.st_size
                    total_count += 1
        except Exception:
            pass  # 如果计算失败，使用默认值

        # 获取磁盘空间信息
        try:
            statvfs = os.statvfs(IMAGE_CACHE_DIR)
            total_space = statvfs.f_frsize * statvfs.f_blocks
            free_space = statvfs.f_frsize * statvfs.f_bavail
            used_space = total_space - free_space
        except (AttributeError, OSError):
            # Windows系统或获取失败时的处理
            import shutil
            try:
                total_space, free_space = shutil.disk_usage(IMAGE_CACHE_DIR)[:2]
                used_space = total_space - free_space
            except:
                total_space = free_space = used_space = 0

        return jsonify({
            'total_images': total_count,
            'storage_info': {
                'image_directory': str(IMAGE_CACHE_DIR),
                'total_size_bytes': total_size,
                'total_size_human': format_bytes(total_size),
                'disk_total_bytes': total_space,
                'disk_total_human': format_bytes(total_space),
                'disk_used_bytes': used_space,
                'disk_used_human': format_bytes(used_space),
                'disk_free_bytes': free_space,
                'disk_free_human': format_bytes(free_space),
                'usage_percentage': round((used_space / total_space * 100), 2) if total_space > 0 else 0
            },
            'last_updated': datetime.now().isoformat()
        })

    except Exception as e:
        logger = logging.getLogger('gemini_pool.api')
        logger.error(f"获取图片统计失败: {e}")
        return jsonify({"error": "获取图片统计失败"}), 500'''

    # 2. 添加删除单个图片的API
    delete_image_function = '''
@app.route('/v1/images/delete', methods=['POST'])
@require_api_key
def delete_image_by_filename():
    """通过文件名删除图片"""
    try:
        user_id = get_user_id_from_request()
        if not user_id:
            return jsonify({"error": "无法识别用户"}), 401

        data = request.get_json()
        if not data or 'filename' not in data:
            return jsonify({"error": "请提供文件名"}), 400

        filename = data['filename']
        if not filename or isinstance(filename, str):
            return jsonify({"error": "无效的文件名"}), 400

        # 安全检查：只允许图片文件名
        allowed_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp')
        if not filename.lower().endswith(allowed_extensions):
            return jsonify({"error": "不支持的文件类型"}), 400

        # 构建文件路径
        file_path = IMAGE_CACHE_DIR / filename

        # 检查文件是否存在
        if not file_path.exists():
            return jsonify({"error": "文件不存在"}), 404

        # 检查是否为文件
        if not file_path.is_file():
            return jsonify({"error": "无效的文件路径"}), 400

        # 删除文件
        try:
            file_path.unlink()
            logger = logging.getLogger('gemini_pool.api')
            logger.info(f"用户 {user_id} 删除了图片: {filename}")

            return jsonify({
                "message": f"图片 {filename} 删除成功",
                "filename": filename
            })
        except OSError as e:
            logger = logging.getLogger('gemini_pool.api')
            logger.error(f"删除文件失败: {filename}, 错误: {e}")
            return jsonify({"error": "删除文件失败"}), 500

    except Exception as e:
        logger = logging.getLogger('gemini_pool.api')
        logger.error(f"删除图片失败: {e}")
        return jsonify({"error": "删除图片失败"}), 500

# 添加字节格式化函数
def format_bytes(bytes_value):
    """格式化字节数为人类可读格式"""
    if bytes_value == 0:
        return "0 B"

    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} PB"'''

    # 3. 添加批量删除API
    batch_delete_function = '''
@app.route('/v1/images/batch-delete', methods=['POST'])
@require_api_key
def batch_delete_images():
    """批量删除图片"""
    try:
        user_id = get_user_id_from_request()
        if not user_id:
            return jsonify({"error": "无法识别用户"}), 401

        data = request.get_json()
        if not data or 'filenames' not in data:
            return jsonify({"error": "请提供要删除的文件名列表"}), 400

        filenames = data['filenames']
        if not isinstance(filenames, list) or len(filenames) == 0:
            return jsonify({"error": "无效的文件名列表"}), 400

        if len(filenames) > 50:  # 限制批量删除数量
            return jsonify({"error": "一次最多删除50张图片"}), 400

        # 安全检查和删除
        deleted_files = []
        failed_files = []

        for filename in filenames:
            if not isinstance(filename, str):
                failed_files.append({"filename": str(filename), "error": "无效的文件名"})
                continue

            # 只允许图片文件
            allowed_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp')
            if not filename.lower().endswith(allowed_extensions):
                failed_files.append({"filename": filename, "error": "不支持的文件类型"})
                continue

            file_path = IMAGE_CACHE_DIR / filename

            if not file_path.exists():
                failed_files.append({"filename": filename, "error": "文件不存在"})
                continue

            if not file_path.is_file():
                failed_files.append({"filename": filename, "error": "无效的文件路径"})
                continue

            try:
                file_path.unlink()
                deleted_files.append(filename)
            except OSError as e:
                failed_files.append({"filename": filename, "error": f"删除失败: {str(e)}"})

        logger = logging.getLogger('gemini_pool.api')
        logger.info(f"用户 {user_id} 批量删除图片: 成功 {len(deleted_files)}, 失��� {len(failed_files)}")

        return jsonify({
            "message": f"批量删除完成",
            "deleted_count": len(deleted_files),
            "deleted_files": deleted_files,
            "failed_count": len(failed_files),
            "failed_files": failed_files
        })

    except Exception as e:
        logger = logging.getLogger('gemini_pool.api')
        logger.error(f"批量删除图片失败: {e}")
        return jsonify({"error": "批量删除图片失败"}), 500'''

    # 进行替换
    if old_stats_function in content:
        content = content.replace(old_stats_function, new_stats_function)
        print("✅ 更新统计API成功")
    else:
        print("❌ 未找到统计API函数")
        return False

    # 添加新的删除API函数
    # 在统计API后面添加
    if delete_image_function not in content:
        stats_end = content.find('return jsonify({"error": "获取图片统计失败"}), 500')
        if stats_end != -1:
            insert_pos = content.find('\n', stats_end) + 1
            content = content[:insert_pos] + delete_image_function + content[insert_pos:]
            print("✅ 添加删除图片API成功")
        else:
            print("❌ 未找到统计API结束位置")
            return False
    else:
        print("✅ 删除图片API已存在")

    # 添加批量删除API
    if batch_delete_function not in content:
        # 在删除单个图片API后面添加
        delete_end = content.find('return jsonify({"error": "删除图片失败"}), 500')
        if delete_end != -1:
            insert_pos = content.find('\n', delete_end) + 1
            content = content[:insert_pos] + batch_delete_function + content[insert_pos:]
            print("✅ 添加批量删除API成功")
        else:
            print("❌ 未找到删除API结束位置")
            return False
    else:
        print("✅ 批量删除API已存在")

    # 写回文件
    with open('gemini.py', 'w', encoding='utf-8') as f:
        f.write(content)

    print("✅ gemini.py 文件修改完成")
    return True

if __name__ == "__main__":
    print("=== 为相册添加删除和存储空间功能 ===")
    success = modify_gemini_file()

    if success:
        print("\n✅ 所有功能添加成功!")
        print("新增的API接口:")
        print("- DELETE /v1/images/delete - 删除单张图片")
        print("- POST /v1/images/batch-delete - 批量删除图片")
        print("- GET /v1/images/statistics - 获取统计和存储空间信息")
    else:
        print("\n❌ 部分功能添加失败，请检查错误信息")