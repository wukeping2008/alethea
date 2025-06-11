#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
最小化Alethea启动脚本 - 用于测试基本功能
"""

import os
import sys
from flask import Flask, render_template, send_from_directory, jsonify
import datetime

# 配置日志文件
log_file_path = os.path.join(os.path.dirname(__file__), "minimal_start.log")
sys.stdout = open(log_file_path, "w", encoding="utf-8")
sys.stderr = sys.stdout

def log_message(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")
    sys.stdout.flush() # 确保立即写入

log_message("🚀 启动最小化Alethea测试服务器")
log_message("=" * 50)

# 设置环境变量
os.environ['FLASK_ENV'] = 'development'
os.environ['FLASK_DEBUG'] = 'True'

# 创建Flask应用
app = Flask(__name__, static_folder='src/static', template_folder='src/static')
app.config['SECRET_KEY'] = 'alethea-test-key-2024'

log_message("✅ Flask应用创建成功")

@app.route('/')
def index():
    """主页"""
    try:
        return send_from_directory('src/static', 'index.html')
    except Exception as e:
        return f"""
        <html>
        <head><title>Alethea AI教学平台</title></head>
        <body>
            <h1>🚀 Alethea AI教学平台</h1>
            <h2>✅ 服务器运行正常</h2>
            <p>这是最小化测试版本</p>
            <p>时间: {__import__('datetime').datetime.now()}</p>
            <p>错误信息: {str(e)}</p>
            <p>日志文件: minimal_start.log</p>
            <hr>
            <h3>测试API:</h3>
            <ul>
                <li><a href="/api/health">健康检查</a></li>
                <li><a href="/api/test">测试接口</a></li>
            </ul>
        </body>
        </html>
        """

@app.route('/api/health')
def health():
    """健康检查"""
    return jsonify({
        'status': 'ok',
        'message': 'Alethea最小化服务器运行正常',
        'version': 'minimal-test',
        'timestamp': __import__('datetime').datetime.now().isoformat()
    })

@app.route('/api/test')
def test():
    """测试接口"""
    return jsonify({
        'message': '测试成功',
        'python_version': sys.version,
        'flask_version': __import__('flask').__version__,
        'working_directory': os.getcwd(),
        'environment': dict(os.environ)
    })

@app.route('/<path:filename>')
def static_files(filename):
    """静态文件服务"""
    try:
        return send_from_directory('src/static', filename)
    except Exception as e:
        return jsonify({'error': f'文件未找到: {filename}', 'details': str(e)}), 404

if __name__ == '__main__':
    log_message("✅ 路由注册完成")
    log_message("🌐 启动服务器...")
    log_message("📍 访问地址: http://localhost:8083")
    log_message("⏹️  按 Ctrl+C 停止服务器")
    log_message("=" * 50)
    
    try:
        app.run(
            host='0.0.0.0',
            port=8083,
            debug=True,
            use_reloader=False
        )
    except Exception as e:
        log_message(f"❌ 服务器启动失败: {e}")
        import traceback
        traceback.print_exc(file=sys.stdout) # 确保traceback也写入日志
        log_message("按回车键退出...") # 模拟input
        # input("按回车键退出...") # 在重定向输出时，input会引发问题
    finally:
        log_message("脚本执行结束。")
        if sys.stdout != sys.__stdout__: # 如果stdout被重定向
            sys.stdout.close()
            sys.stdout = sys.__stdout__ # 恢复原始stdout
        if sys.stderr != sys.__stderr__:
            sys.stderr.close()
            sys.stderr = sys.__stderr__
