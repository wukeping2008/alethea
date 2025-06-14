# Alethea HTTP版本部署指南

## 🌐 HTTP版本说明

由于您的域名 `alethealab.cn` 没有ICP备案，我们为您准备了HTTP版本的部署方案。这个版本不使用SSL证书，直接通过HTTP协议提供服务，适合没有备案的域名使用。

## 🚀 HTTP版本快速部署

### 前置条件

1. **阿里云ECS服务器**
   - 推荐配置：1核2GB内存，40GB存储
   - 操作系统：Ubuntu 20.04 LTS
   - 安全组开放端口：22 (SSH), 80 (HTTP), 8083 (应用)

2. **域名解析**
   - 将 `alethealab.cn` 和 `www.alethealab.cn` 解析到服务器IP
   - 无需SSL证书和ICP备案

### 🎯 一键部署步骤

#### 步骤1：上传代码到服务器

```bash
# 在本地终端执行
cd /Users/kepingwu/Desktop/alethea

# 上传代码到服务器（替换YOUR_SERVER_IP为实际IP）
./deploy/upload_to_server.sh YOUR_SERVER_IP
```

#### 步骤2：连接服务器并运行HTTP部署脚本

```bash
# 连接到服务器
ssh root@YOUR_SERVER_IP

# 进入应用目录
cd /home/alethea/alethea

# 运行HTTP版本部署脚本
./deploy/aliyun_http_deploy.sh
```

#### 步骤3：配置环境变量

```bash
# 编辑环境配置文件
nano /home/alethea/alethea/.env

# 配置AI服务API密钥等参数
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
- **http://alethealab.cn**
- **http://www.alethealab.cn**

⚠️ **注意**：HTTP版本没有SSL加密，数据传输不加密。

## 🔧 HTTP版本特点

### ✅ 优势
- **无需ICP备案**：适合没有备案的域名
- **部署简单**：不需要申请SSL证书
- **快速上线**：几分钟内即可完成部署
- **功能完整**：所有AI问答功能正常工作

### ⚠️ 注意事项
- **数据不加密**：HTTP传输数据不加密
- **浏览器警告**：现代浏览器可能显示"不安全"提示
- **SEO影响**：搜索引擎更偏好HTTPS网站
- **功能限制**：某些现代Web功能需要HTTPS

## 📋 HTTP版本配置详情

### 环境变量配置

编辑 `/home/alethea/alethea/.env` 文件：

```bash
# 生产环境配置 (HTTP版本)
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your_generated_secret_key

# 数据库配置
DATABASE_URL=sqlite:///instance/alethea.db

# AI服务配置（请填入您的实际API密钥）
OPENAI_API_KEY=sk-your-openai-api-key
CLAUDE_API_KEY=your-claude-api-key
GEMINI_API_KEY=your-gemini-api-key

# 域名配置 (HTTP版本)
DOMAIN=alethealab.cn
WWW_DOMAIN=www.alethealab.cn

# 应用配置
HOST=0.0.0.0
PORT=8083
WORKERS=4

# HTTP模式标识
USE_HTTPS=False
```

### Nginx HTTP配置

HTTP版本使用专门的Nginx配置文件 `nginx_http.conf`：

- **监听端口**：仅监听80端口（HTTP）
- **域名配置**：alethealab.cn, www.alethealab.cn
- **静态文件**：直接由Nginx服务
- **API代理**：代理到Gunicorn (端口8083)
- **Gzip压缩**：启用文件压缩
- **访问限制**：API限流保护

### 安全组配置

确保阿里云ECS安全组开放以下端口：

| 端口 | 协议 | 用途 | 授权对象 |
|------|------|------|----------|
| 22 | TCP | SSH连接 | 0.0.0.0/0 |
| 80 | TCP | HTTP访问 | 0.0.0.0/0 |
| 8083 | TCP | 应用端口 | 0.0.0.0/0 |

⚠️ **注意**：HTTP版本不需要开放443端口（HTTPS）

## 🔄 升级到HTTPS版本

当您获得ICP备案后，可以升级到HTTPS版本：

### 方法1：使用Let's Encrypt证书

```bash
# 安装Certbot
apt install -y certbot python3-certbot-nginx

# 申请SSL证书
certbot --nginx -d alethealab.cn -d www.alethealab.cn

