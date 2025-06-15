#!/usr/bin/env python3
"""
启动脚本 - 使用端口8084启动Alethea项目
"""

import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# 导入主应用
from src.main import app, initialize_app

if __name__ == '__main__':
    # 初始化应用
    initialize_app()
    
    print("正在启动Alethea优化版平台...")
    print("功能特性:")
    print("- AI智能问答")
    print("- 用户管理与认证")
    print("- 数字画像生成")
    print("- 学习分析")
    print("- 个性化项目推荐")
    print("- 知识图谱追踪")
    print("\n访问地址: http://localhost:8084")
    
    # 启动服务器
    app.run(host='0.0.0.0', port=8084, debug=True)
