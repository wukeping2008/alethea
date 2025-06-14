#!/bin/bash

# Alethea 阿里云自动部署脚本
# 域名: alethealab.cn, www.alethealab.cn
# 作者: Alethea Team
# 版本: 1.0

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置变量
DOMAIN="alethealab.cn"
WWW_DOMAIN="www.alethealab.cn"
APP_NAME="alethea"
APP_USER="alethea"
APP_DIR="/home/${APP_USER}/${APP_NAME}"
PYTHON_VERSION="3.9"
NODE_VERSION="16"

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

# 检查是否为root用户
check_root() {
    if [[ $EUID -eq 0 ]]; then
        log_info "检测到root用户，开始部署..."
    else
        log_error "请使用root用户运行此脚本"
        exit 1
    fi
}

# 检查系统类型
check_system() {
    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        OS=$NAME
        VER=$VERSION_ID
        log_info "检测到系统: $OS $VER"
    else
        log_error "无法检测系统类型"
        exit 1
    fi
}

# 更新系统
update_system() {
    log_info "更新系统包..."
    if [[ $OS == *"Ubuntu"* ]]; then
        apt update && apt upgrade -y
        apt install -y curl wget git unzip software-properties-common
    elif [[ $OS == *"CentOS"* ]] || [[ $OS == *"Red Hat"* ]]; then
        yum update -y
        yum install -y curl wget git unzip epel-release
    fi
    log_success "系统更新完成"
}

# 安装Python
install_python() {
    log_info "安装Python ${PYTHON_VERSION}..."
    if [[ $OS == *"Ubuntu"* ]]; then
        apt install -y python3 python3-pip python3-venv python3-dev
        apt install -y build-essential libssl-dev libffi-dev
    elif [[ $OS == *"CentOS"* ]] || [[ $OS == *"Red Hat"* ]]; then
        yum install -y python3 python3-pip python3-devel
        yum groupinstall -y "Development Tools"
        yum install -y openssl-devel libffi-devel
    fi
    
    # 升级pip
    python3 -m pip install --upgrade pip
    log_success "Python安装完成"
}

# 安装Nginx
install_nginx() {
    log_info "安装Nginx..."
    if [[ $OS == *"Ubuntu"* ]]; then
        apt install -y nginx
    elif [[ $OS == *"CentOS"* ]] || [[ $OS == *"Red Hat"* ]]; then
        yum install -y nginx
    fi
    
    systemctl enable nginx
    log_success "Nginx安装完成"
}

# 安装MySQL客户端
install_mysql_client() {
    log_info "安装MySQL客户端..."
    if [[ $OS == *"Ubuntu"* ]]; then
        apt install -y mysql-client
    elif [[ $OS == *"CentOS"* ]] || [[ $OS == *"Red Hat"* ]]; then
        yum install -y mysql
    fi
    log_success "MySQL客户端安装完成"
}

# 创建应用用户
create_app_user() {
    log_info "创建应用用户 ${APP_USER}..."
    if id "$APP_USER" &>/dev/null; then
        log_warning "用户 ${APP_USER} 已存在"
    else
        useradd -m -s /bin/bash $APP_USER
        usermod -aG sudo $APP_USER
        log_success "用户 ${APP_USER} 创建完成"
    fi
}

