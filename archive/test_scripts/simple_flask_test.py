#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
最简单的Flask测试脚本
"""

print("开始导入Flask...")
try:
    from flask import Flask
    print("✅ Flask导入成功")
except ImportError as e:
    print(f"❌ Flask导入失败: {e}")
    exit(1)

print("创建Flask应用...")
app = Flask(__name__)

@app.route('/')
def hello():
    return "<h1>Hello from Simple Flask Test!</h1><p>如果您看到这个页面，说明Flask服务器正在正常工作。</p>"

@app.route('/test')
def test():
    return {"status": "ok", "message": "测试成功"}

if __name__ == '__main__':
    print("启动Flask服务器...")
    print("访问地址: http://localhost:8083")
    print("按 Ctrl+C 停止服务器")
    
    try:
        app.run(host='0.0.0.0', port=8083, debug=True, use_reloader=False)
    except Exception as e:
        print(f"服务器启动失败: {e}")
        input("按回车键退出...")
