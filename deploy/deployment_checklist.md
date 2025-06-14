# Alethea 阿里云部署检查清单

## 部署前准备 ✅

### 1. 阿里云服务准备
- [ ] **ECS云服务器**
  - [ ] 已购买2核4GB内存配置
  - [ ] 已安装Ubuntu 20.04 LTS
  - [ ] 已配置VPC网络
  - [ ] 已设置安全组规则（22, 80, 443, 8083端口）
  - [ ] 已获取公网IP地址
  - [ ] 已配置SSH密钥或密码访问

- [ ] **RDS MySQL数据库**
  - [ ] 已创建MySQL 8.0实例
  - [ ] 已配置数据库用户名和密码
  - [ ] 已设置白名单（添加ECS内网IP）
  - [ ] 已创建数据库 `alethea`
  - [ ] 已测试连接

- [ ] **OSS对象存储**（可选）
  - [ ] 已创建OSS Bucket
  - [ ] 已配置访问权限
  - [ ] 已获取AccessKey和SecretKey
  - [ ] 已记录Endpoint地址

- [ ] **Redis缓存**（可选）
  - [ ] 已创建Redis实例
  - [ ] 已配置白名单
  - [ ] 已获取连接地址和密码

### 2. 域名和证书
- [ ] **域名准备**
  - [ ] 已购买域名
  - [ ] 已完成备案（如需要）
  - [ ] 已配置DNS解析到ECS公网IP

- [ ] **SSL证书**
  - [ ] 已申请SSL证书
  - [ ] 已下载证书文件
  - [ ] 已准备证书安装

### 3. API密钥准备
- [ ] **AI模型API**
  - [ ] OpenAI API Key
  - [ ] Anthropic API Key
  - [ ] Google Gemini API Key
  - [ ] DeepSeek API Key
  - [ ] 阿里云通义千问API Key

- [ ] **其他服务API**
  - [ ] 阿里云AccessKey和SecretKey
  - [ ] 邮件服务配置
  - [ ] 监控服务配置（如Sentry）

## 部署过程检查 ✅

### 1. 服务器连接
- [ ] 能够SSH连接到服务器
- [ ] 已创建应用用户 `alethea`
- [ ] 用户具有sudo权限

### 2. 代码部署
- [ ] 已克隆项目代码到 `/home/alethea/alethea`
- [ ] 已设置正确的文件权限
- [ ] 已创建Python虚拟环境
- [ ] 已安装所有依赖包

### 3. 环境配置
- [ ] 已复制并编辑 `.env` 文件
- [ ] 已配置数据库连接字符串
- [ ] 已设置所有必要的API密钥
- [ ] 已配置文件上传路径

### 4. 数据库初始化
- [ ] 数据库连接测试成功
- [ ] 数据表创建成功
- [ ] 初始数据导入完成

### 5. Web服务配置
- [ ] Nginx配置文件已部署
- [ ] Nginx配置测试通过
- [ ] Gunicorn配置正确
- [ ] Supervisor配置已部署

### 6. 服务启动
- [ ] Nginx服务运行正常
- [ ] Supervisor服务运行正常
- [ ] Alethea应用进程启动成功
- [ ] 所有服务设置为开机自启

## 部署后验证 ✅

### 1. 基本功能测试
- [ ] **网站访问**
  - [ ] HTTP访问正常
  - [ ] HTTPS访问正常
  - [ ] 主页加载正常
  - [ ] 静态资源加载正常

- [ ] **用户功能**
  - [ ] 用户注册功能正常
  - [ ] 用户登录功能正常
  - [ ] 用户信息显示正常

- [ ] **AI功能**
  - [ ] AI问答功能正常
  - [ ] 多个AI模型切换正常
  - [ ] 个性化功能正常

### 2. 性能测试
- [ ] 页面加载速度 < 3秒
- [ ] API响应时间 < 2秒
- [ ] 并发用户测试通过
- [ ] 内存使用率 < 80%
- [ ] CPU使用率 < 70%

### 3. 安全检查
- [ ] HTTPS强制跳转正常
- [ ] 安全头配置正确
- [ ] 敏感文件无法直接访问
- [ ] 防火墙规则正确
- [ ] 数据库访问限制正确

### 4. 监控和日志
- [ ] 应用日志正常记录
- [ ] Nginx访问日志正常
- [ ] 错误日志监控设置
- [ ] 系统监控配置完成

## 生产环境优化 ✅

### 1. 性能优化
- [ ] 启用Gzip压缩
- [ ] 配置静态文件缓存
- [ ] 数据库连接池优化
- [ ] Redis缓存配置

### 2. 安全加固
- [ ] 修改默认SSH端口
- [ ] 禁用root用户登录
- [ ] 配置fail2ban
- [ ] 设置定期安全更新

### 3. 备份策略
- [ ] 数据库自动备份配置
- [ ] 代码版本控制
- [ ] 配置文件备份
- [ ] 恢复流程测试

### 4. 监控告警
- [ ] 系统资源监控
- [ ] 应用性能监控
- [ ] 错误日志告警
- [ ] 可用性监控

## 维护计划 ✅

### 1. 定期维护
- [ ] 系统更新计划
- [ ] 依赖包更新计划
- [ ] 安全补丁计划
- [ ] 性能优化计划

### 2. 应急预案
- [ ] 故障处理流程
- [ ] 数据恢复流程
- [ ] 服务降级方案
- [ ] 联系人信息

## 部署命令快速参考

### 连接服务器
```bash
ssh alethea@your-server-ip
```

### 应用管理
```bash
# 重启应用
sudo supervisorctl restart alethea

# 查看状态
sudo supervisorctl status

# 查看日志
tail -f /var/log/alethea/supervisor.log
```

### 服务管理
```bash
# 重启Nginx
sudo systemctl restart nginx

# 查看Nginx状态
sudo systemctl status nginx

# 测试Nginx配置
sudo nginx -t
```

### 数据库操作
```bash
# 连接数据库
mysql -h rds-host -u username -p

# 备份数据库
mysqldump -h rds-host -u username -p alethea > backup.sql
```

### 日志查看
```bash
# 应用日志
tail -f /var/log/alethea/gunicorn_error.log

# Nginx日志
tail -f /var/log/nginx/alethea_error.log

# 系统日志
tail -f /var/log/syslog
```

## 常见问题解决

### 1. 应用无法启动
```bash
# 检查配置文件
cat .env

# 检查Python环境
source venv/bin/activate
python -c "import src.main"

# 查看详细错误
sudo supervisorctl tail alethea stderr
```

### 2. 数据库连接失败
```bash
# 测试数据库连接
mysql -h rds-host -u username -p -e "SELECT 1"

# 检查网络连通性
telnet rds-host 3306
```

### 3. 静态文件404
```bash
# 检查文件权限
ls -la /home/alethea/alethea/src/static/

# 检查Nginx配置
sudo nginx -t
```

---

**部署完成后，请保存此检查清单作为运维参考文档。**
