#!/bin/bash

# Alethea 快速部署脚本
# 适用于已经配置好基础环境的阿里云服务器

echo "=== Alethea 快速部署脚本 ==="
echo "此脚本将帮助您快速部署 Alethea 到阿里云"
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 检查是否为root用户
if [[ $EUID -eq 0 ]]; then
   echo -e "${RED}错误: 请不要使用root用户运行此脚本${NC}"
   echo "请先创建普通用户: useradd -m -s /bin/bash alethea"
   exit 1
fi

# 获取用户输入
echo -e "${YELLOW}请提供以下信息:${NC}"
read -p "域名 (例如: example.com): " DOMAIN
read -p "数据库主机 (RDS地址): " DB_HOST
read -p "数据库用户名: " DB_USER
read -s -p "数据库密码: " DB_PASS
echo ""
read -p "OpenAI API Key (可选): " OPENAI_KEY
read -p "DeepSeek API Key (可选): " DEEPSEEK_KEY

echo ""
echo -e "${GREEN}开始部署...${NC}"

# 1. 更新系统
echo "1. 更新系统包..."
sudo apt update -y

# 2. 安装必要软件
echo "2. 安装必要软件..."
sudo apt install -y python3 python3-pip python3-venv nginx supervisor git mysql-client

# 3. 创建目录
echo "3. 创建必要目录..."
sudo mkdir -p /var/log/alethea /var/run/alethea
sudo chown -R $USER:$USER /var/log/alethea /var/run/alethea

# 4. 设置Python环境
echo "4. 设置Python环境..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt gunicorn

# 5. 配置环境变量
echo "5. 配置环境变量..."
cat > .env << EOF
# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=$(openssl rand -hex 32)

# Database Configuration
DATABASE_URL=mysql+pymysql://${DB_USER}:${DB_PASS}@${DB_HOST}:3306/alethea

# AI Model API Keys
OPENAI_API_KEY=${OPENAI_KEY}
DEEPSEEK_API_KEY=${DEEPSEEK_KEY}

# JWT Configuration
JWT_SECRET_KEY=$(openssl rand -hex 32)
JWT_ACCESS_TOKEN_EXPIRES=3600

# File Upload Configuration
MAX_CONTENT_LENGTH=16777216
UPLOAD_FOLDER=$(pwd)/uploads

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=/var/log/alethea/alethea.log

# Security Configuration
BCRYPT_LOG_ROUNDS=12
WTF_CSRF_ENABLED=True

# Production Settings
TESTING=False
DEBUG_TB_ENABLED=False
SERVER_NAME=${DOMAIN}
PREFERRED_URL_SCHEME=https
EOF

# 6. 初始化数据库
echo "6. 初始化数据库..."
python3 -c "
from src.main import app, db
with app.app_context():
    db.create_all()
    print('数据库初始化成功')
" || echo "数据库初始化失败，请检查连接配置"

# 7. 配置Nginx
echo "7. 配置Nginx..."
sudo cp deploy/nginx.conf /etc/nginx/sites-available/alethea

# 更新域名
sudo sed -i "s/your-domain.com/${DOMAIN}/g" /etc/nginx/sites-available/alethea

# 临时禁用SSL配置（稍后手动配置）
sudo sed -i 's/listen 443 ssl http2;/listen 443;/' /etc/nginx/sites-available/alethea
sudo sed -i 's/ssl_certificate/#ssl_certificate/' /etc/nginx/sites-available/alethea
sudo sed -i 's/ssl_/#ssl_/' /etc/nginx/sites-available/alethea

sudo ln -sf /etc/nginx/sites-available/alethea /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# 8. 配置Supervisor
echo "8. 配置Supervisor..."
sudo cp deploy/supervisor.conf /etc/supervisor/conf.d/alethea.conf

# 更新路径
sudo sed -i "s|/home/alethea/alethea|$(pwd)|g" /etc/supervisor/conf.d/alethea.conf
sudo sed -i "s/user=alethea/user=$USER/" /etc/supervisor/conf.d/alethea.conf
sudo sed -i "s/group=alethea/group=$USER/" /etc/supervisor/conf.d/alethea.conf

# 9. 启动服务
echo "9. 启动服务..."
sudo nginx -t && sudo systemctl restart nginx
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start alethea

# 10. 设置防火墙
echo "10. 配置防火墙..."
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw --force enable

echo ""
echo -e "${GREEN}=== 部署完成! ===${NC}"
echo ""
echo "接下来的步骤:"
echo "1. 配置域名DNS解析指向服务器IP"
echo "2. 申请并安装SSL证书"
echo "3. 测试网站访问: http://${DOMAIN}"
echo ""
echo "服务管理命令:"
echo "  重启应用: sudo supervisorctl restart alethea"
echo "  查看状态: sudo supervisorctl status"
echo "  查看日志: tail -f /var/log/alethea/supervisor.log"
echo ""
echo "SSL证书配置 (使用Let's Encrypt):"
echo "  sudo apt install certbot python3-certbot-nginx"
echo "  sudo certbot --nginx -d ${DOMAIN}"
echo ""

# 检查服务状态
echo "当前服务状态:"
echo "Nginx: $(sudo systemctl is-active nginx)"
echo "Supervisor: $(sudo supervisorctl status alethea | awk '{print $2}')"
echo ""

# 显示访问信息
SERVER_IP=$(curl -s ifconfig.me)
echo "服务器IP: ${SERVER_IP}"
echo "临时访问地址: http://${SERVER_IP}"
echo "域名访问地址: http://${DOMAIN} (需要DNS解析)"
