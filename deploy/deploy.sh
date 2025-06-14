#!/bin/bash

# Alethea 阿里云部署脚本
# 使用方法: chmod +x deploy.sh && ./deploy.sh

set -e  # 遇到错误立即退出

echo "=== Alethea 阿里云部署脚本 ==="
echo "开始部署 Alethea 到阿里云服务器..."

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查是否为root用户
check_root() {
    if [[ $EUID -eq 0 ]]; then
        log_error "请不要使用root用户运行此脚本"
        exit 1
    fi
}

# 创建必要的目录
create_directories() {
    log_info "创建必要的目录..."
    
    sudo mkdir -p /var/log/alethea
    sudo mkdir -p /var/run/alethea
    sudo mkdir -p /home/alethea/alethea/uploads
    
    sudo chown -R alethea:alethea /var/log/alethea
    sudo chown -R alethea:alethea /var/run/alethea
    sudo chown -R alethea:alethea /home/alethea/alethea/uploads
    
    log_info "目录创建完成"
}

# 安装系统依赖
install_system_dependencies() {
    log_info "更新系统包..."
    sudo apt update && sudo apt upgrade -y
    
    log_info "安装系统依赖..."
    sudo apt install -y \
        python3 \
        python3-pip \
        python3-venv \
        python3-dev \
        nginx \
        supervisor \
        git \
        mysql-client \
        build-essential \
        libssl-dev \
        libffi-dev \
        redis-tools \
        htop \
        curl \
        wget \
        unzip
    
    log_info "系统依赖安装完成"
}

# 设置Python虚拟环境
setup_python_env() {
    log_info "设置Python虚拟环境..."
    
    cd /home/alethea/alethea
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        log_info "虚拟环境创建完成"
    fi
    
    source venv/bin/activate
    
    log_info "升级pip..."
    pip install --upgrade pip
    
    log_info "安装Python依赖..."
    pip install -r requirements.txt
    pip install gunicorn
    
    log_info "Python环境设置完成"
}

# 配置环境变量
setup_environment() {
    log_info "配置环境变量..."
    
    if [ ! -f ".env" ]; then
        if [ -f "deploy/.env.production" ]; then
            cp deploy/.env.production .env
            log_info "生产环境配置文件已复制"
            log_warn "请编辑 .env 文件，填入正确的配置信息"
        else
            cp .env.example .env
            log_warn "请编辑 .env 文件，填入正确的配置信息"
        fi
    else
        log_info "环境配置文件已存在"
    fi
}

# 配置Nginx
setup_nginx() {
    log_info "配置Nginx..."
    
    # 复制配置文件
    sudo cp deploy/nginx.conf /etc/nginx/sites-available/alethea
    
    # 创建软链接
    sudo ln -sf /etc/nginx/sites-available/alethea /etc/nginx/sites-enabled/
    
    # 删除默认配置
    sudo rm -f /etc/nginx/sites-enabled/default
    
    # 测试配置
    sudo nginx -t
    
    # 重启Nginx
    sudo systemctl restart nginx
    sudo systemctl enable nginx
    
    log_info "Nginx配置完成"
}

# 配置Supervisor
setup_supervisor() {
    log_info "配置Supervisor..."
    
    # 复制配置文件
    sudo cp deploy/supervisor.conf /etc/supervisor/conf.d/alethea.conf
    
    # 重新加载配置
    sudo supervisorctl reread
    sudo supervisorctl update
    
    # 启动应用
    sudo supervisorctl start alethea
    
    log_info "Supervisor配置完成"
}

# 初始化数据库
init_database() {
    log_info "初始化数据库..."
    
    source venv/bin/activate
    
    python3 -c "
from src.main import app, db
with app.app_context():
    db.create_all()
    print('数据库初始化成功')
"
    
    log_info "数据库初始化完成"
}

# 设置防火墙
setup_firewall() {
    log_info "配置防火墙..."
    
    sudo ufw --force enable
    sudo ufw allow ssh
    sudo ufw allow 'Nginx Full'
    sudo ufw allow 8083
    
    log_info "防火墙配置完成"
}

# 设置日志轮转
setup_logrotate() {
    log_info "配置日志轮转..."
    
    sudo tee /etc/logrotate.d/alethea > /dev/null <<EOF
/var/log/alethea/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 alethea alethea
    postrotate
        supervisorctl restart alethea
    endscript
}
EOF
    
    log_info "日志轮转配置完成"
}

# 创建启动脚本
create_startup_script() {
    log_info "创建启动脚本..."
    
    cat > /home/alethea/start_alethea.sh << 'EOF'
#!/bin/bash
cd /home/alethea/alethea
source venv/bin/activate
supervisorctl start alethea
echo "Alethea 已启动"
EOF
    
    chmod +x /home/alethea/start_alethea.sh
    
    log_info "启动脚本创建完成"
}

# 检查服务状态
check_services() {
    log_info "检查服务状态..."
    
    echo "=== Nginx 状态 ==="
    sudo systemctl status nginx --no-pager -l
    
    echo "=== Supervisor 状态 ==="
    sudo supervisorctl status
    
    echo "=== 应用进程 ==="
    ps aux | grep gunicorn | grep -v grep || echo "未找到gunicorn进程"
    
    echo "=== 端口监听 ==="
    sudo netstat -tlnp | grep -E ':(80|443|8083)'
}

# 主函数
main() {
    log_info "开始部署流程..."
    
    check_root
    create_directories
    install_system_dependencies
    setup_python_env
    setup_environment
    init_database
    setup_nginx
    setup_supervisor
    setup_firewall
    setup_logrotate
    create_startup_script
    
    log_info "部署完成！"
    log_info "请检查以下内容："
    log_info "1. 编辑 .env 文件，填入正确的配置"
    log_info "2. 配置域名DNS解析"
    log_info "3. 申请SSL证书"
    log_info "4. 测试应用访问"
    
    check_services
    
    echo ""
    log_info "部署完成！访问 http://your-domain.com 查看应用"
}

# 运行主函数
main "$@"
