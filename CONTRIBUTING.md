# 贡献指南 / Contributing Guide

[English](#english) | [中文](#中文)

## 中文

感谢您对 Alethea 项目的关注！我们欢迎所有形式的贡献，包括但不限于：

- 🐛 报告 Bug
- 💡 提出新功能建议
- 📝 改进文档
- 🔧 提交代码修复
- ✨ 添加新功能
- 🧪 编写测试用例

### 开始之前

在开始贡献之前，请确保您已经：

1. 阅读了项目的 [README](README.md)
2. 查看了现有的 [Issues](https://github.com/wukeping2008/alethea/issues)
3. 了解了项目的技术栈和架构

### 开发环境设置

1. **Fork 项目**
   ```bash
   # 在 GitHub 上 Fork 项目，然后克隆到本地
   git clone https://github.com/YOUR_USERNAME/alethea.git
   cd alethea
   ```

2. **设置上游仓库**
   ```bash
   git remote add upstream https://github.com/wukeping2008/alethea.git
   ```

3. **创建虚拟环境**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # 或
   venv\Scripts\activate     # Windows
   ```

4. **安装依赖**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # 开发依赖
   ```

5. **配置环境变量**
   ```bash
   cp .env.example .env
   # 编辑 .env 文件，配置必要的环境变量
   ```

### 贡献流程

1. **创建分支**
   ```bash
   git checkout -b feature/your-feature-name
   # 或
   git checkout -b fix/your-bug-fix
   ```

2. **进行开发**
   - 编写代码
   - 添加测试
   - 更新文档

3. **代码质量检查**
   ```bash
   # 代码格式化
   black src/
   
   # 代码风格检查
   flake8 src/
   
   # 运行测试
   python -m pytest tests/
   ```

4. **提交更改**
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```

5. **推送到 Fork 仓库**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **创建 Pull Request**
   - 在 GitHub 上创建 Pull Request
   - 填写详细的描述
   - 关联相关的 Issue

### 提交信息规范

我们使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

- `feat:` 新功能
- `fix:` Bug 修复
- `docs:` 文档更新
- `style:` 代码格式化（不影响功能）
- `refactor:` 代码重构
- `test:` 添加或修改测试
- `chore:` 构建过程或辅助工具的变动

示例：
```
feat: add user authentication system
fix: resolve database connection issue
docs: update API documentation
```

### 代码规范

- 遵循 [PEP 8](https://www.python.org/dev/peps/pep-0008/) Python 代码规范
- 使用 Black 进行代码格式化
- 使用 Flake8 进行代码风格检查
- 编写清晰的注释和文档字符串
- 为新功能编写测试用例

### 报告 Bug

在报告 Bug 时，请提供以下信息：

1. **Bug 描述**：清晰简洁地描述问题
2. **重现步骤**：详细的重现步骤
3. **期望行为**：您期望发生什么
4. **实际行为**：实际发生了什么
5. **环境信息**：
   - 操作系统
   - Python 版本
   - 浏览器版本（如果相关）
6. **截图或日志**：如果有帮助的话

### 功能建议

在提出新功能建议时，请：

1. 检查是否已有类似的建议
2. 清晰描述功能的用途和价值
3. 提供具体的使用场景
4. 考虑实现的复杂性和维护成本

### 文档贡献

文档改进包括：

- 修复错别字和语法错误
- 改进现有文档的清晰度
- 添加缺失的文档
- 翻译文档到其他语言

### 测试

- 为新功能编写单元测试
- 确保所有测试通过
- 测试覆盖率应保持在合理水平
- 编写集成测试（如果适用）

### 代码审查

所有的 Pull Request 都需要经过代码审查：

- 保持耐心，审查可能需要时间
- 积极回应审查意见
- 根据反馈进行必要的修改
- 保持友好和建设性的讨论

---

## English

Thank you for your interest in contributing to Alethea! We welcome all forms of contributions, including but not limited to:

- 🐛 Bug reports
- 💡 Feature suggestions
- 📝 Documentation improvements
- 🔧 Code fixes
- ✨ New features
- 🧪 Test cases

### Before You Start

Before contributing, please make sure you have:

1. Read the project [README](README_EN.md)
2. Checked existing [Issues](https://github.com/wukeping2008/alethea/issues)
3. Understood the project's tech stack and architecture

### Development Setup

1. **Fork the project**
   ```bash
   # Fork on GitHub, then clone locally
   git clone https://github.com/YOUR_USERNAME/alethea.git
   cd alethea
   ```

2. **Set up upstream remote**
   ```bash
   git remote add upstream https://github.com/wukeping2008/alethea.git
   ```

3. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate     # Windows
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Development dependencies
   ```

5. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env file to configure necessary environment variables
   ```

### Contribution Workflow

1. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

2. **Develop**
   - Write code
   - Add tests
   - Update documentation

3. **Quality checks**
   ```bash
   # Code formatting
   black src/
   
   # Style checking
   flake8 src/
   
   # Run tests
   python -m pytest tests/
   ```

4. **Commit changes**
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```

5. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create Pull Request**
   - Create PR on GitHub
   - Fill in detailed description
   - Link related issues

### Commit Message Convention

We use [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation updates
- `style:` Code formatting (no functional changes)
- `refactor:` Code refactoring
- `test:` Adding or modifying tests
- `chore:` Build process or auxiliary tool changes

Examples:
```
feat: add user authentication system
fix: resolve database connection issue
docs: update API documentation
```

### Code Standards

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) Python coding standards
- Use Black for code formatting
- Use Flake8 for style checking
- Write clear comments and docstrings
- Write test cases for new features

### Bug Reports

When reporting bugs, please provide:

1. **Bug description**: Clear and concise description
2. **Reproduction steps**: Detailed steps to reproduce
3. **Expected behavior**: What you expected to happen
4. **Actual behavior**: What actually happened
5. **Environment info**:
   - Operating system
   - Python version
   - Browser version (if relevant)
6. **Screenshots or logs**: If helpful

### Feature Suggestions

When suggesting new features, please:

1. Check for similar existing suggestions
2. Clearly describe the feature's purpose and value
3. Provide specific use cases
4. Consider implementation complexity and maintenance cost

### Documentation Contributions

Documentation improvements include:

- Fixing typos and grammar errors
- Improving clarity of existing documentation
- Adding missing documentation
- Translating documentation to other languages

### Testing

- Write unit tests for new features
- Ensure all tests pass
- Maintain reasonable test coverage
- Write integration tests (if applicable)

### Code Review

All Pull Requests require code review:

- Be patient, reviews may take time
- Respond actively to review comments
- Make necessary changes based on feedback
- Maintain friendly and constructive discussions

---

## 联系我们 / Contact Us

如果您有任何问题，请通过以下方式联系我们：

If you have any questions, please contact us through:

- **GitHub Issues**: [https://github.com/wukeping2008/alethea/issues](https://github.com/wukeping2008/alethea/issues)
- **项目维护者 / Maintainer**: [wukeping2008](https://github.com/wukeping2008)

感谢您的贡献！🎉

Thank you for your contributions! 🎉
