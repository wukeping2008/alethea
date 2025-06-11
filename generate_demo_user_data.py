"""
生成演示用户数据脚本
专门为客户展示AI个性化教学功能而设计
包含完整的学习数据、数字画像、项目推荐等
"""

import sys
import os
import json
from datetime import datetime, timedelta
import random

# 添加路径以便导入模块
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from flask import Flask
from models.user import db, User, Subject, Question
from models.user_analytics import UserAnalyticsManager, UserBehavior, UserDigitalPortrait, LearningSession, UserKnowledgePoint, ProjectRecommendation

def create_app():
    """创建Flask应用"""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///alethea.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'demo-key'
    
    db.init_app(app)
    return app

def generate_demo_user_data():
    """生成演示用户数据"""
    
    # 创建演示用户 - wkp
    demo_user = User(
        username='wkp',
        email='wkp@alethea.edu',
        password_hash='hashed_password_wkp',
        full_name='王科鹏',
        created_at=datetime.now() - timedelta(days=120)  # 120天前注册
    )
    
    db.session.add(demo_user)
    db.session.commit()
    
    print(f"创建演示用户: {demo_user.username} (ID: {demo_user.id})")
    
    # 创建详细的学科数据
    subjects_data = [
        {'name': '电路分析', 'description': '电路基础理论与分析方法', 'category': 'circuit_analysis'},
        {'name': '数字电路', 'description': '数字逻辑电路设计与应用', 'category': 'digital_circuits'},
        {'name': '模拟电路', 'description': '模拟电子技术基础', 'category': 'analog_circuits'},
        {'name': '信号与系统', 'description': '信号处理与系统分析', 'category': 'signals_systems'},
        {'name': '通信原理', 'description': '通信系统基础理论', 'category': 'communication'},
        {'name': '嵌入式系统', 'description': '嵌入式硬件与软件设计', 'category': 'embedded_systems'},
        {'name': '控制工程', 'description': '自动控制理论与应用', 'category': 'control_engineering'},
        {'name': '电磁场理论', 'description': '电磁场与电磁波基础', 'category': 'electromagnetics'},
        {'name': '微波技术', 'description': '微波电路与天线技术', 'category': 'microwave'},
        {'name': '数字信号处理', 'description': 'DSP理论与算法实现', 'category': 'dsp'}
    ]
    
    subjects = []
    for subject_data in subjects_data:
        existing_subject = Subject.query.filter_by(name=subject_data['name']).first()
        if existing_subject:
            subjects.append(existing_subject)
        else:
            subject = Subject(
                name=subject_data['name'],
                description=subject_data['description'],
                category=subject_data['category']
            )
            db.session.add(subject)
            subjects.append(subject)
    
    db.session.commit()
    print(f"创建了 {len(subjects)} 个学科")
    
    # 生成丰富的问题历史数据（过去120天）
    questions_data = [
        # 电路分析 - 高频提问学科
        {'question': '基尔霍夫定律的应用条件是什么？', 'subject': '电路分析', 'difficulty': 'easy', 'days_ago': 2},
        {'question': '如何用节点电压法分析复杂电路？', 'subject': '电路分析', 'difficulty': 'medium', 'days_ago': 5},
        {'question': '戴维南等效电路的求解步骤', 'subject': '电路分析', 'difficulty': 'medium', 'days_ago': 8},
        {'question': 'RLC串联谐振电路的特性分析', 'subject': '电路分析', 'difficulty': 'hard', 'days_ago': 12},
        {'question': '三相电路功率的计算方法', 'subject': '电路分析', 'difficulty': 'medium', 'days_ago': 15},
        {'question': '互感电路的分析方法', 'subject': '电路分析', 'difficulty': 'hard', 'days_ago': 20},
        {'question': '非正弦周期电流电路的分析', 'subject': '电路分析', 'difficulty': 'hard', 'days_ago': 25},
        {'question': '二端口网络的参数矩阵', 'subject': '电路分析', 'difficulty': 'hard', 'days_ago': 30},
        
        # 数字电路 - 重点学习学科
        {'question': '逻辑门的真值表如何设计？', 'subject': '数字电路', 'difficulty': 'easy', 'days_ago': 3},
        {'question': '组合逻辑电路的设计流程', 'subject': '数字电路', 'difficulty': 'medium', 'days_ago': 7},
        {'question': '触发器的工作原理和分类', 'subject': '数字电路', 'difficulty': 'medium', 'days_ago': 10},
        {'question': '计数器的设计与应用', 'subject': '数字电路', 'difficulty': 'medium', 'days_ago': 14},
        {'question': '状态机的设计方法', 'subject': '数字电路', 'difficulty': 'hard', 'days_ago': 18},
        {'question': 'FPGA的基本原理和应用', 'subject': '数字电路', 'difficulty': 'hard', 'days_ago': 22},
        
        # 模拟电路
        {'question': '运算放大器的基本电路配置', 'subject': '模拟电路', 'difficulty': 'medium', 'days_ago': 4},
        {'question': '晶体管的偏置电路设计', 'subject': '模拟电路', 'difficulty': 'medium', 'days_ago': 9},
        {'question': '反馈电路的稳定性分析', 'subject': '模拟电路', 'difficulty': 'hard', 'days_ago': 16},
        {'question': '滤波器的频率响应特性', 'subject': '模拟电路', 'difficulty': 'medium', 'days_ago': 24},
        
        # 信号与系统
        {'question': '傅里叶变换的物理意义', 'subject': '信号与系统', 'difficulty': 'medium', 'days_ago': 6},
        {'question': '拉普拉斯变换在系统分析中的应用', 'subject': '信号与系统', 'difficulty': 'hard', 'days_ago': 11},
        {'question': '系统的冲激响应和阶跃响应', 'subject': '信号与系统', 'difficulty': 'medium', 'days_ago': 17},
        {'question': '采样定理的证明和应用', 'subject': '信号与系统', 'difficulty': 'hard', 'days_ago': 26},
        
        # 通信原理
        {'question': '调制解调的基本原理', 'subject': '通信原理', 'difficulty': 'medium', 'days_ago': 13},
        {'question': '数字通信系统的性能指标', 'subject': '通信原理', 'difficulty': 'medium', 'days_ago': 19},
        {'question': '信道编码的基本概念', 'subject': '通信原理', 'difficulty': 'hard', 'days_ago': 28},
        
        # 嵌入式系统
        {'question': 'ARM处理器的体系结构', 'subject': '嵌入式系统', 'difficulty': 'medium', 'days_ago': 21},
        {'question': '实时操作系统的任务调度', 'subject': '嵌入式系统', 'difficulty': 'hard', 'days_ago': 32},
        
        # 控制工程
        {'question': 'PID控制器的参数整定方法', 'subject': '控制工程', 'difficulty': 'hard', 'days_ago': 23},
        {'question': '根轨迹法的应用', 'subject': '控制工程', 'difficulty': 'hard', 'days_ago': 35},
        
        # 其他学科的问题
        {'question': '电磁波的传播特性', 'subject': '电磁场理论', 'difficulty': 'medium', 'days_ago': 27},
        {'question': '微带线的特性阻抗计算', 'subject': '微波技术', 'difficulty': 'hard', 'days_ago': 40},
        {'question': 'FFT算法的实现原理', 'subject': '数字信号处理', 'difficulty': 'hard', 'days_ago': 45}
    ]
    
    # 创建问题历史记录
    for q_data in questions_data:
        subject = next((s for s in subjects if s.name == q_data['subject']), subjects[0])
        
        question = Question(
            user_id=demo_user.id,
            subject_id=subject.id,
            content=q_data['question'],
            response=f"这是关于{q_data['question']}的详细AI回答，包含了理论分析、实例说明和应用场景。",
            provider='claude',
            model='claude-3-opus',
            created_at=datetime.now() - timedelta(days=q_data['days_ago'])
        )
        db.session.add(question)
    
    db.session.commit()
    print(f"创建了 {len(questions_data)} 个问题历史记录")
    
    # 生成详细的用户行为数据
    analytics_manager = UserAnalyticsManager(db)
    
    # 定义行为类型和权重（模拟真实学习模式）
    behavior_patterns = {
        'question_asked': {'weight': 0.25, 'duration_range': (60, 300)},
        'experiment_viewed': {'weight': 0.20, 'duration_range': (300, 1800)},
        'simulation_run': {'weight': 0.15, 'duration_range': (600, 2400)},
        'project_viewed': {'weight': 0.15, 'duration_range': (180, 900)},
        'knowledge_point_studied': {'weight': 0.10, 'duration_range': (120, 600)},
        'video_watched': {'weight': 0.08, 'duration_range': (300, 1200)},
        'document_downloaded': {'weight': 0.04, 'duration_range': (30, 120)},
        'quiz_completed': {'weight': 0.03, 'duration_range': (300, 900)}
    }
    
    # 生成过去120天的学习行为数据
    total_behaviors = 0
    for day in range(120):
        date = datetime.now() - timedelta(days=day)
        
        # 模拟学习强度变化（工作日更活跃）
        weekday = date.weekday()
        if weekday < 5:  # 工作日
            daily_interactions = random.randint(3, 12)
        else:  # 周末
            daily_interactions = random.randint(1, 6)
        
        # 根据时间衰减调整活跃度
        activity_factor = max(0.3, 1 - (day / 120) * 0.7)
        daily_interactions = int(daily_interactions * activity_factor)
        
        for _ in range(daily_interactions):
            # 根据权重选择行为类型
            behavior_type = random.choices(
                list(behavior_patterns.keys()),
                weights=[p['weight'] for p in behavior_patterns.values()]
            )[0]
            
            # 选择学科（偏向电路分析和数字电路）
            subject_weights = [
                0.3 if s.name == '电路分析' else
                0.25 if s.name == '数字电路' else
                0.15 if s.name == '模拟电路' else
                0.1 if s.name == '信号与系统' else
                0.05 for s in subjects
            ]
            subject = random.choices(subjects, weights=subject_weights)[0]
            
            # 生成行为内容
            duration_range = behavior_patterns[behavior_type]['duration_range']
            duration = random.randint(*duration_range)
            
            behavior = UserBehavior(
                user_id=demo_user.id,
                action_type=behavior_type,
                action_data={
                    'content': f"{behavior_type.replace('_', ' ').title()} - {subject.name}",
                    'difficulty': random.choice(['easy', 'medium', 'hard']),
                    'completion_rate': random.uniform(0.7, 1.0)
                },
                subject_id=subject.id,
                session_id=f"session_{day}_{_}",
                duration=duration,
                created_at=date - timedelta(
                    hours=random.randint(8, 22),
                    minutes=random.randint(0, 59)
                )
            )
            db.session.add(behavior)
            total_behaviors += 1
    
    db.session.commit()
    print(f"创建了 {total_behaviors} 条用户行为记录")
    
    # 生成知识点掌握数据
    knowledge_points = [
        # 电路分析知识点
        {'name': '基尔霍夫定律', 'subject': '电路分析', 'mastery': 0.95, 'study_time': 180},
        {'name': '节点电压法', 'subject': '电路分析', 'mastery': 0.88, 'study_time': 240},
        {'name': '戴维南定理', 'subject': '电路分析', 'mastery': 0.82, 'study_time': 200},
        {'name': 'RLC谐振电路', 'subject': '电路分析', 'mastery': 0.75, 'study_time': 320},
        {'name': '三相电路', 'subject': '电路分析', 'mastery': 0.70, 'study_time': 280},
        
        # 数字电路知识点
        {'name': '逻辑门电路', 'subject': '数字电路', 'mastery': 0.92, 'study_time': 150},
        {'name': '组合逻辑设计', 'subject': '数字电路', 'mastery': 0.85, 'study_time': 220},
        {'name': '触发器原理', 'subject': '数字电路', 'mastery': 0.78, 'study_time': 260},
        {'name': '计数器设计', 'subject': '数字电路', 'mastery': 0.72, 'study_time': 300},
        {'name': '状态机设计', 'subject': '数字电路', 'mastery': 0.65, 'study_time': 350},
        
        # 模拟电路知识点
        {'name': '运算放大器', 'subject': '模拟电路', 'mastery': 0.80, 'study_time': 200},
        {'name': '晶体管偏置', 'subject': '模拟电路', 'mastery': 0.75, 'study_time': 180},
        {'name': '反馈电路', 'subject': '模拟电路', 'mastery': 0.68, 'study_time': 250},
        
        # 其他学科知识点
        {'name': '傅里叶变换', 'subject': '信号与系统', 'mastery': 0.73, 'study_time': 220},
        {'name': '调制解调', 'subject': '通信原理', 'mastery': 0.70, 'study_time': 190},
        {'name': 'ARM架构', 'subject': '嵌入式系统', 'mastery': 0.65, 'study_time': 280}
    ]
    
    for kp_data in knowledge_points:
        subject = next((s for s in subjects if s.name == kp_data['subject']), subjects[0])
        
        knowledge_point = UserKnowledgePoint(
            user_id=demo_user.id,
            subject_id=subject.id,
            knowledge_point=kp_data['name'],
            mastery_level=kp_data['mastery'],
            interaction_count=random.randint(3, 15),
            last_interaction=datetime.now() - timedelta(days=random.randint(1, 30))
        )
        db.session.add(knowledge_point)
    
    db.session.commit()
    print(f"创建了 {len(knowledge_points)} 个知识点掌握记录")
    
    # 生成学习会话数据
    for i in range(50):  # 50个学习会话
        session_date = datetime.now() - timedelta(days=random.randint(0, 120))
        session_duration = random.randint(1800, 7200)  # 30分钟到2小时
        
        session = LearningSession(
            user_id=demo_user.id,
            session_id=f"session_{i}_{random.randint(1000, 9999)}",
            start_time=session_date,
            end_time=session_date + timedelta(seconds=session_duration),
            duration=session_duration,
            pages_visited=[f"page_{j}" for j in range(random.randint(5, 20))],
            actions_performed=[f"action_{j}" for j in range(random.randint(8, 25))],
            subjects_explored=[random.choice(subjects).id for _ in range(random.randint(1, 4))],
            questions_asked=random.randint(1, 8),
            projects_viewed=random.randint(0, 5),
            engagement_score=random.uniform(0.6, 0.95)
        )
        db.session.add(session)
    
    db.session.commit()
    print("创建了学习会话数据")
    
    # 生成项目推荐数据
    project_recommendations = [
        {
            'title': '智能家居控制系统',
            'description': '基于STM32的智能家居控制系统设计，包含传感器数据采集、无线通信和移动端控制',
            'difficulty': 'medium',
            'estimated_duration': '4-6周',
            'skills_required': ['嵌入式编程', '传感器应用', '无线通信', 'APP开发'],
            'match_score': 0.92,
            'reason': '基于您在嵌入式系统和数字电路方面的扎实基础，这个项目能很好地整合您的知识点'
        },
        {
            'title': '数字滤波器设计与实现',
            'description': '使用MATLAB和FPGA实现FIR/IIR数字滤波器，包含理论分析和硬件验证',
            'difficulty': 'hard',
            'estimated_duration': '6-8周',
            'skills_required': ['数字信号处理', 'MATLAB编程', 'FPGA开发', '算法优化'],
            'match_score': 0.88,
            'reason': '您在信号与系统方面表现优秀，这个项目能进一步提升您的DSP技能'
        },
        {
            'title': '电路仿真分析平台',
            'description': '开发基于Web的电路仿真分析工具，支持直流、交流和瞬态分析',
            'difficulty': 'hard',
            'estimated_duration': '8-10周',
            'skills_required': ['电路分析', 'Web开发', '数值计算', '算法设计'],
            'match_score': 0.85,
            'reason': '您在电路分析方面的深厚功底使您非常适合这个综合性项目'
        },
        {
            'title': '无线传感器网络节点',
            'description': '设计低功耗无线传感器网络节点，实现数据采集和无线传输',
            'difficulty': 'medium',
            'estimated_duration': '3-4周',
            'skills_required': ['嵌入式系统', '无线通信', '低功耗设计', '传感器技术'],
            'match_score': 0.82,
            'reason': '结合您的嵌入式和通信原理知识，这个项目能提升您的实际工程能力'
        }
    ]
    
    for i, proj_data in enumerate(project_recommendations):
        recommendation = ProjectRecommendation(
            user_id=demo_user.id,
            project_id=f"project_{i+1}",
            project_title=proj_data['title'],
            recommendation_score=proj_data['match_score'],
            recommendation_reason=proj_data['reason'],
            difficulty_match=0.8,
            interest_match=0.9,
            skill_development=proj_data['skills_required'],
            is_viewed=i < 2,  # 前两个项目已查看
            is_started=i < 1,  # 第一个项目已开始
            is_completed=False
        )
        db.session.add(recommendation)
    
    db.session.commit()
    print(f"创建了 {len(project_recommendations)} 个项目推荐")
    
    # 生成AI数字画像
    try:
        # 手动创建详细的数字画像数据
        portrait_data = {
            'learning_style': '理论与实践并重型',
            'strengths': ['电路分析能力强', '逻辑思维清晰', '学习主动性高', '问题解决能力优秀'],
            'areas_for_improvement': ['高级数学应用', '系统级设计思维', '项目管理能力'],
            'preferred_subjects': ['电路分析', '数字电路', '模拟电路'],
            'learning_patterns': {
                'peak_hours': '9:00-11:00, 14:00-16:00',
                'session_duration': '平均45分钟',
                'question_frequency': '每天2-3个问题',
                'preferred_difficulty': '中等偏难'
            },
            'engagement_metrics': {
                'total_study_time': '156小时',
                'avg_session_length': '52分钟',
                'completion_rate': '87%',
                'consistency_score': '0.85'
            },
            'ai_insights': '王科鹏同学在电路分析和数字电路方面表现突出，具有扎实的理论基础和较强的实践能力。学习态度积极主动，善于提出深入的技术问题。建议在保持现有优势的基础上，加强系统级设计和跨学科知识的整合应用。',
            'recommendations': [
                '参与更多综合性项目，提升系统设计能力',
                '加强数学建模和算法优化训练',
                '多参与团队协作项目，提升沟通协调能力',
                '关注前沿技术发展，拓宽知识视野'
            ]
        }
        
        digital_portrait = UserDigitalPortrait(
            user_id=demo_user.id,
            learning_style=portrait_data['learning_style'],
            strengths=portrait_data['strengths'],
            improvement_areas=portrait_data['areas_for_improvement'],
            preferred_subjects=portrait_data['preferred_subjects'],
            engagement_pattern=portrait_data['learning_patterns'],
            ai_insights=portrait_data['ai_insights'],
            confidence_score=0.89,
            last_updated=datetime.now()
        )
        db.session.add(digital_portrait)
        db.session.commit()
        
        print("创建了详细的AI数字画像")
        
    except Exception as e:
        print(f"创建数字画像时出错: {e}")
    
    # 计算统计数据
    total_questions = len(questions_data)
    study_days = 120
    total_projects = len([r for r in project_recommendations if r['match_score'] > 0.8])
    learning_points = int(total_behaviors * 0.5 + total_questions * 2)
    
    print("\n=== 演示用户数据生成完成 ===")
    print(f"用户名: {demo_user.username} ({demo_user.full_name})")
    print(f"用户ID: {demo_user.id}")
    print(f"学习天数: {study_days}")
    print(f"提问次数: {total_questions}")
    print(f"项目参与: {total_projects}")
    print(f"学习积分: {learning_points}")
    print(f"学科数量: {len(subjects)}")
    print(f"知识点掌握: {len(knowledge_points)}")
    print(f"行为记录: {total_behaviors}")
    print(f"项目推荐: {len(project_recommendations)}")
    print("\n现在可以登录用户 'wkp' 查看完整的AI个性化教学展示效果！")
    
    return demo_user.id

