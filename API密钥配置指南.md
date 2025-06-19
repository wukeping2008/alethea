# Alethea平台API密钥配置指南

## 概述

Alethea平台支持多个AI提供商，为确保AI功能正常运行，需要正确配置API密钥。本指南详细说明了在发布后如何配置API密钥。

## 配置文件位置

### 主要配置文件
- **位置**: `src/config.json`
- **作用**: 存储所有AI提供商的API密钥和配置信息
- **重要性**: 这是系统运行的核心配置文件

### 配置文件优先级
1. **src/config.json** - 主配置文件（优先级最高）
2. **环境变量** - 系统环境变量（备用方案）
3. **默认配置** - 代码中的默认值（最低优先级）

## 支持的AI提供商

### 1. Claude (Anthropic)
```json
"claude": {
    "api_key": "sk-ant-api03-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "default_model": "claude-3-sonnet-20240229"
}
```
- **获取方式**: https://console.anthropic.com/
- **推荐模型**: claude-3-sonnet-20240229, claude-3-haiku-20240307
- **特点**: 高质量回答，适合复杂推理

### 2. Google Gemini
```json
"gemini": {
    "api_key": "AIzaSyxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "default_model": "gemini-1.5-flash"
}
```
- **获取方式**: https://makersuite.google.com/app/apikey
- **推荐模型**: gemini-1.5-flash, gemini-1.5-pro
- **特点**: 快速响应，多模态支持

### 3. 火山引擎DeepSeek
```json
"volces_deepseek": {
    "api_key": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "base_url": "https://ark.cn-beijing.volces.com/api/v3/chat/completions",
    "default_model": "deepseek-r1-250528",
    "max_tokens": 16191
}
```
- **获取方式**: https://console.volcengine.com/ark
- **推荐模型**: deepseek-r1-250528
- **特点**: 中文优化，推理能力强

### 4. 阿里云通义千问Plus
```json
"qwen_plus": {
    "api_key": "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
    "default_model": "qwen-plus-2025-04-28",
    "max_tokens": 16191
}
```
- **获取方式**: https://dashscope.aliyuncs.com/
- **推荐模型**: qwen-plus-2025-04-28
- **特点**: 中文理解优秀，成本较低

### 5. OpenAI (可选)
```json
"openai": {
    "api_key": "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "default_model": "gpt-4o"
}
```
- **获取方式**: https://platform.openai.com/api-keys
- **推荐模型**: gpt-4o, gpt-3.5-turbo
- **特点**: 通用性强，但需要科学上网

## 配置步骤

### 方法一：直接编辑配置文件（推荐）

1. **定位配置文件**
   ```bash
   cd /path/to/alethea
   ls src/config.json
   ```

2. **编辑配置文件**
   ```bash
   nano src/config.json
   # 或使用其他编辑器
   vim src/config.json
   ```

3. **完整配置示例**
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

4. **设置默认提供商**
   - 修改 `"default_provider"` 字段
   - 推荐设置为您有有效API密钥的提供商
   - 建议优先级：gemini > volces_deepseek > qwen_plus > claude

### 方法二：使用环境变量

如果不想直接编辑配置文件，可以设置环境变量：

```bash
# Claude
export CLAUDE_API_KEY="your-claude-api-key"

# Gemini
export GEMINI_API_KEY="your-gemini-api-key"

# 火山引擎DeepSeek
export VOLCES_DEEPSEEK_API_KEY="your-volces-deepseek-api-key"

# 阿里云通义千问
export ALI_QWEN_API_KEY="your-qwen-plus-api-key"

# 设置默认提供商
export DEFAULT_LLM_PROVIDER="gemini"
```

## 最小配置要求

### 基础运行（至少需要1个）
为了确保AI功能正常，**至少需要配置以下任意一个提供商**：

1. **Gemini** (推荐 - 免费额度较高)
2. **火山引擎DeepSeek** (推荐 - 中文优化)
3. **阿里云通义千问Plus** (推荐 - 成本较低)
4. **Claude** (高质量但成本较高)

