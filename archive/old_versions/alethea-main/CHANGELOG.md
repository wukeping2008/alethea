# 更新日志 / Changelog

所有重要的项目变更都会记录在这个文件中。

All notable changes to this project will be documented in this file.

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
并且本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [未发布 / Unreleased]

### 新增 / Added
- 初始项目结构和核心功能
- 多AI模型集成支持
- 个性化学习分析系统
- 智能项目推荐算法
- 在线实验仿真功能
- 知识图谱系统
- 用户认证和权限管理
- 响应式Web界面
- 中英文双语支持

### 变更 / Changed
- 无

### 已弃用 / Deprecated
- 无

### 移除 / Removed
- 无

### 修复 / Fixed
- 无

### 安全性 / Security
- 实现JWT身份认证
- 添加输入验证和过滤
- 密码加密存储

## [1.0.0] - 2025-06-09

### 新增 / Added
- 🎉 **首次发布** / **Initial Release**
- 🤖 **多模型AI集成** / **Multi-Model AI Integration**
  - OpenAI GPT-4 支持
  - Anthropic Claude-3 支持
  - Google Gemini Pro 支持
  - DeepSeek Chat 支持
  - 阿里通义千问支持
  - 火山引擎豆包支持
  - 本地Ollama模型支持
  - 智能模型选择算法
  - 负载均衡和容错机制

- 📊 **个性化学习分析** / **Personalized Learning Analytics**
  - 学习行为自动追踪
  - AI驱动的数字画像生成
  - 学习分析仪表板
  - 知识点掌握度计算
  - 学习进度可视化
  - 个性特征评估

- 💡 **智能推荐系统** / **Intelligent Recommendation System**
  - 协同过滤算法
  - 内容过滤算法
  - 混合推荐策略
  - 个性化项目推荐
  - 学习路径规划
  - 难度自适应匹配

- 🔬 **在线实验仿真** / **Online Experiment Simulation**
  - 虚拟电路实验室
  - 丰富的电子元件库
  - 虚拟测量工具
  - 分步实验指导
  - 实验数据分析
  - 结果可视化

- 🧠 **知识图谱系统** / **Knowledge Graph System**
  - 知识点关联管理
  - 个人知识图谱
  - 掌握度可视化
  - 薄弱环节识别
  - 学习建议生成
  - 知识网络构建

- 👤 **用户管理系统** / **User Management System**
  - 用户注册和登录
  - JWT安全认证
  - 多角色权限控制
  - 个人资料管理
  - 学习偏好设置
  - 隐私控制选项

- 🌐 **Web界面** / **Web Interface**
  - 响应式设计
  - 现代化UI/UX
  - Tailwind CSS样式
  - 移动端适配
  - 交互式图表
  - 实时数据更新

- 🌍 **国际化支持** / **Internationalization**
  - 中英文双语界面
  - 多语言内容支持
  - 本地化格式
  - 语言自动检测
  - 一键语言切换

- 📱 **技术特性** / **Technical Features**
  - Flask Web框架
  - SQLAlchemy ORM
  - RESTful API设计
  - 数学公式渲染 (MathJax)
  - 代码语法高亮
  - 图表可视化 (Chart.js)
  - 模块化架构
  - 可扩展设计

- 📚 **学科支持** / **Subject Support**
  - 电工电子实验
  - 电路分析
  - 模拟电子技术
  - 数字电子技术
  - 电力电子技术
  - 自动控制原理
  - 机器学习
  - 深度学习

- 🛠️ **开发工具** / **Development Tools**
  - 完整的开发环境配置
  - 代码质量检查工具
  - 自动化测试框架
  - 文档生成工具
  - 部署脚本
  - 开发者指南

### 技术规格 / Technical Specifications
- **后端**: Python 3.9+, Flask 2.x, SQLAlchemy
- **前端**: HTML5, CSS3, JavaScript ES6+, Tailwind CSS
- **数据库**: SQLite (开发) / PostgreSQL (生产)
- **AI集成**: 多提供商API集成
- **认证**: JWT Token
- **部署**: Docker支持, 云平台兼容

### 性能指标 / Performance Metrics
- **代码量**: 28,298 行
- **响应时间**: < 2秒 (页面加载)
- **API响应**: < 500ms
- **并发支持**: 10-50 用户
- **浏览器兼容**: Chrome, Firefox, Safari, Edge

### 安全特性 / Security Features
- JWT身份认证
- 密码加密存储 (BCrypt)
- 输入验证和过滤
- SQL注入防护
- XSS防护
- CSRF防护
- 会话管理
- 权限控制

---

## 版本说明 / Version Notes

### 版本命名规则 / Version Naming Convention
- **主版本号 / Major**: 不兼容的API修改
- **次版本号 / Minor**: 向下兼容的功能性新增
- **修订号 / Patch**: 向下兼容的问题修正

### 发布周期 / Release Cycle
- **主版本**: 每年1-2次
- **次版本**: 每季度1次
- **修订版本**: 根据需要发布

### 支持政策 / Support Policy
- **当前版本**: 完全支持
- **前一版本**: 安全更新
- **更早版本**: 不再支持

---

## 贡献者 / Contributors

感谢所有为 Alethea 项目做出贡献的开发者！

Thanks to all the developers who contributed to the Alethea project!

- [wukeping2008](https://github.com/wukeping2008) - 项目创建者和维护者 / Project Creator & Maintainer

---

## 链接 / Links

- **项目主页 / Homepage**: [https://github.com/wukeping2008/alethea](https://github.com/wukeping2008/alethea)
- **问题反馈 / Issues**: [https://github.com/wukeping2008/alethea/issues](https://github.com/wukeping2008/alethea/issues)
- **发布页面 / Releases**: [https://github.com/wukeping2008/alethea/releases](https://github.com/wukeping2008/alethea/releases)
- **文档 / Documentation**: [docs/](docs/)
