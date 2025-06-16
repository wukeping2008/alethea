#!/bin/bash

# Alethea优化版本 v2.0 部署脚本
# 使用方法: ./deploy.sh [环境类型]
# 环境类型: dev (开发环境) | prod (生产环境)

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_message() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE} Alethea优化版本 v2.0 部署脚本${NC}"
    echo -e "${BLUE}================================${NC}"
}

# 检查Python版本
check_python() {
    print_message "检查Python版本..."
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        print_message "Python版本: $PYTHON_VERSION"
        
        # 检查是否为Python 3.8+
        if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
            print_message "Python版本符合要求 (3.8+)"
        else
            print_error "Python版本过低，需要3.8或更高版本"
            exit 1
        fi
    else
        print_error "未找到Python3，请先安装Python 3.8+"
        exit 1
    fi
}

# 检查并安装依赖
install_dependencies() {
    print_message "安装Python依赖..."
    
    # 检查是否存在虚拟环境
    if [ ! -d "venv" ]; then
        print_message "创建虚拟环境..."
        python3 -m venv venv
    fi
    
    # 激活虚拟环境
    print_message "激活虚拟环境..."
    source venv/bin/activate
    
    # 升级pip
    print_message "升级pip..."
    pip install --upgrade pip
    
    # 安装依赖
    print_message "安装项目依赖..."
    pip install -r requirements.txt
    
    print_message "依赖安装完成"
}

# 配置环境
setup_environment() {
    local env_type=$1
    print_message "配置$env_type环境..."
    
    # 复制配置文件模板
    if [ ! -f "src/config.json" ]; then
        print_message "创建配置文件..."
        cp src/config.json.example src/config.json
        print_warning "请编辑 src/config.json 文件，配置AI服务API密钥"
    else
        print_message "配置文件已存在"
    fi
    
    # 创建环境变量文件
    if [ ! -f ".env" ]; then
        print_message "创建环境变量文件..."
        cat > .env << EOF
# Alethea优化版本环境变量
FLASK_ENV=$env_type
SECRET_KEY=alethea-optimized-secret-key-$(date +%s)

# 数据库配置
DATABASE_URL=sqlite:///alethea.db

# AI服务配置 (请填入您的API密钥)
DEEPSEEK_API_KEY=
ALI_QWEN_API_KEY=
BAIDU_WENXIN_API_KEY=
ZHIPU_AI_API_KEY=
KIMI_API_KEY=

# 本地AI服务
OLLAMA_BASE_URL=http://localhost:11434

# 国外AI服务 (默认禁用)
OPENAI_ENABLED=false
CLAUDE_ENABLED=false
GEMINI_ENABLED=false
EOF
        print_warning "请编辑 .env 文件，配置必要的环境变量"
    else
        print_message "环境变量文件已存在"
    fi
}

# 初始化数据库
init_database() {
    print_message "初始化数据库..."
    
    # 激活虚拟环境
    source venv/bin/activate
    
    # 运行数据库初始化
    python3 -c "
from src.main import app, db
with app.app_context():
    db.create_all()
    print('数据库初始化完成')
"
    
    print_message "数据库初始化完成"
}

# 运行测试
run_tests() {
    print_message "运行测试..."
    
    # 激活虚拟环境
    source venv/bin/activate
    
    # 检查基本功能
    python3 -c "
import sys
sys.path.insert(0, 'src')
try:
    from models.llm_models_optimized import OptimizedLLMManager
    from models.user import UserManager
    print('✅ 核心模块导入成功')
except ImportError as e:
    print(f'❌ 模块导入失败: {e}')
    sys.exit(1)
"
    
    print_message "基本测试通过"
}

# 启动应用
start_application() {
    local env_type=$1
    print_message "启动Alethea应用..."
    
    # 激活虚拟环境
    source venv/bin/activate
    
    if [ "$env_type" = "prod" ]; then
        print_message "生产环境启动..."
        # 生产环境使用gunicorn
        if command -v gunicorn &> /dev/null; then
            gunicorn -w 4 -b 0.0.0.0:8084 src.main:app
        else
            print_warning "未安装gunicorn，使用开发服务器"
            cd src && python3 main.py
        fi
    else
        print_message "开发环境启动..."
        cd src && python3 main.py
    fi
}

# 显示帮助信息
show_help() {
    echo "Alethea优化版本 v2.0 部署脚本"
    echo ""
    echo "使用方法:"
    echo "  ./deploy.sh [选项] [环境类型]"
    echo ""
    echo "环境类型:"
    echo "  dev     开发环境 (默认)"
    echo "  prod    生产环境"
    echo ""
    echo "选项:"
    echo "  --help, -h     显示帮助信息"
    echo "  --check        仅检查环境，不启动应用"
    echo "  --install      仅安装依赖，不启动应用"
    echo ""
    echo "示例:"
    echo "  ./deploy.sh dev          # 部署开发环境"
    echo "  ./deploy.sh prod         # 部署生产环境"
    echo "  ./deploy.sh --check      # 检查环境"
    echo "  ./deploy.sh --install    # 仅安装依赖"
}

# 主函数
main() {
    local env_type="dev"
    local check_only=false
    local install_only=false
    
    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            --help|-h)
                show_help
                exit 0
                ;;
            --check)
                check_only=true
                shift
                ;;
            --install)
                install_only=true
                shift
                ;;
            dev|prod)
                env_type=$1
                shift
                ;;
            *)
                print_error "未知参数: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    print_header
    
    # 检查环境
    check_python
    
    # 安装依赖
    install_dependencies
    
    # 配置环境
    setup_environment $env_type
    
    # 初始化数据库
    init_database
    
    # 运行测试
    run_tests
    
    if [ "$check_only" = true ]; then
        print_message "环境检查完成，所有组件正常"
        exit 0
    fi
    
    if [ "$install_only" = true ]; then
        print_message "依赖安装完成"
        exit 0
    fi
    
    # 显示启动信息
    echo ""
    print_message "部署完成！"
    print_message "环境类型: $env_type"
    print_message "访问地址: http://localhost:8084"
    print_message "API文档: http://localhost:8084/api/health"
    echo ""
    print_warning "首次运行请确保已配置AI服务API密钥"
    print_warning "配置文件: src/config.json 和 .env"
    echo ""
    
    # 启动应用
    start_application $env_type
}

# 检查是否在正确的目录
if [ ! -f "requirements.txt" ] || [ ! -f "src/main.py" ]; then
    print_error "请在Alethea项目根目录下运行此脚本"
    exit 1
fi

# 运行主函数
main "$@"
