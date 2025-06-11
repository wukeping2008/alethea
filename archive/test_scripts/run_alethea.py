#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Alethea 项目启动脚本
"""

import os
import sys
import subprocess
import time

def check_python():
    """检查Python环境"""
    print("检查Python环境...")
    print(f"Python版本: {sys.version}")
    return True

def check_dependencies():
    """检查依赖包"""
    print("检查依赖包...")
    try:
        import flask
        import flask_sqlalchemy
        import requests
        print("✅ 主要依赖包已安装")
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖包: {e}")
        return False

def start_server():
    """启动服务器"""
    print("正在启动Alethea服务器...")
    print("=" * 50)
    
    try:
        # 设置环境变量
        os.environ['FLASK_ENV'] = 'development'
        os.environ['FLASK_DEBUG'] = 'True'
        
        # 导入并启动应用
        from src.main import app, initialize_app
        
        print("初始化应用...")
        initialize_app()
        
        print("启动Flask服务器...")
        print("访问地址: http://localhost:8083")
        print("按 Ctrl+C 停止服务器")
        print("=" * 50)
        
        # 启动服务器
        app.run(
            host='0.0.0.0',
            port=8083,
            debug=True,
            use_reloader=False
        )
        
    except Exception as e:
        print(f"启动失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def main():
    """主函数"""
    print("🚀 Alethea AI教学平台启动器")
    print("=" * 50)
    
    # 检查环境
    if not check_python():
        input("按回车键退出...")
        return
    
    if not check_dependencies():
        print("请运行: pip install -r requirements.txt")
        input("按回车键退出...")
        return
    
    # 启动服务器
    start_server()

if __name__ == '__main__':
    main()
