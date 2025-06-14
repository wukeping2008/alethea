#!/bin/bash

# Alethea 一键部署到阿里云脚本
# 服务器IP: 8.155.57.140
# 实例ID: i-f8zdzpazpk567qbg8caj

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 配置变量
SERVER_IP="8.155.57.140"
SERVER_USER="root"
APP_USER="alethea"
APP_DIR="/home/${APP_USER}/alethea"
LOCAL_DIR="/Users/kepingwu/Desktop/alethea"

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
    echo "🚀 Alethea 一键部署到阿里云"
    echo "================================"
    echo "服务器IP: ${SERVER_IP}"
    echo "目标域名: alethealab.cn"
    echo "部署目录: ${APP_DIR}"
    echo
}

# 检查SSH连接
check_ssh_connection() {
    log_info "测试SSH连接到 ${SERVER_IP}..."
    
    if ssh -o ConnectTimeout=10 -o BatchMode=yes $SERVER_USER@$SERVER_IP exit 2>/dev/null; then
        log_success "SSH连接测试成功"
        return 0
    else
        log_error "SSH连接失败"
        echo
        log_warning "请先完成以下步骤："
        echo "1. 登录阿里云ECS控制台：https://ecs.console.aliyun.com"
        echo "2. 找到实例 i-f8zdzpazpk567qbg8caj"
        echo "3. 重置root密码或配置SSH密钥"
        echo "4. 确保安全组开放了22端口"
        echo "5. 测试连接：ssh root@${SERVER_IP}"
        echo
        log_info "配置完成后，重新运行此脚本"
        exit 1
    fi
}

