#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
使用Miniconda Python启动Alethea项目
"""

import os
import sys
import subprocess
import datetime

def log_message(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

log_message("🚀 使用Miniconda Python启动Alethea项目")
log_message("=" * 60)

# 设置Python路径
PYTHON_PATH = "/c/ProgramData/miniconda3/python.exe"
PROJECT_DIR = "/c/Users/wukep/Documents/alethea"

log_message(f"Python路径: {PYTHON_PATH}")
log_message(f"项目目录: {PROJECT_DIR}")

# 检查Python是否可用
try:
    result = subprocess.run([PYTHON_PATH, "--version"], 
                          capture_output=True, text=True, cwd=PROJECT_DIR)
    if result.returncode == 0:
        log_message(f"✅ Python版本: {result.stdout.strip()}")
    else:
        log_message(f"❌ Python检查失败: {result.stderr}")
        exit(1)
except Exception as e:
    log_message(f"❌ 无法执行Python: {e}")
    exit(1)

# 检查Flask是否可用
try:
    result = subprocess.run([PYTHON_PATH, "-c", "import flask; print(f'Flask {flask.__version__}')"], 
                          capture_output=True, text=True, cwd=PROJECT_DIR)
    if result.returncode == 0:
        log_message(f"✅ {result.stdout.strip()}")
    else:
        log_message(f"❌ Flask检查失败: {result.stderr}")
        exit(1)
except Exception as e:
    log_message(f"❌ 无法检查Flask: {e}")
    exit(1)

log_message("🌐 启动Alethea服务器...")
log_message("📍 访问地址: http://localhost:8083")
log_message("⏹️  按 Ctrl+C 停止服务器")
log_message("=" * 60)

# 启动主应用
try:
    # 首先尝试启动最小化版本
    log_message("启动最小化测试版本...")
    subprocess.run([PYTHON_PATH, "minimal_start.py"], cwd=PROJECT_DIR)
except KeyboardInterrupt:
    log_message("用户中断服务器")
except Exception as e:
    log_message(f"❌ 服务器启动失败: {e}")
    
    # 如果最小化版本失败，尝试完整版本
    log_message("尝试启动完整版本...")
    try:
        subprocess.run([PYTHON_PATH, "src/main.py"], cwd=PROJECT_DIR)
    except Exception as e2:
        log_message(f"❌ 完整版本也启动失败: {e2}")

log_message("程序结束")
