"""
API routes for LLM integration in Alethea platform
"""

from flask import Blueprint, request, jsonify, session
import json
import os
from models.llm_models_optimized import optimized_llm_manager as llm_manager

# Create blueprint
llm_bp = Blueprint('llm', __name__, url_prefix='/api/llm')

@llm_bp.route('/ask', methods=['POST'])
def ask_question():
    """
    Endpoint to ask a question to the selected LLM with personalized settings
    
    Request body:
    {
        "question": "Your question here",
        "provider": "openai", // optional, defaults to user preference or system default
        "model": "gpt-4o",    // optional, defaults to provider default
        "options": {          // optional
            "temperature": 0.7,
            "max_tokens": 1000
        },
        "use_knowledge_base": true, // optional, whether to search personal knowledge base
        "context": "additional context" // optional
    }
    """
    try:
        data = request.json
        
        if not data or 'question' not in data:
            return jsonify({
                'error': 'Missing required parameter: question'
            }), 400
        
        question = data['question']
        provider = data.get('provider')
        model = data.get('model')
        options = data.get('options', {})
        use_knowledge_base = data.get('use_knowledge_base', True)
        context = data.get('context', '')
        
        # Get user personalized settings
        user_id = session.get('user_id', 1)
        user_settings = get_user_ai_settings(user_id)
        
        # Apply user preferences if not explicitly provided
        if not provider and user_settings.get('ai_preferences', {}).get('preferred_provider') != 'auto':
            provider = user_settings.get('ai_preferences', {}).get('preferred_provider')
        
        # Adjust options based on user settings
        response_length = user_settings.get('ai_preferences', {}).get('response_length', 'medium')
        if response_length == 'short':
            options['max_tokens'] = options.get('max_tokens', 500)
        elif response_length == 'long':
            options['max_tokens'] = options.get('max_tokens', 2000)
        else:  # medium
            options['max_tokens'] = options.get('max_tokens', 1000)
        
        # Combine options with model if provided
        if model:
            options['model'] = model
        
        # Build enhanced prompt with user preferences and knowledge base
        enhanced_prompt = build_enhanced_prompt(question, user_settings, use_knowledge_base, context, user_id)
        
        # Generate response from LLM (using asyncio.run for sync compatibility)
        import asyncio
        response = asyncio.run(llm_manager.generate_response(
            prompt=enhanced_prompt,
            provider=provider,
            **options
        ))
        
        # Add knowledge base references if used
        if use_knowledge_base and response.get('content'):
            knowledge_refs = get_knowledge_base_references(question, user_id)
            if knowledge_refs:
                response['knowledge_base_references'] = knowledge_refs
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'message': 'An error occurred while processing your request'
        }), 500

@llm_bp.route('/providers', methods=['GET'])
def get_providers():
    """Get all available LLM providers"""
    try:
        providers = llm_manager.get_all_providers()
        return jsonify({
            'providers': providers,
            'default_provider': llm_manager.default_provider
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'message': 'An error occurred while fetching providers'
        }), 500

@llm_bp.route('/models/<provider>', methods=['GET'])
def get_provider_models(provider):
    """Get available models for a specific provider"""
    try:
        models = llm_manager.get_provider_models(provider)
        return jsonify({
            'provider': provider,
            'models': models
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'message': f'An error occurred while fetching models for {provider}'
        }), 500

@llm_bp.route('/generate-related-content', methods=['POST'])
def generate_related_content():
    """
    Generate related knowledge points and experiments based on question and answer using AI
    
    Request body:
    {
        "question": "用户的问题",
        "answer": "AI的回答内容"
    }
    """
    try:
        data = request.json
        
        if not data or 'question' not in data or 'answer' not in data:
            return jsonify({
                'error': 'Missing required parameters: question and answer'
            }), 400
        
        question = data['question']
        answer = data['answer']
        
        # 使用AI生成相关内容
        return generate_ai_related_content(question, answer)
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'message': 'An error occurred while generating related content'
        }), 500

@llm_bp.route('/project-assistant', methods=['POST'])
def project_assistant():
    """
    AI项目助手 - 为用户提供项目相关的智能指导
    
    Request body:
    {
        "question": "用户的问题",
        "project_id": "项目ID",
        "module_name": "模块名称（可选）",
        "context": "项目上下文信息（可选）"
    }
    """
    try:
        data = request.json
        
        if not data or 'question' not in data:
            return jsonify({
                'error': 'Missing required parameter: question'
            }), 400
        
        question = data['question']
        project_id = data.get('project_id', '')
        module_name = data.get('module_name', '')
        context = data.get('context', '')
        
        # 使用AI生成项目助手回答
        return generate_project_assistant_response(question, project_id, module_name, context)
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'message': 'An error occurred while processing your question'
        }), 500

@llm_bp.route('/recommend-projects', methods=['POST'])
def recommend_projects():
    """
    智能项目推荐 - 基于用户偏好和技能水平推荐合适的项目
    
    Request body:
    {
        "user_skills": ["技能1", "技能2"],
        "difficulty_preference": "easy|medium|hard",
        "interests": ["兴趣领域1", "兴趣领域2"],
        "completed_projects": ["已完成项目ID1", "已完成项目ID2"]
    }
    """
    try:
        data = request.json
        
        user_skills = data.get('user_skills', [])
        difficulty_preference = data.get('difficulty_preference', 'medium')
        interests = data.get('interests', [])
        completed_projects = data.get('completed_projects', [])
        
        # 使用AI生成项目推荐
        return generate_project_recommendations(user_skills, difficulty_preference, interests, completed_projects)
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'message': 'An error occurred while generating recommendations'
        }), 500

@llm_bp.route('/enhanced-qa', methods=['POST'])
def enhanced_qa():
    """
    增强的智能问答 - 结合项目上下文的智能问答
    
    Request body:
    {
        "question": "用户的问题",
        "knowledge_point": "知识点名称",
        "project_context": "项目上下文（可选）"
    }
    """
    try:
        data = request.json
        
        if not data or 'question' not in data:
            return jsonify({
                'error': 'Missing required parameter: question'
            }), 400
        
        question = data['question']
        knowledge_point = data.get('knowledge_point', '')
        project_context = data.get('project_context', '')
        
        # 使用AI生成增强的问答回答
        return generate_enhanced_qa_response(question, knowledge_point, project_context)
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'message': 'An error occurred while processing your question'
        }), 500

@llm_bp.route('/generate-experiment', methods=['POST'])
def generate_experiment():
    """
    生成实验内容 - 基于问题生成相关的实验设计
    
    Request body:
    {
        "question": "用户的问题",
        "subject": "学科领域（可选）",
        "difficulty": "难度级别（可选）"
    }
    """
    try:
        data = request.json
        
        if not data or 'question' not in data:
            return jsonify({
                'error': 'Missing required parameter: question'
            }), 400
        
        question = data['question']
        subject = data.get('subject', '')
        difficulty = data.get('difficulty', 'medium')
        
        # 使用AI生成实验内容
        return generate_experiment_content(question, subject, difficulty)
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'message': 'An error occurred while generating experiment'
        }), 500

def generate_ai_related_content(question, answer):
    """使用AI生成相关知识点、实验和仿真内容"""
    import asyncio
    
    try:
        # 构建AI提示词来生成相关内容
        content_prompt = f"""
基于以下问题和回答，请生成相关的学习内容：

问题：{question}
回答：{answer}

请按照以下JSON格式返回内容：

{{
    "knowledge_points": [
        {{
            "title": "知识点标题",
            "description": "知识点描述"
        }}
    ],
    "experiments": [
        {{
            "title": "实验标题",
            "type": "实验类型（如circuit_simulation, physics_simulation等）",
            "description": "实验描述",
            "equipment": ["所需设备1", "所需设备2"],
            "steps": ["步骤1", "步骤2", "步骤3"],
            "simulation_url": "第三方仿真平台URL（如果适用）"
        }}
    ],
    "simulation": {{
        "title": "仿真标题",
        "type": "仿真类型",
        "description": "仿真描述",
        "third_party_platform": "第三方平台名称（如CircuitJS, PhET, Desmos等）",
        "platform_url": "平台URL",
        "parameters": [
            {{
                "name": "参数名称",
                "type": "slider",
                "min": 最小值,
                "max": 最大值,
                "default": 默认值,
                "unit": "单位"
            }}
        ],
        "outputs": [
            {{
                "name": "输出名称",
                "type": "chart或value",
                "description": "输出描述"
            }}
        ]
    }}
}}

要求：
1. 生成4个相关知识点，要与问题主题密切相关
2. 生成4个实验，包括具体的实验步骤和所需设备
3. 为每个实验匹配合适的第三方仿真平台URL
4. 仿真内容要与实验内容对应
5. 如果是电路相关，推荐CircuitJS或Falstad仿真器
6. 如果是物理相关，推荐PhET仿真
7. 如果是数学相关，推荐Desmos或GeoGebra
8. 如果是化学相关，推荐ChemSketch或分子建模工具
9. 确保所有内容都是中文
10. 只返回JSON格式，不要其他文字
"""

        # 使用AI生成内容
        response = asyncio.run(llm_manager.generate_response(
            prompt=content_prompt,
            provider=None,  # 使用默认提供商
            temperature=0.7,
            max_tokens=2000
        ))
        
        if 'error' in response:
            # 如果AI生成失败，使用备用方案
            return generate_fallback_content(question, answer)
        
        # 尝试解析AI返回的JSON
        try:
            import json
            ai_content = response['content']
            
            # 提取JSON部分（去除可能的前后文字）
            start_idx = ai_content.find('{')
            end_idx = ai_content.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = ai_content[start_idx:end_idx]
                parsed_content = json.loads(json_str)
                
                # 验证和补充内容
                validated_content = validate_and_enhance_content(parsed_content, question, answer)
                
                return jsonify({
                    **validated_content,
                    'success': True,
                    'generated_by': 'ai'
                })
            else:
                raise ValueError("No valid JSON found in AI response")
                
        except (json.JSONDecodeError, ValueError) as e:
            print(f"JSON parsing error: {e}")
            # JSON解析失败，使用备用方案
            return generate_fallback_content(question, answer)
    
    except Exception as e:
        print(f"AI content generation error: {e}")
        return generate_fallback_content(question, answer)

