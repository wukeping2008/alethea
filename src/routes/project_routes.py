"""
项目制学习路由
Project-based Learning Routes
"""

from flask import Blueprint, request, jsonify, session
from models.llm_models import llm_manager
import json
import logging
from datetime import datetime

# 创建蓝图
project_bp = Blueprint('project', __name__)

# 设置日志
logger = logging.getLogger(__name__)

@project_bp.route('/api/projects/recommend', methods=['POST'])
def recommend_projects():
    """AI项目推荐"""
    try:
        data = request.get_json()
        
        # 获取用户偏好
        user_skills = data.get('user_skills', [])
        difficulty_preference = data.get('difficulty_preference', 'medium')
        interests = data.get('interests', [])
        completed_projects = data.get('completed_projects', [])
        
        # 构建推荐提示
        prompt = f"""
作为一个教育AI助手，请根据用户的技能和偏好推荐最适合的项目制学习项目。

用户信息：
- 已掌握技能：{', '.join(user_skills)}
- 难度偏好：{difficulty_preference}
- 兴趣领域：{', '.join(interests)}
- 已完成项目：{', '.join(completed_projects)}

可选项目类别：
1. electronics（电子工程）- 包括Arduino、传感器、电路设计等
2. robotics（机器人）- 包括机械臂、无人机、循迹机器人等
3. iot（物联网）- 包括智能家居、WiFi感知、环境监测等
4. ai（人工智能）- 包括机器学习、计算机视觉、自然语言处理等
5. automation（自动化）- 包括PLC控制、电机调速、工业控制等

请推荐3-6个最适合的项目，返回JSON格式：
{{
    "success": true,
    "recommendations": [
        {{
            "project_id": "项目ID",
            "title": "项目标题",
            "description": "项目描述",
            "category": "项目类别",
            "difficulty": "easy/medium/hard",
            "duration": "预计时间",
            "skills_required": ["所需技能1", "所需技能2"],
            "match_score": 85,
            "reason": "推荐理由"
        }}
    ],
    "learning_path": "学习路径建议"
}}

请确保推荐的项目：
1. 与用户技能水平匹配
2. 符合用户兴趣领域
3. 有适当的挑战性
4. 避免重复已完成的项目
"""

        # 调用LLM生成推荐
        import asyncio
        response = asyncio.run(llm_manager.generate_response(prompt))
        
        # 检查响应格式
        if isinstance(response, dict) and 'content' in response:
            response_content = response['content']
        else:
            response_content = str(response)
        
        try:
            # 尝试解析JSON响应
            recommendation_data = json.loads(response_content)
            return jsonify(recommendation_data)
        except json.JSONDecodeError:
            # 如果无法解析JSON，返回备用推荐
            logger.warning("无法解析AI推荐响应，使用备用推荐")
            return jsonify(get_fallback_recommendations(interests, difficulty_preference))
            
    except Exception as e:
        logger.error(f"项目推荐错误: {e}")
        return jsonify({
            'success': False,
            'error': '推荐服务暂时不可用',
            'recommendations': get_fallback_recommendations(['electronics'], 'medium')
        }), 500

@project_bp.route('/api/projects/progress', methods=['POST'])
def update_project_progress():
    """更新项目进度"""
    try:
        data = request.get_json()
        project_id = data.get('project_id')
        stage = data.get('stage')
        progress = data.get('progress', 0)
        
        # 这里应该保存到数据库
        # 暂时使用session存储
        if 'project_progress' not in session:
            session['project_progress'] = {}
        
        session['project_progress'][project_id] = {
            'stage': stage,
            'progress': progress,
            'updated_at': str(datetime.utcnow())
        }
        
        return jsonify({
            'success': True,
            'message': '进度已更新'
        })
        
    except Exception as e:
        logger.error(f"更新进度错误: {e}")
        return jsonify({
            'success': False,
            'error': '更新失败'
        }), 500

