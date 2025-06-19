# Alethea平台配置设置指南

## 配置文件说明

为了保护API密钥安全，项目采用以下配置文件管理策略：

### 文件结构
- `src/config.json` - Git仓库中的模板文件（不包含真实API密钥）
- `src/config.json.local` - 本地配置文件（包含真实API密钥，不会推送到Git）
- `src/config.json.example` - 配置示例文件

### 本地开发设置

1. **复制本地配置文件**：
   ```bash
   cp src/config.json.local src/config.json
   ```

2. **或者手动配置API密钥**：
   编辑 `src/config.json` 文件，添加您的API密钥：
   ```json
   {
       "claude": {
           "api_key": "your-claude-api-key-here",
           "default_model": "claude-3-sonnet-20240229"
       },
       "gemini": {
           "api_key": "your-gemini-api-key-here",
           "default_model": "gemini-1.5-flash"
       },
       "volces_deepseek": {
           "api_key": "your-volces-deepseek-api-key-here",
           "base_url": "https://ark.cn-beijing.volces.com/api/v3/chat/completions",
           "default_model": "deepseek-r1-250528",
           "max_tokens": 16191
       },
       "qwen_plus": {
           "api_key": "your-qwen-plus-api-key-here",
           "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
           "default_model": "qwen-plus-2025-04-28",
           "max_tokens": 16191
       },
       "default_provider": "gemini"
   }
   ```

### 安全注意事项

⚠️ **重要提醒**：
- 永远不要将包含真实API密钥的配置文件推送到Git仓库
- `src/config.json.local` 和 `*.pem` 文件已被添加到 `.gitignore` 中
- 在生产环境中，建议使用环境变量或密钥管理服务

### 部署配置

在服务器部署时：
1. 手动创建 `src/config.json` 文件
2. 添加生产环境的API密钥
3. 确保文件权限设置正确：`chmod 600 src/config.json`

### 故障排除

如果遇到API密钥相关错误：
1. 检查 `src/config.json` 文件是否存在
2. 确认API密钥格式正确
3. 验证API密钥是否有效且有足够的配额

---
*最后更新：2025年6月19日*