def validate_and_enhance_content(content, question, answer):
    """验证和增强AI生成的内容"""
    
    # 确保必要的字段存在
    if 'knowledge_points' not in content:
        content['knowledge_points'] = []
    if 'experiments' not in content:
        content['experiments'] = []
    if 'simulation' not in content:
        content['simulation'] = {}
    
    # 补充缺失的知识点
    while len(content['knowledge_points']) < 4:
        content['knowledge_points'].append({
            "title": f"相关概念{len(content['knowledge_points']) + 1}",
            "description": "与主题相关的重要概念"
        })
    
    # 补充缺失的实验
    while len(content['experiments']) < 4:
        content['experiments'].append({
            "title": f"相关实验{len(content['experiments']) + 1}",
            "type": "general_experiment",
            "description": "验证相关理论的实验",
            "equipment": ["基础实验设备"],
            "steps": ["准备实验", "进行测量", "记录数据", "分析结果"],
            "simulation_url": ""
        })
    
    # 为实验添加第三方仿真平台URL
    for experiment in content['experiments']:
        if 'simulation_url' not in experiment or not experiment['simulation_url']:
            experiment['simulation_url'] = get_simulation_url_for_experiment(experiment, question)
    
    # 增强仿真内容
    if not content['simulation'] or 'title' not in content['simulation']:
        content['simulation'] = generate_default_simulation(question, answer)
    
    # 确保仿真有第三方平台信息
    if 'third_party_platform' not in content['simulation']:
        platform_info = get_third_party_platform(question, answer)
        content['simulation'].update(platform_info)
    
    return content

def get_simulation_url_for_experiment(experiment, question):
    """为实验获取合适的第三方仿真平台URL"""
    
    # 根据实验类型和问题内容推荐仿真平台
    question_lower = question.lower()
    exp_type = experiment.get('type', '').lower()
    exp_title = experiment.get('title', '').lower()
    
    # 电路仿真
    if any(keyword in question_lower + exp_title for keyword in ['电路', '电阻', '电容', '电感', '运放', '二极管']):
        return "https://www.falstad.com/circuit/circuitjs.html"
    
    # 物理仿真
    elif any(keyword in question_lower + exp_title for keyword in ['物理', '力学', '波动', '光学', '电磁']):
        return "https://phet.colorado.edu/zh_CN/"
    
    # 数学仿真
    elif any(keyword in question_lower + exp_title for keyword in ['数学', '函数', '几何', '统计']):
        return "https://www.desmos.com/calculator"
    
    # 化学仿真
    elif any(keyword in question_lower + exp_title for keyword in ['化学', '分子', '反应', '化合物']):
        return "https://molview.org/"
    
    # 控制系统仿真
    elif any(keyword in question_lower + exp_title for keyword in ['控制', 'pid', '系统']):
        return "https://www.mathworks.com/products/simulink.html"
    
    # 默认通用仿真
    else:
        return "https://www.geogebra.org/"

def get_third_party_platform(question, answer):
    """获取第三方仿真平台信息"""
    
    question_lower = (question + ' ' + answer).lower()
    
    # 电路相关
    if any(keyword in question_lower for keyword in ['电路', '电阻', '电容', '电感', '运放']):
        return {
            "third_party_platform": "CircuitJS",
            "platform_url": "https://www.falstad.com/circuit/circuitjs.html",
            "platform_description": "在线电路仿真器，支持实时电路分析和波形显示"
        }
    
    # 物理相关
    elif any(keyword in question_lower for keyword in ['物理', '力学', '波动', '光学']):
        return {
            "third_party_platform": "PhET Interactive Simulations",
            "platform_url": "https://phet.colorado.edu/zh_CN/",
            "platform_description": "科罗拉多大学开发的交互式物理仿真平台"
        }
    
    # 数学相关
    elif any(keyword in question_lower for keyword in ['数学', '函数', '几何', '微积分']):
        return {
            "third_party_platform": "Desmos Graphing Calculator",
            "platform_url": "https://www.desmos.com/calculator",
            "platform_description": "强大的在线数学图形计算器和函数绘图工具"
        }
    
    # 化学相关
    elif any(keyword in question_lower for keyword in ['化学', '分子', '原子', '化合物']):
        return {
            "third_party_platform": "MolView",
            "platform_url": "https://molview.org/",
            "platform_description": "在线分子结构查看器和化学仿真工具"
        }
    
    # 控制系统相关
    elif any(keyword in question_lower for keyword in ['控制', 'pid', '系统', '反馈']):
        return {
            "third_party_platform": "MATLAB Simulink Online",
            "platform_url": "https://www.mathworks.com/products/simulink-online.html",
            "platform_description": "专业的控制系统建模和仿真平台"
        }
    
    # 默认通用平台
    else:
        return {
            "third_party_platform": "GeoGebra",
            "platform_url": "https://www.geogebra.org/",
            "platform_description": "多功能数学和科学仿真平台"
        }

def generate_default_simulation(question, answer):
    """生成默认仿真配置"""
    
    platform_info = get_third_party_platform(question, answer)
    
    return {
        "title": "交互式仿真实验",
        "type": "interactive_simulation",
        "description": "基于问题内容的交互式仿真，支持参数调节和实时观察",
        **platform_info,
        "parameters": [
            {"name": "参数1", "type": "slider", "min": 0, "max": 100, "default": 50, "unit": ""},
            {"name": "参数2", "type": "slider", "min": 0, "max": 10, "default": 5, "unit": ""},
            {"name": "参数3", "type": "slider", "min": 1, "max": 20, "default": 10, "unit": ""}
        ],
        "outputs": [
            {"name": "仿真结果", "type": "chart", "description": "显示仿真结果的图表"},
            {"name": "数值输出", "type": "value", "description": "显示计算得到的数值"}
        ]
    }

def generate_fallback_content(question, answer):
    """AI生成失败时的备用内容生成方案"""
    
    # 分析问题类型，确定学科领域
    subject_analysis = analyze_subject_domain(question, answer)
    
    # 根据学科领域生成相关内容
    if subject_analysis['domain'] == 'electronics':
        return generate_electronics_content(question, answer, subject_analysis)
    elif subject_analysis['domain'] == 'physics':
        return generate_physics_content(question, answer, subject_analysis)
    elif subject_analysis['domain'] == 'mathematics':
        return generate_mathematics_content(question, answer, subject_analysis)
    elif subject_analysis['domain'] == 'chemistry':
        return generate_chemistry_content(question, answer, subject_analysis)
    elif subject_analysis['domain'] == 'control':
        return generate_control_content(question, answer, subject_analysis)
    elif subject_analysis['domain'] == 'computer_science':
        return generate_computer_science_content(question, answer, subject_analysis)
    elif subject_analysis['domain'] == 'biology':
        return generate_biology_content(question, answer, subject_analysis)
    elif subject_analysis['domain'] == 'semiconductor':
        return generate_semiconductor_content(question, answer, subject_analysis)
    elif subject_analysis['domain'] == 'artificial_intelligence':
        return generate_ai_content(question, answer, subject_analysis)
    else:
        return generate_general_content(question, answer, subject_analysis)

