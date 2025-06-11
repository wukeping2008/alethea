@echo off
echo 启动Git Bash并运行Alethea项目
echo ================================

REM 检查Git Bash是否存在
if not exist "C:\Program Files\Git\bin\bash.exe" (
    echo 错误: 找不到Git Bash，请确保Git已安装
    pause
    exit /b 1
)

echo 正在启动Git Bash...
"C:\Program Files\Git\bin\bash.exe" --login -i -c "cd /c/Users/wukep/Documents/alethea && echo '当前目录:' && pwd && echo '启动Alethea项目...' && python start_simple.py"

pause
