from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Float, Text, Boolean, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class LearningSession(Base):
    """学习会话记录"""
    __tablename__ = 'learning_sessions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    session_start = Column(DateTime, default=datetime.utcnow)
    session_end = Column(DateTime)
    duration_minutes = Column(Integer)
    activities_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关联关系
    user = relationship("User", back_populates="learning_sessions")
    questions = relationship("QuestionRecord", back_populates="session")
    experiments = relationship("ExperimentRecord", back_populates="session")
    knowledge_interactions = relationship("KnowledgeInteraction", back_populates="session")

class QuestionRecord(Base):
    """问答记录"""
    __tablename__ = 'question_records'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    session_id = Column(Integer, ForeignKey('learning_sessions.id'))
    question_text = Column(Text, nullable=False)
    answer_text = Column(Text)
    ai_model_used = Column(String(50))  # 使用的AI模型
    subject_category = Column(String(100))  # 学科分类
    difficulty_level = Column(String(20))  # 难度级别
    response_time_seconds = Column(Float)  # AI响应时间
    user_rating = Column(Integer)  # 用户评分 1-5
    is_helpful = Column(Boolean)  # 是否有帮助
    follow_up_questions = Column(Integer, default=0)  # 后续问题数量
    knowledge_points_extracted = Column(JSON)  # 提取的知识点
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关联关系
    user = relationship("User", back_populates="questions")
    session = relationship("LearningSession", back_populates="questions")

class KnowledgePoint(Base):
    """知识点库"""
    __tablename__ = 'knowledge_points'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    subject = Column(String(100), nullable=False)
    category = Column(String(100))
    difficulty_level = Column(String(20))  # beginner, intermediate, advanced
    prerequisites = Column(JSON)  # 前置知识点ID列表
    related_points = Column(JSON)  # 相关知识点ID列表
    content_modules = Column(JSON)  # 模块化内容结构
    simulation_config = Column(JSON)  # 仿真配置
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    interactions = relationship("KnowledgeInteraction", back_populates="knowledge_point")

class KnowledgeInteraction(Base):
    """知识点交互记录"""
    __tablename__ = 'knowledge_interactions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    session_id = Column(Integer, ForeignKey('learning_sessions.id'))
    knowledge_point_id = Column(Integer, ForeignKey('knowledge_points.id'), nullable=False)
    interaction_type = Column(String(50))  # view, study, practice, test, simulate
    time_spent_seconds = Column(Integer)
    completion_percentage = Column(Float)  # 完成百分比
    mastery_level = Column(Float)  # 掌握程度 0-1
    attempts_count = Column(Integer, default=1)
    success_rate = Column(Float)  # 成功率
    notes = Column(Text)  # 用户笔记
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关联关系
    user = relationship("User", back_populates="knowledge_interactions")
    session = relationship("LearningSession", back_populates="knowledge_interactions")
    knowledge_point = relationship("KnowledgePoint", back_populates="interactions")

class ExperimentRecord(Base):
    """实验记录"""
    __tablename__ = 'experiment_records'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    session_id = Column(Integer, ForeignKey('learning_sessions.id'))
    experiment_name = Column(String(200), nullable=False)
    experiment_type = Column(String(100))  # circuit, physics, chemistry, etc.
    subject = Column(String(100))
    simulation_platform = Column(String(100))  # CircuitJS, PhET, etc.
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime)
    duration_minutes = Column(Integer)
    completion_status = Column(String(20))  # started, in_progress, completed, abandoned
    score = Column(Float)  # 实验得分
    parameters_used = Column(JSON)  # 使用的参数配置
    results_data = Column(JSON)  # 实验结果数据
    screenshots = Column(JSON)  # 截图记录
    notes = Column(Text)  # 实验笔记
    teacher_feedback = Column(Text)  # 教师反馈
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关联关系
    user = relationship("User", back_populates="experiments")
    session = relationship("LearningSession", back_populates="experiments")

class SimulationInteraction(Base):
    """仿真交互记录"""
    __tablename__ = 'simulation_interactions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    experiment_id = Column(Integer, ForeignKey('experiment_records.id'))
    simulation_type = Column(String(100))  # circuit, pid_control, signal_processing, etc.
    platform = Column(String(100))  # 仿真平台
    interaction_data = Column(JSON)  # 交互数据
    parameter_changes = Column(JSON)  # 参数变化记录
    results_captured = Column(JSON)  # 捕获的结果
    learning_objectives_met = Column(JSON)  # 达成的学习目标
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # 关联关系
    user = relationship("User", back_populates="simulation_interactions")

class LearningPath(Base):
    """学习路径记录"""
    __tablename__ = 'learning_paths'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    subject = Column(String(100), nullable=False)
    current_level = Column(String(20))  # beginner, intermediate, advanced
    progress_percentage = Column(Float, default=0.0)
    knowledge_points_mastered = Column(JSON)  # 已掌握的知识点ID列表
    recommended_next_steps = Column(JSON)  # AI推荐的下一步学习内容
    learning_style_profile = Column(JSON)  # 学习风格画像
    strengths = Column(JSON)  # 优势领域
    weaknesses = Column(JSON)  # 薄弱环节
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    user = relationship("User", back_populates="learning_paths")

class Achievement(Base):
    """成就系统"""
    __tablename__ = 'achievements'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    category = Column(String(50))  # knowledge, experiment, streak, social, etc.
    icon = Column(String(100))  # 图标名称
    criteria = Column(JSON)  # 获得条件
    points = Column(Integer, default=0)  # 积分奖励
    rarity = Column(String(20))  # common, rare, epic, legendary
    created_at = Column(DateTime, default=datetime.utcnow)

class UserAchievement(Base):
    """用户成就记录"""
    __tablename__ = 'user_achievements'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    achievement_id = Column(Integer, ForeignKey('achievements.id'), nullable=False)
    earned_at = Column(DateTime, default=datetime.utcnow)
    progress_data = Column(JSON)  # 获得成就时的进度数据
    
    # 关联关系
    user = relationship("User", back_populates="user_achievements")
    achievement = relationship("Achievement")

class StudyStreak(Base):
    """学习连续记录"""
    __tablename__ = 'study_streaks'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime)
    current_streak = Column(Integer, default=1)
    longest_streak = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    
    # 关联关系
    user = relationship("User", back_populates="study_streaks")

class TeacherStudentMapping(Base):
    """师生关系映射"""
    __tablename__ = 'teacher_student_mappings'
    
    id = Column(Integer, primary_key=True)
    teacher_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    student_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    subject = Column(String(100))  # 教授科目
    class_name = Column(String(100))  # 班级名称
    semester = Column(String(50))  # 学期
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关联关系
    teacher = relationship("User", foreign_keys=[teacher_id])
    student = relationship("User", foreign_keys=[student_id])

# 扩展User模型的关联关系
def extend_user_model():
    """扩展User模型以支持学习分析"""
    from src.models.user import User
    
    # 添加关联关系
    User.learning_sessions = relationship("LearningSession", back_populates="user")
    User.questions = relationship("QuestionRecord", back_populates="user")
    User.knowledge_interactions = relationship("KnowledgeInteraction", back_populates="user")
    User.experiments = relationship("ExperimentRecord", back_populates="user")
    User.simulation_interactions = relationship("SimulationInteraction", back_populates="user")
    User.learning_paths = relationship("LearningPath", back_populates="user")
    User.user_achievements = relationship("UserAchievement", back_populates="user")
    User.study_streaks = relationship("StudyStreak", back_populates="user")