# 自动续期
echo "0 12 * * * /usr/bin/certbot renew --quiet" | crontab -
```

### 方法2：重新部署HTTPS版本

```bash
# 使用原始的HTTPS部署脚本
./deploy/aliyun_auto_deploy.sh
```

### 方法3：手动配置SSL

```bash
# 替换Nginx配置
cp deploy/nginx.conf /etc/nginx/sites-available/alethea

# 上传SSL证书文件
# /etc/ssl/certs/alethealab.cn.crt
# /etc/ssl/private/alethealab.cn.key

# 重启Nginx
systemctl restart nginx
```

## 🛠️ 服务管理

### 常用管理命令

```bash
# 查看服务状态
systemctl status alethea nginx

# 重启服务
systemctl restart alethea nginx

# 查看日志
journalctl -u alethea -f
tail -f /var/log/nginx/alethea_access.log

# 查看系统资源
htop
df -h
free -h
```

### 监控和备份

HTTP版本包含完整的监控和备份功能：

```bash
# 监控脚本（每5分钟运行）
/usr/local/bin/alethea-monitor.sh

# 备份脚本（每天凌晨2点运行）
/usr/local/bin/alethea-backup.sh

# 查看监控日志
tail -f /var/log/alethea-monitor.log

# 查看备份文件
ls -la /backup/alethea/
```

## 🚨 故障排除

### 常见问题

#### 1. 网站无法访问

```bash
# 检查域名解析
nslookup alethealab.cn

# 检查Nginx状态
systemctl status nginx

# 检查端口监听
netstat -tulpn | grep :80

# 检查防火墙
ufw status
```

#### 2. 应用无法启动

```bash
# 查看应用日志
journalctl -u alethea -n 50

# 检查Python环境
cd /home/alethea/alethea
source venv/bin/activate
python3 -c "import src.main"

# 检查端口占用
netstat -tulpn | grep :8083
```

#### 3. AI功能不工作

```bash
# 检查环境变量
cat /home/alethea/alethea/.env | grep API_KEY

# 测试API连接
curl -X POST http://localhost:8083/api/llm/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "测试问题", "subject": "数学"}'
```

## 📊 性能优化

### HTTP版本优化建议

1. **启用Gzip压缩**（已配置）
2. **静态文件缓存**（已配置）
3. **API限流保护**（已配置）
4. **数据库优化**：
   ```bash
   # 定期清理日志
   find /var/log -name "*.log" -mtime +7 -delete
   
   # 数据库备份
   cp /home/alethea/alethea/instance/alethea.db /backup/
   ```

### 系统资源监控

```bash
# 查看CPU和内存使用
htop

# 查看磁盘使用
df -h

# 查看网络连接
ss -tulpn

# 查看进程
ps aux | grep alethea
```

## 🎯 部署验证清单

- [ ] ECS服务器已创建并运行
- [ ] 安全组已配置（22, 80, 8083端口）
- [ ] 域名解析已配置（HTTP）
- [ ] 代码已上传到服务器
- [ ] HTTP部署脚本已运行完成
- [ ] 环境变量已配置（.env文件）
- [ ] 应用服务正在运行
- [ ] Nginx服务正在运行
- [ ] 网站可以通过HTTP访问
- [ ] AI功能正常工作
- [ ] 监控和备份脚本已配置

## 🌟 最终验证

部署完成后，请验证以下功能：

1. **网站访问**：
   - http://alethealab.cn ✅
   - http://www.alethealab.cn ✅

2. **功能测试**：
   - 首页48个学科分类显示正常 ✅
   - 点击学科卡片可以进行AI问答 ✅
   - 主题切换功能正常 ✅
   - 各个页面导航正常 ✅

3. **性能测试**：
   - 页面加载速度正常 ✅
   - AI问答响应及时 ✅
   - 静态资源加载正常 ✅

---

## 📞 技术支持

如果在HTTP版本部署过程中遇到问题：

1. 查看应用日志：`journalctl -u alethea -f`
2. 查看Nginx日志：`tail -f /var/log/nginx/alethea_error.log`
3. 检查系统资源：`htop`, `df -h`
4. 验证域名解析：`nslookup alethealab.cn`
5. 测试端口连通性：`telnet YOUR_SERVER_IP 80`

**HTTP版本部署完成后，您的Alethea网站将通过 http://alethealab.cn 正式上线！**

虽然是HTTP版本，但所有AI学科问答功能都完全正常，用户可以正常使用48个理工科学科的AI问答服务。