# 上传代码
upload_code() {
    log_info "上传代码到服务器..."
    
    # 检查本地目录
    if [ ! -d "$LOCAL_DIR" ]; then
        log_error "本地目录不存在: $LOCAL_DIR"
        exit 1
    fi
    
    # 创建远程目录
    ssh $SERVER_USER@$SERVER_IP "
        if ! id '$APP_USER' &>/dev/null; then
            useradd -m -s /bin/bash $APP_USER
            usermod -aG sudo $APP_USER
            echo '用户 $APP_USER 创建完成'
        fi
        mkdir -p $APP_DIR
        chown -R $APP_USER:$APP_USER /home/$APP_USER
    "
    
    # 上传代码
    rsync -avz --progress \
        --exclude='.git' \
        --exclude='__pycache__' \
        --exclude='*.pyc' \
        --exclude='.DS_Store' \
        --exclude='node_modules' \
        --exclude='venv' \
        --exclude='env' \
        --exclude='.env' \
        --exclude='instance' \
        --exclude='logs' \
        --exclude='*.log' \
        "$LOCAL_DIR/" \
        "$SERVER_USER@$SERVER_IP:$APP_DIR/"
    
    # 设置权限
    ssh $SERVER_USER@$SERVER_IP "
        chown -R $APP_USER:$APP_USER $APP_DIR
        chmod +x $APP_DIR/deploy/*.sh
    "
    
    log_success "代码上传完成"
}

# 运行部署脚本
run_deployment() {
    log_info "在服务器上运行自动部署脚本..."
    
    ssh $SERVER_USER@$SERVER_IP "
        cd $APP_DIR
        chmod +x deploy/aliyun_auto_deploy.sh
        ./deploy/aliyun_auto_deploy.sh
    "
    
    log_success "自动部署完成"
}

# 配置环境变量
configure_environment() {
    log_info "配置生产环境变量..."
    
    # 生成随机密钥
    SECRET_KEY=$(openssl rand -hex 32)
    
    ssh $SERVER_USER@$SERVER_IP "
        cd $APP_DIR
        cat > .env << 'EOF'
# 生产环境配置
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=$SECRET_KEY

# 数据库配置
DATABASE_URL=sqlite:///instance/alethea.db

# AI服务配置（请填入您的实际API密钥）
OPENAI_API_KEY=sk-your-openai-api-key-here
CLAUDE_API_KEY=your-claude-api-key-here
GEMINI_API_KEY=your-gemini-api-key-here
DEEPSEEK_API_KEY=your-deepseek-api-key-here
QIANWEN_API_KEY=your-qianwen-api-key-here

# 阿里云配置（可选）
ALIYUN_ACCESS_KEY_ID=your_access_key_id
ALIYUN_ACCESS_KEY_SECRET=your_access_key_secret

# 域名配置
DOMAIN=alethealab.cn
WWW_DOMAIN=www.alethealab.cn

# 应用配置
HOST=0.0.0.0
PORT=8083
WORKERS=4
EOF
        chown $APP_USER:$APP_USER .env
        chmod 600 .env
    "
    
    log_success "环境变量配置完成"
    log_warning "请稍后编辑 /home/alethea/alethea/.env 文件，填入实际的API密钥"
}

# 启动服务
start_services() {
    log_info "启动应用服务..."
    
    ssh $SERVER_USER@$SERVER_IP "
        systemctl daemon-reload
        systemctl enable alethea
        systemctl start alethea
        systemctl enable nginx
        systemctl restart nginx
        
        # 等待服务启动
        sleep 5
        
        # 检查服务状态
        echo '=== 应用服务状态 ==='
        systemctl status alethea --no-pager -l
        echo
        echo '=== Nginx服务状态 ==='
        systemctl status nginx --no-pager -l
    "
    
    log_success "服务启动完成"
}

# 验证部署
verify_deployment() {
    log_info "验证部署结果..."
    
    ssh $SERVER_USER@$SERVER_IP "
        echo '=== 端口监听状态 ==='
        netstat -tulpn | grep -E ':(80|443|8083) '
        echo
        echo '=== 测试本地访问 ==='
        curl -s -o /dev/null -w 'HTTP状态码: %{http_code}\n' http://localhost:8083/ || echo '应用端口测试失败'
        curl -s -o /dev/null -w 'HTTP状态码: %{http_code}\n' http://localhost/ || echo 'Nginx测试失败'
        echo
        echo '=== 防火墙状态 ==='
        ufw status || echo '防火墙未启用'
    "
    
    log_success "部署验证完成"
}

# 显示部署结果
show_deployment_result() {
    echo
    log_success "🎉 Alethea 部署完成！"
    echo "================================"
    echo
    log_info "网站访问地址："
    echo "  - http://${SERVER_IP}"
    echo "  - http://alethealab.cn (域名解析生效后)"
    echo "  - http://www.alethealab.cn"
    echo
    log_info "管理命令："
    echo "  - 查看应用状态: ssh root@${SERVER_IP} 'systemctl status alethea'"
    echo "  - 重启应用: ssh root@${SERVER_IP} 'systemctl restart alethea'"
    echo "  - 查看日志: ssh root@${SERVER_IP} 'journalctl -u alethea -f'"
    echo "  - 编辑配置: ssh root@${SERVER_IP} 'nano /home/alethea/alethea/.env'"
    echo
    log_warning "重要提醒："
    echo "1. 请配置域名解析：alethealab.cn → ${SERVER_IP}"
    echo "2. 请编辑 .env 文件，填入实际的AI服务API密钥"
    echo "3. 建议申请SSL证书以启用HTTPS访问"
    echo
    log_info "配置API密钥："
    echo "ssh root@${SERVER_IP}"
    echo "nano /home/alethea/alethea/.env"
    echo "systemctl restart alethea nginx"
    echo
}

# 主函数
main() {
    show_welcome
    check_ssh_connection
    upload_code
    run_deployment
    configure_environment
    start_services
    verify_deployment
    show_deployment_result
}

# 错误处理
trap 'log_error "部署过程中发生错误，请检查上面的错误信息"; exit 1' ERR

# 运行主函数
main "$@"