def analyze_subject_domain(question, answer):
    """分析问题所属的学科领域"""
    import re
    
    # 关键词映射 - 增加新的学科领域
    domain_keywords = {
        'electronics': ['电路', '电阻', '电容', '电感', '二极管', '晶体管', '运放', '运算放大器', '滤波', '放大', '振荡', '数字电路', '模拟电路', '集成电路', 'PCB', '电压', '电流', '功率', '基本电路', '放大器', '反相', '同相', '差分', '运放电路', '电子', '电子学'],
        'physics': ['力学', '热力学', '电磁学', '光学', '量子', '相对论', '波动', '振动', '能量', '动量', '加速度', '速度', '质量', '重力', '磁场', '电场', '物理', '牛顿', '单摆', '自由落体', '干涉', '衍射'],
        'mathematics': ['函数', '导数', '积分', '微分', '矩阵', '向量', '概率', '统计', '几何', '代数', '三角', '对数', '指数', '极限', '级数', '方程', '数学', '计算', '求解'],
        'chemistry': ['化学', '分子', '原子', '离子', '化合物', '反应', '催化', '平衡', '酸碱', '氧化', '还原', '有机', '无机', '聚合物', '滴定', '溶液'],
        'control': ['控制', 'PID', '反馈', '系统', '传递函数', '稳定性', '响应', '调节', '自动化', '伺服', '闭环', '开环', '控制器', '控制系统'],
        'computer_science': ['编程', '程序', '算法', '数据结构', '计算机', '软件', '网络', '操作系统', 'CPU', '内存', '数据库', 'Java', 'Python', 'C++', '面向对象', '软件工程', '计算机组成', '编译原理'],
        'biology': ['生物', '细胞', '基因', 'DNA', 'RNA', '蛋白质', '酶', '代谢', '遗传', '进化', '生态', '微生物', '病毒', '细菌', '生理', '解剖', '分子生物学', '生物化学'],
        'semiconductor': ['半导体', '集成电路', 'IC', 'VLSI', 'CMOS', 'MOSFET', '晶圆', '光刻', '刻蚀', '离子注入', 'EDA', '版图', '工艺', '制程', '芯片', '硅', '掺杂'],
        'artificial_intelligence': ['人工智能', 'AI', '机器学习', '深度学习', '神经网络', '卷积', 'CNN', 'RNN', 'Transformer', '自然语言处理', 'NLP', '计算机视觉', '数据挖掘', '模式识别', '强化学习', '监督学习', '无监督学习']
    }
    
    # 计算每个领域的匹配度
    domain_scores = {}
    text = (question + ' ' + answer).lower()
    
    for domain, keywords in domain_keywords.items():
        score = 0
        for keyword in keywords:
            if keyword in text:
                # 给电子学相关词汇更高的权重
                if domain == 'electronics' and keyword in ['运放', '运算放大器', '基本电路', '放大器', '电路']:
                    score += 3  # 高权重
                elif keyword in ['电路', '电阻', '电容', '电压', '电流']:
                    score += 2  # 中等权重
                else:
                    score += 1  # 基础权重
        domain_scores[domain] = score
    
    # 确定主要领域
    main_domain = max(domain_scores, key=domain_scores.get) if max(domain_scores.values()) > 0 else 'general'
    
    # 提取关键概念
    key_concepts = []
    for domain, keywords in domain_keywords.items():
        for keyword in keywords:
            if keyword in text:
                key_concepts.append(keyword)
    
    # 调试信息
    print(f"Question: {question}")
    print(f"Domain scores: {domain_scores}")
    print(f"Selected domain: {main_domain}")
    print(f"Key concepts: {key_concepts[:5]}")
    
    return {
        'domain': main_domain,
        'scores': domain_scores,
        'key_concepts': key_concepts[:5]  # 最多5个关键概念
    }

def generate_electronics_content(question, answer, analysis):
    """生成电子学相关内容"""
    knowledge_points = [
        {"title": "基尔霍夫定律", "description": "电路分析的基本定律，包括电流定律和电压定律"},
        {"title": "欧姆定律", "description": "描述电压、电流和电阻之间关系的基本定律"},
        {"title": "RC电路分析", "description": "电阻-电容电路的时域和频域分析方法"},
        {"title": "运算放大器", "description": "理想运放的特性和基本应用电路"}
    ]
    
    experiments = [
        {
            "title": "基础电路搭建实验", 
            "type": "circuit_simulation", 
            "description": "使用面包板搭建简单的电阻分压电路",
            "equipment": ["面包板", "电阻", "导线", "万用表"],
            "steps": ["准备元件", "搭建电路", "测量电压", "分析结果"],
            "simulation_url": "https://www.falstad.com/circuit/circuitjs.html"
        },
        {
            "title": "RC充放电实验", 
            "type": "circuit_simulation",
            "description": "观察RC电路的充放电过程和时间常数",
            "equipment": ["电阻", "电容", "示波器", "信号发生器"],
            "steps": ["连接RC电路", "施加方波信号", "观察波形", "计算时间常数"],
            "simulation_url": "https://www.falstad.com/circuit/circuitjs.html"
        },
        {
            "title": "运放放大电路实验", 
            "type": "circuit_simulation",
            "description": "设计和测试反相放大器和同相放大器",
            "equipment": ["运算放大器", "电阻", "信号发生器", "示波器"],
            "steps": ["设计电路", "搭建放大器", "测试增益", "分析频响"],
            "simulation_url": "https://www.falstad.com/circuit/circuitjs.html"
        },
        {
            "title": "滤波器设计实验", 
            "type": "circuit_simulation",
            "description": "设计低通、高通和带通滤波器",
            "equipment": ["运放", "电阻", "电容", "网络分析仪"],
            "steps": ["设计滤波器", "搭建电路", "测试频响", "优化参数"],
            "simulation_url": "https://www.falstad.com/circuit/circuitjs.html"
        }
    ]
    
    # 获取第三方平台信息
    platform_info = get_third_party_platform(question, answer)
    
    simulation = {
        "title": "交互式电路仿真",
        "type": "circuit_simulator",
        "description": "可视化电路仿真，支持实时参数调节和波形观察",
        **platform_info,  # 添加第三方平台信息
        "parameters": [
            {"name": "电阻值", "type": "slider", "min": 100, "max": 10000, "default": 1000, "unit": "Ω"},
            {"name": "电容值", "type": "slider", "min": 1, "max": 1000, "default": 100, "unit": "μF"},
            {"name": "输入电压", "type": "slider", "min": 1, "max": 12, "default": 5, "unit": "V"}
        ],
        "outputs": [
            {"name": "电压波形", "type": "chart", "description": "显示各节点的电压随时间变化"},
            {"name": "电流值", "type": "value", "description": "实时显示电路中的电流值"}
        ]
    }
    
    return jsonify({
        'knowledge_points': knowledge_points,
        'experiments': experiments,
        'simulation': simulation,
        'success': True
    })

def generate_project_assistant_response(question, project_id, module_name, context):
    """生成项目助手的AI回答"""
    import asyncio
    
    try:
        # 构建项目助手的提示词
        assistant_prompt = f"""
你是一个专业的理工科项目学习助手，专门帮助学生完成理工科项目。

【知识范围限定】
- 只回答理工科项目相关问题：电子工程、计算机科学、机械工程、自动化、物理、数学等
- 对于缩写词，优先解释理工科含义（如PID指比例-积分-微分控制器）
- 如果问题不属于理工科范围，请说明这超出了理工科项目指导范围

项目信息：
- 项目ID: {project_id}
- 模块名称: {module_name}
- 上下文: {context}

用户问题: {question}

请根据以下要求回答：
1. 针对具体理工科项目和模块提供专业技术指导
2. 如果是技术问题，提供详细的解决方案和步骤
3. 如果是概念问题，用专业术语结合通俗解释
4. 提供相关的理工科学习资源和参考资料
5. 鼓励学生动手实践和深入思考技术原理
6. 回答要具体、实用、有针对性，符合工程实践
7. 使用中文回答，确保技术准确性

回答格式：
- 直接回答理工科技术问题
- 提供具体的技术操作步骤（如果适用）
- 给出理工科学习建议
- 推荐相关技术资源
"""

        # 使用AI生成回答
        response = asyncio.run(llm_manager.generate_response(
            prompt=assistant_prompt,
            provider=None,  # 使用默认提供商
            temperature=0.7,
            max_tokens=1500
        ))
        
        if 'error' in response:
            return jsonify({
                'error': 'AI服务暂时不可用',
                'message': '请稍后再试，或联系技术支持'
            }), 500
        
        return jsonify({
            'answer': response['content'],
            'project_id': project_id,
            'module_name': module_name,
            'success': True,
            'assistant_type': 'project_assistant'
        })
    
    except Exception as e:
        print(f"Project assistant error: {e}")
        return jsonify({
            'error': str(e),
            'message': 'AI助手服务出现错误'
        }), 500

def generate_project_recommendations(user_skills, difficulty_preference, interests, completed_projects):
    """生成智能项目推荐"""
    import asyncio
    
    try:
        # 构建项目推荐的提示词
        recommendation_prompt = f"""
基于用户的技能和偏好，为其推荐合适的理工科项目。

用户信息：
- 技能水平: {', '.join(user_skills) if user_skills else '初学者'}
- 难度偏好: {difficulty_preference}
- 兴趣领域: {', '.join(interests) if interests else '通用'}
- 已完成项目: {', '.join(completed_projects) if completed_projects else '无'}

请按照以下JSON格式返回推荐结果：

{{
    "recommendations": [
        {{
            "project_id": "项目ID",
            "title": "项目标题",
            "description": "项目描述",
            "difficulty": "easy|medium|hard",
            "category": "项目分类",
            "skills_required": ["所需技能1", "所需技能2"],
            "duration": "预计时间",
            "reason": "推荐理由",
            "match_score": 85
        }}
    ],
    "learning_path": [
        {{
            "step": 1,
            "project_title": "项目标题",
            "description": "为什么推荐这个顺序",
            "skills_gained": ["获得的技能1", "获得的技能2"]
        }}
    ]
}}

要求：
1. 推荐6个项目，按匹配度排序
2. 考虑用户的技能水平和兴趣
3. 避免推荐已完成的项目
4. 提供学习路径建议
5. 匹配分数要合理（0-100）
6. 确保项目的渐进性和连贯性
7. 只返回JSON格式，不要其他文字
"""

        # 使用AI生成推荐
        response = asyncio.run(llm_manager.generate_response(
            prompt=recommendation_prompt,
            provider=None,
            temperature=0.8,
            max_tokens=2000
        ))
        
        if 'error' in response:
            # 使用备用推荐算法
            return generate_fallback_recommendations(user_skills, difficulty_preference, interests, completed_projects)
        
        # 尝试解析AI返回的JSON
        try:
            import json
            ai_content = response['content']
            
            # 提取JSON部分
            start_idx = ai_content.find('{')
            end_idx = ai_content.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = ai_content[start_idx:end_idx]
                parsed_content = json.loads(json_str)
                
                return jsonify({
                    **parsed_content,
                    'success': True,
                    'generated_by': 'ai'
                })
            else:
                raise ValueError("No valid JSON found in AI response")
                
        except (json.JSONDecodeError, ValueError) as e:
            print(f"JSON parsing error: {e}")
            return generate_fallback_recommendations(user_skills, difficulty_preference, interests, completed_projects)
    
    except Exception as e:
        print(f"Project recommendation error: {e}")
        return generate_fallback_recommendations(user_skills, difficulty_preference, interests, completed_projects)