@project_bp.route('/api/projects/progress/<project_id>', methods=['GET'])
def get_project_progress(project_id):
    """获取项目进度"""
    try:
        progress_data = session.get('project_progress', {}).get(project_id, {
            'stage': 0,
            'progress': 0
        })
        
        return jsonify({
            'success': True,
            'progress': progress_data
        })
        
    except Exception as e:
        logger.error(f"获取进度错误: {e}")
        return jsonify({
            'success': False,
            'error': '获取失败'
        }), 500

@project_bp.route('/api/projects/code-help', methods=['POST'])
def get_code_help():
    """获取编程帮助"""
    try:
        data = request.get_json()
        context = data.get('context', '')
        question = data.get('question', '')
        code = data.get('code', '')
        
        # 构建编程帮助提示
        prompt = f"""
作为一个专业的编程导师，请帮助学生解决编程问题。

上下文：{context}
问题：{question}
代码：
```
{code}
```

请提供：
1. 问题分析
2. 解决方案
3. 代码示例（如果需要）
4. 学习建议

请用中文回答，语言要通俗易懂，适合初学者理解。
"""

        # 调用LLM生成帮助
        import asyncio
        response = asyncio.run(llm_manager.generate_response(prompt))
        
        # 检查响应格式
        if isinstance(response, dict) and 'content' in response:
            response_content = response['content']
        else:
            response_content = str(response)
        
        return jsonify({
            'success': True,
            'help': response_content
        })
        
    except Exception as e:
        logger.error(f"编程帮助错误: {e}")
        return jsonify({
            'success': False,
            'error': '帮助服务暂时不可用'
        }), 500

@project_bp.route('/api/projects/generate-code', methods=['POST'])
def generate_code():
    """生成代码模板"""
    try:
        data = request.get_json()
        project_type = data.get('project_type', '')
        stage = data.get('stage', '')
        requirements = data.get('requirements', '')
        
        # 构建代码生成提示
        prompt = f"""
请为{project_type}项目的{stage}阶段生成Python代码模板。

需求：{requirements}

请生成：
1. 完整的代码模板
2. 详细的注释说明
3. 使用示例
4. 注意事项

代码要求：
- 结构清晰，易于理解
- 包含错误处理
- 适合初学者学习
- 遵循Python最佳实践
"""

        # 调用LLM生成代码
        import asyncio
        response = asyncio.run(llm_manager.generate_response(prompt))
        
        # 检查响应格式
        if isinstance(response, dict) and 'content' in response:
            response_content = response['content']
        else:
            response_content = str(response)
        
        return jsonify({
            'success': True,
            'code': response_content
        })
        
    except Exception as e:
        logger.error(f"代码生成错误: {e}")
        return jsonify({
            'success': False,
            'error': '代码生成服务暂时不可用'
        }), 500

def get_fallback_recommendations(interests, difficulty):
    """备用推荐方案"""
    fallback_projects = {
        'electronics': [
            {
                "project_id": "led-matrix",
                "title": "LED点阵显示屏",
                "description": "制作可编程LED点阵显示屏，实现文字滚动、图案显示等功能",
                "category": "electronics",
                "difficulty": "easy",
                "duration": "1-2周",
                "skills_required": ["数字电路", "LED驱动", "单片机编程"],
                "match_score": 80,
                "reason": "适合电子工程入门，涉及基础的数字电路和编程知识"
            }
        ],
        'iot': [
            {
                "project_id": "wifi-sensing",
                "title": "WiFi智能感知系统",
                "description": "基于WiFi CSI信号的人体存在检测系统，结合机器学习实现无接触式感知",
                "category": "iot",
                "difficulty": "medium",
                "duration": "3-4周",
                "skills_required": ["WiFi通信", "信号处理", "机器学习"],
                "match_score": 85,
                "reason": "结合物联网和AI技术，是当前热门的研究方向"
            }
        ]
    }
    
    recommendations = []
    for interest in interests:
        if interest in fallback_projects:
            recommendations.extend(fallback_projects[interest])
    
    if not recommendations:
        recommendations = fallback_projects['electronics']
    
    return {
        'success': True,
        'recommendations': recommendations,
        'learning_path': '建议从基础项目开始，逐步提升难度'
    }
