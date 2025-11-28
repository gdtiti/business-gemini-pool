#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理端口冲突并用最新代码启动Flask应用
"""

import subprocess
import sys
import time
import os

def kill_processes_on_port(port):
    """强制终止占用指定端口的进程"""
    try:
        # 查找占用端口的进程
        result = subprocess.run(
            ['netstat', '-ano'],
            capture_output=True,
            text=True,
            encoding='gbk'
        )

        pids = []
        for line in result.stdout.split('\n'):
            if f':{port}' in line and 'LISTENING' in line:
                parts = line.split()
                if len(parts) >= 5:
                    pid = parts[-1]
                    if pid.isdigit():
                        pids.append(pid)

        # 去重
        pids = list(set(pids))
        print(f"Found processes on port {port}: {pids}")

        # 终止进程
        for pid in pids:
            try:
                subprocess.run(['taskkill', '/PID', pid, '/F'],
                             capture_output=True, check=False)
                print(f"Killed process {pid}")
            except Exception as e:
                print(f"Failed to kill process {pid}: {e}")

        return len(pids) > 0

    except Exception as e:
        print(f"Error killing processes: {e}")
        return False

def wait_for_port_free(port, timeout=10):
    """等待端口释放"""
    for i in range(timeout):
        try:
            result = subprocess.run(
                ['netstat', '-ano'],
                capture_output=True,
                text=True,
                encoding='gbk'
            )

            if f':{port}' not in result.stdout or 'LISTENING' not in result.stdout:
                print(f"Port {port} is free!")
                return True

        except Exception:
            pass

        print(f"Waiting for port {port} to be free... ({i+1}/{timeout})")
        time.sleep(1)

    return False

def start_flask_app(port=7860):
    """启动Flask应用"""
    try:
        print(f"Starting Flask app on port {port}...")

        # 切换到正确的工作目录
        os.chdir('D:/_Works/_HFSpace/business-gemini-pool')

        # 构建启动命令
        cmd = [
            sys.executable, '-c',
            f'''
import sys
sys.path.insert(0, ".")
from gemini import app
print("Starting Flask app with latest code...")
print("Image gallery route should be available now!")
app.run(host="0.0.0.0", port={port}, debug=False)
'''
        ]

        # 启动应用
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8'
        )

        print(f"Flask app started with PID: {process.pid}")
        return process

    except Exception as e:
        print(f"Failed to start Flask app: {e}")
        return None

if __name__ == "__main__":
    port = 7860

    print("=== Fix 7860 Port 404 Issue ===")
    print(f"Target port: {port}")

    # 1. 终止占用端口的进程
    print("\n1. Killing processes on port 7860...")
    if kill_processes_on_port(port):
        print("✓ Processes killed")
    else:
        print("No processes to kill")

    # 2. 等待端口释放
    print(f"\n2. Waiting for port {port} to be free...")
    if wait_for_port_free(port):
        print("✓ Port is free")
    else:
        print("⚠ Port might still be in use")

    # 3. 启动最新的Flask应用
    print(f"\n3. Starting latest Flask app on port {port}...")
    flask_process = start_flask_app(port)

    if flask_process:
        print("✓ Flask app started successfully!")
        print(f"Visit: http://127.0.0.1:{port}/image_gallery.html")
        print(f"API: http://127.0.0.1:{port}/v1/images")
        print("\nPress Ctrl+C to stop the application")

        try:
            # 等待进程输出
            while True:
                output = flask_process.stdout.readline()
                if output:
                    print(output.strip())
                if flask_process.poll() is not None:
                    break
        except KeyboardInterrupt:
            print("\nStopping Flask app...")
            flask_process.terminate()
    else:
        print("❌ Failed to start Flask app")