#!/usr/bin/env python3
"""
简化的用户wkp学习数据生成脚本
直接向数据库插入模拟数据
"""

import sqlite3
import json
import random
from datetime import datetime, timedelta

def create_sample_data():
    """创建示例学习数据"""
    
    # 连接数据库
    db_path = 'instance/alethea.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("🚀 开始生成用户wkp的学习数据...")
    
    # 1. 检查用户是否存在，如果不存在则创建
    cursor.execute("SELECT id FROM users WHERE username = ?", ('wkp',))
    user_result = cursor.fetchone()
    
    if user_result:
        user_id = user_result[0]
        print(f"✅ 用户wkp已存在，ID: {user_id}")
    else:
        # 创建用户
        cursor.execute("""
            INSERT INTO users (username, email, password_hash, full_name, student_id, major, grade, phone, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            'wkp', 'wkp@alethea.edu', 'hashed_password', '王科鹏', 
            'STU2024001', '电子信息工程', '大三', '13800138001', datetime.now()
        ))
        user_id = cursor.lastrowid
        print(f"✅ 用户wkp创建成功，ID: {user_id}")
    
    # 2. 创建学科数据
    subjects = [
        ('电路分析', 'EE101', '电路基础理论与分析方法', '专业基础课', 4, 3),
        ('数字电路', 'EE201', '数字逻辑设计与分析', '专业核心课', 4, 4),
        ('模拟电路', 'EE202', '模拟电子技术基础', '专业核心课', 4, 4),
        ('信号与系统', 'EE301', '信号处理与系统分析', '专业核心课', 3, 5),
        ('通信原理', 'EE401', '通信系统原理与技术', '专业选修课', 3, 4),
        ('嵌入式系统', 'EE402', '嵌入式系统设计与开发', '专业选修课', 3, 4)
    ]
    
    subject_ids = {}
    for subject in subjects:
        cursor.execute("SELECT id FROM subjects WHERE code = ?", (subject[1],))
        existing = cursor.fetchone()
        
        if existing:
            subject_ids[subject[0]] = existing[0]
            print(f"✅ 学科已存在: {subject[0]}")
        else:
            cursor.execute("""
                INSERT INTO subjects (name, code, description, category, credits, difficulty_level, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (*subject, datetime.now()))
            subject_ids[subject[0]] = cursor.lastrowid
            print(f"✅ 学科创建成功: {subject[0]}")
    
    # 3. 生成问答历史数据
    questions_data = [
        {
            'subject': '电路分析',
            'questions': [
                ('什么是欧姆定律？请解释其物理意义和数学表达式。', '欧姆定律是电路分析的基础定律...', 2, 'claude', 95),
                ('请解释基尔霍夫电流定律(KCL)和电压定律(KVL)。', 'KCL(基尔霍夫电流定律)：在任意时刻...', 3, 'gemini', 88),
                ('什么是戴维南定理？如何应用戴维南等效电路？', '戴维南定理：任何线性有源二端网络...', 4, 'ollama_deepseek', 92)
            ]
        },
        {
            'subject': '数字电路',
            'questions': [
                ('什么是布尔代数？请列举基本的布尔运算。', '布尔代数是处理逻辑变量的数学体系...', 3, 'claude', 90),
                ('请解释D触发器的工作原理和真值表。', 'D触发器是边沿触发的存储器件...', 4, 'ali_qwen', 85)
            ]
        },
        {
            'subject': '模拟电路',
            'questions': [
                ('请解释三极管的三种工作状态及其特点。', '三极管有三种工作状态...', 4, 'gemini', 87),
                ('什么是运算放大器？请说明理想运放的特点。', '运算放大器(Op-Amp)是高增益的直流耦合放大器...', 4, 'claude', 93)
            ]
        }
    ]
    
    # 插入问答数据
    base_time = datetime.now() - timedelta(days=90)
    question_count = 0
    
    for subject_data in questions_data:
        subject_name = subject_data['subject']
        subject_id = subject_ids.get(subject_name)
        
        if subject_id:
            for i, (question, answer, difficulty, ai_model, score) in enumerate(subject_data['questions']):
                question_time = base_time + timedelta(days=random.randint(0, 85), hours=random.randint(0, 23))
                
                cursor.execute("""
                    INSERT INTO question_history 
                    (user_id, subject_id, question, answer, ai_model, response_time, satisfaction_rating, difficulty_level, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    user_id, subject_id, question, answer, ai_model, 
                    random.uniform(2.0, 8.0), random.randint(4, 5), difficulty, question_time
                ))
                question_count += 1
    
    print(f"✅ 生成问答记录: {question_count}条")
    
    # 4. 生成学习行为数据
    behavior_types = ['question_asked', 'experiment_completed', 'project_milestone', 'study_session', 'resource_accessed']
    
    for i in range(50):  # 生成50条行为记录
        behavior_time = datetime.now() - timedelta(days=random.randint(1, 90))
        subject_id = random.choice(list(subject_ids.values()))
        
        cursor.execute("""
            INSERT INTO user_behaviors 
            (user_id, behavior_type, subject_id, duration_minutes, engagement_score, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            user_id, random.choice(behavior_types), subject_id,
            random.randint(10, 120), random.uniform(0.6, 1.0), behavior_time
        ))
    
    print("✅ 生成学习行为记录: 50条")
    
    # 5. 生成知识点掌握数据
    knowledge_points = {
        '电路分析': ['欧姆定律', '基尔霍夫定律', '节点电压法', '戴维南定理', 'RC电路'],
        '数字电路': ['布尔代数', '逻辑门', '组合逻辑电路', '触发器', '计数器'],
        '模拟电路': ['三极管', '运算放大器', '反馈电路', '振荡器', '滤波器'],
        '信号与系统': ['卷积', '傅里叶变换', '拉普拉斯变换', '滤波器设计'],
        '通信原理': ['调制解调', 'AM调制', 'FM调制', 'OFDM'],
        '嵌入式系统': ['ARM架构', 'STM32', '实时操作系统', '传感器接口']
    }
    
    kp_count = 0
    for subject_name, kps in knowledge_points.items():
        subject_id = subject_ids.get(subject_name)
        if subject_id:
            for kp in kps:
                cursor.execute("""
                    INSERT INTO user_knowledge_points 
                    (user_id, subject_id, knowledge_point, mastery_level, confidence_level, last_updated)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    user_id, subject_id, kp, 
                    random.uniform(0.6, 0.95), random.uniform(0.5, 0.9),
                    datetime.now() - timedelta(days=random.randint(1, 30))
                ))
                kp_count += 1
    
    print(f"✅ 生成知识点掌握数据: {kp_count}个")
    
    # 6. 生成项目推荐数据
    projects = [
        ('智能家居控制系统', '基于STM32的智能家居控制系统设计与实现', 4, 'completed', 100),
        ('数字信号处理器设计', '基于FPGA的FIR滤波器设计与实现', 5, 'completed', 100),
        ('无线通信系统仿真', 'OFDM通信系统的MATLAB仿真与性能分析', 4, 'in_progress', 75),
        ('模拟电路综合设计', '音频功率放大器的设计与制作', 4, 'planned', 0)
    ]
    
    for project in projects:
        cursor.execute("""
            INSERT INTO project_recommendations 
            (user_id, project_name, description, difficulty_level, status, progress, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, *project, datetime.now()))
    
    print(f"✅ 生成项目推荐数据: {len(projects)}个")
    
    # 7. 生成数字画像数据
    portrait_data = {
        'learning_style': 'visual_kinesthetic',
        'preferred_subjects': ['电路分析', '数字电路', '嵌入式系统'],
        'difficulty_preference': 'medium_high',
        'study_time_preference': 'evening',
        'learning_pace': 'moderate',
        'strengths': ['逻辑思维', '动手实践', '系统设计'],
        'improvement_areas': ['理论深度', '数学基础'],
        'engagement_level': 0.85,
        'completion_rate': 0.78,
        'average_score': 89.5
    }
    
    cursor.execute("""
        INSERT INTO user_digital_portraits 
        (user_id, portrait_data, generated_at, updated_at)
        VALUES (?, ?, ?, ?)
    """, (user_id, json.dumps(portrait_data, ensure_ascii=False), datetime.now(), datetime.now()))
    
    print("✅ 生成数字画像数据")
    
    # 提交事务
    conn.commit()
    conn.close()
    
    print("🎉 用户wkp学习数据生成完成！")
    print(f"📊 数据统计:")
    print(f"   - 学科数量: {len(subjects)}")
    print(f"   - 问答记录: {question_count}条")
    print(f"   - 学习行为: 50条")
    print(f"   - 知识点: {kp_count}个")
    print(f"   - 项目推荐: {len(projects)}个")
    print(f"   - 数字画像: 1个")

if __name__ == "__main__":
    try:
        create_sample_data()
    except Exception as e:
        print(f"❌ 数据生成失败: {str(e)}")
