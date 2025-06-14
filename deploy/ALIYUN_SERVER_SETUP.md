# 阿里云服务端配置详细指南

## 🏗️ 阿里云基础设施准备

### 1. 购买和配置ECS云服务器

#### 1.1 购买ECS实例
1. 登录阿里云控制台：https://ecs.console.aliyun.com
2. 点击"创建实例"
3. 选择配置：
   - **地域**：选择离用户最近的地域（如华东1-杭州）
   - **实例规格**：ecs.t5-lc1m2.small（1核2GB）或更高
   - **镜像**：Ubuntu 20.04 64位
   - **存储**：40GB高效云盘
   - **网络**：专有网络VPC
   - **安全组**：新建安全组
   - **登录凭证**：设置密码或密钥对

#### 1.2 配置安全组规则
在ECS控制台 → 网络与安全 → 安全组：

| 方向 | 协议类型 | 端口范围 | 授权对象 | 描述 |
|------|----------|----------|----------|------|
| 入方向 | SSH(22) | 22/22 | 0.0.0.0/0 | SSH远程连接 |
| 入方向 | HTTP(80) | 80/80 | 0.0.0.0/0 | HTTP访问 |
| 入方向 | HTTPS(443) | 443/443 | 0.0.0.0/0 | HTTPS访问 |
| 入方向 | 自定义TCP | 8083/8083 | 0.0.0.0/0 | 应用端口 |

### 2. 域名解析配置

#### 2.1 在阿里云DNS控制台配置
1. 登录阿里云控制台 → 域名与网站 → 云解析DNS
2. 找到域名 `alethealab.cn`
3. 添加解析记录：

| 记录类型 | 主机记录 | 解析线路 | 记录值 | TTL |
|----------|----------|----------|--------|-----|
| A | @ | 默认 | 您的ECS公网IP | 600 |
| A | www | 默认 | 您的ECS公网IP | 600 |

#### 2.2 验证域名解析
```bash
# 在本地测试域名解析
nslookup alethealab.cn
nslookup www.alethealab.cn

# 或使用ping测试
ping alethealab.cn
ping www.alethealab.cn
```

## 🖥️ 服务器端操作步骤

### 步骤1：连接到服务器

```bash
# 使用SSH连接到服务器（替换为您的实际IP）
ssh root@YOUR_SERVER_IP

# 如果使用密钥文件
ssh -i /path/to/your-key.pem root@YOUR_SERVER_IP
```

### 步骤2：上传代码到服务器

在**本地终端**执行：
```bash
# 进入项目目录
cd /Users/kepingwu/Desktop/alethea

# 上传代码到服务器
./deploy/upload_to_server.sh YOUR_SERVER_IP
```

### 步骤3：在服务器上运行自动部署脚本

连接到服务器后执行：
```bash
# 进入应用目录
cd /home/alethea/alethea

# 运行自动部署脚本
./deploy/aliyun_auto_deploy.sh
```

### 步骤4：配置环境变量

```bash
# 编辑环境配置文件
nano /home/alethea/alethea/.env
```

在`.env`文件中配置以下内容：
```bash
# 生产环境配置
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your_generated_secret_key

# 数据库配置
DATABASE_URL=sqlite:///instance/alethea.db

# AI服务配置（请填入您的实际API密钥）
OPENAI_API_KEY=sk-your-openai-api-key
CLAUDE_API_KEY=your-claude-api-key
GEMINI_API_KEY=your-gemini-api-key

# 阿里云配置（可选）
ALIYUN_ACCESS_KEY_ID=your_access_key_id
ALIYUN_ACCESS_KEY_SECRET=your_access_key_secret

# 域名配置
DOMAIN=alethealab.cn
WWW_DOMAIN=www.alethealab.cn

# 应用配置
HOST=0.0.0.0
PORT=8083
WORKERS=4
```

### 步骤5：重启服务

```bash
# 重启应用服务
systemctl restart alethea

# 重启Nginx
systemctl restart nginx

# 检查服务状态
systemctl status alethea
systemctl status nginx
```

### 步骤6：验证部署

```bash
# 检查应用是否正在运行
curl http://localhost:8083/health

# 检查Nginx是否正常
curl http://localhost/health

# 查看服务日志
journalctl -u alethea -f
```

## 🔧 详细的服务器配置说明

### 自动部署脚本做了什么

`./deploy/aliyun_auto_deploy.sh` 脚本会自动执行以下操作：

