from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Float, Text, Boolean, ForeignKey, JSON, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()

class DifficultyLevel(enum.Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class AssessmentType(enum.Enum):
    THEORETICAL = "theoretical"
    PRACTICAL = "practical"
    SIMULATION = "simulation"
    EXPERIMENTAL = "experimental"
    COMPUTATIONAL = "computational"
    APPLIED = "applied"
    ANALYTICAL = "analytical"

class BloomLevel(enum.Enum):
    REMEMBER = "remember"
    UNDERSTAND = "understand"
    APPLY = "apply"
    ANALYZE = "analyze"
    EVALUATE = "evaluate"
    CREATE = "create"

class CompetencyLevel(enum.Enum):
    NOVICE = "novice"
    ADVANCED_BEGINNER = "advanced_beginner"
    COMPETENT = "competent"
    PROFICIENT = "proficient"
    EXPERT = "expert"

class MultimediaType(enum.Enum):
    VIDEO = "video"
    ANIMATION = "animation"
    SIMULATION = "simulation"
    DOCUMENT = "document"
    IMAGE = "image"
    AUDIO = "audio"
    INTERACTIVE = "interactive"

class KnowledgeDomain(Base):
    """知识领域"""
    __tablename__ = 'knowledge_domains'
    
    id = Column(Integer, primary_key=True)
    domain_key = Column(String(100), unique=True, nullable=False)  # e.g., 'electrical_engineering'
    name = Column(String(200), nullable=False)  # e.g., '电工电子工程'
    description = Column(Text)
    parent_domain_id = Column(Integer, ForeignKey('knowledge_domains.id'))
    subdirectory = Column(String(100))  # e.g., 'basic_concepts'
    difficulty_levels = Column(JSON)  # 支持的难度级别
    assessment_types = Column(JSON)  # 支持的评估类型
    metadata = Column(JSON)  # 额外的元数据
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    parent_domain = relationship("KnowledgeDomain", remote_side=[id])
    child_domains = relationship("KnowledgeDomain")
    knowledge_points = relationship("EnhancedKnowledgePoint", back_populates="domain")

class EnhancedKnowledgePoint(Base):
    """增强的知识点模型"""
    __tablename__ = 'enhanced_knowledge_points'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    domain_id = Column(Integer, ForeignKey('knowledge_domains.id'), nullable=False)
    
    # 层级关系
    parent_id = Column(Integer, ForeignKey('enhanced_knowledge_points.id'))
    order_index = Column(Integer, default=0)  # 在同级中的排序
    depth_level = Column(Integer, default=0)  # 层级深度
    
    # 教学属性
    difficulty_level = Column(Enum(DifficultyLevel), default=DifficultyLevel.INTERMEDIATE)
    bloom_level = Column(Enum(BloomLevel), default=BloomLevel.UNDERSTAND)
    estimated_duration_minutes = Column(Integer)  # 预计学习时长
    
    # 内容结构
    learning_objectives = Column(JSON)  # 学习目标列表
    prerequisites = Column(JSON)  # 前置知识点ID列表
    related_points = Column(JSON)  # 相关知识点ID列表
    key_concepts = Column(JSON)  # 核心概念列表
    formulas = Column(JSON)  # 公式列表
    examples = Column(JSON)  # 示例列表
    applications = Column(JSON)  # 应用场景列表
    
    # 多模态内容
    content_modules = Column(JSON)  # 模块化内容结构
    multimedia_resources = Column(JSON)  # 多媒体资源引用
    interactive_elements = Column(JSON)  # 交互元素配置
    simulation_config = Column(JSON)  # 仿真配置
    
    # 评估相关
    assessment_criteria = Column(JSON)  # 评估标准
    practice_questions = Column(JSON)  # 练习题目
    competency_indicators = Column(JSON)  # 能力指标
    
    # 质量控制
    content_version = Column(String(20), default="1.0.0")
    quality_score = Column(Float, default=0.0)  # 内容质量评分
    review_status = Column(String(20), default="draft")  # draft, reviewed, approved
    last_reviewed_at = Column(DateTime)
    reviewer_id = Column(Integer, ForeignKey('users.id'))
    
    # 使用统计
    view_count = Column(Integer, default=0)
    completion_rate = Column(Float, default=0.0)  # 完成率
    average_rating = Column(Float, default=0.0)  # 平均评分
    
    # 元数据
    tags = Column(JSON)  # 标签列表
    language = Column(String(10), default="zh-CN")
    accessibility_features = Column(JSON)  # 可访问性特性
    cultural_context = Column(JSON)  # 文化背景信息
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    domain = relationship("KnowledgeDomain", back_populates="knowledge_points")
    parent = relationship("EnhancedKnowledgePoint", remote_side=[id])
    children = relationship("EnhancedKnowledgePoint")
    multimedia_files = relationship("MultimediaResource", back_populates="knowledge_point")
    assessments = relationship("Assessment", back_populates="knowledge_point")
    interactions = relationship("KnowledgeInteraction", back_populates="knowledge_point")

class MultimediaResource(Base):
    """多媒体资源"""
    __tablename__ = 'multimedia_resources'
    
    id = Column(Integer, primary_key=True)
    knowledge_point_id = Column(Integer, ForeignKey('enhanced_knowledge_points.id'))
    
    # 文件信息
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255))
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer)  # 文件大小（字节）
    file_format = Column(String(20))  # 文件格式
    mime_type = Column(String(100))
    
    # 资源类型和属性
    resource_type = Column(Enum(MultimediaType), nullable=False)
    title = Column(String(200))
    description = Column(Text)
    duration_seconds = Column(Integer)  # 视频/音频时长
    resolution = Column(String(20))  # 分辨率（如 1920x1080）
    quality_level = Column(String(20))  # 质量级别
    
    # 内容标注
    timestamps = Column(JSON)  # 时间戳标注
    captions = Column(JSON)  # 字幕/说明文字
    annotations = Column(JSON)  # 注释信息
    interactive_hotspots = Column(JSON)  # 交互热点
    
    # 教学属性
    learning_objectives = Column(JSON)  # 学习目标
    difficulty_level = Column(Enum(DifficultyLevel))
    bloom_level = Column(Enum(BloomLevel))
    usage_context = Column(JSON)  # 使用场景
    
    # 技术属性
    encoding_settings = Column(JSON)  # 编码设置
    streaming_urls = Column(JSON)  # 流媒体URL
    thumbnail_path = Column(String(500))  # 缩略图路径
    preview_path = Column(String(500))  # 预览文件路径
    
    # 可访问性
    alt_text = Column(Text)  # 替代文本
    transcription = Column(Text)  # 转录文本
    sign_language_video = Column(String(500))  # 手语视频路径
    audio_description = Column(String(500))  # 音频描述路径
    
    # 版权和许可
    copyright_info = Column(JSON)  # 版权信息
    license_type = Column(String(50))  # 许可类型
    attribution = Column(Text)  # 署名信息
    usage_rights = Column(JSON)  # 使用权限
    
    # 质量和状态
    processing_status = Column(String(20), default="pending")  # pending, processing, completed, failed
    quality_score = Column(Float, default=0.0)
    review_status = Column(String(20), default="draft")
    is_public = Column(Boolean, default=False)
    
    # 使用统计
    download_count = Column(Integer, default=0)
    view_count = Column(Integer, default=0)
    average_rating = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    knowledge_point = relationship("EnhancedKnowledgePoint", back_populates="multimedia_files")
    usage_logs = relationship("MultimediaUsageLog", back_populates="resource")

