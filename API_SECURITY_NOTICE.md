# 🔐 API密钥安全配置说明

## ⚠️ 重要安全提醒

**请务必注意：API密钥是敏感信息，绝对不能上传到GitHub或其他公共代码仓库！**

## 📋 安全配置步骤

### 1. 配置API密钥

1. 复制 `src/config.json.example` 为 `src/config.json`：
   ```bash
   cp src/config.json.example src/config.json
   ```

2. 编辑 `src/config.json` 文件，将占位符替换为真实的API密钥：
   ```json
   {
       "claude": {
           "api_key": "sk-ant-api03-your-real-claude-key-here",
           "default_model": "claude-3-sonnet-20240229"
       },
       "gemini": {
           "api_key": "AIzaSy-your-real-gemini-key-here",
           "default_model": "gemini-1.5-flash"
       }
   }
   ```

### 2. 验证安全配置

确保以下文件在 `.gitignore` 中：
- `src/config.json`
- `.env`
- `*.pem`
- `secrets.json`

### 3. 检查Git状态

在提交代码前，务必检查：
```bash
git status
git ls-files | grep config.json
```

确保 `src/config.json` 不在Git跟踪列表中。

## 🛡️ 安全最佳实践

1. **永远不要**将真实API密钥提交到版本控制系统
2. **使用环境变量**或配置文件来存储敏感信息
3. **定期轮换**API密钥
4. **限制API密钥权限**，只授予必要的访问权限
5. **监控API使用情况**，及时发现异常调用

## 🔄 如果密钥已泄露

如果不小心将API密钥上传到了公共仓库：

1. **立即撤销**泄露的API密钥
2. **生成新的**API密钥
3. **更新配置**文件
4. **清理Git历史**（如果需要）

## 📞 获取API密钥

- **Claude**: https://console.anthropic.com/
- **Gemini**: https://makersuite.google.com/app/apikey
- **DeepSeek**: https://platform.deepseek.com/
- **通义千问**: https://dashscope.aliyuncs.com/

## ✅ 配置验证

启动应用后，检查控制台输出：
```
Provider claude: ✓ API key configured
Provider gemini: ✓ API key configured
```

看到 ✓ 表示配置成功，✗ 表示需要配置API密钥。
