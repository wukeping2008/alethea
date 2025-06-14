#!/bin/bash

# Alethea 快速部署脚本
# 用于快速部署到阿里云服务器 alethealab.cn

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 显示欢迎信息
show_welcome() {
    echo
    echo "🚀 Alethea 阿里云快速部署工具"
    echo "=================================="
    echo "域名: alethealab.cn, www.alethealab.cn"
    echo "版本: 1.0"
    echo
}

# 检查参数
check_params() {
    if [ $# -ne 1 ]; then
        log_error "使用方法: $0 <服务器IP地址>"
        echo
        log_info "示例:"
        echo "  $0 123.456.789.123"
        echo
        log_info "部署步骤:"
        echo "  1. 上传代码到服务器"
        echo "  2. 连接服务器运行部署脚本"
        echo "  3. 配置环境变量"
        echo "  4. 访问 https://alethealab.cn"
        echo
        exit 1
    fi
}

# 主函数
main() {
    show_welcome
    check_params "$@"
    
    SERVER_IP=$1
    
    log_info "开始部署到服务器: $SERVER_IP"
    echo
    
    # 步骤1：上传代码
    log_info "步骤 1/4: 上传代码到服务器..."
    if ./deploy/upload_to_server.sh "$SERVER_IP"; then
        log_success "代码上传完成"
    else
        log_error "代码上传失败"
        exit 1
    fi
    
    echo
    log_success "=== 代码上传完成 ==="
    echo
    log_info "接下来请手动执行以下步骤："
    echo
    echo "步骤 2/4: 连接到服务器"
    echo "  ssh root@$SERVER_IP"
    echo
    echo "步骤 3/4: 运行部署脚本"
    echo "  cd /home/alethea/alethea"
    echo "  ./deploy/aliyun_auto_deploy.sh"
    echo
    echo "步骤 4/4: 配置环境变量"
    echo "  nano /home/alethea/alethea/.env"
    echo "  # 配置AI API密钥等参数"
    echo "  systemctl restart alethea"
    echo
    log_success "部署完成后访问: https://alethealab.cn"
    echo
    log_warning "重要提醒:"
    echo "- 确保域名已解析到服务器IP"
    echo "- 配置.env文件中的API密钥"
    echo "- 检查防火墙和安全组设置"
    echo
}

# 运行主函数
main "$@"