class Assessment(Base):
    """评估/测试"""
    __tablename__ = 'assessments'
    
    id = Column(Integer, primary_key=True)
    knowledge_point_id = Column(Integer, ForeignKey('enhanced_knowledge_points.id'))
    
    # 基本信息
    title = Column(String(200), nullable=False)
    description = Column(Text)
    assessment_type = Column(Enum(AssessmentType), nullable=False)
    
    # 评估属性
    difficulty_level = Column(Enum(DifficultyLevel))
    bloom_level = Column(Enum(BloomLevel))
    competency_level = Column(Enum(CompetencyLevel))
    estimated_duration_minutes = Column(Integer)
    max_attempts = Column(Integer, default=3)
    passing_score = Column(Float, default=60.0)
    
    # 内容结构
    questions = Column(JSON)  # 题目列表
    rubrics = Column(JSON)  # 评分标准
    answer_key = Column(JSON)  # 答案和解析
    feedback_templates = Column(JSON)  # 反馈模板
    
    # 自适应评估
    adaptive_rules = Column(JSON)  # 自适应规则
    difficulty_adjustment = Column(JSON)  # 难度调整策略
    personalization_config = Column(JSON)  # 个性化配置
    
    # 评估配置
    randomize_questions = Column(Boolean, default=False)
    randomize_options = Column(Boolean, default=False)
    show_correct_answers = Column(Boolean, default=True)
    immediate_feedback = Column(Boolean, default=True)
    
    # 统计信息
    total_attempts = Column(Integer, default=0)
    average_score = Column(Float, default=0.0)
    completion_rate = Column(Float, default=0.0)
    average_duration = Column(Float, default=0.0)
    
    # 质量控制
    review_status = Column(String(20), default="draft")
    quality_score = Column(Float, default=0.0)
    last_reviewed_at = Column(DateTime)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    knowledge_point = relationship("EnhancedKnowledgePoint", back_populates="assessments")
    attempts = relationship("AssessmentAttempt", back_populates="assessment")