def generate_enhanced_qa_response(question, knowledge_point, project_context):
    """生成增强的智能问答回答"""
    import asyncio
    
    try:
        # 构建增强问答的提示词
        qa_prompt = f"""
你是一个专业的理工科教学助手，专门回答学生的理工科学术问题。

【知识范围限定】
- 只回答理工科相关问题：数学、物理、化学、电子工程、计算机科学、机械工程等
- 对于缩写词，优先解释理工科含义（如PID指比例-积分-微分控制器）
- 如果问题不属于理工科范围，请说明这超出了理工科教学范围

问题信息：
- 用户问题: {question}
- 知识点: {knowledge_point}
- 项目上下文: {project_context}

请按照以下要求回答：
1. 结合理工科知识点和项目上下文提供精准技术回答
2. 如果有项目上下文，要将理论与实际工程项目联系起来
3. 提供清晰的技术概念解释和工程实例
4. 包含相关的数学公式、技术图表说明（如果适用）
5. 给出理工科学习建议和进一步探索的技术方向
6. 推荐相关的理工科实验或仿真
7. 使用中文回答，语言要专业准确且易懂

回答结构：
1. 直接回答理工科技术问题
2. 详细解释相关技术概念
3. 结合工程项目实例（如果有项目上下文）
4. 提供理工科学习建议
5. 推荐相关技术资源
"""

        # 使用AI生成回答
        response = asyncio.run(llm_manager.generate_response(
            prompt=qa_prompt,
            provider=None,
            temperature=0.7,
            max_tokens=2000
        ))
        
        if 'error' in response:
            return jsonify({
                'error': 'AI服务暂时不可用',
                'message': '请稍后再试，或联系技术支持'
            }), 500
        
        return jsonify({
            'answer': response['content'],
            'knowledge_point': knowledge_point,
            'project_context': project_context,
            'success': True,
            'qa_type': 'enhanced_qa'
        })
    
    except Exception as e:
        print(f"Enhanced QA error: {e}")
        return jsonify({
            'error': str(e),
            'message': '智能问答服务出现错误'
        }), 500

def generate_fallback_recommendations(user_skills, difficulty_preference, interests, completed_projects):
    """备用项目推荐算法"""
    
    # 预定义的项目数据库（简化版）
    all_projects = [
        {
            "project_id": "smart-car",
            "title": "智能小车",
            "description": "基于Arduino的避障智能小车",
            "difficulty": "medium",
            "category": "robotics",
            "skills_required": ["Arduino编程", "传感器应用", "电机控制"],
            "duration": "2-3周",
            "reason": "适合学习嵌入式编程和硬件控制",
            "match_score": 85
        },
        {
            "project_id": "led-matrix",
            "title": "LED点阵显示屏",
            "description": "制作可编程LED点阵显示屏",
            "difficulty": "easy",
            "category": "electronics",
            "skills_required": ["数字电路", "LED驱动", "单片机编程"],
            "duration": "1-2周",
            "reason": "入门级项目，适合初学者",
            "match_score": 75
        },
        {
            "project_id": "face-recognition",
            "title": "人脸识别系统",
            "description": "基于深度学习的人脸识别系统",
            "difficulty": "hard",
            "category": "ai",
            "skills_required": ["深度学习", "计算机视觉", "Python编程"],
            "duration": "4-5周",
            "reason": "适合有编程基础的学生学习AI技术",
            "match_score": 90
        },
        {
            "project_id": "smart-home",
            "title": "智能家居系统",
            "description": "构建物联网智能家居系统",
            "difficulty": "medium",
            "category": "iot",
            "skills_required": ["WiFi通信", "传感器网络", "移动应用"],
            "duration": "3-4周",
            "reason": "结合硬件和软件，实用性强",
            "match_score": 80
        },
        {
            "project_id": "plc-control",
            "title": "PLC控制系统",
            "description": "设计工业自动化PLC控制系统",
            "difficulty": "hard",
            "category": "automation",
            "skills_required": ["PLC编程", "工业控制", "传感器应用"],
            "duration": "4-6周",
            "reason": "工业应用导向，就业前景好",
            "match_score": 70
        },
        {
            "project_id": "weather-station",
            "title": "气象监测站",
            "description": "制作实时环境监测系统",
            "difficulty": "easy",
            "category": "iot",
            "skills_required": ["环境传感器", "数据采集", "无线传输"],
            "duration": "1-2周",
            "reason": "简单实用，容易上手",
            "match_score": 65
        }
    ]
    
    # 过滤已完成的项目
    available_projects = [p for p in all_projects if p['project_id'] not in completed_projects]
    
    # 根据难度偏好筛选
    if difficulty_preference != 'all':
        available_projects = [p for p in available_projects if p['difficulty'] == difficulty_preference]
    
    # 根据兴趣筛选
    if interests:
        filtered_projects = []
        for project in available_projects:
            for interest in interests:
                if interest.lower() in project['category'].lower() or any(interest.lower() in skill.lower() for skill in project['skills_required']):
                    filtered_projects.append(project)
                    break
        if filtered_projects:
            available_projects = filtered_projects
    
    # 按匹配分数排序并取前6个
    recommendations = sorted(available_projects, key=lambda x: x['match_score'], reverse=True)[:6]
    
    # 生成学习路径
    learning_path = []
    for i, project in enumerate(recommendations[:3]):
        learning_path.append({
            "step": i + 1,
            "project_title": project['title'],
            "description": f"第{i+1}步：{project['reason']}",
            "skills_gained": project['skills_required']
        })
    
    return jsonify({
        'recommendations': recommendations,
        'learning_path': learning_path,
        'success': True,
        'generated_by': 'fallback'
    })

def generate_computer_science_content(question, answer, analysis):
    """生成计算机科学相关内容"""
    knowledge_points = [
        {"title": "算法复杂度", "description": "时间复杂度和空间复杂度的分析方法"},
        {"title": "数据结构", "description": "线性表、树、图等数据组织方式"},
        {"title": "面向对象编程", "description": "封装、继承、多态等编程思想"},
        {"title": "计算机网络协议", "description": "TCP/IP、HTTP等网络通信协议"}
    ]
    
    experiments = [
        {
            "title": "排序算法性能比较", 
            "type": "algorithm_simulation", 
            "description": "比较不同排序算法的时间复杂度",
            "equipment": ["编程环境", "性能测试工具", "数据生成器"],
            "steps": ["实现算法", "生成测试数据", "性能测试", "结果分析"],
            "simulation_url": "https://visualgo.net/zh/sorting"
        },
        {
            "title": "数据结构可视化", 
            "type": "data_structure_simulation",
            "description": "可视化展示树、图等数据结构操作",
            "equipment": ["可视化工具", "编程环境"],
            "steps": ["构建数据结构", "执行操作", "观察变化", "分析性能"],
            "simulation_url": "https://visualgo.net/zh"
        },
        {
            "title": "网络协议分析", 
            "type": "network_simulation",
            "description": "分析TCP/IP协议的工作原理",
            "equipment": ["网络分析工具", "虚拟网络环境"],
            "steps": ["搭建网络", "发送数据包", "抓包分析", "协议解析"],
            "simulation_url": "https://www.netacad.com/courses/packet-tracer"
        },
        {
            "title": "操作系统进程调度", 
            "type": "os_simulation",
            "description": "模拟操作系统的进程调度算法",
            "equipment": ["操作系统模拟器", "进程监控工具"],
            "steps": ["创建进程", "设置调度策略", "运行模拟", "分析结果"],
            "simulation_url": "https://www.cs.usfca.edu/~galles/visualization/Algorithms.html"
        }
    ]
    
    platform_info = {
        "third_party_platform": "VisuAlgo",
        "platform_url": "https://visualgo.net/zh",
        "platform_description": "算法和数据结构可视化学习平台"
    }
    
    simulation = {
        "title": "算法可视化仿真",
        "type": "algorithm_simulator",
        "description": "交互式算法演示，可视化算法执行过程",
        **platform_info,
        "parameters": [
            {"name": "数组大小", "type": "slider", "min": 5, "max": 100, "default": 20, "unit": ""},
            {"name": "算法类型", "type": "selector", "options": ["冒泡排序", "快速排序", "归并排序"], "default": "快速排序"},
            {"name": "动画速度", "type": "slider", "min": 1, "max": 10, "default": 5, "unit": ""}
        ],
        "outputs": [
            {"name": "执行步骤", "type": "chart", "description": "显示算法执行的每个步骤"},
            {"name": "比较次数", "type": "value", "description": "统计算法的比较操作次数"}
        ]
    }
    
    return jsonify({
        'knowledge_points': knowledge_points,
        'experiments': experiments,
        'simulation': simulation,
        'success': True
    })

