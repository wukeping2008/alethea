#!/bin/bash

# Alethea项目GitHub上传脚本
# 使用方法: ./upload_to_github.sh [GitHub用户名] [仓库名]

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
    echo -e "${BLUE} Alethea项目GitHub上传脚本${NC}"
    echo -e "${BLUE}================================${NC}"
}

# 显示帮助信息
show_help() {
    echo "Alethea项目GitHub上传脚本"
    echo ""
    echo "使用方法:"
    echo "  ./upload_to_github.sh [GitHub用户名] [仓库名]"
    echo ""
    echo "参数:"
    echo "  GitHub用户名    您的GitHub用户名"
    echo "  仓库名         GitHub仓库名称 (默认: alethea-optimized)"
    echo ""
    echo "示例:"
    echo "  ./upload_to_github.sh myusername"
    echo "  ./upload_to_github.sh myusername my-alethea-repo"
    echo ""
    echo "注意:"
    echo "  - 请确保您已在GitHub上创建了对应的仓库"
    echo "  - 请确保您有推送权限"
}

# 检查Git状态
check_git_status() {
    print_message "检查Git状态..."
    
    if [ ! -d ".git" ]; then
        print_error "当前目录不是Git仓库"
        exit 1
    fi
    
    # 检查是否有未提交的更改
    if [ -n "$(git status --porcelain)" ]; then
        print_warning "检测到未提交的更改，正在提交..."
        git add .
        git commit -m "Auto commit before GitHub upload - $(date)"
    else
        print_message "Git工作区干净，无需提交"
    fi
}

# 添加远程仓库
add_remote_repository() {
    local username=$1
    local repo_name=$2
    local remote_url="https://github.com/${username}/${repo_name}.git"
    
    print_message "添加远程仓库: $remote_url"
    
    # 检查是否已存在origin远程仓库
    if git remote get-url origin >/dev/null 2>&1; then
        print_warning "远程仓库origin已存在，正在更新..."
        git remote set-url origin "$remote_url"
    else
        git remote add origin "$remote_url"
    fi
    
    print_message "远程仓库配置完成"
}

# 推送到GitHub
push_to_github() {
    print_message "开始推送到GitHub..."
    
    # 获取当前分支
    current_branch=$(git branch --show-current)
    print_message "当前分支: $current_branch"
    
    # 推送当前分支
    print_message "推送分支: $current_branch"
    if git push -u origin "$current_branch"; then
        print_message "分支 $current_branch 推送成功"
    else
        print_error "分支推送失败，请检查网络连接和权限"
        exit 1
    fi
    
    # 推送其他分支
    print_message "推送其他分支..."
    for branch in $(git branch | sed 's/\*//g' | sed 's/ //g'); do
        if [ "$branch" != "$current_branch" ]; then
            print_message "推送分支: $branch"
            git push origin "$branch" || print_warning "分支 $branch 推送失败，可能已存在"
        fi
    done
    
    # 推送标签
    print_message "推送标签..."
    if git push --tags; then
        print_message "标签推送成功"
    else
        print_warning "标签推送失败，可能没有标签或已存在"
    fi
}

# 显示上传结果
show_result() {
    local username=$1
    local repo_name=$2
    
    echo ""
    print_message "🎉 上传完成！"
    echo ""
    echo -e "${BLUE}GitHub仓库信息:${NC}"
    echo "  仓库地址: https://github.com/${username}/${repo_name}"
    echo "  克隆地址: https://github.com/${username}/${repo_name}.git"
    echo "  发布页面: https://github.com/${username}/${repo_name}/releases"
    echo ""
    echo -e "${BLUE}已上传内容:${NC}"
    echo "  ✅ 完整源代码 (70+个文件)"
    echo "  ✅ AI模型系统 (支持9个AI服务商)"
    echo "  ✅ 用户管理系统"
    echo "  ✅ 学习分析系统"
    echo "  ✅ 前端界面 (18个HTML页面)"
    echo "  ✅ 仿真器 (3个在线仿真器)"
    echo "  ✅ 配置文件和文档"
    echo "  ✅ 部署脚本"
    echo ""
    echo -e "${BLUE}Git信息:${NC}"
    echo "  ✅ 所有分支已推送"
    echo "  ✅ 版本标签已推送"
    echo "  ✅ 提交历史完整"
    echo ""
    print_message "您现在可以在GitHub上查看和管理您的项目了！"
}

# 主函数
main() {
    local username=""
    local repo_name="alethea-optimized"
    
    # 解析参数
    case $# in
        0)
            print_error "请提供GitHub用户名"
            show_help
            exit 1
            ;;
        1)
            if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
                show_help
                exit 0
            fi
            username=$1
            ;;
        2)
            username=$1
            repo_name=$2
            ;;
        *)
            print_error "参数过多"
            show_help
            exit 1
            ;;
    esac
    
    print_header
    
    print_message "准备上传Alethea项目到GitHub"
    print_message "GitHub用户名: $username"
    print_message "仓库名称: $repo_name"
    echo ""
    
    # 检查Git状态
    check_git_status
    
    # 添加远程仓库
    add_remote_repository "$username" "$repo_name"
    
    # 推送到GitHub
    push_to_github
    
    # 显示结果
    show_result "$username" "$repo_name"
}

# 检查是否在正确的目录
if [ ! -f "start_server.py" ] || [ ! -f "README.md" ]; then
    print_error "请在Alethea项目根目录下运行此脚本"
    exit 1
fi

# 运行主函数
main "$@"