# 部署应用代码
deploy_application() {
    log_info "部署应用代码..."
    
    # 切换到应用用户
    sudo -u $APP_USER bash << EOF
        cd /home/$APP_USER
        
        # 如果目录已存在，备份
        if [ -d "$APP_NAME" ]; then
            mv $APP_NAME ${APP_NAME}_backup_\$(date +%Y%m%d_%H%M%S)
        fi
        
        # 克隆代码（这里需要替换为实际的Git仓库地址）
        # git clone https://github.com/your-username/alethea.git
        # 由于我们在本地，直接复制代码
        mkdir -p $APP_NAME
EOF
    
    # 复制当前代码到服务器
    log_info "复制应用代码到 ${APP_DIR}..."
    cp -r /Users/kepingwu/Desktop/alethea/* ${APP_DIR}/ 2>/dev/null || {
        log_warning "无法从本地复制，请手动上传代码到 ${APP_DIR}"
        log_info "您可以使用以下命令上传代码："
        log_info "scp -r /path/to/alethea root@your-server-ip:${APP_DIR}/"
    }
    
    chown -R $APP_USER:$APP_USER $APP_DIR
    log_success "应用代码部署完成"
}

# 配置Python环境
setup_python_env() {
    log_info "配置Python虚拟环境..."
    
    sudo -u $APP_USER bash << EOF
        cd $APP_DIR
        
        # 创建虚拟环境
        python3 -m venv venv
        source venv/bin/activate
        
        # 安装依赖
        pip install --upgrade pip
        pip install -r requirements.txt
        pip install gunicorn supervisor
        
        # 创建生产环境配置
        cp .env.example .env
EOF
    
    log_success "Python环境配置完成"
}

# 配置环境变量
configure_env() {
    log_info "配置环境变量..."
    
    cat > ${APP_DIR}/.env << EOF
# 生产环境配置
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=$(openssl rand -hex 32)

# 数据库配置（请根据实际情况修改）
DATABASE_URL=sqlite:///instance/alethea.db

# AI服务配置（请填入实际的API密钥）
OPENAI_API_KEY=your_openai_api_key_here
CLAUDE_API_KEY=your_claude_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here

# 阿里云配置（请填入实际的配置）
ALIYUN_ACCESS_KEY_ID=your_access_key_id
ALIYUN_ACCESS_KEY_SECRET=your_access_key_secret
ALIYUN_OSS_BUCKET=your_oss_bucket
ALIYUN_OSS_ENDPOINT=your_oss_endpoint

# 域名配置
DOMAIN=${DOMAIN}
WWW_DOMAIN=${WWW_DOMAIN}

# 应用配置
HOST=0.0.0.0
PORT=8083
WORKERS=4
EOF
    
    chown $APP_USER:$APP_USER ${APP_DIR}/.env
    chmod 600 ${APP_DIR}/.env
    
    log_success "环境变量配置完成"
    log_warning "请编辑 ${APP_DIR}/.env 文件，填入实际的API密钥和数据库配置"
}

# 初始化数据库
init_database() {
    log_info "初始化数据库..."
    
    sudo -u $APP_USER bash << EOF
        cd $APP_DIR
        source venv/bin/activate
        
        # 创建instance目录
        mkdir -p instance
        
        # 初始化数据库
        python3 -c "
from src.main import app, db
with app.app_context():
    db.create_all()
    print('Database initialized successfully')
"
EOF
    
    log_success "数据库初始化完成"
}

# 配置Gunicorn
configure_gunicorn() {
    log_info "配置Gunicorn..."
    
    cp ${APP_DIR}/deploy/gunicorn.conf.py ${APP_DIR}/
    
    # 创建Gunicorn服务文件
    cat > /etc/systemd/system/alethea.service << EOF
[Unit]
Description=Alethea Web Application
After=network.target

[Service]
Type=notify
User=${APP_USER}
Group=${APP_USER}
RuntimeDirectory=alethea
WorkingDirectory=${APP_DIR}
Environment=PATH=${APP_DIR}/venv/bin
ExecStart=${APP_DIR}/venv/bin/gunicorn --config gunicorn.conf.py src.main:app
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=on-failure
RestartSec=5
TimeoutStopSec=20

[Install]
WantedBy=multi-user.target
EOF
    
    systemctl daemon-reload
    systemctl enable alethea
    
    log_success "Gunicorn配置完成"
}

# 配置Nginx
configure_nginx() {
    log_info "配置Nginx..."
    
    # 复制Nginx配置
    cp ${APP_DIR}/deploy/nginx.conf /etc/nginx/sites-available/alethea
    
    # 启用站点
    ln -sf /etc/nginx/sites-available/alethea /etc/nginx/sites-enabled/
    
    # 删除默认站点
    rm -f /etc/nginx/sites-enabled/default
    
    # 测试Nginx配置
    nginx -t
    
    log_success "Nginx配置完成"
}

# 申请SSL证书
setup_ssl() {
    log_info "设置SSL证书..."
    
    # 安装Certbot
    if [[ $OS == *"Ubuntu"* ]]; then
        apt install -y certbot python3-certbot-nginx
    elif [[ $OS == *"CentOS"* ]] || [[ $OS == *"Red Hat"* ]]; then
        yum install -y certbot python3-certbot-nginx
    fi
    
    # 临时启动Nginx（HTTP模式）
    systemctl start nginx
    
    # 申请SSL证书
    log_info "申请SSL证书，请按提示操作..."
    certbot --nginx -d $DOMAIN -d $WWW_DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN || {
        log_warning "SSL证书申请失败，将使用HTTP模式"
        # 使用HTTP版本的Nginx配置
        cat > /etc/nginx/sites-available/alethea << EOF
server {
    listen 80;
    server_name ${DOMAIN} ${WWW_DOMAIN};
    
    # 日志配置
    access_log /var/log/nginx/alethea_access.log;
    error_log /var/log/nginx/alethea_error.log;
    
    # 静态文件处理
    location /static/ {
        alias ${APP_DIR}/src/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # 主应用代理
    location / {
        proxy_pass http://127.0.0.1:8083;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF
    }
    
    # 设置自动续期
    echo "0 12 * * * /usr/bin/certbot renew --quiet" | crontab -
    
    log_success "SSL证书配置完成"
}

# 配置防火墙
configure_firewall() {
    log_info "配置防火墙..."
    
    if command -v ufw &> /dev/null; then
        ufw --force enable
        ufw allow ssh
        ufw allow 'Nginx Full'
        ufw allow 8083
    elif command -v firewall-cmd &> /dev/null; then
        systemctl enable firewalld
        systemctl start firewalld
        firewall-cmd --permanent --add-service=ssh
        firewall-cmd --permanent --add-service=http
        firewall-cmd --permanent --add-service=https
        firewall-cmd --permanent --add-port=8083/tcp
        firewall-cmd --reload
    fi
    
    log_success "防火墙配置完成"
}

# 启动服务
start_services() {
    log_info "启动服务..."
    
    # 启动应用
    systemctl start alethea
    systemctl status alethea --no-pager
    
    # 重启Nginx
    systemctl restart nginx
    systemctl status nginx --no-pager
    
    log_success "服务启动完成"
}

# 创建监控脚本
create_monitoring() {
    log_info "创建监控脚本..."
    
    cat > /usr/local/bin/alethea-monitor.sh << 'EOF'
#!/bin/bash

# Alethea 监控脚本
LOG_FILE="/var/log/alethea-monitor.log"

check_service() {
    local service=$1
    if systemctl is-active --quiet $service; then
        echo "$(date): $service is running" >> $LOG_FILE
        return 0
    else
        echo "$(date): $service is down, restarting..." >> $LOG_FILE
        systemctl restart $service
        return 1
    fi
}

# 检查应用服务
check_service alethea

# 检查Nginx
check_service nginx

# 检查磁盘空间
DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "$(date): Disk usage is ${DISK_USAGE}%, cleaning up..." >> $LOG_FILE
    # 清理日志文件
    find /var/log -name "*.log" -mtime +7 -delete
fi

# 检查内存使用
MEM_USAGE=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
if [ $MEM_USAGE -gt 90 ]; then
    echo "$(date): Memory usage is ${MEM_USAGE}%, restarting application..." >> $LOG_FILE
    systemctl restart alethea
fi
EOF
    
    chmod +x /usr/local/bin/alethea-monitor.sh
    
    # 添加到crontab
    echo "*/5 * * * * /usr/local/bin/alethea-monitor.sh" | crontab -
    
    log_success "监控脚本创建完成"
}

