# Alethea 阿里云部署完整指南

## 🚀 快速部署指南

### 前置条件

1. **阿里云ECS服务器**
   - 推荐配置：2核4GB内存，40GB系统盘
   - 操作系统：Ubuntu 20.04 LTS
   - 已配置安全组（开放22, 80, 443, 8083端口）

2. **域名配置**
   - 域名：alethealab.cn, www.alethealab.cn
   - DNS解析已指向服务器IP地址

3. **本地环境**
   - macOS/Linux系统
   - 已安装SSH客户端
   - 已配置SSH密钥或密码认证

### 🎯 一键部署步骤

#### 步骤1：上传代码到服务器

```bash
# 在本地终端执行
cd /Users/kepingwu/Desktop/alethea
chmod +x deploy/upload_to_server.sh

# 替换YOUR_SERVER_IP为实际的服务器IP地址
./deploy/upload_to_server.sh YOUR_SERVER_IP
```

#### 步骤2：连接到服务器并运行部署脚本

```bash
# 连接到服务器
ssh root@YOUR_SERVER_IP

# 进入应用目录
cd /home/alethea/alethea

# 运行自动部署脚本
chmod +x deploy/aliyun_auto_deploy.sh
./deploy/aliyun_auto_deploy.sh
```

#### 步骤3：配置环境变量

```bash
# 编辑环境配置文件
nano /home/alethea/alethea/.env

# 配置以下重要参数：
# - AI服务API密钥
# - 数据库连接信息
# - 阿里云服务配置
```

#### 步骤4：重启服务

```bash
# 重启应用服务
systemctl restart alethea

# 重启Nginx
systemctl restart nginx

# 检查服务状态
systemctl status alethea
systemctl status nginx
```

### 🌐 访问网站

部署完成后，您可以通过以下地址访问网站：
- https://alethealab.cn
- https://www.alethealab.cn

## 📋 详细配置说明

### 环境变量配置

编辑 `/home/alethea/alethea/.env` 文件：

```bash
# 生产环境配置
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your_secret_key_here

# 数据库配置
DATABASE_URL=sqlite:///instance/alethea.db
# 或使用MySQL: mysql+pymysql://user:password@host:3306/database

# AI服务配置
OPENAI_API_KEY=your_openai_api_key
CLAUDE_API_KEY=your_claude_api_key
GEMINI_API_KEY=your_gemini_api_key

# 阿里云配置
ALIYUN_ACCESS_KEY_ID=your_access_key_id
ALIYUN_ACCESS_KEY_SECRET=your_access_key_secret
ALIYUN_OSS_BUCKET=your_oss_bucket
ALIYUN_OSS_ENDPOINT=your_oss_endpoint

# 域名配置
DOMAIN=alethealab.cn
WWW_DOMAIN=www.alethealab.cn

# 应用配置
HOST=0.0.0.0
PORT=8083
WORKERS=4
```

### SSL证书配置

部署脚本会自动申请Let's Encrypt免费SSL证书。如果自动申请失败，可以手动配置：

```bash
# 手动申请SSL证书
certbot --nginx -d alethealab.cn -d www.alethealab.cn

# 设置自动续期
echo "0 12 * * * /usr/bin/certbot renew --quiet" | crontab -
```

### 数据库配置

#### 使用SQLite（默认）
```bash
# SQLite数据库会自动创建在 instance/alethea.db
# 无需额外配置
```

#### 使用MySQL（推荐生产环境）
```bash
# 1. 创建数据库
mysql -h your-rds-host -u username -p
CREATE DATABASE alethea CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 2. 更新.env文件
DATABASE_URL=mysql+pymysql://username:password@rds-host:3306/alethea

# 3. 重新初始化数据库
cd /home/alethea/alethea
source venv/bin/activate
python3 -c "
from src.main import app, db
with app.app_context():
    db.create_all()
    print('Database initialized successfully')
"
```

## 🔧 服务管理

### 应用服务管理

```bash
# 查看应用状态
systemctl status alethea

# 启动应用
systemctl start alethea

# 停止应用
systemctl stop alethea

# 重启应用
systemctl restart alethea

# 查看应用日志
journalctl -u alethea -f

# 查看应用错误日志
journalctl -u alethea --since "1 hour ago"
```

### Nginx服务管理

```bash
# 查看Nginx状态
systemctl status nginx

# 重启Nginx
systemctl restart nginx

# 重新加载Nginx配置
systemctl reload nginx

# 测试Nginx配置
nginx -t

# 查看Nginx日志
tail -f /var/log/nginx/alethea_access.log
tail -f /var/log/nginx/alethea_error.log
```

### 数据库管理

```bash
# 备份SQLite数据库
cp /home/alethea/alethea/instance/alethea.db /backup/alethea_$(date +%Y%m%d).db

# 查看数据库大小
du -h /home/alethea/alethea/instance/alethea.db

# 数据库迁移（如果有新的模型变更）
cd /home/alethea/alethea
source venv/bin/activate
python3 -c "
from src.main import app, db
with app.app_context():
    db.create_all()
"
```

