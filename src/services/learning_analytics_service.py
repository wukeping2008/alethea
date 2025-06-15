from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
import json

from src.models.learning_analytics import (
    LearningSession, QuestionRecord, KnowledgePoint, KnowledgeInteraction,
    ExperimentRecord, SimulationInteraction, LearningPath, Achievement,
    UserAchievement, StudyStreak, TeacherStudentMapping
)
from src.models.user import User

class LearningAnalyticsService:
    """学习分析服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def start_learning_session(self, user_id: int) -> LearningSession:
        """开始学习会话"""
        session = LearningSession(
            user_id=user_id,
            session_start=datetime.utcnow()
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session
    
    def end_learning_session(self, session_id: int) -> LearningSession:
        """结束学习会话"""
        session = self.db.query(LearningSession).filter(
            LearningSession.id == session_id
        ).first()
        
        if session:
            session.session_end = datetime.utcnow()
            session.duration_minutes = int(
                (session.session_end - session.session_start).total_seconds() / 60
            )
            self.db.commit()
            
            # 更新学习连续记录
            self._update_study_streak(session.user_id)
            
        return session
    
    def record_question(self, user_id: int, session_id: Optional[int], 
                       question_data: Dict[str, Any]) -> QuestionRecord:
        """记录问答"""
        # 提取知识点
        knowledge_points = self._extract_knowledge_points(question_data.get('question_text', ''))
        
        question_record = QuestionRecord(
            user_id=user_id,
            session_id=session_id,
            question_text=question_data.get('question_text'),
            answer_text=question_data.get('answer_text'),
            ai_model_used=question_data.get('ai_model_used'),
            subject_category=question_data.get('subject_category'),
            difficulty_level=question_data.get('difficulty_level'),
            response_time_seconds=question_data.get('response_time_seconds'),
            knowledge_points_extracted=knowledge_points
        )
        
        self.db.add(question_record)
        self.db.commit()
        self.db.refresh(question_record)
        
        # 更新学习路径
        self._update_learning_path(user_id, question_data.get('subject_category'))
        
        return question_record
    
    def record_knowledge_interaction(self, user_id: int, session_id: Optional[int],
                                   interaction_data: Dict[str, Any]) -> KnowledgeInteraction:
        """记录知识点交互"""
        interaction = KnowledgeInteraction(
            user_id=user_id,
            session_id=session_id,
            knowledge_point_id=interaction_data.get('knowledge_point_id'),
            interaction_type=interaction_data.get('interaction_type'),
            time_spent_seconds=interaction_data.get('time_spent_seconds'),
            completion_percentage=interaction_data.get('completion_percentage'),
            mastery_level=interaction_data.get('mastery_level'),
            attempts_count=interaction_data.get('attempts_count', 1),
            success_rate=interaction_data.get('success_rate'),
            notes=interaction_data.get('notes')
        )
        
        self.db.add(interaction)
        self.db.commit()
        self.db.refresh(interaction)
        
        # 检查成就
        self._check_achievements(user_id)
        
        return interaction
    
    def record_experiment(self, user_id: int, session_id: Optional[int],
                         experiment_data: Dict[str, Any]) -> ExperimentRecord:
        """记录实验"""
        experiment = ExperimentRecord(
            user_id=user_id,
            session_id=session_id,
            experiment_name=experiment_data.get('experiment_name'),
            experiment_type=experiment_data.get('experiment_type'),
            subject=experiment_data.get('subject'),
            simulation_platform=experiment_data.get('simulation_platform'),
            start_time=experiment_data.get('start_time', datetime.utcnow()),
            completion_status=experiment_data.get('completion_status', 'started'),
            parameters_used=experiment_data.get('parameters_used'),
            results_data=experiment_data.get('results_data'),
            notes=experiment_data.get('notes')
        )
        
        self.db.add(experiment)
        self.db.commit()
        self.db.refresh(experiment)
        
        return experiment
    
    def record_simulation_interaction(self, user_id: int, experiment_id: Optional[int],
                                    simulation_data: Dict[str, Any]) -> SimulationInteraction:
        """记录仿真交互"""
        interaction = SimulationInteraction(
            user_id=user_id,
            experiment_id=experiment_id,
            simulation_type=simulation_data.get('simulation_type'),
            platform=simulation_data.get('platform'),
            interaction_data=simulation_data.get('interaction_data'),
            parameter_changes=simulation_data.get('parameter_changes'),
            results_captured=simulation_data.get('results_captured'),
            learning_objectives_met=simulation_data.get('learning_objectives_met')
        )
        
        self.db.add(interaction)
        self.db.commit()
        self.db.refresh(interaction)
        
        return interaction
    
    def get_user_learning_analytics(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """获取用户学习分析数据"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # 基础统计
        total_sessions = self.db.query(LearningSession).filter(
            and_(LearningSession.user_id == user_id,
                 LearningSession.session_start >= start_date)
        ).count()
        
        total_questions = self.db.query(QuestionRecord).filter(
            and_(QuestionRecord.user_id == user_id,
                 QuestionRecord.created_at >= start_date)
        ).count()
        
        total_experiments = self.db.query(ExperimentRecord).filter(
            and_(ExperimentRecord.user_id == user_id,
                 ExperimentRecord.start_time >= start_date)
        ).count()
        
        # 学习时长
        total_study_time = self.db.query(
            func.sum(LearningSession.duration_minutes)
        ).filter(
            and_(LearningSession.user_id == user_id,
                 LearningSession.session_start >= start_date)
        ).scalar() or 0
        
        # 知识点掌握情况
        knowledge_stats = self._get_knowledge_mastery_stats(user_id)
        
        # 学科分布
        subject_distribution = self._get_subject_distribution(user_id, start_date)
        
        # 学习趋势
        learning_trend = self._get_learning_trend(user_id, days)
        
        # 当前连续学习天数
        current_streak = self._get_current_streak(user_id)
        
        # 成就统计
        achievements = self._get_user_achievements(user_id)
        
        return {
            'total_sessions': total_sessions,
            'total_questions': total_questions,
            'total_experiments': total_experiments,
            'total_study_time_minutes': total_study_time,
            'knowledge_stats': knowledge_stats,
            'subject_distribution': subject_distribution,
            'learning_trend': learning_trend,
            'current_streak': current_streak,
            'achievements': achievements,
            'period_days': days
        }
    
    def get_teacher_class_analytics(self, teacher_id: int, class_name: Optional[str] = None) -> Dict[str, Any]:
        """获取教师班级分析数据"""
        # 获取学生列表
        student_query = self.db.query(TeacherStudentMapping).filter(
            TeacherStudentMapping.teacher_id == teacher_id,
            TeacherStudentMapping.is_active == True
        )
        
        if class_name:
            student_query = student_query.filter(
                TeacherStudentMapping.class_name == class_name
            )
        
        student_mappings = student_query.all()
        student_ids = [mapping.student_id for mapping in student_mappings]
        
        if not student_ids:
            return {'error': 'No students found'}
        
        # 聚合学生数据
        start_date = datetime.utcnow() - timedelta(days=30)
        
        # 总体统计
        total_students = len(student_ids)
        active_students = self.db.query(LearningSession.user_id.distinct()).filter(
            and_(LearningSession.user_id.in_(student_ids),
                 LearningSession.session_start >= start_date)
        ).count()
        
        # 知识点统计
        total_knowledge_points = self.db.query(
            func.count(KnowledgeInteraction.id)
        ).filter(
            and_(KnowledgeInteraction.user_id.in_(student_ids),
                 KnowledgeInteraction.created_at >= start_date)
        ).scalar() or 0
        
        # 实验统计
        total_experiments = self.db.query(ExperimentRecord).filter(
            and_(ExperimentRecord.user_id.in_(student_ids),
                 ExperimentRecord.start_time >= start_date)
        ).count()
        
        # 平均学习进度
        avg_progress = self._calculate_class_average_progress(student_ids)
        
        # 学科分布
        class_subject_distribution = self._get_class_subject_distribution(student_ids, start_date)
        
        # 学生详细数据
        student_details = []
        for student_id in student_ids:
            student_data = self.get_user_learning_analytics(student_id, 30)
            student = self.db.query(User).filter(User.id == student_id).first()
            student_details.append({
                'id': student_id,
                'name': student.username if student else f'Student {student_id}',
                'analytics': student_data
            })
        
        return {
            'total_students': total_students,
            'active_students': active_students,
            'total_knowledge_points': total_knowledge_points,
            'total_experiments': total_experiments,
            'average_progress': avg_progress,
            'subject_distribution': class_subject_distribution,
            'student_details': student_details,
            'class_name': class_name
        }
    
    def _extract_knowledge_points(self, question_text: str) -> List[str]:
        """从问题中提取知识点"""
        # 简单的关键词匹配，实际应用中可以使用NLP技术
        knowledge_keywords = {
            '基尔霍夫定律': ['基尔霍夫', 'KCL', 'KVL', '电流定律', '电压定律'],
            '欧姆定律': ['欧姆', '电阻', '电压', '电流'],
            '运算放大器': ['运放', '放大器', 'op-amp', '运算放大'],
            'PID控制': ['PID', '比例', '积分', '微分', '控制器'],
            '数字信号处理': ['DSP', '数字信号', '滤波器', 'FFT'],
            '模拟电路': ['模拟', '晶体管', '二极管', '放大电路'],
            '数字电路': ['数字', '逻辑门', '触发器', '计数器']
        }
        
        extracted_points = []
        question_lower = question_text.lower()
        
        for point, keywords in knowledge_keywords.items():
            if any(keyword.lower() in question_lower for keyword in keywords):
                extracted_points.append(point)
        
        return extracted_points
    
    def _update_learning_path(self, user_id: int, subject: Optional[str]):
        """更新学习路径"""
        if not subject:
            return
        
        learning_path = self.db.query(LearningPath).filter(
            and_(LearningPath.user_id == user_id,
                 LearningPath.subject == subject)
        ).first()
        
        if not learning_path:
            learning_path = LearningPath(
                user_id=user_id,
                subject=subject,
                current_level='beginner'
            )
            self.db.add(learning_path)
        
        # 更新进度
        mastered_points = self.db.query(KnowledgeInteraction).filter(
            and_(KnowledgeInteraction.user_id == user_id,
                 KnowledgeInteraction.mastery_level >= 0.8)
        ).count()
        
        total_points = self.db.query(KnowledgePoint).filter(
            KnowledgePoint.subject == subject
        ).count()
        
        if total_points > 0:
            learning_path.progress_percentage = (mastered_points / total_points) * 100
        
        learning_path.last_updated = datetime.utcnow()
        self.db.commit()
    
    def _update_study_streak(self, user_id: int):
        """更新学习连续记录"""
        today = datetime.utcnow().date()
        
        streak = self.db.query(StudyStreak).filter(
            and_(StudyStreak.user_id == user_id,
                 StudyStreak.is_active == True)
        ).first()
        
        if not streak:
            streak = StudyStreak(
                user_id=user_id,
                start_date=datetime.utcnow(),
                current_streak=1,
                longest_streak=1
            )
            self.db.add(streak)
        else:
            last_activity = streak.end_date or streak.start_date
            if last_activity.date() == today - timedelta(days=1):
                # 连续学习
                streak.current_streak += 1
                streak.longest_streak = max(streak.longest_streak, streak.current_streak)
            elif last_activity.date() != today:
                # 中断了，重新开始
                streak.current_streak = 1
                streak.start_date = datetime.utcnow()
            
            streak.end_date = datetime.utcnow()
        
        self.db.commit()
    
    def _check_achievements(self, user_id: int):
        """检查并授予成就"""
        # 获取用户统计数据
        user_stats = self.get_user_learning_analytics(user_id, 365)  # 一年数据
        
        # 定义成就条件
        achievement_conditions = [
            {
                'name': '知识探索者',
                'condition': user_stats['knowledge_stats']['total_mastered'] >= 10,
                'category': 'knowledge'
            },
            {
                'name': '实验达人',
                'condition': user_stats['total_experiments'] >= 5,
                'category': 'experiment'
            },
            {
                'name': '学习坚持者',
                'condition': user_stats['current_streak'] >= 7,
                'category': 'streak'
            }
        ]
        
        for condition in achievement_conditions:
            if condition['condition']:
                self._award_achievement(user_id, condition['name'], condition['category'])
    
    def _award_achievement(self, user_id: int, achievement_name: str, category: str):
        """授予成就"""
        # 检查是否已经获得
        existing = self.db.query(UserAchievement).join(Achievement).filter(
            and_(UserAchievement.user_id == user_id,
                 Achievement.name == achievement_name)
        ).first()
        
        if existing:
            return
        
        # 查找或创建成就
        achievement = self.db.query(Achievement).filter(
            Achievement.name == achievement_name
        ).first()
        
        if not achievement:
            achievement = Achievement(
                name=achievement_name,
                category=category,
                description=f'获得{achievement_name}成就',
                points=10
            )
            self.db.add(achievement)
            self.db.commit()
            self.db.refresh(achievement)
        
        # 授予成就
        user_achievement = UserAchievement(
            user_id=user_id,
            achievement_id=achievement.id
        )
        self.db.add(user_achievement)
        self.db.commit()
    
    def _get_knowledge_mastery_stats(self, user_id: int) -> Dict[str, Any]:
        """获取知识点掌握统计"""
        total_interactions = self.db.query(KnowledgeInteraction).filter(
            KnowledgeInteraction.user_id == user_id
        ).count()
        
        mastered_count = self.db.query(KnowledgeInteraction).filter(
            and_(KnowledgeInteraction.user_id == user_id,
                 KnowledgeInteraction.mastery_level >= 0.8)
        ).count()
        
        return {
            'total_interactions': total_interactions,
            'total_mastered': mastered_count,
            'mastery_rate': (mastered_count / total_interactions * 100) if total_interactions > 0 else 0
        }
    
    def _get_subject_distribution(self, user_id: int, start_date: datetime) -> Dict[str, int]:
        """获取学科分布"""
        results = self.db.query(
            QuestionRecord.subject_category,
            func.count(QuestionRecord.id)
        ).filter(
            and_(QuestionRecord.user_id == user_id,
                 QuestionRecord.created_at >= start_date)
        ).group_by(QuestionRecord.subject_category).all()
        
        return {subject: count for subject, count in results if subject}
    
    def _get_learning_trend(self, user_id: int, days: int) -> List[Dict[str, Any]]:
        """获取学习趋势"""
        trend_data = []
        for i in range(days):
            date = datetime.utcnow().date() - timedelta(days=i)
            
            sessions = self.db.query(LearningSession).filter(
                and_(LearningSession.user_id == user_id,
                     func.date(LearningSession.session_start) == date)
            ).count()
            
            questions = self.db.query(QuestionRecord).filter(
                and_(QuestionRecord.user_id == user_id,
                     func.date(QuestionRecord.created_at) == date)
            ).count()
            
            trend_data.append({
                'date': date.isoformat(),
                'sessions': sessions,
                'questions': questions
            })
        
        return list(reversed(trend_data))
    
    def _get_current_streak(self, user_id: int) -> int:
        """获取当前连续学习天数"""
        streak = self.db.query(StudyStreak).filter(
            and_(StudyStreak.user_id == user_id,
                 StudyStreak.is_active == True)
        ).first()
        
        return streak.current_streak if streak else 0
    
    def _get_user_achievements(self, user_id: int) -> List[Dict[str, Any]]:
        """获取用户成就"""
        achievements = self.db.query(UserAchievement, Achievement).join(
            Achievement
        ).filter(UserAchievement.user_id == user_id).all()
        
        return [
            {
                'name': achievement.name,
                'description': achievement.description,
                'category': achievement.category,
                'earned_at': user_achievement.earned_at.isoformat(),
                'points': achievement.points
            }
            for user_achievement, achievement in achievements
        ]
    
    def _calculate_class_average_progress(self, student_ids: List[int]) -> float:
        """计算班级平均进度"""
        if not student_ids:
            return 0.0
        
        total_progress = 0
        for student_id in student_ids:
            learning_paths = self.db.query(LearningPath).filter(
                LearningPath.user_id == student_id
            ).all()
            
            if learning_paths:
                avg_progress = sum(path.progress_percentage for path in learning_paths) / len(learning_paths)
                total_progress += avg_progress
        
        return total_progress / len(student_ids) if student_ids else 0.0
    
    def _get_class_subject_distribution(self, student_ids: List[int], start_date: datetime) -> Dict[str, int]:
        """获取班级学科分布"""
        results = self.db.query(
            QuestionRecord.subject_category,
            func.count(QuestionRecord.id)
        ).filter(
            and_(QuestionRecord.user_id.in_(student_ids),
                 QuestionRecord.created_at >= start_date)
        ).group_by(QuestionRecord.subject_category).all()
        
        return {subject: count for subject, count in results if subject}
