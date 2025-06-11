# Ollama DeepSeek 本地集成说明

## 🎉 集成完成

Alethea Enhanced 项目已成功集成本地 Ollama DeepSeek 模型支持！

## 🚀 功能特性

### 智能模型选择
系统会根据问题内容自动选择最适合的 AI 模型：

- **代码/编程问题** → 优先使用本地 Ollama DeepSeek
- **数学/计算问题** → 优先使用本地 Ollama DeepSeek  
- **中文学科问题** → 按学科权重选择云端专业模型
- **其他问题** → 使用 Claude 或 Gemini 云端模型
- **无网络环境** → 自动降级到本地 Ollama DeepSeek

### 本地优势
- ✅ **零成本**：本地运行，无 API 调用费用
- ✅ **隐私保护**：数据不离开本地环境
- ✅ **快速响应**：无网络延迟，响应更快
- ✅ **中文优化**：DeepSeek 对中文支持优秀
- ✅ **代码专精**：DeepSeek-Coder 专门优化代码生成

## 📋 当前状态

### 已安装的 DeepSeek 模型
```
✅ deepseek-coder:latest (0.7 GB) - 代码生成专用
✅ deepseek-r1:7b (4.4 GB) - 通用推理模型  
✅ deepseek-r1:latest (4.4 GB) - 最新版本
```

### 系统配置
- **Ollama 服务地址**: http://localhost:11434
- **默认模型**: deepseek-r1:7b
- **集成状态**: ✅ 已激活并正常工作

## 🔧 使用方法

### 自动模式（推荐）
系统会自动检测问题类型并选择最佳模型：

```python
# 中文 + 代码问题 → 自动选择 Ollama DeepSeek
"请用Python编写一个快速排序算法的代码实现"

# 数学问题 → 自动选择 Ollama DeepSeek  
"如何计算矩阵的特征值和特征向量？"

# 一般问题 → 使用云端模型
"What is the capital of France?"
```

### 手动指定模型
如果需要强制使用特定模型：

```python
# 在 API 调用中指定 provider
response = await llm_manager.generate_response(
    prompt="你的问题",
    provider="ollama_deepseek"
)
```

## 📊 性能对比

| 特性 | Ollama DeepSeek | 云端模型 |
|------|----------------|----------|
| 成本 | 免费 | 按使用付费 |
| 隐私 | 完全本地 | 数据上传云端 |
| 速度 | 快速（本地） | 依赖网络 |
| 中文支持 | 优秀 | 良好 |
| 代码生成 | 专业 | 良好 |
| 复杂推理 | 良好 | 优秀 |

## 🛠️ 测试工具

项目包含了专门的测试脚本：

```bash
# 运行连接测试
python test_ollama_deepseek.py
```

测试内容：
- ✅ Ollama 服务连接状态
- ✅ DeepSeek 模型可用性
- ✅ 模型生成功能测试

## 📈 使用统计

系统会在日志中显示模型选择信息：

```
INFO:models.llm_models:Detected characteristics: ['code', 'chinese', 'general']
INFO:models.llm_models:Selected Ollama DeepSeek for Chinese/code/math content
INFO:models.llm_models:Auto-selected provider: ollama_deepseek, model: deepseek-r1:7b
```

## 🔍 故障排除

### 如果 Ollama DeepSeek 不可用
系统会自动降级到云端模型，并在日志中显示：

```
INFO:models.llm_models:Ollama DeepSeek not available, falling back to other providers
```

### 常见问题解决

1. **Ollama 服务未启动**
   ```bash
   ollama serve
   ```

2. **模型未安装**
   ```bash
   ollama pull deepseek-r1:7b
   ollama pull deepseek-coder:latest
   ```

3. **端口冲突**
   - 检查 11434 端口是否被占用
   - 修改配置文件中的 base_url

## 🎯 最佳实践

### 推荐使用场景
- **编程学习**：代码解释、算法实现、调试帮助
- **中文问答**：学术问题、技术讨论、概念解释  
- **数学计算**：公式推导、问题求解、概念理解
- **本地开发**：离线环境、隐私敏感项目

### 性能优化建议
- 使用 `deepseek-coder:latest` 处理代码相关问题
- 使用 `deepseek-r1:7b` 处理一般推理问题
- 复杂学术问题可考虑使用云端 Claude 模型

## 🔄 配置管理

### 修改默认模型
编辑 `src/config.json`：

```json
{
  "ollama_deepseek": {
    "base_url": "http://localhost:11434",
    "default_model": "deepseek-coder:latest"
  }
}
```

### 调整选择策略
修改 `src/models/llm_models.py` 中的 `select_model` 方法。

## 🎊 总结

Ollama DeepSeek 集成为 Alethea Enhanced 带来了：

- 🆓 **零成本运行**：本地模型无需 API 费用
- 🔒 **隐私保护**：数据完全本地处理
- 🚀 **性能提升**：中文和代码问题响应更快更准确
- 🧠 **智能选择**：自动选择最适合的模型
- 🛡️ **稳定可靠**：云端模型作为备选方案

现在您可以享受本地 AI 模型带来的高效、安全、经济的问答体验！