def generate_biology_content(question, answer, analysis):
    """生成生物学相关内容"""
    knowledge_points = [
        {"title": "细胞结构与功能", "description": "细胞膜、细胞核、细胞器的结构和功能"},
        {"title": "DNA复制与转录", "description": "遗传信息的复制和转录过程"},
        {"title": "蛋白质合成", "description": "从mRNA到蛋白质的翻译过程"},
        {"title": "酶催化机理", "description": "酶的结构、活性位点和催化机制"}
    ]
    
    experiments = [
        {
            "title": "细胞观察实验", 
            "type": "microscopy_simulation", 
            "description": "使用显微镜观察不同类型的细胞",
            "equipment": ["光学显微镜", "载玻片", "细胞样本", "染色剂"],
            "steps": ["制备样本", "显微镜调节", "观察记录", "结构分析"],
            "simulation_url": "https://www.cellsalive.com/"
        },
        {
            "title": "DNA提取实验", 
            "type": "molecular_biology_simulation",
            "description": "从生物样本中提取和纯化DNA",
            "equipment": ["离心机", "缓冲液", "乙醇", "生物样本"],
            "steps": ["细胞破碎", "蛋白质去除", "DNA沉淀", "纯化检测"],
            "simulation_url": "https://learn.genetics.utah.edu/"
        },
        {
            "title": "酶活性测定", 
            "type": "biochemistry_simulation",
            "description": "测定酶的活性和影响因素",
            "equipment": ["分光光度计", "酶溶液", "底物", "缓冲液"],
            "steps": ["配制溶液", "反应体系", "活性测定", "数据分析"],
            "simulation_url": "https://www.labxchange.org/"
        },
        {
            "title": "生态系统模拟", 
            "type": "ecology_simulation",
            "description": "模拟生态系统中的种群动态",
            "equipment": ["生态模拟软件", "数据记录工具"],
            "steps": ["设置参数", "运行模拟", "观察变化", "分析趋势"],
            "simulation_url": "https://www.ecolab-game.com/"
        }
    ]
    
    platform_info = {
        "third_party_platform": "CellsAlive",
        "platform_url": "https://www.cellsalive.com/",
        "platform_description": "细胞生物学互动学习平台"
    }
    
    simulation = {
        "title": "生物过程仿真",
        "type": "biology_simulator",
        "description": "模拟细胞分裂、蛋白质合成等生物过程",
        **platform_info,
        "parameters": [
            {"name": "温度", "type": "slider", "min": 20, "max": 40, "default": 37, "unit": "°C"},
            {"name": "pH值", "type": "slider", "min": 6, "max": 8, "default": 7.4, "unit": ""},
            {"name": "酶浓度", "type": "slider", "min": 0.1, "max": 2.0, "default": 1.0, "unit": "mg/mL"}
        ],
        "outputs": [
            {"name": "反应速率", "type": "chart", "description": "显示生化反应速率随时间变化"},
            {"name": "产物浓度", "type": "value", "description": "实时显示反应产物浓度"}
        ]
    }
    
    return jsonify({
        'knowledge_points': knowledge_points,
        'experiments': experiments,
        'simulation': simulation,
        'success': True
    })

def generate_semiconductor_content(question, answer, analysis):
    """生成半导体相关内容"""
    knowledge_points = [
        {"title": "能带理论", "description": "固体中电子能级的分布和能带结构"},
        {"title": "PN结原理", "description": "P型和N型半导体接触形成的结构"},
        {"title": "MOSFET器件", "description": "金属-氧化物-半导体场效应晶体管"},
        {"title": "集成电路工艺", "description": "芯片制造的关键工艺步骤"}
    ]
    
    experiments = [
        {
            "title": "PN结特性测试", 
            "type": "semiconductor_simulation", 
            "description": "测量PN结的伏安特性曲线",
            "equipment": ["半导体参数分析仪", "PN结样品", "探针台"],
            "steps": ["样品准备", "参数设置", "特性测试", "数据分析"],
            "simulation_url": "https://www.falstad.com/circuit/circuitjs.html"
        },
        {
            "title": "MOSFET建模", 
            "type": "device_simulation",
            "description": "建立MOSFET器件的电学模型",
            "equipment": ["SPICE仿真软件", "器件参数", "测试电路"],
            "steps": ["参数提取", "模型建立", "仿真验证", "优化调整"],
            "simulation_url": "https://www.analog.com/en/design-center/design-tools-and-calculators.html"
        },
        {
            "title": "光刻工艺仿真", 
            "type": "process_simulation",
            "description": "模拟光刻工艺的图形转移过程",
            "equipment": ["工艺仿真软件", "掩膜版图", "工艺参数"],
            "steps": ["版图设计", "工艺建模", "仿真运行", "结果分析"],
            "simulation_url": "https://www.silvaco.com/"
        },
        {
            "title": "集成电路版图设计", 
            "type": "layout_simulation",
            "description": "设计和验证集成电路版图",
            "equipment": ["EDA工具", "设计规则", "版图编辑器"],
            "steps": ["电路设计", "版图绘制", "规则检查", "后仿真"],
            "simulation_url": "https://www.cadence.com/"
        }
    ]
    
    platform_info = {
        "third_party_platform": "Falstad Circuit Simulator",
        "platform_url": "https://www.falstad.com/circuit/circuitjs.html",
        "platform_description": "在线电路和半导体器件仿真平台"
    }
    
    simulation = {
        "title": "半导体器件仿真",
        "type": "semiconductor_simulator",
        "description": "模拟半导体器件的电学特性和工艺过程",
        **platform_info,
        "parameters": [
            {"name": "掺杂浓度", "type": "slider", "min": 1e14, "max": 1e18, "default": 1e16, "unit": "cm⁻³"},
            {"name": "栅极电压", "type": "slider", "min": 0, "max": 5, "default": 2.5, "unit": "V"},
            {"name": "温度", "type": "slider", "min": 200, "max": 400, "default": 300, "unit": "K"}
        ],
        "outputs": [
            {"name": "I-V特性", "type": "chart", "description": "显示器件的电流-电压特性曲线"},
            {"name": "阈值电压", "type": "value", "description": "计算器件的阈值电压"}
        ]
    }
    
    return jsonify({
        'knowledge_points': knowledge_points,
        'experiments': experiments,
        'simulation': simulation,
        'success': True
    })

def generate_ai_content(question, answer, analysis):
    """生成人工智能相关内容"""
    knowledge_points = [
        {"title": "机器学习算法", "description": "监督学习、无监督学习和强化学习算法"},
        {"title": "神经网络结构", "description": "前馈网络、卷积网络、循环网络的结构"},
        {"title": "深度学习框架", "description": "TensorFlow、PyTorch等深度学习工具"},
        {"title": "自然语言处理", "description": "文本处理、语言模型、机器翻译技术"}
    ]
    
    experiments = [
        {
            "title": "线性回归实验", 
            "type": "ml_simulation", 
            "description": "实现和训练线性回归模型",
            "equipment": ["Python环境", "机器学习库", "数据集"],
            "steps": ["数据准备", "模型构建", "训练优化", "性能评估"],
            "simulation_url": "https://playground.tensorflow.org/"
        },
        {
            "title": "神经网络可视化", 
            "type": "neural_network_simulation",
            "description": "可视化神经网络的训练过程",
            "equipment": ["深度学习框架", "可视化工具", "训练数据"],
            "steps": ["网络设计", "参数初始化", "训练过程", "结果分析"],
            "simulation_url": "https://playground.tensorflow.org/"
        },
        {
            "title": "图像分类实验", 
            "type": "computer_vision_simulation",
            "description": "使用卷积神经网络进行图像分类",
            "equipment": ["GPU环境", "图像数据集", "CNN模型"],
            "steps": ["数据预处理", "模型训练", "验证测试", "性能优化"],
            "simulation_url": "https://teachablemachine.withgoogle.com/"
        },
        {
            "title": "强化学习游戏", 
            "type": "reinforcement_learning_simulation",
            "description": "训练智能体玩简单游戏",
            "equipment": ["强化学习环境", "智能体算法", "奖励函数"],
            "steps": ["环境搭建", "策略设计", "训练过程", "性能评估"],
            "simulation_url": "https://gym.openai.com/"
        }
    ]
    
    platform_info = {
        "third_party_platform": "TensorFlow Playground",
        "platform_url": "https://playground.tensorflow.org/",
        "platform_description": "交互式神经网络学习和实验平台"
    }
    
    simulation = {
        "title": "机器学习模型训练",
        "type": "ai_simulator",
        "description": "交互式机器学习模型训练和可视化",
        **platform_info,
        "parameters": [
            {"name": "学习率", "type": "slider", "min": 0.001, "max": 0.1, "default": 0.01, "unit": ""},
            {"name": "隐藏层数", "type": "slider", "min": 1, "max": 5, "default": 2, "unit": ""},
            {"name": "训练轮数", "type": "slider", "min": 100, "max": 5000, "default": 1000, "unit": ""}
        ],
        "outputs": [
            {"name": "损失函数", "type": "chart", "description": "显示训练过程中损失函数的变化"},
            {"name": "准确率", "type": "value", "description": "模型在测试集上的准确率"}
        ]
    }
    
    return jsonify({
        'knowledge_points': knowledge_points,
        'experiments': experiments,
        'simulation': simulation,
        'success': True
    })

