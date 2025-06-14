#!/bin/bash

# Alethea 代码上传脚本
# 用于将本地代码上传到阿里云服务器

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

# 检查参数
if [ $# -ne 1 ]; then
    log_error "使用方法: $0 <服务器IP地址>"
    log_info "示例: $0 123.456.789.123"
    exit 1
fi

SERVER_IP=$1
SERVER_USER="root"
APP_USER="alethea"
APP_DIR="/home/${APP_USER}/alethea"
LOCAL_DIR="/Users/kepingwu/Desktop/alethea"

log_info "开始上传Alethea代码到服务器..."
log_info "服务器IP: ${SERVER_IP}"
log_info "本地目录: ${LOCAL_DIR}"
log_info "远程目录: ${APP_DIR}"

# 检查本地目录是否存在
if [ ! -d "$LOCAL_DIR" ]; then
    log_error "本地目录不存在: $LOCAL_DIR"
    exit 1
fi

# 检查SSH连接
log_info "测试SSH连接..."
if ! ssh -o ConnectTimeout=10 -o BatchMode=yes $SERVER_USER@$SERVER_IP exit 2>/dev/null; then
    log_error "无法连接到服务器 $SERVER_IP"
    log_info "请确保："
    log_info "1. 服务器IP地址正确"
    log_info "2. SSH服务正在运行"
    log_info "3. 已配置SSH密钥认证或密码认证"
    exit 1
fi

log_success "SSH连接测试成功"

# 创建远程目录
log_info "创建远程目录..."
ssh $SERVER_USER@$SERVER_IP "
    # 创建应用用户（如果不存在）
    if ! id '$APP_USER' &>/dev/null; then
        useradd -m -s /bin/bash $APP_USER
        usermod -aG sudo $APP_USER
        echo '用户 $APP_USER 创建完成'
    fi
    
    # 创建应用目录
    mkdir -p $APP_DIR
    chown -R $APP_USER:$APP_USER /home/$APP_USER
"

# 排除不需要上传的文件和目录
EXCLUDE_LIST="
--exclude='.git'
--exclude='__pycache__'
--exclude='*.pyc'
--exclude='*.pyo'
--exclude='.DS_Store'
--exclude='node_modules'
--exclude='venv'
--exclude='env'
--exclude='.env'
--exclude='instance'
--exclude='logs'
--exclude='*.log'
--exclude='.pytest_cache'
--exclude='coverage'
--exclude='.coverage'
--exclude='dist'
--exclude='build'
--exclude='*.egg-info'
"

# 上传代码
log_info "上传代码文件..."
rsync -avz --progress $EXCLUDE_LIST \
    "$LOCAL_DIR/" \
    "$SERVER_USER@$SERVER_IP:$APP_DIR/"

if [ $? -eq 0 ]; then
    log_success "代码上传完成"
else
    log_error "代码上传失败"
    exit 1
fi

# 设置文件权限
log_info "设置文件权限..."
ssh $SERVER_USER@$SERVER_IP "
    chown -R $APP_USER:$APP_USER $APP_DIR
    chmod +x $APP_DIR/deploy/*.sh
    chmod 600 $APP_DIR/.env.example
"

# 显示后续步骤
log_success "=== 代码上传完成 ==="
echo
log_info "后续步骤："
echo "1. 连接到服务器:"
echo "   ssh $SERVER_USER@$SERVER_IP"
echo
echo "2. 运行自动部署脚本:"
echo "   cd $APP_DIR"
echo "   chmod +x deploy/aliyun_auto_deploy.sh"
echo "   ./deploy/aliyun_auto_deploy.sh"
echo
echo "3. 或者手动部署:"
echo "   cd $APP_DIR"
echo "   python3 -m venv venv"
echo "   source venv/bin/activate"
echo "   pip install -r requirements.txt"
echo "   cp .env.example .env"
echo "   # 编辑 .env 文件配置"
echo "   python3 src/main.py"
echo
log_warning "重要提醒："
echo "- 请确保域名 alethealab.cn 和 www.alethealab.cn 已解析到服务器IP"
echo "- 运行部署脚本前请备份重要数据"
echo "- 部署完成后请配置 .env 文件中的API密钥"
