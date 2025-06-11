#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试启动脚本
"""

import sys
import os

print("=== Alethea 启动测试 ===")
print(f"Python版本: {sys.version}")
print(f"当前目录: {os.getcwd()}")
print(f"Python路径: {sys.path}")

# 测试基本导入
print("\n=== 测试基本导入 ===")
try:
    import flask
    print(f"✅ Flask版本: {flask.__version__}")
except ImportError as e:
    print(f"❌ Flask导入失败: {e}")
    sys.exit(1)

try:
    import flask_sqlalchemy
    print("✅ Flask-SQLAlchemy导入成功")
except ImportError as e:
    print(f"❌ Flask-SQLAlchemy导入失败: {e}")

# 测试项目导入
print("\n=== 测试项目导入 ===")
try:
    # 添加项目路径
    project_path = os.path.dirname(os.path.abspath(__file__))
    if project_path not in sys.path:
        sys.path.insert(0, project_path)
    
    print(f"项目路径: {project_path}")
    
    # 测试导入主模块
    from src.main import app
    print("✅ 主应用导入成功")
    
    # 测试基本Flask功能
    with app.test_client() as client:
        print("✅ Flask测试客户端创建成功")
    
    print("\n=== 启动服务器 ===")
    print("启动地址: http://localhost:8083")
    print("按 Ctrl+C 停止服务器")
    
    # 启动服务器
    app.run(host='127.0.0.1', port=8083, debug=True, use_reloader=False)
    
except ImportError as e:
    print(f"❌ 项目导入失败: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"❌ 启动失败: {e}")
    import traceback
    traceback.print_exc()
