#!/bin/bash

# Alethea项目Git Bash启动脚本

echo "🚀 使用Git Bash启动 Alethea AI教学平台"
echo "=================================================="

# 检查Python环境
echo "检查Python环境..."
if ! command -v python &> /dev/null; then
    echo "❌ Python未找到，请确保Python已安装并添加到PATH"
    read -p "按回车键退出..."
    exit 1
fi

echo "✅ Python版本: $(python --version)"

# 检查项目文件
echo "检查项目文件..."
if [ ! -f "src/main.py" ]; then
    echo "❌ 找不到src/main.py文件"
    read -p "按回车键退出..."
    exit 1
fi

if [ ! -f ".env" ]; then
    echo "❌ 找不到.env配置文件"
    read -p "按回车键退出..."
    exit 1
fi

echo "✅ 项目文件检查完成"

# 设置环境变量
export FLASK_ENV=development
export FLASK_DEBUG=True

echo "正在启动Alethea服务器..."
echo "📍 访问地址: http://localhost:8083"
echo "⏹️  按 Ctrl+C 停止服务器"
echo "=================================================="

# 启动Python应用
python start_simple.py

echo ""
echo "服务器已停止"
read -p "按回车键退出..."
