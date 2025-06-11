#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
简单启动脚本 - 直接在终端显示输出
"""

import os
import sys

print("🚀 启动 Alethea AI教学平台")
print("=" * 50)

# 设置环境变量
os.environ['FLASK_ENV'] = 'development'
os.environ['FLASK_DEBUG'] = 'True'

try:
    print("正在导入Flask应用...")
    from src.main import app, initialize_app
    
    print("正在初始化应用...")
    initialize_app()
    
    print("✅ 应用初始化成功!")
    print("🌐 启动服务器...")
    print("📍 访问地址: http://localhost:8083")
    print("⏹️  按 Ctrl+C 停止服务器")
    print("=" * 50)
    
    # 启动服务器
    app.run(
        host='0.0.0.0',
        port=8083,
        debug=True,
        use_reloader=False,
        threaded=True
    )
    
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    print("请确保已安装所有依赖: pip install -r requirements.txt")
except Exception as e:
    print(f"❌ 启动失败: {e}")
    import traceback
    traceback.print_exc()

print("\n服务器已停止")
