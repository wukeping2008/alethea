"""
生成测试用户数据脚本
用于演示AI数字画像和项目推荐功能
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
from models.user_analytics import UserAnalyticsManager, UserBehavior, UserDigitalPortrait, LearningSession

def create_app():
    """创建Flask应用"""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///alethea.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'test-key'
    
    db.init_app(app)
    return app

def generate_test_user_data():
    """生成测试用户数据"""
    
    # 创建测试用户
    test_user = User(
        username='demo_student',
        email='demo@alethea.edu',
        password_hash='hashed_password_demo',  # 实际应用中应该是哈希后的密码
        full_name='张明华',
        created_at=datetime.now() - timedelta(days=90)  # 90天前注册
    )
    
    db.session.add(test_user)
    db.session.commit()
    
    print(f"创建测试用户: {test_user.username} (ID: {test_user.id})")
    
    # 创建学科数据
    subjects_data = [
        {'name': '电子电路', 'description': '模拟电路与数字电路基础', 'category': 'electronics'},
        {'name': '信号处理', 'description': '数字信号处理理论与应用', 'category': 'signal_processing'},
        {'name': '控制系统', 'description': '自动控制原理与应用', 'category': 'control'},
        {'name': '微处理器', 'description': '单片机原理与应用', 'category': 'microprocessor'},
        {'name': '通信原理', 'description': '通信系统基础理论', 'category': 'communication'},
        {'name': '电磁场理论', 'description': '电磁场与电磁波', 'category': 'electromagnetics'},
        {'name': '数字图像处理', 'description': '图像处理算法与应用', 'category': 'image_processing'},
        {'name': '嵌入式系统', 'description': '嵌入式硬件与软件设计', 'category': 'embedded'}
    ]
    
    subjects = []
    for subject_data in subjects_data:
        # 检查学科是否已存在
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
    print(f"使用了 {len(subjects)} 个学科（包括已存在的）")
    
    # 生成问题历史数据
    questions_data = [
        # 电子电路相关问题
        {'question': '运算放大器的基本原理是什么？', 'subject': '电子电路', 'difficulty': 'medium'},
        {'question': '如何设计一个反相放大器电路？', 'subject': '电子电路', 'difficulty': 'medium'},
        {'question': '什么是共模抑制比？', 'subject': '电子电路', 'difficulty': 'hard'},
        {'question': '二极管的伏安特性曲线如何分析？', 'subject': '电子电路', 'difficulty': 'easy'},
        {'question': '晶体管的三种工作状态是什么？', 'subject': '电子电路', 'difficulty': 'medium'},
        {'question': '如何计算RC滤波器的截止频率？', 'subject': '电子电路', 'difficulty': 'medium'},
        {'question': '差分放大器的工作原理', 'subject': '电子电路', 'difficulty': 'hard'},
        {'question': '什么是负反馈？它有什么作用？', 'subject': '电子电路', 'difficulty': 'medium'},
        
        # 信号处理相关问题
        {'question': '什么是傅里叶变换？', 'subject': '信号处理', 'difficulty': 'medium'},
        {'question': '数字滤波器与模拟滤波器的区别', 'subject': '信号处理', 'difficulty': 'medium'},
        {'question': '如何设计FIR滤波器？', 'subject': '信号处理', 'difficulty': 'hard'},
        {'question': '采样定理的内容是什么？', 'subject': '信号处理', 'difficulty': 'medium'},
        {'question': 'FFT算法的基本思想', 'subject': '信号处理', 'difficulty': 'hard'},
        
        # 控制系统相关问题
        {'question': 'PID控制器的参数如何调节？', 'subject': '控制系统', 'difficulty': 'hard'},
        {'question': '什么是系统的稳定性？', 'subject': '控制系统', 'difficulty': 'medium'},
        {'question': '开环控制和闭环控制的区别', 'subject': '控制系统', 'difficulty': 'easy'},
        {'question': '传递函数的物理意义', 'subject': '控制系统', 'difficulty': 'medium'},
        
        # 微处理器相关问题
        {'question': '单片机的基本结构包括哪些部分？', 'subject': '微处理器', 'difficulty': 'easy'},
        {'question': '如何编写单片机的中断服务程序？', 'subject': '微处理器', 'difficulty': 'medium'},
        {'question': 'I2C通信协议的工作原理', 'subject': '微处理器', 'difficulty': 'medium'},
        {'question': 'SPI和UART通信的区别', 'subject': '微处理器', 'difficulty': 'medium'},
        
        # 通信原理相关问题
        {'question': '什么是调制和解调？', 'subject': '通信原理', 'difficulty': 'medium'},
        {'question': 'AM和FM调制的区别', 'subject': '通信原理', 'difficulty': 'medium'},
        {'question': '数字通信系统的基本组成', 'subject': '通信原理', 'difficulty': 'easy'},
        
        # 电磁场理论相关问题
        {'question': '麦克斯韦方程组的物理意义', 'subject': '电磁场理论', 'difficulty': 'hard'},
        {'question': '电磁波的传播特性', 'subject': '电磁场理论', 'difficulty': 'medium'},
        
        # 数字图像处理相关问题
        {'question': '图像的空间域和频域处理有什么区别？', 'subject': '数字图像处理', 'difficulty': 'medium'},
        {'question': '如何进行图像的边缘检测？', 'subject': '数字图像处理', 'difficulty': 'medium'},
        
        # 嵌入式系统相关问题
        {'question': '嵌入式系统的特点是什么？', 'subject': '嵌入式系统', 'difficulty': 'easy'},
        {'question': '实时操作系统的调度算法', 'subject': '嵌入式系统', 'difficulty': 'hard'}
    ]
    
    # 为每个问题创建历史记录
    for i, q_data in enumerate(questions_data):
        # 找到对应的学科
        subject = next((s for s in subjects if s.name == q_data['subject']), subjects[0])
        
        # 创建问题历史
        question = Question(
            user_id=test_user.id,
            subject_id=subject.id,
            content=q_data['question'],
            response='这是一个详细的AI回答，解释了相关概念和原理。',
            provider='claude',
            model='claude-3-opus',
            created_at=datetime.now() - timedelta(days=random.randint(1, 89))
        )
        db.session.add(question)
    
    db.session.commit()
    print(f"创建了 {len(questions_data)} 个问题历史记录")
    
    # 创建用户交互数据
    analytics_manager = UserAnalyticsManager(db)
    
    # 生成多样化的交互数据
    interaction_types = [
        'question_asked', 'experiment_viewed', 'simulation_run', 
        'project_viewed', 'knowledge_point_studied', 'video_watched',
        'document_downloaded', 'quiz_completed', 'lab_report_submitted'
    ]
    
    # 生成过去90天的交互数据
    for day in range(90):
        date = datetime.now() - timedelta(days=day)
        
        # 每天随机生成1-8个交互
        daily_interactions = random.randint(1, 8)
        
        for _ in range(daily_interactions):
            interaction_type = random.choice(interaction_types)
            subject = random.choice(subjects)
            
            # 根据交互类型生成不同的内容
            if interaction_type == 'question_asked':
                content = f"询问了关于{subject.name}的问题"
            elif interaction_type == 'experiment_viewed':
                content = f"查看了{subject.name}相关实验"
            elif interaction_type == 'simulation_run':
                content = f"运行了{subject.name}仿真实验"
            elif interaction_type == 'project_viewed':
                content = f"浏览了{subject.name}项目案例"
            else:
                content = f"学习了{subject.name}相关内容"
            
            behavior = UserBehavior(
                user_id=test_user.id,
                action_type=interaction_type,
                action_data={'content': content},
                subject_id=subject.id,
                session_id=f"session_{day}_{_}",
                duration=random.randint(30, 1800),  # 30秒到30分钟
                created_at=date - timedelta(
                    hours=random.randint(8, 22),
                    minutes=random.randint(0, 59)
                )
            )
            db.session.add(behavior)
    
    db.session.commit()
    print("创建了用户交互数据")
    
    # 创建学习进度数据
    for subject in subjects:
        # 根据问题数量和交互频率计算进度
        subject_questions = [q for q in questions_data if q['subject'] == subject.name]
        progress_percentage = min(95, len(subject_questions) * 10 + random.randint(10, 30))
        
        # 创建学习会话数据
        session = LearningSession(
            user_id=test_user.id,
            session_id=f"session_{subject.id}_{random.randint(1000, 9999)}",
            start_time=datetime.now() - timedelta(days=random.randint(0, 7)),
            end_time=datetime.now() - timedelta(days=random.randint(0, 7)) + timedelta(minutes=random.randint(30, 120)),
            duration=random.randint(1800, 7200),  # 30分钟到2小时
            pages_visited=[f"page_{i}" for i in range(random.randint(3, 10))],
            actions_performed=[f"action_{i}" for i in range(random.randint(5, 15))],
            subjects_explored=[subject.id],
            questions_asked=random.randint(1, 5),
            projects_viewed=random.randint(0, 3),
            engagement_score=random.uniform(0.6, 1.0)
        )
        db.session.add(session)
    
    db.session.commit()
    print("创建了学习进度数据")
    
    # 生成用户画像
    try:
        success, profile_data = analytics_manager.generate_digital_portrait(test_user.id)
        if success:
            print("生成了用户数字画像")
            print(f"用户画像摘要: {profile_data.get('ai_insights', 'N/A')}")
        else:
            print(f"生成用户画像失败: {profile_data}")
    except Exception as e:
        print(f"生成用户画像时出错: {e}")
    
    print("\n=== 测试数据生成完成 ===")
    print(f"测试用户: {test_user.username}")
    print(f"用户ID: {test_user.id}")
    print(f"学科数量: {len(subjects)}")
    print(f"问题历史: {len(questions_data)}")
    print("可以使用此用户测试AI数字画像和项目推荐功能")
    
    return test_user.id

def main():
    """主函数"""
    app = create_app()
    
    with app.app_context():
        # 创建数据库表
        db.create_all()
        
        # 检查是否已存在测试用户
        existing_user = User.query.filter_by(username='demo_student').first()
        if existing_user:
            print("测试用户已存在，删除旧数据...")
            # 删除相关数据
            UserBehavior.query.filter_by(user_id=existing_user.id).delete()
            LearningSession.query.filter_by(user_id=existing_user.id).delete()
            Question.query.filter_by(user_id=existing_user.id).delete()
            UserDigitalPortrait.query.filter_by(user_id=existing_user.id).delete()
            db.session.delete(existing_user)
            db.session.commit()
        
        # 生成新的测试数据
        user_id = generate_test_user_data()
        
        print(f"\n测试用户创建成功！用户ID: {user_id}")
        print("现在可以使用以下API测试功能：")
        print("1. 数字画像: GET /api/analytics/profile/{user_id}")
        print("2. 项目推荐: POST /api/llm/recommend-projects")
        print("3. 学习分析: GET /api/analytics/learning-analysis/{user_id}")

if __name__ == '__main__':
    main()