# 创建备份脚本
create_backup() {
    log_info "创建备份脚本..."
    
    mkdir -p /backup/alethea
    
    cat > /usr/local/bin/alethea-backup.sh << EOF
#!/bin/bash

BACKUP_DIR="/backup/alethea"
DATE=\$(date +%Y%m%d_%H%M%S)
APP_DIR="${APP_DIR}"

# 创建备份目录
mkdir -p \$BACKUP_DIR/\$DATE

# 备份应用代码
tar -czf \$BACKUP_DIR/\$DATE/code.tar.gz -C \$APP_DIR .

# 备份数据库
if [ -f "\$APP_DIR/instance/alethea.db" ]; then
    cp \$APP_DIR/instance/alethea.db \$BACKUP_DIR/\$DATE/
fi

# 备份配置文件
cp \$APP_DIR/.env \$BACKUP_DIR/\$DATE/
cp /etc/nginx/sites-available/alethea \$BACKUP_DIR/\$DATE/nginx.conf

# 清理7天前的备份
find \$BACKUP_DIR -type d -mtime +7 -exec rm -rf {} +

echo "\$(date): Backup completed to \$BACKUP_DIR/\$DATE"
EOF
    
    chmod +x /usr/local/bin/alethea-backup.sh
    
    # 添加到crontab（每天凌晨2点备份）
    echo "0 2 * * * /usr/local/bin/alethea-backup.sh" | crontab -
    
    log_success "备份脚本创建完成"
}

