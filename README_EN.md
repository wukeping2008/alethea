# Alethea - AI-Powered Personalized Learning Platform

<div align="center">

![Alethea Logo](src/static/logo.png)

**An AI-driven personalized learning platform designed for higher education in STEM fields**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-2.x-green.svg)](https://flask.palletsprojects.com/)
[![GitHub stars](https://img.shields.io/github/stars/wukeping2008/alethea.svg)](https://github.com/wukeping2008/alethea/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/wukeping2008/alethea.svg)](https://github.com/wukeping2008/alethea/network)

English | [简体中文](README.md)

</div>

## 🌟 Overview

Alethea is a powerful AI-driven personalized learning platform that integrates multiple advanced large language models to provide intelligent solutions for higher education, particularly in STEM fields. The platform leverages AI technology to deliver personalized learning analytics, intelligent Q&A, project recommendations, and more, aiming to enhance teaching efficiency and learning experience.

### ✨ Key Features

- 🤖 **Multi-Model AI Integration** - Supports OpenAI, Claude, Gemini, DeepSeek, and other AI models
- 📊 **Personalized Learning Analytics** - AI-driven learning behavior analysis and digital profile generation
- 💡 **Intelligent Project Recommendations** - Personalized learning content recommendations based on user profiles
- 🔬 **Online Experiment Simulation** - Virtual laboratory and circuit simulation capabilities
- 🧠 **Knowledge Graph System** - Personal knowledge point mastery visualization
- 🌍 **Multi-language Support** - Bilingual interface and content in Chinese and English
- 📱 **Responsive Design** - Perfect adaptation for desktop and mobile devices

## 🚀 Quick Start

### Requirements

- Python 3.9+
- Flask 2.x
- SQLAlchemy
- Modern browsers (Chrome, Firefox, Safari, Edge)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/wukeping2008/alethea.git
cd alethea
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env file to configure database and API keys
```

5. **Initialize database**
```bash
python -c "from src.main import app, db; app.app_context().push(); db.create_all()"
```

6. **Start the application**
```bash
python src/main.py
```

7. **Access the application**
Open your browser and visit `http://localhost:5000`

## 📖 Documentation

### Core Modules

#### 🤖 Intelligent Q&A System
- **Multi-AI Provider Support**: OpenAI GPT-4, Claude-3, Gemini Pro, DeepSeek, etc.
- **Smart Model Selection**: Automatically selects the most suitable AI model based on question type
- **Specialized Q&A**: Optimized for STEM subjects like electrical engineering and circuit analysis
- **Math Formula Rendering**: Supports LaTeX format mathematical formula display
- **Code Highlighting**: Automatic code snippet recognition and highlighting

#### 📊 Personalized Learning Analytics
- **Learning Behavior Tracking**: Automatically records and analyzes user learning behaviors
- **Digital Profile Generation**: AI analysis generates personalized learning characteristic profiles
- **Learning Analytics Dashboard**: Visual display of learning progress and achievements
- **Knowledge Point Mastery**: Calculates knowledge point mastery based on behavioral data

#### 💡 Intelligent Recommendation System
- **Personalized Project Recommendations**: Recommends suitable learning projects based on user profiles
- **Collaborative Filtering**: Recommendations based on similar user behaviors
- **Content Filtering**: Matching based on project content and user interests
- **Learning Path Planning**: Constructs personalized learning paths

#### 🔬 Experiment Simulation System
- **Virtual Laboratory**: Online circuit construction and simulation
- **Rich Component Library**: Various electronic components and measurement tools
- **Experiment Guidance**: Step-by-step experimental operation guidance
- **Result Analysis**: Experimental data analysis and visualization

### Technical Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Alethea Architecture                   │
├─────────────────────────────────────────────────────────────┤
│  Frontend Layer                                             │
│  ├── HTML/CSS/JavaScript                                   │
│  ├── Tailwind CSS                                          │
│  ├── Chart.js / MathJax                                    │
│  └── Responsive Design                                     │
├─────────────────────────────────────────────────────────────┤
│  Application Layer                                          │
│  ├── Flask Web Framework                                   │
│  ├── RESTful API                                           │
│  ├── JWT Authentication                                    │
│  └── Route Management                                      │
├─────────────────────────────────────────────────────────────┤
│  Business Logic Layer                                       │
│  ├── LLM Model Management                                  │
│  ├── User Analytics System                                 │
│  ├── Recommendation Algorithms                             │
│  └── Knowledge Graph                                       │
├─────────────────────────────────────────────────────────────┤
│  Data Layer                                                 │
│  ├── SQLAlchemy ORM                                        │
│  ├── SQLite/PostgreSQL                                     │
│  └── Data Models                                           │
└─────────────────────────────────────────────────────────────┘
```

## 🛠️ Development Guide

### Project Structure

```
alethea/
├── src/                    # Source code directory
│   ├── models/            # Data models
│   │   ├── user.py        # User model
│   │   ├── subject.py     # Subject model
│   │   ├── llm_models.py  # LLM model management
│   │   └── ...
│   ├── routes/            # Route controllers
│   │   ├── user.py        # User routes
│   │   ├── llm_routes.py  # LLM routes
│   │   └── ...
│   ├── static/            # Static files
│   │   ├── css/           # Style files
│   │   ├── js/            # JavaScript files
│   │   └── images/        # Image resources
│   └── main.py           # Main application entry
├── tests/                 # Test files
├── docs/                  # Documentation directory
├── requirements.txt       # Dependencies list
├── .env.example          # Environment variables example
├── .gitignore            # Git ignore file
└── README.md             # Project description
```

### Development Environment Setup

1. **Install development dependencies**
```bash
pip install -r requirements-dev.txt
```

2. **Code formatting**
```bash
black src/
flake8 src/
```

3. **Run tests**
```bash
python -m pytest tests/
```

### API Documentation

For detailed API documentation, please refer to [API Documentation](docs/API.md)

Main API endpoints:

- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `POST /api/llm/ask` - AI Q&A
- `GET /api/analytics/dashboard` - Learning analytics data
- `GET /api/analytics/recommendations` - Get recommendations

## 🤝 Contributing

We welcome all forms of contributions! Please check [CONTRIBUTING.md](CONTRIBUTING.md) for detailed information.

### Contribution Process

1. Fork this project
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Create a Pull Request

### Development Standards

- Follow PEP 8 Python coding standards
- Write clear commit messages
- Add appropriate test cases
- Update relevant documentation

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [OpenAI](https://openai.com/) - GPT model support
- [Anthropic](https://www.anthropic.com/) - Claude model support
- [Google](https://ai.google/) - Gemini model support
- [Flask](https://flask.palletsprojects.com/) - Web framework
- [Tailwind CSS](https://tailwindcss.com/) - CSS framework

## 📞 Contact

- **Project Maintainer**: [wukeping2008](https://github.com/wukeping2008)
- **Project Homepage**: [https://github.com/wukeping2008/alethea](https://github.com/wukeping2008/alethea)
- **Issue Reporting**: [Issues](https://github.com/wukeping2008/alethea/issues)

## 🌟 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=wukeping2008/alethea&type=Date)](https://star-history.com/#wukeping2008/alethea&Date)

---

<div align="center">

**If this project helps you, please give us a ⭐️**

Made with ❤️ by [wukeping2008](https://github.com/wukeping2008)

</div>