def generate_physics_content(question, answer, analysis):
    """生成物理学相关内容"""
    knowledge_points = [
        {"title": "牛顿运动定律", "description": "描述物体运动与力的关系的三个基本定律"},
        {"title": "能量守恒定律", "description": "能量既不能创造也不能消灭，只能转化"},
        {"title": "波动方程", "description": "描述波的传播规律的微分方程"},
        {"title": "电磁感应", "description": "变化的磁场产生电场的物理现象"}
    ]
    
    experiments = [
        {
            "title": "单摆周期测量", 
            "type": "mechanics_simulation", 
            "description": "测量单摆周期与摆长的关系",
            "equipment": ["单摆装置", "秒表", "米尺", "量角器"],
            "steps": ["准备实验装置", "测量摆长", "释放单摆", "记录周期", "分析数据"],
            "simulation_url": "https://phet.colorado.edu/zh_CN/simulation/pendulum-lab"
        },
        {
            "title": "自由落体实验", 
            "type": "mechanics_simulation",
            "description": "验证重力加速度的测量实验",
            "equipment": ["重物", "计时器", "高度测量工具"],
            "steps": ["设置实验高度", "释放重物", "测量时间", "计算加速度"],
            "simulation_url": "https://phet.colorado.edu/zh_CN/simulation/projectile-motion"
        },
        {
            "title": "波的干涉实验", 
            "type": "wave_simulation",
            "description": "观察水波或声波的干涉现象",
            "equipment": ["波动演示器", "双缝装置", "观察屏"],
            "steps": ["设置双缝", "产生波源", "观察干涉图样", "测量波长"],
            "simulation_url": "https://phet.colorado.edu/zh_CN/simulation/wave-interference"
        },
        {
            "title": "电磁感应演示", 
            "type": "electromagnetic_simulation",
            "description": "通过线圈和磁铁演示电磁感应现象",
            "equipment": ["线圈", "磁铁", "电流表", "导线"],
            "steps": ["连接电路", "移动磁铁", "观察电流", "分析感应规律"],
            "simulation_url": "https://phet.colorado.edu/zh_CN/simulation/faradays-law"
        }
    ]
    
    # 获取第三方平台信息
    platform_info = get_third_party_platform(question, answer)
    
    simulation = {
        "title": "物理现象仿真",
        "type": "physics_simulator",
        "description": "交互式物理仿真，可调节各种物理参数观察现象",
        **platform_info,  # 添加第三方平台信息
        "parameters": [
            {"name": "重力加速度", "type": "slider", "min": 1, "max": 20, "default": 9.8, "unit": "m/s²"},
            {"name": "初始速度", "type": "slider", "min": 0, "max": 50, "default": 10, "unit": "m/s"},
            {"name": "质量", "type": "slider", "min": 0.1, "max": 10, "default": 1, "unit": "kg"}
        ],
        "outputs": [
            {"name": "运动轨迹", "type": "chart", "description": "显示物体的运动轨迹"},
            {"name": "速度变化", "type": "chart", "description": "显示速度随时间的变化"}
        ]
    }
    
    return jsonify({
        'knowledge_points': knowledge_points,
        'experiments': experiments,
        'simulation': simulation,
        'success': True
    })

def generate_mathematics_content(question, answer, analysis):
    """生成数学相关内容"""
    knowledge_points = [
        {"title": "导数的定义", "description": "函数在某点的变化率，切线斜率"},
        {"title": "积分的概念", "description": "求曲线下面积，导数的逆运算"},
        {"title": "极限理论", "description": "函数在某点附近的趋势行为"},
        {"title": "线性代数", "description": "向量、矩阵和线性变换的数学理论"}
    ]
    
    experiments = [
        {"title": "函数图像绘制", "type": "math_visualization", "description": "绘制各种函数的图像并分析性质"},
        {"title": "数值积分计算", "description": "使用数值方法计算定积分的近似值"},
        {"title": "矩阵运算验证", "description": "验证矩阵乘法、求逆等运算规律"},
        {"title": "概率分布模拟", "description": "模拟各种概率分布的随机数生成"}
    ]
    
    simulation = {
        "title": "数学函数可视化",
        "type": "math_plotter",
        "description": "交互式数学函数绘图工具，支持参数调节",
        "parameters": [
            {"name": "系数a", "type": "slider", "min": -5, "max": 5, "default": 1, "unit": ""},
            {"name": "系数b", "type": "slider", "min": -5, "max": 5, "default": 0, "unit": ""},
            {"name": "系数c", "type": "slider", "min": -5, "max": 5, "default": 0, "unit": ""}
        ],
        "outputs": [
            {"name": "函数图像", "type": "chart", "description": "显示函数y=ax²+bx+c的图像"},
            {"name": "函数性质", "type": "value", "description": "显示函数的极值、零点等性质"}
        ]
    }
    
    return jsonify({
        'knowledge_points': knowledge_points,
        'experiments': experiments,
        'simulation': simulation,
        'success': True
    })

def generate_chemistry_content(question, answer, analysis):
    """生成化学相关内容"""
    knowledge_points = [
        {"title": "化学平衡", "description": "可逆反应中正逆反应速率相等的状态"},
        {"title": "酸碱理论", "description": "阿伦尼乌斯、布朗斯特等酸碱理论"},
        {"title": "氧化还原", "description": "电子转移反应的基本原理"},
        {"title": "化学键理论", "description": "原子间结合的本质和类型"}
    ]
    
    experiments = [
        {"title": "酸碱滴定实验", "type": "chemistry_simulation", "description": "用标准溶液测定未知酸碱浓度"},
        {"title": "化学平衡移动", "description": "观察温度、浓度对化学平衡的影响"},
        {"title": "电解实验", "description": "通过电解观察氧化还原反应"},
        {"title": "分子模型搭建", "description": "使用分子模型理解化学键和分子结构"}
    ]
    
    simulation = {
        "title": "化学反应仿真",
        "type": "chemistry_simulator",
        "description": "模拟化学反应过程，观察分子行为",
        "parameters": [
            {"name": "温度", "type": "slider", "min": 273, "max": 373, "default": 298, "unit": "K"},
            {"name": "浓度", "type": "slider", "min": 0.1, "max": 2.0, "default": 1.0, "unit": "mol/L"},
            {"name": "pH值", "type": "slider", "min": 0, "max": 14, "default": 7, "unit": ""}
        ],
        "outputs": [
            {"name": "反应进程", "type": "chart", "description": "显示反应物和产物浓度变化"},
            {"name": "反应速率", "type": "value", "description": "实时显示反应速率"}
        ]
    }
    
    return jsonify({
        'knowledge_points': knowledge_points,
        'experiments': experiments,
        'simulation': simulation,
        'success': True
    })

def generate_control_content(question, answer, analysis):
    """生成控制工程相关内容"""
    knowledge_points = [
        {"title": "PID控制器", "description": "比例-积分-微分控制器的原理和调节"},
        {"title": "传递函数", "description": "描述线性时不变系统输入输出关系"},
        {"title": "系统稳定性", "description": "控制系统稳定性的判据和分析方法"},
        {"title": "频域分析", "description": "使用频率响应分析系统性能"}
    ]
    
    experiments = [
        {"title": "PID参数调节实验", "type": "control_simulation", "description": "调节PID参数观察系统响应"},
        {"title": "系统辨识实验", "description": "通过输入输出数据确定系统模型"},
        {"title": "稳定性分析实验", "description": "分析不同参数下系统的稳定性"},
        {"title": "频率响应测试", "description": "测量系统的频率响应特性"}
    ]
    
    simulation = {
        "title": "控制系统仿真",
        "type": "control_simulator",
        "description": "交互式控制系统仿真，可调节控制器参数",
        "parameters": [
            {"name": "比例增益Kp", "type": "slider", "min": 0, "max": 10, "default": 1, "unit": ""},
            {"name": "积分时间Ti", "type": "slider", "min": 0.1, "max": 10, "default": 1, "unit": "s"},
            {"name": "微分时间Td", "type": "slider", "min": 0, "max": 1, "default": 0.1, "unit": "s"}
        ],
        "outputs": [
            {"name": "系统响应", "type": "chart", "description": "显示系统的阶跃响应曲线"},
            {"name": "性能指标", "type": "value", "description": "显示超调量、调节时间等指标"}
        ]
    }
    
    return jsonify({
        'knowledge_points': knowledge_points,
        'experiments': experiments,
        'simulation': simulation,
        'success': True
    })

