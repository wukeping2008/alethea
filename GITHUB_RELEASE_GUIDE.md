# GitHub 发布指南 / GitHub Release Guide

本文档提供了在GitHub上发布Alethea项目的详细步骤和最佳实践。

This document provides detailed steps and best practices for releasing the Alethea project on GitHub.

## 发布前准备 / Pre-Release Preparation

### 1. 代码质量检查 / Code Quality Check

```bash
# 代码格式化
black src/

# 代码风格检查
flake8 src/

# 运行测试
python -m pytest tests/

# 检查依赖
pip check
```

### 2. 文档更新 / Documentation Update

- [ ] 更新 README.md
- [ ] 更新 CHANGELOG.md
- [ ] 更新 API 文档
- [ ] 检查所有链接是否有效
- [ ] 确保示例代码可以运行

### 3. 版本号管理 / Version Management

遵循 [语义化版本](https://semver.org/) 规范：

Follow [Semantic Versioning](https://semver.org/) specification:

- **主版本号 (Major)**: 不兼容的API修改
- **次版本号 (Minor)**: 向下兼容的功能性新增  
- **修订号 (Patch)**: 向下兼容的问题修正

## 发布流程 / Release Process

### 步骤 1: 准备发布分支 / Step 1: Prepare Release Branch

```bash
# 确保在主分支
git checkout main
git pull origin main

# 创建发布分支
git checkout -b release/v1.0.0

# 更新版本信息
# 编辑 src/__init__.py 或相关版本文件
echo "__version__ = '1.0.0'" > src/__version__.py
```

### 步骤 2: 更新 CHANGELOG / Step 2: Update CHANGELOG

在 `CHANGELOG.md` 中添加新版本信息：

Add new version information to `CHANGELOG.md`:

```markdown
## [1.0.0] - 2025-06-09

### 新增 / Added
- 新功能描述

### 变更 / Changed
- 变更描述

### 修复 / Fixed
- 修复描述
```

### 步骤 3: 提交和推送 / Step 3: Commit and Push

```bash
# 提交所有更改
git add .
git commit -m "chore: prepare release v1.0.0"

# 推送到远程仓库
git push origin release/v1.0.0
```

### 步骤 4: 创建 Pull Request / Step 4: Create Pull Request

1. 在 GitHub 上创建从 `release/v1.0.0` 到 `main` 的 Pull Request
2. 填写详细的发布说明
3. 请求代码审查
4. 合并 Pull Request

### 步骤 5: 创建 Git 标签 / Step 5: Create Git Tag

```bash
# 切换到主分支
git checkout main
git pull origin main

# 创建标签
git tag -a v1.0.0 -m "Release version 1.0.0"

# 推送标签
git push origin v1.0.0
```

### 步骤 6: 创建 GitHub Release / Step 6: Create GitHub Release

1. 访问 GitHub 仓库页面
2. 点击 "Releases" 标签
3. 点击 "Create a new release"
4. 填写发布信息：

#### 发布标题 / Release Title
```
Alethea v1.0.0 - AI个性化教学平台首次发布
```

#### 发布说明模板 / Release Notes Template

```markdown
# 🎉 Alethea v1.0.0 - 首次发布

我们很高兴地宣布 Alethea AI个性化教学平台的首次正式发布！

We are excited to announce the first official release of Alethea AI-powered personalized learning platform!

## ✨ 主要特性 / Key Features

### 🤖 多模型AI集成 / Multi-Model AI Integration
- 支持 OpenAI GPT-4, Claude-3, Gemini Pro, DeepSeek 等多种AI模型
- 智能模型选择和负载均衡
- 容错机制和自动重试

### 📊 个性化学习分析 / Personalized Learning Analytics  
- AI驱动的学习行为分析
- 数字画像生成
- 学习进度可视化
- 知识点掌握度评估

### 💡 智能推荐系统 / Intelligent Recommendation System
- 基于协同过滤和内容过滤的混合推荐
- 个性化学习路径规划
- 难度自适应匹配

### 🔬 在线实验仿真 / Online Experiment Simulation
- 虚拟电路实验室
- 丰富的电子元件库
- 实验数据分析和可视化

## 🚀 快速开始 / Quick Start

```bash
# 克隆项目
git clone https://github.com/wukeping2008/alethea.git
cd alethea

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env

# 启动应用
python src/main.py
```

## 📋 系统要求 / System Requirements

- Python 3.9+
- Flask 2.x
- SQLAlchemy
- 现代浏览器 (Chrome, Firefox, Safari, Edge)

## 📖 文档 / Documentation

- [README](README.md) - 项目介绍和快速开始
- [功能文档](FEATURE_DOCUMENTATION.md) - 详细功能说明
- [贡献指南](CONTRIBUTING.md) - 如何参与贡献
- [更新日志](CHANGELOG.md) - 版本更新记录

## 🐛 已知问题 / Known Issues

- 暂无已知问题

## 🔄 升级指南 / Upgrade Guide

这是首次发布，无需升级。

This is the initial release, no upgrade needed.

## 🤝 贡献 / Contributing

我们欢迎所有形式的贡献！请查看 [贡献指南](CONTRIBUTING.md) 了解详情。

We welcome all forms of contributions! Please check our [Contributing Guide](CONTRIBUTING.md) for details.

## 📞 支持 / Support

- 🐛 [报告问题](https://github.com/wukeping2008/alethea/issues)
- 💬 [讨论区](https://github.com/wukeping2008/alethea/discussions)
- 📧 联系维护者: [wukeping2008](https://github.com/wukeping2008)

## 🙏 致谢 / Acknowledgments

感谢所有为这个项目做出贡献的开发者和用户！

Thanks to all developers and users who contributed to this project!

---

**完整更新日志**: [CHANGELOG.md](CHANGELOG.md)
**Full Changelog**: [CHANGELOG.md](CHANGELOG.md)
```

## 发布后任务 / Post-Release Tasks

### 1. 验证发布 / Verify Release

```bash
# 验证标签
git tag -l | grep v1.0.0

# 验证发布包
curl -L https://github.com/wukeping2008/alethea/archive/v1.0.0.tar.gz -o alethea-v1.0.0.tar.gz
tar -tzf alethea-v1.0.0.tar.gz | head -10
```

### 2. 更新文档网站 / Update Documentation Site

- 更新在线文档
- 更新API文档
- 发布博客文章（如果有）

### 3. 社交媒体宣传 / Social Media Promotion

- 在相关社区分享发布信息
- 更新项目主页
- 通知用户和贡献者

### 4. 监控和反馈 / Monitoring and Feedback

- 监控下载量和使用情况
- 收集用户反馈
- 跟踪问题报告

## 发布检查清单 / Release Checklist

### 发布前 / Pre-Release
- [ ] 所有测试通过
- [ ] 代码质量检查通过
- [ ] 文档已更新
- [ ] CHANGELOG.md 已更新
- [ ] 版本号已更新
- [ ] 依赖项已检查

### 发布中 / During Release
- [ ] 创建发布分支
- [ ] 创建 Pull Request
- [ ] 代码审查完成
- [ ] 合并到主分支
- [ ] 创建 Git 标签
- [ ] 创建 GitHub Release

### 发布后 / Post-Release
- [ ] 验证发布包
- [ ] 更新文档网站
- [ ] 社交媒体宣传
- [ ] 监控反馈
- [ ] 准备下一版本

## 回滚流程 / Rollback Process

如果发现严重问题需要回滚：

If serious issues are found and rollback is needed:

```bash
# 删除有问题的标签
git tag -d v1.0.0
git push origin :refs/tags/v1.0.0

# 在 GitHub 上删除 Release
# 手动在 GitHub Release 页面删除

# 创建修复版本
git checkout -b hotfix/v1.0.1
# 修复问题...
git commit -m "fix: critical issue"
git tag -a v1.0.1 -m "Hotfix version 1.0.1"
git push origin v1.0.1
```

## 自动化发布 / Automated Release

可以使用 GitHub Actions 自动化发布流程：

You can use GitHub Actions to automate the release process:

```yaml
# .github/workflows/release.yml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Create Release
        uses: actions/create-release@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          tag_name: ${{ github.ref }}
          release_name: Release ${{ github.ref }}
          draft: false
          prerelease: false
```

## 最佳实践 / Best Practices

1. **定期发布**: 保持稳定的发布节奏
2. **语义化版本**: 严格遵循语义化版本规范
3. **详细说明**: 提供清晰的发布说明
4. **向后兼容**: 尽量保持API向后兼容
5. **安全更新**: 及时发布安全修复
6. **用户沟通**: 提前通知重大变更
7. **测试覆盖**: 确保充分的测试覆盖
8. **文档同步**: 保持文档与代码同步

---

**维护者**: [wukeping2008](https://github.com/wukeping2008)  
**最后更新**: 2025-06-09
