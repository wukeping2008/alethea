# Git Bash 环境配置指南

## 🚀 Git Bash 配置完成

所有命令行操作现在都已配置为在Git Bash中执行！

### ✅ 已完成的配置：

#### 1. VSCode 默认终端设置
- **默认终端**: Git Bash
- **路径**: `C:\Program Files\Git\bin\bash.exe`
- **图标**: terminal-bash

#### 2. VSCode 任务配置
所有任务现在都在Git Bash中执行：
- 启动Alethea服务器
- 安装依赖
- 诊断环境
- 初始化数据库
- 测试Flask服务器

#### 3. Code Runner 配置
- 运行在终端中
- 自动清除之前输出
- 保存文件后运行

### 🎯 使用方法：

#### 方法1: VSCode 任务 (推荐)
1. 按 `Ctrl + Shift + P`
2. 输入 "Tasks: Run Task"
3. 选择 "启动Alethea服务器"
4. 任务将在Git Bash终端中执行

#### 方法2: VSCode 集成终端
1. 按 `Ctrl + `` (反引号) 打开终端
2. 终端将自动使用Git Bash
3. 运行命令：`python start_simple.py`

#### 方法3: Code Runner
1. 打开 `start_simple.py`
2. 按 `Ctrl + F5`
3. 代码将在Git Bash终端中运行

#### 方法4: 直接使用Git Bash脚本
```bash
# 运行启动脚本
./start_with_bash.sh

# 或使用批处理文件
run_bash.bat
```

### 🔧 Git Bash 优势：

#### Unix 风格命令支持
```bash
# 文件操作
ls -la
pwd
cd /c/Users/wukep/Documents/alethea

# 进程管理
ps aux | grep python
kill -9 <pid>

# 网络检查
curl http://localhost:8083
netstat -an | grep :8083
```

#### 环境变量管理
```bash
# 设置环境变量
export FLASK_ENV=development
export FLASK_DEBUG=True

# 查看环境变量
echo $FLASK_ENV
env | grep FLASK
```

#### 脚本执行
```bash
# 给脚本执行权限
chmod +x start_with_bash.sh

# 运行脚本
./start_with_bash.sh
```

### 📋 常用Git Bash命令：

#### 项目管理
```bash
# 启动项目
python start_simple.py

# 安装依赖
pip install -r requirements.txt

# 检查Python环境
python --version
which python

# 查看项目文件
ls -la src/
tree src/ (如果安装了tree命令)
```

#### 进程和端口管理
```bash
# 查看端口占用
netstat -an | grep :8083
lsof -i :8083 (在Git Bash中可能不可用)

# 查看Python进程
ps aux | grep python
tasklist | grep python (Windows命令)

# 结束进程
kill -9 <pid>
taskkill /f /pid <pid> (Windows命令)
```

#### 日志和调试
```bash
# 查看实时日志
tail -f logs/alethea.log (如果有日志文件)

# 测试网络连接
curl -I http://localhost:8083
wget --spider http://localhost:8083
```

### 🌐 启动项目：

#### 快速启动
```bash
# 方法1: 使用Python脚本
python start_simple.py

# 方法2: 使用Bash脚本
./start_with_bash.sh

# 方法3: 使用批处理文件
./run_bash.bat
```

#### 后台启动
```bash
# 后台运行
nohup python start_simple.py &

# 查看后台进程
jobs
ps aux | grep python
```

### 🔍 故障排除：

#### 检查Git Bash安装
```bash
# 检查bash版本
bash --version

# 检查Git版本
git --version

# 检查路径
which bash
which python
```

#### 权限问题
```bash
# 给脚本执行权限
chmod +x *.sh

# 检查文件权限
ls -la *.sh
```

#### 路径问题
```bash
# Windows路径转换
cd /c/Users/wukep/Documents/alethea
cd /c/Program\ Files/Git/

# 查看当前路径
pwd
```

### 💡 最佳实践：

1. **使用VSCode任务**: 最方便的启动方式
2. **保持终端打开**: 可以看到实时日志
3. **使用Ctrl+C停止**: 优雅停止服务器
4. **检查端口**: 启动前确保端口未被占用
5. **查看日志**: 注意终端输出的错误信息

### 🎉 配置完成！

现在所有命令行操作都将在Git Bash中执行，您可以享受Unix风格的命令行体验！

访问地址: http://localhost:8083
