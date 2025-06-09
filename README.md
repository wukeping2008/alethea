# Alethea - AI个性化教学平台

<div align="center">

![Alethea Logo](src/static/logo.png)

**基于人工智能的个性化教学平台，专为高等教育理工科师生打造**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-2.x-green.svg)](https://flask.palletsprojects.com/)
[![GitHub stars](https://img.shields.io/github/stars/wukeping2008/alethea.svg)](https://github.com/wukeping2008/alethea/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/wukeping2008/alethea.svg)](https://github.com/wukeping2008/alethea/network)

[English](README_EN.md) | 简体中文

</div>

## 🌟 项目简介

Alethea 是一个功能强大的AI驱动个性化教学平台，集成了多种先进的大语言模型，为高等教育特别是理工科教学提供智能化解决方案。平台通过AI技术实现个性化学习分析、智能问答、项目推荐等功能，旨在提升教学效率和学习体验。

### ✨ 核心特性

- 🤖 **多模型AI集成** - 支持OpenAI、Claude、Gemini、DeepSeek等多种AI模型
- 📊 **个性化学习分析** - AI驱动的学习行为分析和数字画像生成
- 💡 **智能项目推荐** - 基于用户画像的个性化学习内容推荐
- 🔬 **在线实验仿真** - 虚拟实验室和电路仿真功能
- 🧠 **知识图谱系统** - 个人知识点掌握度可视化
- 🌍 **多语言支持** - 中英文双语界面和内容
- 📱 **响应式设计** - 完美适配桌面端和移动端

## 🚀 快速开始

### 环境要求

- Python 3.9+
- Flask 2.x
- SQLAlchemy
- 现代浏览器 (Chrome, Firefox, Safari, Edge)

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/wukeping2008/alethea.git
cd alethea
```

2. **创建虚拟环境**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **配置环境变量**
```bash
cp .env.example .env
# 编辑 .env 文件，配置数据库和API密钥
```

5. **初始化数据库**
```bash
python -c "from src.main import app, db; app.app_context().push(); db.create_all()"
```

6. **启动应用**
```bash
python src/main.py
```

7. **访问应用**
打开浏览器访问 `http://localhost:5000`

## 📖 功能文档

### 核心功能模块

#### 🤖 智能问答系统
- **多AI提供商支持**: OpenAI GPT-4, Claude-3, Gemini Pro, DeepSeek等
- **智能模型选择**: 根据问题类型自动选择最适合的AI模型
- **专业化问答**: 针对电工电子、电路分析等理工科专业优化
- **数学公式渲染**: 支持LaTeX格式数学公式显示
- **代码高亮**: 自动识别和高亮代码片段

#### 📊 个性化学习分析
- **学习行为追踪**: 自动记录和分析用户学习行为
- **数字画像生成**: AI分析生成个性化学习特征画像
- **学习分析仪表板**: 可视化展示学习进度和成果
- **知识点掌握度**: 基于行为数据计算知识点掌握程度

#### 💡 智能推荐系统
- **个性化项目推荐**: 基于用户画像推荐适合的学习项目
- **协同过滤算法**: 基于相似用户行为的推荐
- **内容过滤算法**: 基于项目内容和用户兴趣匹配
- **学习路径规划**: 构建个性化的学习路径

#### 🔬 实验仿真系统
- **虚拟实验室**: 在线电路搭建和仿真
- **丰富元件库**: 包含各种电子元件和测量工具
- **实验指导**: 分步骤实验操作指导
- **结果分析**: 实验数据分析和可视化

### 技术架构

```
┌─────────────────────────────────────────────────────────────┐
│                      Alethea 系统架构                       │
├─────────────────────────────────────────────────────────────┤
│  前端层 (Frontend)                                          │
│  ├── HTML/CSS/JavaScript                                   │
│  ├── Tailwind CSS                                          │
│  ├── Chart.js / MathJax                                    │
│  └── 响应式设计                                             │
├─────────────────────────────────────────────────────────────┤
│  应用层 (Application Layer)                                 │
│  ├── Flask Web框架                                         │
│  ├── RESTful API                                           │
│  ├── JWT身份认证                                           │
│  └── 路由管理                                              │
├─────────────────────────────────────────────────────────────┤
│  业务逻辑层 (Business Logic)                               │
│  ├── LLM模型管理                                           │
│  ├── 用户分析系统                                          │
│  ├── 推荐算法                                              │
│  └── 知识图谱                                              │
├─────────────────────────────────────────────────────────────┤
│  数据层 (Data Layer)                                       │
│  ├── SQLAlchemy ORM                                        │
│  ├── SQLite/PostgreSQL                                     │
│  └── 数据模型                                              │
└─────────────────────────────────────────────────────────────┘
```

## 🛠️ 开发指南

### 项目结构

```
alethea/
├── src/                    # 源代码目录
│   ├── models/            # 数据模型
│   │   ├── user.py        # 用户模型
│   │   ├── subject.py     # 学科模型
│   │   ├── llm_models.py  # LLM模型管理
│   │   └── ...
│   ├── routes/            # 路由控制器
│   │   ├── user.py        # 用户路由
│   │   ├── llm_routes.py  # LLM路由
│   │   └── ...
│   ├── static/            # 静态文件
│   │   ├── css/           # 样式文件
│   │   ├── js/            # JavaScript文件
│   │   └── images/        # 图片资源
│   └── main.py           # 主应用入口
├── tests/                 # 测试文件
├── docs/                  # 文档目录
├── requirements.txt       # 依赖列表
├── .env.example          # 环境变量示例
├── .gitignore            # Git忽略文件
└── README.md             # 项目说明
```

### 开发环境设置

1. **安装开发依赖**
```bash
pip install -r requirements-dev.txt
```

2. **代码格式化**
```bash
black src/
flake8 src/
```

3. **运行测试**
```bash
python -m pytest tests/
```

### API文档

详细的API文档请参考 [API Documentation](docs/API.md)

主要API端点：

- `POST /api/auth/login` - 用户登录
- `POST /api/auth/register` - 用户注册
- `POST /api/llm/ask` - AI问答
- `GET /api/analytics/dashboard` - 学习分析数据
- `GET /api/analytics/recommendations` - 获取推荐内容

## 🤝 贡献指南

我们欢迎所有形式的贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详细信息。

### 贡献流程

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

### 开发规范

- 遵循 PEP 8 Python代码规范
- 编写清晰的提交信息
- 添加适当的测试用例
- 更新相关文档

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [OpenAI](https://openai.com/) - GPT模型支持
- [Anthropic](https://www.anthropic.com/) - Claude模型支持
- [Google](https://ai.google/) - Gemini模型支持
- [Flask](https://flask.palletsprojects.com/) - Web框架
- [Tailwind CSS](https://tailwindcss.com/) - CSS框架

## 📞 联系我们

- **项目维护者**: [wukeping2008](https://github.com/wukeping2008)
- **项目主页**: [https://github.com/wukeping2008/alethea](https://github.com/wukeping2008/alethea)
- **问题反馈**: [Issues](https://github.com/wukeping2008/alethea/issues)

## 🌟 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=wukeping2008/alethea&type=Date)](https://star-history.com/#wukeping2008/alethea&Date)

---

<div align="center">

**如果这个项目对您有帮助，请给我们一个 ⭐️**

Made with ❤️ by [wukeping2008](https://github.com/wukeping2008)

</div>
