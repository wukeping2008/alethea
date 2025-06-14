#!/bin/bash

# Alethea 一键部署到阿里云脚本 (带密码版本)
# 服务器IP: 8.155.57.140
# 实例ID: i-f8zdzpazpk567qbg8caj
# SSH密码: W0526w16616w!
# 安全组: sg-f8z9cbfzw15nm8ku66va

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
SERVER_PASSWORD="W0526w16616w!"
APP_USER="alethea"
APP_DIR="/home/${APP_USER}/alethea"
LOCAL_DIR="/Users/kepingwu/Desktop/alethea"
SECURITY_GROUP="sg-f8z9cbfzw15nm8ku66va"

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
    echo "🚀 Alethea 一键部署到阿里云 (带密码版本)"
    echo "=============================================="
    echo "服务器IP: ${SERVER_IP}"
    echo "安全组: ${SECURITY_GROUP}"
    echo "目标域名: alethealab.cn"
    echo "部署目录: ${APP_DIR}"
    echo
}

# SSH连接函数
ssh_exec() {
    local command="$1"
    if command -v sshpass >/dev/null 2>&1; then
        sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no -o ConnectTimeout=30 "$SERVER_USER@$SERVER_IP" "$command"
    else
        log_warning "sshpass未安装，请手动输入密码: $SERVER_PASSWORD"
        ssh -o StrictHostKeyChecking=no -o ConnectTimeout=30 "$SERVER_USER@$SERVER_IP" "$command"
    fi
}

# SCP上传函数
scp_upload() {
    local local_path="$1"
    local remote_path="$2"
    if command -v sshpass >/dev/null 2>&1; then
        sshpass -p "$SERVER_PASSWORD" scp -o StrictHostKeyChecking=no -r "$local_path" "$SERVER_USER@$SERVER_IP:$remote_path"
    else
        log_warning "sshpass未安装，请手动输入密码: $SERVER_PASSWORD"
        scp -o StrictHostKeyChecking=no -r "$local_path" "$SERVER_USER@$SERVER_IP:$remote_path"
    fi
}

# 检查SSH连接
check_ssh_connection() {
    log_info "测试SSH连接到 ${SERVER_IP}..."
    log_info "使用密码: ${SERVER_PASSWORD}"
    
    if ssh_exec "echo 'SSH连接测试成功'" >/dev/null 2>&1; then
        log_success "SSH连接测试成功"
        return 0
    else
        log_error "SSH连接失败"
        echo
        log_warning "可能的原因："
        echo "1. 安全组 ${SECURITY_GROUP} 未开放22端口"
        echo "2. SSH服务未启动"
        echo "3. 密码不正确"
        echo "4. 服务器防火墙阻止连接"
        echo
        log_info "请检查阿里云控制台的安全组配置："
        echo "https://ecs.console.aliyun.com"
        echo
        log_info "如果问题持续，请使用阿里云控制台的远程连接功能"
        return 1
    fi
}

# 安装sshpass (如果需要)
install_sshpass() {
    if ! command -v sshpass >/dev/null 2>&1; then
        log_info "安装sshpass工具..."
        if [[ "$OSTYPE" == "darwin"* ]]; then
            if command -v brew >/dev/null 2>&1; then
                brew install hudochenkov/sshpass/sshpass
            else
                log_warning "请安装Homebrew或手动安装sshpass"
                log_info "或者在SSH连接时手动输入密码: $SERVER_PASSWORD"
            fi
        elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
            sudo apt-get update && sudo apt-get install -y sshpass
        fi
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
    log_info "创建远程目录和用户..."
    ssh_exec "
        if ! id '$APP_USER' &>/dev/null; then
            useradd -m -s /bin/bash $APP_USER
            usermod -aG sudo $APP_USER
            echo '用户 $APP_USER 创建完成'
        fi
        mkdir -p $APP_DIR
        chown -R $APP_USER:$APP_USER /home/$APP_USER
    "
    
    # 创建临时压缩包
    log_info "压缩代码文件..."
    cd "$LOCAL_DIR"
    tar --exclude='.git' \
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
        -czf /tmp/alethea_deploy.tar.gz .
    
    # 上传压缩包
    log_info "上传代码压缩包..."
    scp_upload "/tmp/alethea_deploy.tar.gz" "/tmp/"
    
    # 解压代码
    log_info "在服务器上解压代码..."
    ssh_exec "
        cd $APP_DIR
        tar -xzf /tmp/alethea_deploy.tar.gz
        chown -R $APP_USER:$APP_USER $APP_DIR
        chmod +x $APP_DIR/deploy/*.sh
        rm -f /tmp/alethea_deploy.tar.gz
    "
    
    # 清理本地临时文件
    rm -f /tmp/alethea_deploy.tar.gz
    
    log_success "代码上传完成"
}

# 运行部署脚本
run_deployment() {
    log_info "在服务器上运行自动部署脚本..."
    
    ssh_exec "
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
    
    ssh_exec "
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
    
    ssh_exec "
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
    
    ssh_exec "
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
    log_info "SSH连接密码: ${SERVER_PASSWORD}"
    echo
}

# 主函数
main() {
    show_welcome
    install_sshpass
    
    if check_ssh_connection; then
        upload_code
        run_deployment
        configure_environment
        start_services
        verify_deployment
        show_deployment_result
    else
        log_error "SSH连接失败，无法继续部署"
        echo
        log_info "请检查以下项目："
        echo "1. 阿里云安全组 ${SECURITY_GROUP} 是否开放22端口"
        echo "2. 服务器是否正在运行"
        echo "3. SSH服务是否启动"
        echo
        log_info "您可以使用阿里云控制台的远程连接功能："
        echo "https://ecs.console.aliyun.com"
        exit 1
    fi
}

# 错误处理
trap 'log_error "部署过程中发生错误，请检查上面的错误信息"; exit 1' ERR

# 运行主函数
main "$@"
