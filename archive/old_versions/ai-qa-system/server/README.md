# 知识库管理后端服务

这是简仪科技AI问答系统的知识库管理后端服务。它提供了文档上传、管理和知识库更新的功能。

## 功能特点

- 支持上传PDF、Word和TXT文档
- 自动提取文档内容并更新知识库
- 文档管理（上传、删除、搜索）
- 与Ollama API集成
- CORS支持，可与前端无缝集成

## 安装步骤

1. 确保已安装Python 3.8+
2. 安装依赖包：
```bash
pip install -r requirements.txt
```

## 启动服务

```bash
python main.py
```
服务将在 http://localhost:8000 启动

## API接口

### 文档管理
- GET /api/documents - 获取所有文档列表
- POST /api/upload - 上传新文档
- DELETE /api/documents/{doc_id} - 删除指定文档
- GET /api/documents/search?q={query} - 搜索文档

### 文件格式支持
- PDF (.pdf)
- Word (.docx)
- 文本文件 (.txt)

## 文件存储

- 上传的文件存储在 `uploads` 目录
- 文档信息存储在 `knowledge_base.json`
- 知识库内容自动更新到 `config/api.json`

## 注意事项

1. 首次运行时会自动创建必要的目录和文件
2. 上传大文件时请注意服务器性能和存储空间
3. 建议定期备份知识库文件
4. 文档上传后会自动更新到AI问答系统的知识库中

## 错误处理

- 如果遇到文件上传失败，检查文件格式是否支持
- 如果知识库更新失败，检查配置文件权限
- 服务启动失败时，检查端口是否被占用

## 安全建议

- 在生产环境中建议配置适当的认证机制
- 限制上传文件的大小
- 定期清理不需要的文档
- 配置防火墙规则
