# Alethea 阿里云部署指南

## 1. 阿里云服务准备

### 1.1 ECS云服务器
- **推荐配置**：2核4GB内存，40GB系统盘
- **操作系统**：Ubuntu 20.04 LTS 或 CentOS 8
- **网络**：选择VPC网络，配置安全组
- **安全组规则**：
  - 入方向：22(SSH), 80(HTTP), 443(HTTPS), 8083(应用端口)
  - 出方向：全部允许

### 1.2 RDS MySQL数据库
- **版本**：MySQL 8.0
- **规格**：1核2GB起步
- **存储**：20GB SSD云盘
- **网络**：与ECS在同一VPC
- **白名单**：添加ECS内网IP

### 1.3 OSS对象存储
- **存储类型**：标准存储
- **读写权限**：私有读写
- **CDN加速**：开启（可选）

### 1.4 域名和SSL证书
- **域名备案**：如果使用.cn域名需要备案
- **SSL证书**：申请免费SSL证书或购买

## 2. 服务器环境配置

### 2.1 连接到ECS服务器
```bash
ssh root@your-server-ip
```

### 2.2 安装基础软件
```bash
# 更新系统
apt update && apt upgrade -y

# 安装Python 3.9+
apt install python3 python3-pip python3-venv -y

# 安装Nginx
apt install nginx -y

# 安装Git
apt install git -y

# 安装MySQL客户端
apt install mysql-client -y

# 安装其他依赖
apt install build-essential libssl-dev libffi-dev python3-dev -y
```

### 2.3 创建应用用户
```bash
# 创建专用用户
useradd -m -s /bin/bash alethea
usermod -aG sudo alethea

# 切换到应用用户
su - alethea
```

## 3. 应用部署

### 3.1 克隆代码
```bash
cd /home/alethea
git clone https://github.com/your-username/alethea.git
cd alethea
```

### 3.2 创建虚拟环境
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3.3 安装依赖
```bash
pip install -r requirements.txt
pip install gunicorn supervisor
```

### 3.4 配置环境变量
```bash
cp .env.example .env
nano .env
```

## 4. 数据库配置

### 4.1 连接RDS数据库
在.env文件中配置：
```
DATABASE_URL=mysql+pymysql://username:password@rds-host:3306/alethea
```

### 4.2 初始化数据库
```bash
python3 -c "
from src.main import app, db
with app.app_context():
    db.create_all()
    print('Database initialized successfully')
"
```

## 5. 生产环境配置

### 5.1 Gunicorn配置
创建 gunicorn.conf.py

### 5.2 Nginx配置
创建 nginx 配置文件

### 5.3 Supervisor配置
创建 supervisor 配置文件

### 5.4 SSL证书配置
配置HTTPS访问

## 6. 监控和日志

### 6.1 日志配置
- 应用日志：/var/log/alethea/
- Nginx日志：/var/log/nginx/
- 系统日志：/var/log/syslog

### 6.2 监控配置
- 系统监控：阿里云监控
- 应用监控：自定义监控脚本

## 7. 备份策略

### 7.1 数据库备份
- RDS自动备份：每日备份，保留7天
- 手动备份：重要更新前

### 7.2 代码备份
- Git版本控制
- 定期推送到远程仓库

## 8. 安全配置

### 8.1 防火墙配置
```bash
ufw enable
ufw allow ssh
ufw allow 'Nginx Full'
```

### 8.2 SSH安全
- 禁用root登录
- 使用密钥认证
- 修改默认端口

## 9. 性能优化

### 9.1 应用优化
- 启用Gzip压缩
- 静态文件CDN
- 数据库连接池

### 9.2 服务器优化
- 内核参数调优
- 文件描述符限制
- 内存管理

## 10. 故障排除

### 10.1 常见问题
- 端口占用
- 权限问题
- 依赖冲突
- 数据库连接

### 10.2 日志分析
- 查看应用日志
- 检查系统资源
- 网络连接测试