def generate_general_content(question, answer, analysis):
    """生成通用内容"""
    # 基于关键概念生成相关内容
    key_concepts = analysis.get('key_concepts', [])
    
    knowledge_points = []
    experiments = []
    
    # 根据关键概念生成知识点
    for i, concept in enumerate(key_concepts[:4]):
        knowledge_points.append({
            "title": f"{concept}相关理论",
            "description": f"关于{concept}的基本概念和应用"
        })
    
    # 如果关键概念不足4个，补充通用知识点
    while len(knowledge_points) < 4:
        general_topics = [
            {"title": "基础理论", "description": "相关领域的基础理论知识"},
            {"title": "实际应用", "description": "理论知识在实际中的应用"},
            {"title": "发展历史", "description": "该领域的发展历程和重要人物"},
            {"title": "前沿技术", "description": "该领域的最新发展和技术趋势"}
        ]
        knowledge_points.append(general_topics[len(knowledge_points)])
    
    # 生成实验
    for i, concept in enumerate(key_concepts[:4]):
        experiments.append({
            "title": f"{concept}验证实验",
            "type": "general_experiment",
            "description": f"通过实验验证{concept}的相关原理"
        })
    
    # 如果实验不足4个，补充通用实验
    while len(experiments) < 4:
        general_experiments = [
            {"title": "基础验证实验", "description": "验证基本理论的实验"},
            {"title": "参数测量实验", "description": "测量相关参数的实验"},
            {"title": "性能分析实验", "description": "分析系统性能的实验"},
            {"title": "应用演示实验", "description": "演示实际应用的实验"}
        ]
        experiments.append(general_experiments[len(experiments) - len(key_concepts)])
    
    simulation = {
        "title": "通用仿真实验",
        "type": "general_simulator",
        "description": "基于问题内容的交互式仿真",
        "parameters": [
            {"name": "参数1", "type": "slider", "min": 0, "max": 100, "default": 50, "unit": ""},
            {"name": "参数2", "type": "slider", "min": 0, "max": 10, "default": 5, "unit": ""},
            {"name": "参数3", "type": "slider", "min": 1, "max": 20, "default": 10, "unit": ""}
        ],
        "outputs": [
            {"name": "结果图表", "type": "chart", "description": "显示仿真结果的图表"},
            {"name": "数值结果", "type": "value", "description": "显示计算得到的数值"}
        ]
    }
    
    return jsonify({
        'knowledge_points': knowledge_points,
        'experiments': experiments,
        'simulation': simulation,
        'success': True
    })

def generate_experiment_content(question, subject, difficulty):
    """生成实验内容"""
    import asyncio
    
    try:
        # 构建实验生成的提示词
        experiment_prompt = f"""
你是一个专业的理工科实验设计助手，专门设计理工科实验。

【知识范围限定】
- 只设计理工科实验：物理、化学、电子工程、计算机科学、机械工程等
- 对于缩写词，优先使用理工科含义（如PID指比例-积分-微分控制器）
- 确保实验内容符合理工科教学要求

基于以下信息生成详细的理工科实验设计：

问题：{question}
学科领域：{subject}
难度级别：{difficulty}

请按照以下JSON格式返回实验内容：

{{
    "experiment": {{
        "title": "理工科实验标题",
        "objective": "理工科实验目的",
        "theory": "理工科理论基础",
        "materials": ["理工科实验器材1", "理工科实验器材2"],
        "procedure": [
            {{
                "step": 1,
                "description": "技术步骤描述",
                "note": "技术注意事项"
            }}
        ],
        "expected_results": "预期技术结果",
        "analysis": "技术结果分析方法",
        "safety_notes": ["理工科安全注意事项1", "理工科安全注意事项2"],
        "simulation_url": "理工科第三方仿真平台URL",
        "difficulty": "{difficulty}",
        "duration": "实验时长"
    }},
    "related_concepts": [
        {{
            "concept": "相关理工科概念",
            "explanation": "理工科概念解释"
        }}
    ],
    "extensions": [
        {{
            "title": "扩展理工科实验标题",
            "description": "扩展理工科实验描述"
        }}
    ]
}}

要求：
1. 实验设计要科学合理，符合理工科教学要求
2. 步骤要详细清晰，便于理工科学生操作
3. 根据难度级别调整理工科实验复杂度
4. 提供相关的理工科理论背景
5. 包含理工科实验安全注意事项
6. 推荐合适的理工科第三方仿真平台
7. 确保所有内容都是中文且符合理工科标准
8. 只返回JSON格式，不要其他文字
"""

        # 使用AI生成实验内容
        response = asyncio.run(llm_manager.generate_response(
            prompt=experiment_prompt,
            provider=None,
            temperature=0.7,
            max_tokens=2000
        ))
        
        if 'error' in response:
            # 使用备用方案
            return generate_fallback_experiment(question, subject, difficulty)
        
        # 尝试解析AI返回的JSON
        try:
            import json
            ai_content = response['content']
            
            # 提取JSON部分
            start_idx = ai_content.find('{')
            end_idx = ai_content.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = ai_content[start_idx:end_idx]
                parsed_content = json.loads(json_str)
                
                return jsonify({
                    **parsed_content,
                    'success': True,
                    'generated_by': 'ai'
                })
            else:
                raise ValueError("No valid JSON found in AI response")
                
        except (json.JSONDecodeError, ValueError) as e:
            print(f"JSON parsing error: {e}")
            return generate_fallback_experiment(question, subject, difficulty)
    
    except Exception as e:
        print(f"Experiment generation error: {e}")
        return generate_fallback_experiment(question, subject, difficulty)

def generate_fallback_experiment(question, subject, difficulty):
    """备用实验生成方案"""
    
    # 分析问题类型
    question_lower = question.lower()
    
    # 根据问题内容确定实验类型
    if any(keyword in question_lower for keyword in ['电路', '电阻', '电容', '电压', '电流']):
        return generate_circuit_experiment(question, difficulty)
    elif any(keyword in question_lower for keyword in ['物理', '力学', '运动', '重力']):
        return generate_physics_experiment(question, difficulty)
    elif any(keyword in question_lower for keyword in ['化学', '反应', '溶液', '酸碱']):
        return generate_chemistry_experiment(question, difficulty)
    else:
        return generate_general_experiment(question, subject, difficulty)

def generate_circuit_experiment(question, difficulty):
    """生成电路实验"""
    
    base_experiment = {
        "title": "基础电路实验",
        "objective": "验证电路基本定律，测量电路参数",
        "theory": "根据欧姆定律和基尔霍夫定律，分析电路中的电压、电流关系",
        "materials": ["面包板", "电阻器", "万用表", "导线", "直流电源"],
        "procedure": [
            {"step": 1, "description": "准备实验器材，检查万用表功能", "note": "确保万用表电池充足"},
            {"step": 2, "description": "在面包板上搭建简单电路", "note": "注意电路连接的正确性"},
            {"step": 3, "description": "使用万用表测量各点电压", "note": "测量时注意表笔极性"},
            {"step": 4, "description": "记录实验数据并分析", "note": "多次测量取平均值"}
        ],
        "expected_results": "测量值应符合理论计算值，误差在允许范围内",
        "analysis": "比较实测值与理论值，分析误差来源",
        "safety_notes": ["注意用电安全", "避免短路", "正确使用万用表"],
        "simulation_url": "https://www.falstad.com/circuit/circuitjs.html",
        "difficulty": difficulty,
        "duration": "2小时"
    }
    
    # 根据难度调整实验复杂度
    if difficulty == "hard":
        base_experiment["materials"].extend(["示波器", "信号发生器", "电容器"])
        base_experiment["procedure"].append(
            {"step": 5, "description": "使用示波器观察波形", "note": "调节示波器参数"}
        )
    
    return jsonify({
        "experiment": base_experiment,
        "related_concepts": [
            {"concept": "欧姆定律", "explanation": "电压、电流、电阻之间的关系"},
            {"concept": "基尔霍夫定律", "explanation": "电路分析的基本定律"}
        ],
        "extensions": [
            {"title": "RC电路分析", "description": "分析RC电路的充放电过程"},
            {"title": "交流电路测量", "description": "测量交流电路的有效值"}
        ],
        "success": True,
        "generated_by": "fallback"
    })

# 全局AI设置和知识库集成的辅助函数
def get_user_ai_settings(user_id):
    """获取用户的AI个性化设置"""
    settings_key = f'user_settings_{user_id}'
    
    # 默认设置
    default_settings = {
        'ai_style': 'detailed',
        'knowledge_scope': 'all',
        'auto_categorize': True,
        'smart_tags': True,
        'language': 'zh-CN',
        'theme': 'light',
        'notifications': {
            'upload_success': True,
            'ai_response': True,
            'daily_summary': False
        },
        'privacy': {
            'default_visibility': 'private',
            'allow_sharing': False
        },
        'ai_preferences': {
            'preferred_provider': 'auto',
            'response_length': 'medium',
            'include_sources': True,
            'explain_reasoning': False
        }
    }
    
    # 从session获取用户设置
    return session.get(settings_key, default_settings)