def main():
    """主函数"""
    app = create_app()
    
    with app.app_context():
        # 创建数据库表
        db.create_all()
        
        # 检查是否已存在演示用户
        existing_user = User.query.filter_by(username='wkp').first()
        if existing_user:
            print("演示用户已存在，删除旧数据...")
            # 删除相关数据
            UserBehavior.query.filter_by(user_id=existing_user.id).delete()
            LearningSession.query.filter_by(user_id=existing_user.id).delete()
            Question.query.filter_by(user_id=existing_user.id).delete()
            UserDigitalPortrait.query.filter_by(user_id=existing_user.id).delete()
            UserKnowledgePoint.query.filter_by(user_id=existing_user.id).delete()
            ProjectRecommendation.query.filter_by(user_id=existing_user.id).delete()
            db.session.delete(existing_user)
            db.session.commit()
        
        # 生成新的演示数据
        user_id = generate_demo_user_data()
        
        print(f"\n演示用户创建成功！用户ID: {user_id}")
        print("\n可以使用以下方式测试：")
        print("1. 登录用户名: wkp")
        print("2. 访问个人中心查看完整数据")
        print("3. 测试API接口:")
        print("   - 数字画像: GET /api/analytics/profile/{user_id}")
        print("   - 项目推荐: POST /api/llm/recommend-projects")
        print("   - 学习分析: GET /api/analytics/learning-analysis/{user_id}")

if __name__ == '__main__':
    main()
