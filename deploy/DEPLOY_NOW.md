# 立即部署到您的阿里云服务器

## 🚀 现在开始部署！

既然您已经有阿里云服务器，我们可以立即开始部署HTTP版本的Alethea网站。

## 📋 部署前检查清单

请确认以下信息：

### 1. 服务器信息
- [ ] 服务器IP地址：`_______________`
- [ ] SSH登录方式：密码 或 密钥
- [ ] 操作系统：Ubuntu 20.04 (推荐) 或 CentOS

### 2. 安全组配置
确保已开放以下端口：
- [ ] 22端口 (SSH)
- [ ] 80端口 (HTTP)
- [ ] 8083端口 (应用)

### 3. 域名解析
- [ ] alethealab.cn → 服务器IP
- [ ] www.alethealab.cn → 服务器IP

## 🎯 立即开始部署

### 步骤1：上传代码到服务器

在您当前的终端执行：

```bash
# 确保在正确目录
cd /Users/kepingwu/Desktop/alethea

# 上传代码（替换YOUR_SERVER_IP为实际IP地址）
./deploy/upload_to_server.sh YOUR_SERVER_IP
```

**示例**：
```bash
# 如果您的服务器IP是 123.456.789.123
./deploy/upload_to_server.sh 123.456.789.123
```

### 步骤2：连接到服务器

```bash
# 连接到服务器（替换为您的实际IP）
ssh root@YOUR_SERVER_IP

# 如果使用密钥文件
ssh -i /path/to/your-key.pem root@YOUR_SERVER_IP
```

### 步骤3：运行HTTP部署脚本

在服务器上执行：

```bash
# 进入应用目录
cd /home/alethea/alethea

# 运行HTTP版本部署脚本
./deploy/aliyun_http_deploy.sh
```

这个脚本会自动完成：
- ✅ 系统更新和软件安装
- ✅ Python环境配置
- ✅ Nginx配置
- ✅ 应用服务配置
- ✅ 防火墙配置
- ✅ 监控和备份设置

### 步骤4：配置API密钥

部署完成后，配置环境变量：

```bash
# 编辑配置文件
nano /home/alethea/alethea/.env

# 找到以下行并填入您的实际API密钥：
# OPENAI_API_KEY=your_openai_api_key_here
# CLAUDE_API_KEY=your_claude_api_key_here
# GEMINI_API_KEY=your_gemini_api_key_here

# 保存并退出（Ctrl+X, 然后Y, 然后Enter）

# 重启服务
systemctl restart alethea nginx
```

### 步骤5：验证部署

```bash
# 检查服务状态
systemctl status alethea
systemctl status nginx

# 测试网站
curl http://localhost/health
```

## 🌐 访问您的网站

部署完成后，访问：
- **http://alethealab.cn**
- **http://www.alethealab.cn**

## 🔧 如果遇到问题

### 常见问题排查

1. **上传代码失败**
```bash
# 检查SSH连接
ssh root@YOUR_SERVER_IP exit

# 检查网络连接
ping YOUR_SERVER_IP
```

2. **部署脚本失败**
```bash
# 查看详细错误
journalctl -u alethea -n 50

# 检查磁盘空间
df -h

# 检查内存
free -h
```

3. **网站无法访问**
```bash
# 检查域名解析
nslookup alethealab.cn

# 检查Nginx状态
systemctl status nginx

# 检查端口
netstat -tulpn | grep :80
```

## 📞 需要帮助？

如果在部署过程中遇到任何问题，请告诉我：

1. **具体的错误信息**
2. **执行到哪一步出现问题**
3. **服务器的系统信息**

我会立即帮您解决！

## 🎉 部署成功标志

当您看到以下信息时，说明部署成功：

```
=== Alethea HTTP版本部署完成 ===

网站地址 (HTTP):
  - http://alethealab.cn
  - http://www.alethealab.cn

HTTP版本部署完成！请访问 http://alethealab.cn 查看网站
```

## 🚀 开始部署吧！

现在就开始第一步：

```bash
# 在当前终端执行
./deploy/upload_to_server.sh YOUR_SERVER_IP
```

**请将 `YOUR_SERVER_IP` 替换为您的实际服务器IP地址！**