#### 1. 系统环境准备
```bash
# 更新系统包
apt update && apt upgrade -y

# 安装必要软件
apt install -y python3 python3-pip python3-venv nginx git mysql-client
apt install -y build-essential libssl-dev libffi-dev python3-dev
```

#### 2. 创建应用用户
```bash
# 创建专用用户
useradd -m -s /bin/bash alethea
usermod -aG sudo alethea
```

#### 3. 配置Python环境
```bash
# 创建虚拟环境
cd /home/alethea/alethea
python3 -m venv venv
source venv/bin/activate

# 安装Python依赖
pip install -r requirements.txt
pip install gunicorn
```

#### 4. 配置Gunicorn服务
创建systemd服务文件：`/etc/systemd/system/alethea.service`

#### 5. 配置Nginx
- 复制Nginx配置到：`/etc/nginx/sites-available/alethea`
- 启用站点：`/etc/nginx/sites-enabled/alethea`
- 配置域名：`alethealab.cn` 和 `www.alethealab.cn`

#### 6. 申请SSL证书
```bash
# 安装Certbot
apt install -y certbot python3-certbot-nginx

# 申请免费SSL证书
certbot --nginx -d alethealab.cn -d www.alethealab.cn
```

#### 7. 配置防火墙
```bash
# 启用UFW防火墙
ufw enable
ufw allow ssh
ufw allow 'Nginx Full'
ufw allow 8083
```

#### 8. 设置监控和备份
- 创建监控脚本：`/usr/local/bin/alethea-monitor.sh`
- 创建备份脚本：`/usr/local/bin/alethea-backup.sh`
- 配置定时任务（crontab）

## 🚨 常见问题和解决方案

### 问题1：SSH连接失败
```bash
# 检查安全组是否开放22端口
# 检查服务器是否正在运行
# 确认IP地址和登录凭证正确
```

### 问题2：域名无法访问
```bash
# 检查域名解析
nslookup alethealab.cn

# 检查Nginx状态
systemctl status nginx

# 检查防火墙
ufw status
```

### 问题3：SSL证书申请失败
```bash
# 手动申请证书
certbot --nginx -d alethealab.cn -d www.alethealab.cn

# 如果失败，先使用HTTP模式
# 编辑 /etc/nginx/sites-available/alethea
# 注释掉SSL相关配置
```

### 问题4：应用无法启动
```bash
# 查看详细错误日志
journalctl -u alethea -n 50

# 检查Python环境
cd /home/alethea/alethea
source venv/bin/activate
python3 -c "import src.main"

# 检查端口占用
netstat -tulpn | grep 8083
```

## 📊 服务管理命令

### 应用服务管理
```bash
# 查看状态
systemctl status alethea

# 启动/停止/重启
systemctl start alethea
systemctl stop alethea
systemctl restart alethea

# 查看日志
journalctl -u alethea -f
journalctl -u alethea --since "1 hour ago"
```

### Nginx服务管理
```bash
# 查看状态
systemctl status nginx

# 重启/重载
systemctl restart nginx
systemctl reload nginx

# 测试配置
nginx -t

# 查看日志
tail -f /var/log/nginx/alethea_access.log
tail -f /var/log/nginx/alethea_error.log
```

### 系统监控
```bash
# 查看系统资源
htop
df -h
free -h

# 查看网络连接
netstat -tulpn | grep :80
netstat -tulpn | grep :443
netstat -tulpn | grep :8083
```

## ✅ 部署完成检查清单

- [ ] ECS服务器已创建并运行
- [ ] 安全组规则已配置（22, 80, 443, 8083端口）
- [ ] 域名解析已配置（alethealab.cn → 服务器IP）
- [ ] 代码已上传到服务器
- [ ] 自动部署脚本已运行完成
- [ ] 环境变量已配置（.env文件）
- [ ] 应用服务正在运行（systemctl status alethea）
- [ ] Nginx服务正在运行（systemctl status nginx）
- [ ] SSL证书已申请成功
- [ ] 网站可以通过HTTPS访问
- [ ] AI功能正常工作

## 🎯 最终验证

部署完成后，请验证以下功能：

1. **网站访问**：
   - https://alethealab.cn
   - https://www.alethealab.cn

2. **功能测试**：
   - 首页学科分类显示正常
   - 点击学科卡片可以进行AI问答
   - 主题切换功能正常
   - 各个页面导航正常

3. **性能测试**：
   - 页面加载速度正常
   - AI问答响应及时
   - 静态资源加载正常

---

**按照以上步骤操作，您的Alethea网站将成功部署到阿里云并通过 https://alethealab.cn 正式上线！**
