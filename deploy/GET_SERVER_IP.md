# 如何获取阿里云服务器IP地址

## 🔍 方法一：通过阿里云控制台查看（推荐）

### 步骤1：登录阿里云控制台
1. 打开浏览器，访问：https://ecs.console.aliyun.com
2. 使用您的阿里云账号登录

### 步骤2：查看ECS实例
1. 在左侧菜单中点击 **"实例与镜像"** → **"实例"**
2. 您会看到您的服务器列表

### 步骤3：找到IP地址
在实例列表中，您会看到两个IP地址：
- **公网IP**：用于外网访问（这是我们需要的）
- **私网IP**：用于内网通信

**示例**：
```
实例名称: alethea-server
公网IP: 123.456.789.123  ← 这就是我们需要的IP
私网IP: 172.16.0.100
```

## 🔍 方法二：通过阿里云手机APP查看

1. 下载 **"阿里云"** 手机APP
2. 登录您的账号
3. 点击 **"云服务器ECS"**
4. 查看实例详情，找到公网IP

## 🔍 方法三：如果您已经连接过服务器

如果您之前连接过服务器，可以查看：

### 查看SSH历史记录
```bash
# 在Mac终端查看SSH历史
history | grep ssh

# 或查看known_hosts文件
cat ~/.ssh/known_hosts
```

### 查看终端历史
在您的终端中按 **↑** 键查看之前执行过的命令，可能会找到之前的SSH连接命令。

## 🔍 方法四：通过域名反查（如果已配置域名解析）

```bash
# 如果您已经配置了域名解析
nslookup alethealab.cn
# 或
ping alethealab.cn
```

## 📋 获取IP后的操作

找到您的服务器IP后，记录下来：

**您的服务器IP：** `_______________`

然后执行部署命令：

```bash
# 在当前目录执行（替换为您的实际IP）
./deploy/upload_to_server.sh 您的服务器IP
```

**示例**：
```bash
# 如果您的IP是 123.456.789.123
./deploy/upload_to_server.sh 123.456.789.123
```

## 🚨 常见问题

### 问题1：找不到ECS实例
- 检查是否选择了正确的地域（华东1、华北1等）
- 确认实例是否已创建并运行中

### 问题2：没有公网IP
- 如果实例没有公网IP，需要：
  1. 停止实例
  2. 升级配置，添加公网IP
  3. 或者购买弹性公网IP并绑定

### 问题3：IP地址变化
- 如果使用的是动态公网IP，重启后可能会变化
- 建议购买固定公网IP（弹性公网IP）

## 🔧 如果没有服务器或找不到IP

### 情况1：还没有购买服务器
请参考：`deploy/ALIYUN_SERVER_SETUP.md` 购买指南

### 情况2：服务器在其他云平台
- 腾讯云：https://console.cloud.tencent.com/cvm
- 华为云：https://console.huaweicloud.com/ecm
- AWS：https://console.aws.amazon.com/ec2

## 📞 需要帮助？

如果您在查找IP地址时遇到困难，请告诉我：

1. **您使用的是哪个云平台？**（阿里云/腾讯云/华为云/其他）
2. **您能否访问云平台控制台？**
3. **您的服务器是什么时候创建的？**

我可以提供更具体的指导！

## 🎯 下一步

找到IP地址后，继续执行部署：

```bash
# 1. 上传代码
./deploy/upload_to_server.sh YOUR_SERVER_IP

# 2. 连接服务器
ssh root@YOUR_SERVER_IP

# 3. 运行部署脚本
cd /home/alethea/alethea
./deploy/aliyun_http_deploy.sh
```

**记住：我们需要的是公网IP，不是私网IP！**