## 📊 监控和维护

### 系统监控

```bash
# 查看系统资源使用情况
htop

# 查看磁盘使用情况
df -h

# 查看内存使用情况
free -h

# 查看网络连接
netstat -tulpn | grep :8083
netstat -tulpn | grep :80
```

### 日志管理

```bash
# 应用日志
journalctl -u alethea --since "1 day ago"

# Nginx访问日志
tail -f /var/log/nginx/alethea_access.log

# Nginx错误日志
tail -f /var/log/nginx/alethea_error.log

# 系统日志
tail -f /var/log/syslog

# 清理旧日志
find /var/log -name "*.log" -mtime +7 -delete
```

### 自动化监控

部署脚本已自动配置监控脚本：

```bash
# 查看监控脚本
cat /usr/local/bin/alethea-monitor.sh

# 手动运行监控
/usr/local/bin/alethea-monitor.sh

# 查看监控日志
tail -f /var/log/alethea-monitor.log
```

### 自动化备份

```bash
# 查看备份脚本
cat /usr/local/bin/alethea-backup.sh

# 手动运行备份
/usr/local/bin/alethea-backup.sh

# 查看备份文件
ls -la /backup/alethea/
```

## 🔒 安全配置

### 防火墙配置

```bash
# 查看防火墙状态
ufw status

# 开放必要端口
ufw allow ssh
ufw allow 'Nginx Full'
ufw allow 8083

# 启用防火墙
ufw enable
```

### SSH安全

```bash
# 编辑SSH配置
nano /etc/ssh/sshd_config

# 推荐配置：
# Port 22
# PermitRootLogin no
# PasswordAuthentication no
# PubkeyAuthentication yes

# 重启SSH服务
systemctl restart ssh
```

### 应用安全

```bash
# 设置文件权限
chown -R alethea:alethea /home/alethea/alethea
chmod 600 /home/alethea/alethea/.env
chmod +x /home/alethea/alethea/deploy/*.sh
```

## 🚨 故障排除

### 常见问题

#### 1. 应用无法启动

```bash
# 检查应用状态
systemctl status alethea

# 查看详细错误日志
journalctl -u alethea -n 50

# 检查Python环境
cd /home/alethea/alethea
source venv/bin/activate
python3 -c "import src.main"
```

#### 2. 网站无法访问

```bash
# 检查Nginx状态
systemctl status nginx

# 测试Nginx配置
nginx -t

# 检查端口监听
netstat -tulpn | grep :80
netstat -tulpn | grep :443
netstat -tulpn | grep :8083

# 检查防火墙
ufw status
```

#### 3. SSL证书问题

```bash
# 检查证书状态
certbot certificates

# 手动续期证书
certbot renew

# 重新申请证书
certbot --nginx -d alethealab.cn -d www.alethealab.cn --force-renewal
```

#### 4. 数据库连接问题

```bash
# 检查数据库文件
ls -la /home/alethea/alethea/instance/

# 测试数据库连接
cd /home/alethea/alethea
source venv/bin/activate
python3 -c "
from src.main import app, db
with app.app_context():
    print('Database connection test:', db.engine.execute('SELECT 1').scalar())
"
```

### 性能优化

#### 1. 应用性能优化

```bash
# 调整Gunicorn工作进程数
nano /home/alethea/alethea/gunicorn.conf.py

# 重启应用
systemctl restart alethea
```

#### 2. Nginx性能优化

```bash
# 编辑Nginx配置
nano /etc/nginx/sites-available/alethea

# 启用Gzip压缩、设置缓存等
# 重新加载配置
nginx -t && systemctl reload nginx
```

#### 3. 系统性能优化

```bash
# 调整系统参数
echo 'net.core.somaxconn = 1024' >> /etc/sysctl.conf
echo 'net.ipv4.tcp_max_syn_backlog = 1024' >> /etc/sysctl.conf
sysctl -p
```

## 📞 技术支持

如果在部署过程中遇到问题，请：

1. 查看相关日志文件
2. 检查系统资源使用情况
3. 确认网络连接和防火墙配置
4. 验证域名DNS解析
5. 检查SSL证书状态

## 📝 更新和维护

### 代码更新

```bash
# 1. 备份当前版本
/usr/local/bin/alethea-backup.sh

# 2. 上传新代码
./deploy/upload_to_server.sh YOUR_SERVER_IP

# 3. 重启服务
systemctl restart alethea
systemctl reload nginx
```

### 系统更新

```bash
# 更新系统包
apt update && apt upgrade -y

# 更新Python包
cd /home/alethea/alethea
source venv/bin/activate
pip install --upgrade -r requirements.txt

# 重启服务
systemctl restart alethea
```

---

**部署完成后，您的Alethea网站将在 https://alethealab.cn 正式上线！**
