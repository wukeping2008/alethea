#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
详细的启动诊断脚本
"""

import sys
import os
import traceback

print("=" * 60)
print("🔍 Alethea 项目启动诊断")
print("=" * 60)

# 1. 检查Python环境
print("\n1. Python环境检查:")
print(f"   Python版本: {sys.version}")
print(f"   Python路径: {sys.executable}")
print(f"   当前工作目录: {os.getcwd()}")

# 2. 检查项目文件
print("\n2. 项目文件检查:")
required_files = [
    'src/main.py',
    'src/__init__.py',
    '.env',
    'requirements.txt'
]

for file_path in required_files:
    if os.path.exists(file_path):
        print(f"   ✅ {file_path}")
    else:
        print(f"   ❌ {file_path} - 文件不存在")

# 3. 检查依赖包
print("\n3. 依赖包检查:")
required_packages = [
    'flask',
    'flask_sqlalchemy',
    'requests'
]

for package in required_packages:
    try:
        __import__(package)
        print(f"   ✅ {package}")
    except ImportError as e:
        print(f"   ❌ {package} - {e}")

# 4. 检查环境变量
print("\n4. 环境变量检查:")
env_vars = [
    'FLASK_ENV',
    'FLASK_DEBUG',
    'SECRET_KEY'
]

for var in env_vars:
    value = os.getenv(var)
    if value:
        print(f"   ✅ {var} = {value}")
    else:
        print(f"   ⚠️  {var} - 未设置")

# 5. 尝试导入主模块
print("\n5. 主模块导入测试:")
try:
    # 添加项目路径
    project_path = os.path.dirname(os.path.abspath(__file__))
    if project_path not in sys.path:
        sys.path.insert(0, project_path)
    
    print(f"   项目路径: {project_path}")
    
    # 尝试导入
    from src.main import app
    print("   ✅ 主应用导入成功")
    
    # 测试Flask应用
    with app.test_client() as client:
        print("   ✅ Flask测试客户端创建成功")
    
    print("\n6. 尝试启动服务器:")
    print("   正在启动Flask服务器...")
    print("   访问地址: http://localhost:8083")
    print("   按 Ctrl+C 停止服务器")
    print("=" * 60)
    
    # 启动服务器
    app.run(host='0.0.0.0', port=8083, debug=True, use_reloader=False)
    
except Exception as e:
    print(f"   ❌ 导入失败: {e}")
    print("\n详细错误信息:")
    traceback.print_exc()
    
    print("\n🔧 可能的解决方案:")
    print("1. 检查是否安装了所有依赖: python -m pip install -r requirements.txt")
    print("2. 检查Python路径是否正确")
    print("3. 检查项目文件是否完整")
    print("4. 检查环境变量配置")
    
    input("\n按回车键退出...")