class AssessmentAttempt(Base):
    """评估尝试记录"""
    __tablename__ = 'assessment_attempts'
    
    id = Column(Integer, primary_key=True)
    assessment_id = Column(Integer, ForeignKey('assessments.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    session_id = Column(Integer, ForeignKey('learning_sessions.id'))
    
    # 尝试信息
    attempt_number = Column(Integer, default=1)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime)
    duration_seconds = Column(Integer)
    
    # 结果信息
    responses = Column(JSON)  # 用户回答
    score = Column(Float)  # 得分
    percentage = Column(Float)  # 百分比
    is_passed = Column(Boolean, default=False)
    
    # 详细分析
    question_analysis = Column(JSON)  # 逐题分析
    competency_scores = Column(JSON)  # 能力维度得分
    bloom_level_scores = Column(JSON)  # 布鲁姆层级得分
    time_per_question = Column(JSON)  # 每题用时
    
    # 反馈信息
    automated_feedback = Column(JSON)  # 自动生成的反馈
    instructor_feedback = Column(Text)  # 教师反馈
    peer_feedback = Column(JSON)  # 同伴反馈
    
    # 状态信息
    completion_status = Column(String(20), default="in_progress")  # in_progress, completed, abandoned
    submission_ip = Column(String(45))  # 提交IP地址
    user_agent = Column(String(500))  # 用户代理
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    assessment = relationship("Assessment", back_populates="attempts")
    user = relationship("User")
    session = relationship("LearningSession")

class MultimediaUsageLog(Base):
    """多媒体资源使用日志"""
    __tablename__ = 'multimedia_usage_logs'
    
    id = Column(Integer, primary_key=True)
    resource_id = Column(Integer, ForeignKey('multimedia_resources.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    session_id = Column(Integer, ForeignKey('learning_sessions.id'))
    
    # 使用信息
    action_type = Column(String(50))  # view, download, play, pause, seek, complete
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime)
    duration_seconds = Column(Integer)
    
    # 播放信息（视频/音频）
    playback_position = Column(Float)  # 播放位置（秒）
    playback_speed = Column(Float, default=1.0)  # 播放速度
    volume_level = Column(Float)  # 音量级别
    quality_setting = Column(String(20))  # 质量设置
    
    # 交互信息
    interactions = Column(JSON)  # 交互记录
    annotations_made = Column(JSON)  # 用户标注
    bookmarks = Column(JSON)  # 书签
    notes = Column(Text)  # 笔记
    
    # 技术信息
    device_type = Column(String(50))  # 设备类型
    browser_info = Column(String(200))  # 浏览器信息
    screen_resolution = Column(String(20))  # 屏幕分辨率
    network_quality = Column(String(20))  # 网络质量
    
    # 学习效果
    comprehension_rating = Column(Integer)  # 理解程度评分 1-5
    engagement_score = Column(Float)  # 参与度评分
    completion_percentage = Column(Float)  # 完成百分比
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关联关系
    resource = relationship("MultimediaResource", back_populates="usage_logs")
    user = relationship("User")
    session = relationship("LearningSession")

class ContentVersion(Base):
    """内容版本控制"""
    __tablename__ = 'content_versions'
    
    id = Column(Integer, primary_key=True)
    knowledge_point_id = Column(Integer, ForeignKey('enhanced_knowledge_points.id'), nullable=False)
    
    # 版本信息
    version_number = Column(String(20), nullable=False)
    version_type = Column(String(20))  # major, minor, patch
    change_summary = Column(Text)
    change_details = Column(JSON)
    
    # 内容快照
    content_snapshot = Column(JSON)  # 完整内容快照
    diff_from_previous = Column(JSON)  # 与前一版本的差异
    
    # 版本元数据
    created_by = Column(Integer, ForeignKey('users.id'))
    approved_by = Column(Integer, ForeignKey('users.id'))
    approval_date = Column(DateTime)
    is_current = Column(Boolean, default=False)
    
    # 质量信息
    quality_metrics = Column(JSON)  # 质量指标
    test_results = Column(JSON)  # 测试结果
    review_comments = Column(JSON)  # 评审意见
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关联关系
    knowledge_point = relationship("EnhancedKnowledgePoint")
    creator = relationship("User", foreign_keys=[created_by])
    approver = relationship("User", foreign_keys=[approved_by])

# 扩展现有的KnowledgeInteraction模型
class EnhancedKnowledgeInteraction(Base):
    """增强的知识点交互记录"""
    __tablename__ = 'enhanced_knowledge_interactions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    session_id = Column(Integer, ForeignKey('learning_sessions.id'))
    knowledge_point_id = Column(Integer, ForeignKey('enhanced_knowledge_points.id'), nullable=False)
    
    # 交互类型和内容
    interaction_type = Column(String(50))  # view, study, practice, test, simulate, discuss
    content_module = Column(String(50))  # theory, examples, practice, simulation
    interaction_data = Column(JSON)  # 详细交互数据
    
    # 时间信息
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime)
    time_spent_seconds = Column(Integer)
    active_time_seconds = Column(Integer)  # 实际活跃时间
    
    # 学习效果
    completion_percentage = Column(Float)
    mastery_level = Column(Float)  # 掌握程度 0-1
    confidence_level = Column(Float)  # 信心程度 0-1
    difficulty_perceived = Column(Float)  # 感知难度 0-1
    
    # 行为分析
    attempts_count = Column(Integer, default=1)
    success_rate = Column(Float)
    error_patterns = Column(JSON)  # 错误模式
    learning_path = Column(JSON)  # 学习路径
    
    # 多模态交互
    multimedia_interactions = Column(JSON)  # 多媒体交互记录
    simulation_parameters = Column(JSON)  # 仿真参数
    annotation_data = Column(JSON)  # 标注数据
    
    # 反馈和评价
    self_assessment = Column(JSON)  # 自我评估
    peer_feedback = Column(JSON)  # 同伴反馈
    ai_feedback = Column(JSON)  # AI反馈
    instructor_feedback = Column(Text)  # 教师反馈
    
    # 个性化数据
    learning_style_indicators = Column(JSON)  # 学习风格指标
    preference_data = Column(JSON)  # 偏好数据
    adaptation_triggers = Column(JSON)  # 适应性触发器
    
    # 上下文信息
    device_context = Column(JSON)  # 设备上下文
    environment_context = Column(JSON)  # 环境上下文
    social_context = Column(JSON)  # 社交上下文
    
    # 质量和状态
    data_quality_score = Column(Float, default=1.0)
    is_valid = Column(Boolean, default=True)
    notes = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    user = relationship("User")
    session = relationship("LearningSession")
    knowledge_point = relationship("EnhancedKnowledgePoint", back_populates="interactions")