def build_enhanced_prompt(question, user_settings, use_knowledge_base, context, user_id):
    """构建增强的AI提示词，集成用户设置和知识库"""
    
    # 基础提示词 - 添加理工科知识范围限定
    prompt_parts = []
    
    # 添加理工科专业限定指令
    engineering_scope_instruction = """
你是一个专业的理工科教学助手，专门回答理工科相关问题。请严格按照以下要求：

【知识范围限定】
- 只回答理工科相关问题：数学、物理、化学、电子工程、计算机科学、机械工程、材料科学、生物工程等
- 对于缩写词，优先解释理工科含义（如PID指比例-积分-微分控制器，而非进程ID）
- 如果问题不属于理工科范围，请礼貌地说明这超出了理工科教学范围

【专业术语处理】
- 优先使用理工科专业术语和概念
- 提供准确的技术定义和公式
- 包含相关的工程应用实例
- 避免非技术领域的解释

【回答要求】
- 确保所有回答都与理工科学习和研究相关
- 提供科学准确的技术信息
- 包含必要的数学公式和技术图表说明
- 结合实际工程应用场景
"""
    
    prompt_parts.append(engineering_scope_instruction)
    
    # 添加用户偏好的回答风格
    ai_style = user_settings.get('ai_style', 'detailed')
    style_instructions = {
        'detailed': '请提供详细、深入的理工科技术回答，包含充分的解释和分析。',
        'concise': '请提供简洁明了的理工科技术回答，直接回答要点。',
        'academic': '请使用正式的学术语言和表达方式回答理工科问题。',
        'casual': '请使用友好、轻松的对话风格回答理工科问题。'
    }
    
    prompt_parts.append(style_instructions.get(ai_style, style_instructions['detailed']))
    
    # 添加知识库上下文
    if use_knowledge_base:
        knowledge_context = get_knowledge_base_context(question, user_id, user_settings)
        if knowledge_context:
            prompt_parts.append(f"\n基于用户的个人知识库内容：\n{knowledge_context}")
    
    # 添加额外上下文
    if context:
        prompt_parts.append(f"\n上下文信息：{context}")
    
    # 添加用户偏好设置
    if user_settings.get('ai_preferences', {}).get('include_sources'):
        prompt_parts.append("\n请在回答中明确标注信息来源。")
    
    if user_settings.get('ai_preferences', {}).get('explain_reasoning'):
        prompt_parts.append("\n请解释你的推理过程和逻辑。")
    
    # 构建完整提示词
    full_prompt = f"""
{' '.join(prompt_parts)}

用户问题：{question}

请根据上述要求回答用户的理工科问题。使用中文回答，确保内容专业准确且符合理工科教学要求。
"""
    
    return full_prompt.strip()

def get_knowledge_base_context(question, user_id, user_settings):
    """从用户的个人知识库获取相关上下文"""
    try:
        # 获取用户文档
        documents_key = f'user_documents_{user_id}'
        user_documents = session.get(documents_key, [])
        
        if not user_documents:
            return ""
        
        # 根据用户设置确定搜索范围
        knowledge_scope = user_settings.get('knowledge_scope', 'all')
        
        if knowledge_scope == 'recent':
            # 只搜索最近的文档
            user_documents = sorted(user_documents, key=lambda x: x.get('upload_time', ''), reverse=True)[:5]
        elif knowledge_scope == 'category':
            # 这里可以根据问题内容智能选择分类，暂时使用全部
            pass
        
        # 搜索相关文档
        relevant_docs = []
        question_lower = question.lower()
        
        for doc in user_documents:
            score = 0
            content_lower = doc.get('content', '').lower()
            filename_lower = doc.get('original_filename', '').lower()
            
            # 计算相关性分数
            words = question_lower.split()
            for word in words:
                if len(word) > 2:
                    score += content_lower.count(word) * 2
                    score += filename_lower.count(word) * 3
            
            if score > 0:
                doc['relevance_score'] = score
                relevant_docs.append(doc)
        
        # 按相关性排序，取前3个
        relevant_docs.sort(key=lambda x: x['relevance_score'], reverse=True)
        top_docs = relevant_docs[:3]
        
        if not top_docs:
            return ""
        
        # 构建知识库上下文
        context_parts = []
        for i, doc in enumerate(top_docs, 1):
            content_preview = doc['content'][:300] + "..." if len(doc['content']) > 300 else doc['content']
            context_parts.append(f"文档{i}：{doc['original_filename']}\n内容：{content_preview}")
        
        return "\n\n".join(context_parts)
        
    except Exception as e:
        print(f"获取知识库上下文失败: {e}")
        return ""

def get_knowledge_base_references(question, user_id):
    """获取知识库引用信息"""
    try:
        # 获取用户文档
        documents_key = f'user_documents_{user_id}'
        user_documents = session.get(documents_key, [])
        
        if not user_documents:
            return []
        
        # 搜索相关文档
        relevant_docs = []
        question_lower = question.lower()
        
        for doc in user_documents:
            score = 0
            content_lower = doc.get('content', '').lower()
            filename_lower = doc.get('original_filename', '').lower()
            
            # 计算相关性分数
            words = question_lower.split()
            for word in words:
                if len(word) > 2:
                    score += content_lower.count(word) * 2
                    score += filename_lower.count(word) * 3
            
            if score > 0:
                relevant_docs.append({
                    'doc_id': doc['doc_id'],
                    'filename': doc['original_filename'],
                    'relevance_score': score,
                    'category': doc.get('category', 'other'),
                    'upload_time': doc.get('upload_time', '')
                })
        
        # 按相关性排序，返回前5个
        relevant_docs.sort(key=lambda x: x['relevance_score'], reverse=True)
        return relevant_docs[:5]
        
    except Exception as e:
        print(f"获取知识库引用失败: {e}")
        return []

def generate_physics_experiment(question, difficulty):
    """生成物理实验"""
    
    base_experiment = {
        "title": "物理测量实验",
        "objective": "验证物理定律，测量物理量",
        "theory": "基于牛顿运动定律和能量守恒定律进行分析",
        "materials": ["秒表", "米尺", "天平", "小球", "斜面"],
        "procedure": [
            {"step": 1, "description": "准备实验装置", "note": "确保装置稳定"},
            {"step": 2, "description": "测量相关物理量", "note": "多次测量提高精度"},
            {"step": 3, "description": "记录实验数据", "note": "注意有效数字"},
            {"step": 4, "description": "数据处理和分析", "note": "使用图表分析"}
        ],
        "expected_results": "实验结果符合理论预期",
        "analysis": "通过图表分析验证物理定律",
        "safety_notes": ["注意实验安全", "小心器材损坏"],
        "simulation_url": "https://phet.colorado.edu/zh_CN/",
        "difficulty": difficulty,
        "duration": "1.5小时"
    }
    
    return jsonify({
        "experiment": base_experiment,
        "related_concepts": [
            {"concept": "运动学", "explanation": "描述物体运动的规律"},
            {"concept": "动力学", "explanation": "研究力与运动的关系"}
        ],
        "extensions": [
            {"title": "自由落体实验", "description": "测量重力加速度"},
            {"title": "单摆实验", "description": "验证单摆周期公式"}
        ],
        "success": True,
        "generated_by": "fallback"
    })

def generate_chemistry_experiment(question, difficulty):
    """生成化学实验"""
    
    base_experiment = {
        "title": "化学反应实验",
        "objective": "观察化学反应现象，验证化学原理",
        "theory": "基于化学反应原理和化学平衡理论",
        "materials": ["试管", "烧杯", "滴管", "化学试剂", "pH试纸"],
        "procedure": [
            {"step": 1, "description": "准备实验试剂", "note": "注意试剂的安全使用"},
            {"step": 2, "description": "按步骤进行反应", "note": "控制反应条件"},
            {"step": 3, "description": "观察反应现象", "note": "详细记录现象"},
            {"step": 4, "description": "分析实验结果", "note": "结合理论分析"}
        ],
        "expected_results": "观察到预期的化学反应现象",
        "analysis": "根据反应现象验证化学原理",
        "safety_notes": ["佩戴防护用品", "注意通风", "正确处理废液"],
        "simulation_url": "https://molview.org/",
        "difficulty": difficulty,
        "duration": "2小时"
    }
    
    return jsonify({
        "experiment": base_experiment,
        "related_concepts": [
            {"concept": "化学反应", "explanation": "原子重新组合形成新物质"},
            {"concept": "化学平衡", "explanation": "可逆反应的平衡状态"}
        ],
        "extensions": [
            {"title": "酸碱滴定", "description": "定量分析酸碱浓度"},
            {"title": "氧化还原反应", "description": "观察电子转移反应"}
        ],
        "success": True,
        "generated_by": "fallback"
    })

def generate_general_experiment(question, subject, difficulty):
    """生成通用实验"""
    
    base_experiment = {
        "title": "综合实验",
        "objective": "通过实验验证相关理论，培养实验技能",
        "theory": "基于相关学科的基础理论",
        "materials": ["基础实验器材", "测量工具", "记录表格"],
        "procedure": [
            {"step": 1, "description": "实验准备", "note": "检查器材完整性"},
            {"step": 2, "description": "实验操作", "note": "按照规范操作"},
            {"step": 3, "description": "数据记录", "note": "准确记录数据"},
            {"step": 4, "description": "结果分析", "note": "结合理论分析"}
        ],
        "expected_results": "获得符合理论预期的实验结果",
        "analysis": "通过数据分析验证理论",
        "safety_notes": ["遵守实验室安全规则", "正确使用实验器材"],
        "simulation_url": "https://www.geogebra.org/",
        "difficulty": difficulty,
        "duration": "2小时"
    }
    
    return jsonify({
        "experiment": base_experiment,
        "related_concepts": [
            {"concept": "实验方法", "explanation": "科学实验的基本方法"},
            {"concept": "数据分析", "explanation": "实验数据的处理方法"}
        ],
        "extensions": [
            {"title": "参数优化实验", "description": "优化实验参数提高精度"},
            {"title": "误差分析实验", "description": "分析实验误差来源"}
        ],
        "success": True,
        "generated_by": "fallback"
    })
