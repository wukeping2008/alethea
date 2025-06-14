# Alethea 阿里云部署文档

## 概述

本文档提供了将Alethea智能教育平台部署到阿里云的完整指南。包含了从服务器配置到应用部署的所有步骤。

## 部署架构

```
用户 → CDN → SLB负载均衡 → ECS云服务器 → RDS数据库
                                    ↓
                              OSS对象存储
                                    ↓
                              Redis缓存
```

## 阿里云服务要求

### 1. ECS云服务器
- **配置**: 2核4GB内存，40GB系统盘
- **操作系统**: Ubuntu 20.04 LTS
- **网络**: VPC网络
- **安全组**: 开放22, 80, 443, 8083端口

### 2. RDS MySQL数据库
- **版本**: MySQL 8.0
- **规格**: 1核2GB起步
- **存储**: 20GB SSD云盘

### 3. OSS对象存储
- **用途**: 存储用户上传文件
- **类型**: 标准存储

### 4. 其他服务（可选）
- **Redis**: 缓存和会话存储
- **CDN**: 静态资源加速
- **SSL证书**: HTTPS支持

## 快速部署

### 1. 准备工作

1. 购买并配置阿里云服务
2. 获取服务器SSH访问权限
3. 准备域名和SSL证书

### 2. 自动部署

```bash
# 连接到服务器
ssh root@your-server-ip

# 创建应用用户
useradd -m -s /bin/bash alethea
usermod -aG sudo alethea
su - alethea

# 克隆项目
git clone https://github.com/your-username/alethea.git
cd alethea

# 运行部署脚本
chmod +x deploy/deploy.sh
./deploy/deploy.sh
```

### 3. 配置环境变量

编辑 `.env` 文件，填入正确的配置：

```bash
nano .env
```

重要配置项：
- `DATABASE_URL`: RDS数据库连接
- `SECRET_KEY`: Flask密钥
- `OPENAI_API_KEY`: AI模型API密钥
- `OSS_*`: 阿里云OSS配置

### 4. 启动服务

```bash
# 重启应用
sudo supervisorctl restart alethea

# 检查状态
sudo supervisorctl status
```

## 手动部署步骤

如果自动部署失败，可以按照以下步骤手动部署：

### 1. 系统环境准备

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装依赖
sudo apt install -y python3 python3-pip python3-venv nginx supervisor git mysql-client
```

### 2. 应用部署

```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
pip install gunicorn

# 配置环境
cp deploy/.env.production .env
# 编辑.env文件
```

### 3. 数据库初始化

```bash
python3 -c "
from src.main import app, db
with app.app_context():
    db.create_all()
    print('数据库初始化成功')
"
```

### 4. 配置服务

```bash
# 配置Nginx
sudo cp deploy/nginx.conf /etc/nginx/sites-available/alethea
sudo ln -s /etc/nginx/sites-available/alethea /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx

# 配置Supervisor
sudo cp deploy/supervisor.conf /etc/supervisor/conf.d/alethea.conf
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start alethea
```

## 配置文件说明

### Gunicorn配置 (`deploy/gunicorn.conf.py`)
- Worker进程数量
- 超时设置
- 日志配置
- 性能优化

### Nginx配置 (`deploy/nginx.conf`)
- SSL/TLS配置
- 静态文件处理
- 反向代理设置
- 安全头配置

### Supervisor配置 (`deploy/supervisor.conf`)
- 进程管理
- 自动重启
- 日志轮转
- 环境变量

## 域名和SSL配置

### 1. 域名解析

在域名管理控制台添加A记录：
```
@ → your-server-ip
www → your-server-ip
```

### 2. SSL证书

#### 使用阿里云免费SSL证书：

1. 在阿里云控制台申请免费SSL证书
2. 下载证书文件
3. 上传到服务器：

```bash
sudo mkdir -p /etc/ssl/certs /etc/ssl/private
sudo cp your-domain.crt /etc/ssl/certs/
sudo cp your-domain.key /etc/ssl/private/
sudo chmod 600 /etc/ssl/private/your-domain.key
```

4. 更新Nginx配置中的证书路径

#### 使用Let's Encrypt免费证书：

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

## 监控和维护

### 1. 日志查看

```bash
# 应用日志
tail -f /var/log/alethea/gunicorn_access.log
tail -f /var/log/alethea/gunicorn_error.log

# Nginx日志
tail -f /var/log/nginx/alethea_access.log
tail -f /var/log/nginx/alethea_error.log

# Supervisor日志
tail -f /var/log/alethea/supervisor.log
```

### 2. 服务管理

```bash
# 重启应用
sudo supervisorctl restart alethea

# 重启Nginx
sudo systemctl restart nginx

# 查看服务状态
sudo supervisorctl status
sudo systemctl status nginx
```

### 3. 性能监控

```bash
# 系统资源
htop
df -h
free -h

# 网络连接
netstat -tlnp
ss -tlnp
```

## 备份策略

### 1. 数据库备份

```bash
# 手动备份
mysqldump -h rds-host -u username -p alethea > backup_$(date +%Y%m%d).sql

# 自动备份脚本
cat > /home/alethea/backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
mysqldump -h $RDS_HOST -u $DB_USER -p$DB_PASS alethea > /home/alethea/backups/db_$DATE.sql
find /home/alethea/backups -name "db_*.sql" -mtime +7 -delete
EOF
chmod +x /home/alethea/backup.sh

# 添加到crontab
crontab -e
# 添加: 0 2 * * * /home/alethea/backup.sh
```

### 2. 代码备份

```bash
# 推送到Git仓库
git add .
git commit -m "Production deployment"
git push origin main
```

## 故障排除

### 常见问题

1. **应用无法启动**
   - 检查.env配置
   - 查看supervisor日志
   - 验证数据库连接

2. **502 Bad Gateway**
   - 检查gunicorn进程
   - 验证端口监听
   - 查看Nginx错误日志

3. **数据库连接失败**
   - 检查RDS白名单
   - 验证连接字符串
   - 测试网络连通性

4. **静态文件404**
   - 检查文件路径
   - 验证Nginx配置
   - 确认文件权限

### 调试命令

```bash
# 检查端口监听
sudo netstat -tlnp | grep :8083

# 测试应用
curl -I http://localhost:8083

# 检查进程
ps aux | grep gunicorn

# 测试数据库连接
mysql -h rds-host -u username -p
```

## 安全建议

1. **服务器安全**
   - 定期更新系统
   - 配置防火墙
   - 禁用root登录
   - 使用密钥认证

2. **应用安全**
   - 使用强密码
   - 启用HTTPS
   - 配置安全头
   - 限制API访问频率

3. **数据安全**
   - 定期备份
   - 加密敏感数据
   - 限制数据库访问
   - 监控异常访问

## 性能优化

1. **应用优化**
   - 启用缓存
   - 优化数据库查询
   - 使用CDN
   - 压缩静态资源

2. **服务器优化**
   - 调整内核参数
   - 优化文件描述符
   - 配置内存管理
   - 监控系统资源

## 联系支持

如果在部署过程中遇到问题，请：

1. 查看日志文件
2. 检查配置文件
3. 参考故障排除部分
4. 联系技术支持

---

**注意**: 请确保在生产环境中使用强密码和安全配置。定期更新系统和应用依赖以保持安全性。