# 显示部署信息
show_deployment_info() {
    log_success "=== Alethea 部署完成 ==="
    echo
    log_info "网站地址:"
    echo "  - https://${DOMAIN}"
    echo "  - https://${WWW_DOMAIN}"
    echo
    log_info "应用目录: ${APP_DIR}"
    log_info "配置文件: ${APP_DIR}/.env"
    log_info "日志文件: /var/log/nginx/alethea_*.log"
    echo
    log_info "服务管理命令:"
    echo "  - 查看应用状态: systemctl status alethea"
    echo "  - 重启应用: systemctl restart alethea"
    echo "  - 查看应用日志: journalctl -u alethea -f"
    echo "  - 重启Nginx: systemctl restart nginx"
    echo
    log_info "监控和备份:"
    echo "  - 监控脚本: /usr/local/bin/alethea-monitor.sh"
    echo "  - 备份脚本: /usr/local/bin/alethea-backup.sh"
    echo "  - 备份目录: /backup/alethea"
    echo
    log_warning "重要提醒:"
    echo "  1. 请编辑 ${APP_DIR}/.env 文件，配置实际的API密钥"
    echo "  2. 如果使用RDS数据库，请更新DATABASE_URL"
    echo "  3. 建议配置阿里云OSS用于文件存储"
    echo "  4. 定期检查SSL证书续期状态"
    echo
}

# 主函数
main() {
    log_info "开始部署Alethea到阿里云..."
    log_info "域名: ${DOMAIN}, ${WWW_DOMAIN}"
    echo
    
    check_root
    check_system
    update_system
    install_python
    install_nginx
    install_mysql_client
    create_app_user
    deploy_application
    setup_python_env
    configure_env
    init_database
    configure_gunicorn
    configure_nginx
    setup_ssl
    configure_firewall
    start_services
    create_monitoring
    create_backup
    show_deployment_info
    
    log_success "部署完成！请访问 https://${DOMAIN} 查看网站"
}

# 错误处理
trap 'log_error "部署过程中发生错误，请检查日志"; exit 1' ERR

# 运行主函数
main "$@"