### 推荐配置（多提供商备用）
```json
{
    "gemini": {
        "api_key": "your-gemini-api-key",
        "default_model": "gemini-1.5-flash"
    },
    "volces_deepseek": {
        "api_key": "your-volces-deepseek-api-key",
        "base_url": "https://ark.cn-beijing.volces.com/api/v3/chat/completions",
        "default_model": "deepseek-r1-250528",
        "max_tokens": 16191
    },
    "default_provider": "gemini"
}
```

## 验证配置

### 1. 重启应用
```bash
# 停止应用
pkill -f "python.*main.py"

# 启动应用
cd /path/to/alethea
python src/main.py
```

### 2. 检查启动日志
启动时会显示配置状态：
```
Loading configuration from /path/to/alethea/src/config.json
Configuration loaded successfully. Default provider: gemini
Provider claude: ✗ API key configured
Provider gemini: ✓ API key configured
Provider volces_deepseek: ✓ API key configured
Provider qwen_plus: ✗ API key configured
```

### 3. 测试AI功能
1. 访问平台：http://your-server:8083
2. 在问答界面输入测试问题
3. 检查是否能正常获得AI回答

## 故障排除

### 常见问题

#### 1. "Provider xxx: ✗ API key configured"
**原因**: API密钥未配置或格式错误
**解决方案**:
- 检查 `src/config.json` 中对应提供商的 `api_key` 字段
- 确保API密钥格式正确，没有多余的空格或换行
- 验证API密钥是否有效

#### 2. "AI服务暂时不可用"
**原因**: 所有配置的提供商都无法使用
**解决方案**:
- 检查网络连接
- 验证API密钥是否过期
- 检查API配额是否用完
- 确保至少有一个提供商配置正确

#### 3. "Config file not found"
**原因**: 配置文件不存在
**解决方案**:
```bash
# 复制示例配置文件
cp src/config.json.example src/config.json
# 然后编辑添加真实的API密钥
```

#### 4. JSON格式错误
**原因**: 配置文件JSON格式不正确
**解决方案**:
- 使用JSON验证工具检查格式
- 确保所有字符串都用双引号包围
- 检查逗号和括号是否匹配

### 调试命令

```bash
# 检查配置文件是否存在
ls -la src/config.json

# 验证JSON格式
python -m json.tool src/config.json

# 查看应用日志
tail -f /var/log/alethea.log

# 测试网络连接
curl -I https://api.anthropic.com
curl -I https://generativelanguage.googleapis.com
```

## 安全建议

### 1. 文件权限
```bash
# 设置配置文件权限，只有所有者可读写
chmod 600 src/config.json
```

### 2. 备份配置
```bash
# 备份配置文件
cp src/config.json src/config.json.backup.$(date +%Y%m%d)
```

### 3. 定期轮换密钥
- 建议每3-6个月更换一次API密钥
- 监控API使用情况，发现异常及时处理

### 4. 环境隔离
- 生产环境和测试环境使用不同的API密钥
- 避免在日志中记录API密钥

## 成本优化建议

### 1. 提供商选择
- **Gemini**: 免费额度较高，适合初期使用
- **火山引擎DeepSeek**: 中文场景性价比高
- **阿里云通义千问**: 成本较低，适合大量使用

### 2. 智能降级
平台已实现智能降级机制：
1. 主要提供商失败 → 备用提供商
2. 所有云端提供商失败 → 本地模型（如果配置）
3. 所有AI失败 → 预定义模板内容

### 3. 缓存优化
平台已实现智能缓存：
- 相同问题24小时内直接返回缓存结果
- 减少API调用次数，降低成本

## 联系支持

如果遇到配置问题，可以：
1. 查看项目GitHub Issues
2. 参考 `CONFIG_SETUP.md` 文档
3. 检查应用启动日志
4. 联系技术支持团队

---

**最后更新**: 2025年6月19日
**版本**: v1.0
