# Alethea HTTP版本快速部署操作指南

## 🚨 重要说明

`./deploy/aliyun_http_deploy.sh` 脚本需要在**阿里云服务器**上运行，不是在本地Mac上运行。

## 🎯 正确的部署步骤

### 第一步：准备阿里云服务器

1. **购买ECS服务器**
   - 登录阿里云控制台：https://ecs.console.aliyun.com
   - 创建Ubuntu 20.04服务器（1核2GB即可）
   - 配置安全组：开放22、80、8083端口

2. **配置域名解析**
   - 在阿里云DNS控制台
   - 将 `alethealab.cn` 和 `www.alethealab.cn` 解析到服务器IP

### 第二步：在本地上传代码

```bash
# 在本地Mac终端执行
cd /Users/kepingwu/Desktop/alethea

# 上传代码到服务器（替换YOUR_SERVER_IP为实际IP）
./deploy/upload_to_server.sh YOUR_SERVER_IP
```

### 第三步：在服务器上运行部署脚本

```bash
# 1. 连接到阿里云服务器
ssh root@YOUR_SERVER_IP

# 2. 进入应用目录
cd /home/alethea/alethea

# 3. 运行HTTP部署脚本
./deploy/aliyun_http_deploy.sh
```

### 第四步：配置环境变量

```bash
# 在服务器上编辑配置文件
nano /home/alethea/alethea/.env

# 配置AI API密钥等参数，然后保存退出

# 重启服务
systemctl restart alethea nginx
```

### 第五步：访问网站

- http://alethealab.cn
- http://www.alethealab.cn

## 🔧 如果您还没有阿里云服务器

### 方案1：购买阿里云ECS

1. **访问阿里云官网**：https://www.aliyun.com
2. **选择云服务器ECS**
3. **推荐配置**：
   - 地域：华东1（杭州）
   - 实例规格：1核2GB
   - 镜像：Ubuntu 20.04 64位
   - 存储：40GB高效云盘
   - 带宽：1-5Mbps

### 方案2：使用其他云服务商

如果不想使用阿里云，也可以使用：
- 腾讯云
- 华为云
- AWS
- 或其他VPS服务商

## 🖥️ 本地测试版本

如果您想先在本地测试，可以运行：

```bash
# 在本地启动开发服务器
cd /Users/kepingwu/Desktop/alethea
python3 src/main.py

# 然后访问 http://localhost:5000
```

## 📞 需要帮助？

如果您需要：
1. **阿里云服务器购买指导**
2. **域名解析配置帮助**
3. **部署过程技术支持**

请告诉我您的具体情况，我可以提供更详细的指导。

## 🎯 总结

- ✅ `aliyun_http_deploy.sh` 是服务器端脚本
- ✅ 需要先有阿里云服务器
- ✅ 需要配置域名解析
- ✅ 本地只需运行 `upload_to_server.sh`
- ✅ 服务器端运行 `aliyun_http_deploy.sh`

**请先准备好阿里云服务器，然后按照上述步骤操作！**
