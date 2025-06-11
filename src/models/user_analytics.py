"""
User Analytics and Digital Portrait Module for Alethea Platform
Tracks user behavior and generates AI-powered insights
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Float, JSON
from sqlalchemy.orm import relationship
from models.user import db, User, Subject

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UserBehavior(db.Model):
    """Track user behavior and interactions"""
    __tablename__ = 'user_behaviors'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    action_type = Column(String(50), nullable=False)  # 'search', 'ask_question', 'view_project', 'start_project', etc.
    action_data = Column(JSON)  # Store additional action data
    subject_id = Column(Integer, ForeignKey('subjects.id'))
    session_id = Column(String(100))  # Track user sessions
    ip_address = Column(String(45))
    user_agent = Column(Text)
    duration = Column(Integer)  # Duration in seconds for time-based actions
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship('User', overlaps="behaviors")
    subject = relationship('Subject', overlaps="user_behaviors")
    
    def __repr__(self):
        return f"<UserBehavior {self.action_type} by user {self.user_id}>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'action_type': self.action_type,
            'action_data': self.action_data,
            'subject_id': self.subject_id,
            'subject_name': self.subject.name if self.subject else None,
            'session_id': self.session_id,
            'duration': self.duration,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class UserKnowledgePoint(db.Model):
    """Track user's knowledge points and mastery levels"""
    __tablename__ = 'user_knowledge_points'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    subject_id = Column(Integer, ForeignKey('subjects.id'), nullable=False)
    knowledge_point = Column(String(200), nullable=False)  # e.g., "Arduino编程", "PID控制"
    mastery_level = Column(Float, default=0.0)  # 0.0 to 1.0
    interaction_count = Column(Integer, default=0)  # Number of interactions with this knowledge point
    last_interaction = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship('User', overlaps="user_knowledge_points")
    subject = relationship('Subject', overlaps="user_knowledge_points")
    
    def __repr__(self):
        return f"<UserKnowledgePoint {self.knowledge_point} for user {self.user_id}>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'subject_id': self.subject_id,
            'subject_name': self.subject.name if self.subject else None,
            'knowledge_point': self.knowledge_point,
            'mastery_level': self.mastery_level,
            'interaction_count': self.interaction_count,
            'last_interaction': self.last_interaction.isoformat() if self.last_interaction else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class UserDigitalPortrait(db.Model):
    """Store AI-generated user digital portrait"""
    __tablename__ = 'user_digital_portraits'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, unique=True)
    learning_style = Column(String(50))  # 'visual', 'auditory', 'kinesthetic', 'mixed'
    preferred_subjects = Column(JSON)  # List of preferred subject IDs
    skill_levels = Column(JSON)  # Dict of subject -> skill level
    learning_pace = Column(String(20))  # 'slow', 'medium', 'fast'
    engagement_pattern = Column(JSON)  # Time patterns, session lengths, etc.
    strengths = Column(JSON)  # List of strength areas
    improvement_areas = Column(JSON)  # List of areas needing improvement
    recommended_projects = Column(JSON)  # List of recommended project IDs
    personality_traits = Column(JSON)  # AI-analyzed personality traits
    learning_goals = Column(JSON)  # Inferred or stated learning goals
    ai_insights = Column(Text)  # AI-generated insights about the user
    confidence_score = Column(Float, default=0.0)  # Confidence in the portrait accuracy
    last_updated = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship('User', uselist=False, overlaps="user_digital_portraits")
    
    def __repr__(self):
        return f"<UserDigitalPortrait for user {self.user_id}>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'learning_style': self.learning_style,
            'preferred_subjects': self.preferred_subjects,
            'skill_levels': self.skill_levels,
            'learning_pace': self.learning_pace,
            'engagement_pattern': self.engagement_pattern,
            'strengths': self.strengths,
            'improvement_areas': self.improvement_areas,
            'recommended_projects': self.recommended_projects,
            'personality_traits': self.personality_traits,
            'learning_goals': self.learning_goals,
            'ai_insights': self.ai_insights,
            'confidence_score': self.confidence_score,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class ProjectRecommendation(db.Model):
    """Store AI-generated project recommendations for users"""
    __tablename__ = 'project_recommendations'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    project_id = Column(String(50), nullable=False)  # Project identifier
    project_title = Column(String(200), nullable=False)
    recommendation_score = Column(Float, nullable=False)  # 0.0 to 1.0
    recommendation_reason = Column(Text)  # AI explanation for recommendation
    difficulty_match = Column(Float)  # How well difficulty matches user level
    interest_match = Column(Float)  # How well it matches user interests
    skill_development = Column(JSON)  # Skills this project would develop
    is_viewed = Column(Boolean, default=False)
    is_started = Column(Boolean, default=False)
    is_completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship('User', overlaps="project_recommendations")
    
    def __repr__(self):
        return f"<ProjectRecommendation {self.project_title} for user {self.user_id}>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'project_id': self.project_id,
            'project_title': self.project_title,
            'recommendation_score': self.recommendation_score,
            'recommendation_reason': self.recommendation_reason,
            'difficulty_match': self.difficulty_match,
            'interest_match': self.interest_match,
            'skill_development': self.skill_development,
            'is_viewed': self.is_viewed,
            'is_started': self.is_started,
            'is_completed': self.is_completed,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class LearningSession(db.Model):
    """Track user learning sessions"""
    __tablename__ = 'learning_sessions'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    session_id = Column(String(100), nullable=False)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime)
    duration = Column(Integer)  # Duration in seconds
    pages_visited = Column(JSON)  # List of pages visited
    actions_performed = Column(JSON)  # List of actions performed
    subjects_explored = Column(JSON)  # List of subject IDs explored
    questions_asked = Column(Integer, default=0)
    projects_viewed = Column(Integer, default=0)
    engagement_score = Column(Float)  # Calculated engagement score
    
    # Relationships
    user = relationship('User', overlaps="learning_sessions")
    
    def __repr__(self):
        return f"<LearningSession {self.session_id} for user {self.user_id}>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration': self.duration,
            'pages_visited': self.pages_visited,
            'actions_performed': self.actions_performed,
            'subjects_explored': self.subjects_explored,
            'questions_asked': self.questions_asked,
            'projects_viewed': self.projects_viewed,
            'engagement_score': self.engagement_score
        }


class UserAnalyticsManager:
    """Manager class for user analytics operations"""
    
    def __init__(self, db_instance):
        """Initialize analytics manager with database instance"""
        self.db = db_instance
    
    def track_behavior(self, user_id, action_type, action_data=None, subject_id=None, 
                      session_id=None, ip_address=None, user_agent=None, duration=None):
        """Track user behavior"""
        try:
            behavior = UserBehavior(
                user_id=user_id,
                action_type=action_type,
                action_data=action_data,
                subject_id=subject_id,
                session_id=session_id,
                ip_address=ip_address,
                user_agent=user_agent,
                duration=duration
            )
            
            self.db.session.add(behavior)
            self.db.session.commit()
            
            # Update knowledge points if relevant
            if action_type in ['ask_question', 'search', 'view_project'] and subject_id:
                self._update_knowledge_points(user_id, subject_id, action_data)
            
            return True, behavior.id
            
        except Exception as e:
            self.db.session.rollback()
            logger.error(f"Error tracking behavior: {str(e)}")
            return False, str(e)
    
    def _update_knowledge_points(self, user_id, subject_id, action_data):
        """Update user knowledge points based on behavior"""
        try:
            if not action_data:
                return
            
            # Extract knowledge points from action data
            knowledge_points = []
            
            if isinstance(action_data, dict):
                # Extract from question content, search terms, etc.
                content = action_data.get('content', '') or action_data.get('query', '')
                if content:
                    # Simple keyword extraction (can be enhanced with NLP)
                    keywords = ['Arduino', 'PID', '传感器', '电机', '控制', '编程', '电路', '算法']
                    for keyword in keywords:
                        if keyword.lower() in content.lower():
                            knowledge_points.append(keyword)
            
            # Update knowledge points
            for point in knowledge_points:
                existing = self.db.session.query(UserKnowledgePoint).filter_by(
                    user_id=user_id,
                    subject_id=subject_id,
                    knowledge_point=point
                ).first()
                
                if existing:
                    existing.interaction_count += 1
                    existing.mastery_level = min(1.0, existing.mastery_level + 0.1)
                    existing.last_interaction = datetime.utcnow()
                    existing.updated_at = datetime.utcnow()
                else:
                    new_point = UserKnowledgePoint(
                        user_id=user_id,
                        subject_id=subject_id,
                        knowledge_point=point,
                        mastery_level=0.1,
                        interaction_count=1
                    )
                    self.db.session.add(new_point)
            
            self.db.session.commit()
            
        except Exception as e:
            logger.error(f"Error updating knowledge points: {str(e)}")
    
    def get_user_analytics(self, user_id, days=30):
        """Get user analytics for the past N days"""
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # Get behaviors
            behaviors = self.db.session.query(UserBehavior).filter(
                UserBehavior.user_id == user_id,
                UserBehavior.created_at >= start_date
            ).all()
            
            # Get knowledge points
            knowledge_points = self.db.session.query(UserKnowledgePoint).filter_by(
                user_id=user_id
            ).all()
            
            # Get learning sessions
            sessions = self.db.session.query(LearningSession).filter(
                LearningSession.user_id == user_id,
                LearningSession.start_time >= start_date
            ).all()
            
            # Calculate analytics
            analytics = {
                'total_actions': len(behaviors),
                'action_breakdown': {},
                'subject_interests': {},
                'knowledge_points': [kp.to_dict() for kp in knowledge_points],
                'learning_sessions': [session.to_dict() for session in sessions],
                'daily_activity': {},
                'engagement_metrics': self._calculate_engagement_metrics(behaviors, sessions)
            }
            
            # Action breakdown
            for behavior in behaviors:
                action_type = behavior.action_type
                analytics['action_breakdown'][action_type] = analytics['action_breakdown'].get(action_type, 0) + 1
                
                # Subject interests
                if behavior.subject_id:
                    subject_name = behavior.subject.name if behavior.subject else 'Unknown'
                    analytics['subject_interests'][subject_name] = analytics['subject_interests'].get(subject_name, 0) + 1
                
                # Daily activity
                date_str = behavior.created_at.strftime('%Y-%m-%d')
                analytics['daily_activity'][date_str] = analytics['daily_activity'].get(date_str, 0) + 1
            
            return True, analytics
            
        except Exception as e:
            logger.error(f"Error getting user analytics: {str(e)}")
            return False, str(e)
    
    def _calculate_engagement_metrics(self, behaviors, sessions):
        """Calculate user engagement metrics"""
        try:
            if not behaviors and not sessions:
                return {
                    'engagement_score': 0.0,
                    'avg_session_duration': 0,
                    'total_time_spent': 0,
                    'consistency_score': 0.0
                }
            
            # Calculate total time spent
            total_time = sum(session.duration or 0 for session in sessions)
            
            # Calculate average session duration
            avg_duration = total_time / len(sessions) if sessions else 0
            
            # Calculate engagement score based on various factors
            action_score = min(1.0, len(behaviors) / 100)  # Normalize to 100 actions
            time_score = min(1.0, total_time / 3600)  # Normalize to 1 hour
            variety_score = len(set(b.action_type for b in behaviors)) / 10  # Variety of actions
            
            engagement_score = (action_score + time_score + variety_score) / 3
            
            # Calculate consistency score (how regularly the user engages)
            if sessions:
                dates = [session.start_time.date() for session in sessions]
                unique_dates = len(set(dates))
                total_days = (max(dates) - min(dates)).days + 1 if len(dates) > 1 else 1
                consistency_score = unique_dates / total_days
            else:
                consistency_score = 0.0
            
            return {
                'engagement_score': round(engagement_score, 2),
                'avg_session_duration': round(avg_duration),
                'total_time_spent': total_time,
                'consistency_score': round(consistency_score, 2)
            }
            
        except Exception as e:
            logger.error(f"Error calculating engagement metrics: {str(e)}")
            return {
                'engagement_score': 0.0,
                'avg_session_duration': 0,
                'total_time_spent': 0,
                'consistency_score': 0.0
            }
    
    def generate_digital_portrait(self, user_id):
        """Generate AI-powered digital portrait for user"""
        try:
            # Get user analytics
            success, analytics = self.get_user_analytics(user_id, days=90)  # 3 months of data
            if not success:
                return False, analytics
            
            # Get user's question history for content analysis
            from src.models.user import Question
            questions = self.db.session.query(Question).filter_by(user_id=user_id).all()
            
            # Analyze learning patterns
            portrait_data = self._analyze_learning_patterns(analytics, questions)
            
            # Check if portrait already exists
            existing = self.db.session.query(UserDigitalPortrait).filter_by(user_id=user_id).first()
            
            if existing:
                # Update existing portrait
                for key, value in portrait_data.items():
                    setattr(existing, key, value)
                existing.last_updated = datetime.utcnow()
                portrait = existing
            else:
                # Create new portrait
                portrait = UserDigitalPortrait(user_id=user_id, **portrait_data)
                self.db.session.add(portrait)
            
            self.db.session.commit()
            
            return True, portrait.to_dict()
            
        except Exception as e:
            self.db.session.rollback()
            logger.error(f"Error generating digital portrait: {str(e)}")
            return False, str(e)
    
    def _analyze_learning_patterns(self, analytics, questions):
        """Analyze user learning patterns to generate portrait"""
        try:
            # Determine learning style based on behavior patterns
            learning_style = self._determine_learning_style(analytics)
            
            # Analyze preferred subjects
            preferred_subjects = list(analytics['subject_interests'].keys())[:5]  # Top 5
            
            # Calculate skill levels
            skill_levels = {}
            for kp in analytics['knowledge_points']:
                subject = kp['subject_name']
                if subject:
                    if subject not in skill_levels:
                        skill_levels[subject] = []
                    skill_levels[subject].append(kp['mastery_level'])
            
            # Average skill levels per subject
            for subject in skill_levels:
                skill_levels[subject] = sum(skill_levels[subject]) / len(skill_levels[subject])
            
            # Determine learning pace
            engagement = analytics['engagement_metrics']
            if engagement['consistency_score'] > 0.7:
                learning_pace = 'fast'
            elif engagement['consistency_score'] > 0.4:
                learning_pace = 'medium'
            else:
                learning_pace = 'slow'
            
            # Analyze engagement patterns
            engagement_pattern = {
                'avg_session_duration': engagement['avg_session_duration'],
                'consistency_score': engagement['consistency_score'],
                'preferred_time': self._analyze_time_patterns(analytics),
                'session_frequency': len(analytics['learning_sessions']) / 30  # per day
            }
            
            # Identify strengths and improvement areas
            strengths = []
            improvement_areas = []
            
            for subject, level in skill_levels.items():
                if level > 0.7:
                    strengths.append(subject)
                elif level < 0.3:
                    improvement_areas.append(subject)
            
            # Generate AI insights
            ai_insights = self._generate_ai_insights(analytics, questions, skill_levels)
            
            # Calculate confidence score
            data_points = len(analytics['knowledge_points']) + len(analytics['learning_sessions'])
            confidence_score = min(1.0, data_points / 50)  # Normalize to 50 data points
            
            return {
                'learning_style': learning_style,
                'preferred_subjects': preferred_subjects,
                'skill_levels': skill_levels,
                'learning_pace': learning_pace,
                'engagement_pattern': engagement_pattern,
                'strengths': strengths,
                'improvement_areas': improvement_areas,
                'personality_traits': self._analyze_personality_traits(analytics, questions),
                'learning_goals': self._infer_learning_goals(analytics, questions),
                'ai_insights': ai_insights,
                'confidence_score': confidence_score
            }
            
        except Exception as e:
            logger.error(f"Error analyzing learning patterns: {str(e)}")
            return {}
    
    def _determine_learning_style(self, analytics):
        """Determine user's learning style based on behavior"""
        # Simple heuristic - can be enhanced with ML
        action_breakdown = analytics['action_breakdown']
        
        visual_actions = action_breakdown.get('view_project', 0) + action_breakdown.get('browse', 0)
        interactive_actions = action_breakdown.get('ask_question', 0) + action_breakdown.get('search', 0)
        practical_actions = action_breakdown.get('start_project', 0) + action_breakdown.get('simulation', 0)
        
        total_actions = sum(action_breakdown.values())
        if total_actions == 0:
            return 'mixed'
        
        visual_ratio = visual_actions / total_actions
        interactive_ratio = interactive_actions / total_actions
        practical_ratio = practical_actions / total_actions
        
        if practical_ratio > 0.4:
            return 'kinesthetic'
        elif interactive_ratio > 0.4:
            return 'auditory'
        elif visual_ratio > 0.4:
            return 'visual'
        else:
            return 'mixed'
    
    def _analyze_time_patterns(self, analytics):
        """Analyze when user is most active"""
        # Simple implementation - can be enhanced
        sessions = analytics['learning_sessions']
        if not sessions:
            return 'unknown'
        
        # Count sessions by hour
        hour_counts = {}
        for session in sessions:
            if session['start_time']:
                hour = datetime.fromisoformat(session['start_time']).hour
                hour_counts[hour] = hour_counts.get(hour, 0) + 1
        
        if not hour_counts:
            return 'unknown'
        
        peak_hour = max(hour_counts, key=hour_counts.get)
        
        if 6 <= peak_hour < 12:
            return 'morning'
        elif 12 <= peak_hour < 18:
            return 'afternoon'
        elif 18 <= peak_hour < 22:
            return 'evening'
        else:
            return 'night'
    
    def _analyze_personality_traits(self, analytics, questions):
        """Analyze personality traits from user behavior"""
        traits = {}
        
        # Curiosity - based on question asking and exploration
        question_count = len(questions)
        exploration_actions = analytics['action_breakdown'].get('search', 0) + analytics['action_breakdown'].get('browse', 0)
        curiosity_score = min(1.0, (question_count + exploration_actions) / 20)
        traits['curiosity'] = round(curiosity_score, 2)
        
        # Persistence - based on session duration and consistency
        engagement = analytics['engagement_metrics']
        persistence_score = (engagement['consistency_score'] + min(1.0, engagement['avg_session_duration'] / 1800)) / 2
        traits['persistence'] = round(persistence_score, 2)
        
        # Methodical approach - based on project completion and structured learning
        project_actions = analytics['action_breakdown'].get('start_project', 0) + analytics['action_breakdown'].get('complete_project', 0)
        methodical_score = min(1.0, project_actions / 5)
        traits['methodical'] = round(methodical_score, 2)
        
        return traits
    
    def _infer_learning_goals(self, analytics, questions):
        """Infer user's learning goals from behavior"""
        goals = []
        
        # Analyze subject interests
        subject_interests = analytics['subject_interests']
        top_subjects = sorted(subject_interests.items(), key=lambda x: x[1], reverse=True)[:3]
        
        for subject, count in top_subjects:
            if count > 5:  # Significant interest
                goals.append(f"掌握{subject}相关知识")
        
        # Analyze project interests
        project_actions = analytics['action_breakdown'].get('view_project', 0) + analytics['action_breakdown'].get('start_project', 0)
        if project_actions > 3:
            goals.append("通过项目实践提升技能")
        
        # Analyze question patterns
        if len(questions) > 10:
            goals.append("深入理解专业概念")
        
        return goals[:5]  # Limit to 5 goals
    
    def _generate_ai_insights(self, analytics, questions, skill_levels):
        """Generate AI insights about the user"""
        insights = []
        
        # Learning pattern insights
        engagement = analytics['engagement_metrics']
        if engagement['consistency_score'] > 0.7:
            insights.append("用户学习习惯良好，能够保持持续的学习节奏。")
        elif engagement['consistency_score'] < 0.3:
            insights.append("建议用户建立更规律的学习习惯，提高学习一致性。")
        
        # Subject expertise insights
        if skill_levels:
            max_skill_subject = max(skill_levels, key=skill_levels.get)
            max_skill_level = skill_levels[max_skill_subject]
            
            if max_skill_level > 0.8:
                insights.append(f"用户在{max_skill_subject}方面表现出色，可以考虑深入学习相关高级内容。")
            elif max_skill_level < 0.3:
                insights.append(f"建议用户加强{max_skill_subject}基础知识的学习。")
        
        # Engagement insights
        if engagement['avg_session_duration'] > 1800:  # 30 minutes
            insights.append("用户具有良好的专注力，能够进行深度学习。")
        elif engagement['avg_session_duration'] < 600:  # 10 minutes
            insights.append("建议用户尝试延长学习时间，进行更深入的探索。")
        
        # Question quality insights
        if len(questions) > 20:
            insights.append("用户善于提问，具有强烈的求知欲。")
        
        return " ".join(insights)
    
    def generate_project_recommendations(self, user_id):
        """Generate personalized project recommendations"""
        try:
            # Get user's digital portrait
            portrait = self.db.session.query(UserDigitalPortrait).filter_by(user_id=user_id).first()
            if not portrait:
                # Generate portrait first
                success, portrait_data = self.generate_digital_portrait(user_id)
                if not success:
                    return False, portrait_data
                portrait = self.db.session.query(UserDigitalPortrait).filter_by(user_id=user_id).first()
            
            # Define available projects (this could be moved to a separate projects table)
            available_projects = self._get_available_projects()
            
            # Generate recommendations
            recommendations = []
            for project in available_projects:
                score = self._calculate_recommendation_score(portrait, project)
                if score > 0.3:  # Minimum threshold
                    recommendation = {
                        'project_id': project['id'],
                        'project_title': project['title'],
                        'recommendation_score': score,
                        'recommendation_reason': self._generate_recommendation_reason(portrait, project, score),
                        'difficulty_match': self._calculate_difficulty_match(portrait, project),
                        'interest_match': self._calculate_interest_match(portrait, project),
                        'skill_development': project.get('skills', [])
                    }
                    recommendations.append(recommendation)
            
            # Sort by recommendation score
            recommendations.sort(key=lambda x: x['recommendation_score'], reverse=True)
            
            # Save top recommendations to database
            self._save_recommendations(user_id, recommendations[:10])  # Top 10
            
            return True, recommendations[:5]  # Return top 5
            
        except Exception as e:
            logger.error(f"Error generating project recommendations: {str(e)}")
            return False, str(e)
    
    def _get_available_projects(self):
        """Get list of available projects"""
        # This is a simplified version - in practice, this would come from a projects database
        return [
            {
                'id': 'smart-car',
                'title': '智能小车',
                'difficulty': 'medium',
                'subjects': ['电工电子实验', '自动控制原理'],
                'skills': ['Arduino编程', '传感器应用', '电机控制'],
                'category': 'robotics'
            },
            {
                'id': 'led-matrix',
                'title': 'LED点阵显示屏',
                'difficulty': 'easy',
                'subjects': ['数字电子技术'],
                'skills': ['数字电路', 'LED驱动', '单片机编程'],
                'category': 'electronics'
            },
            {
                'id': 'line-follower',
                'title': '循迹机器人',
                'difficulty': 'medium',
                'subjects': ['电工电子实验', '自动控制原理'],
                'skills': ['传感器融合', 'PID控制', '路径跟踪'],
                'category': 'robotics'
            },
            {
                'id': 'robotic-arm',
                'title': '机械臂控制系统',
                'difficulty': 'hard',
                'subjects': ['自动控制原理', '机械设计'],
                'skills': ['机械设计', '伺服控制', '运动学'],
                'category': 'robotics'
            },
            {
                'id': 'smart-home',
                'title': '智能家居系统',
                'difficulty': 'medium',
                'subjects': ['电工电子实验', '信号与系统'],
                'skills': ['WiFi通信', '传感器网络', '移动应用'],
                'category': 'iot'
            },
            {
                'id': 'weather-station',
                'title': '气象监测站',
                'difficulty': 'easy',
                'subjects': ['电工电子实验'],
                'skills': ['环境传感器', '数据采集', '无线传输'],
                'category': 'iot'
            },
            {
                'id': 'face-recognition',
                'title': '人脸识别系统',
                'difficulty': 'hard',
                'subjects': ['信号与系统'],
                'skills': ['深度学习', '计算机视觉', 'Python编程'],
                'category': 'ai'
            },
            {
                'id': 'chatbot',
                'title': '智能聊天机器人',
                'difficulty': 'medium',
                'subjects': ['信号与系统'],
                'skills': ['NLP', '机器学习', '对话系统'],
                'category': 'ai'
            }
        ]
    
    def _calculate_recommendation_score(self, portrait, project):
        """Calculate recommendation score for a project"""
        try:
            score = 0.0
            
            # Interest match (40% weight)
            interest_score = self._calculate_interest_match(portrait, project)
            score += interest_score * 0.4
            
            # Difficulty match (30% weight)
            difficulty_score = self._calculate_difficulty_match(portrait, project)
            score += difficulty_score * 0.3
            
            # Skill development potential (20% weight)
            skill_score = self._calculate_skill_development_score(portrait, project)
            score += skill_score * 0.2
            
            # Learning style match (10% weight)
            style_score = self._calculate_style_match(portrait, project)
            score += style_score * 0.1
            
            return min(1.0, score)
            
        except Exception as e:
            logger.error(f"Error calculating recommendation score: {str(e)}")
            return 0.0
    
    def _calculate_interest_match(self, portrait, project):
        """Calculate how well project matches user interests"""
        try:
            if not portrait.preferred_subjects:
                return 0.5  # Neutral score
            
            project_subjects = project.get('subjects', [])
            if not project_subjects:
                return 0.5
            
            # Check overlap between user's preferred subjects and project subjects
            overlap = len(set(portrait.preferred_subjects) & set(project_subjects))
            max_overlap = min(len(portrait.preferred_subjects), len(project_subjects))
            
            if max_overlap == 0:
                return 0.5
            
            return overlap / max_overlap
            
        except Exception as e:
            logger.error(f"Error calculating interest match: {str(e)}")
            return 0.5
    
    def _calculate_difficulty_match(self, portrait, project):
        """Calculate how well project difficulty matches user level"""
        try:
            project_difficulty = project.get('difficulty', 'medium')
            user_pace = portrait.learning_pace or 'medium'
            
            # Map difficulty and pace to numeric values
            difficulty_map = {'easy': 1, 'medium': 2, 'hard': 3}
            pace_map = {'slow': 1, 'medium': 2, 'fast': 3}
            
            project_level = difficulty_map.get(project_difficulty, 2)
            user_level = pace_map.get(user_pace, 2)
            
            # Calculate match score (closer levels = higher score)
            diff = abs(project_level - user_level)
            if diff == 0:
                return 1.0
            elif diff == 1:
                return 0.7
            else:
                return 0.3
                
        except Exception as e:
            logger.error(f"Error calculating difficulty match: {str(e)}")
            return 0.5
    
    def _calculate_skill_development_score(self, portrait, project):
        """Calculate skill development potential"""
        try:
            project_skills = project.get('skills', [])
            if not project_skills:
                return 0.5
            
            user_skills = portrait.skill_levels or {}
            
            # Calculate how many new skills the project would teach
            new_skills = 0
            improvement_skills = 0
            
            for skill in project_skills:
                if skill not in user_skills:
                    new_skills += 1
                elif user_skills[skill] < 0.7:  # Room for improvement
                    improvement_skills += 1
            
            total_skills = len(project_skills)
            development_ratio = (new_skills + improvement_skills * 0.5) / total_skills
            
            return min(1.0, development_ratio)
            
        except Exception as e:
            logger.error(f"Error calculating skill development score: {str(e)}")
            return 0.5
    
    def _calculate_style_match(self, portrait, project):
        """Calculate learning style match"""
        try:
            user_style = portrait.learning_style or 'mixed'
            project_category = project.get('category', 'general')
            
            # Map project categories to learning styles
            category_style_map = {
                'robotics': 'kinesthetic',
                'electronics': 'visual',
                'ai': 'auditory',
                'iot': 'mixed'
            }
            
            project_style = category_style_map.get(project_category, 'mixed')
            
            if user_style == project_style or user_style == 'mixed' or project_style == 'mixed':
                return 1.0
            else:
                return 0.5
                
        except Exception as e:
            logger.error(f"Error calculating style match: {str(e)}")
            return 0.5
    
    def _generate_recommendation_reason(self, portrait, project, score):
        """Generate explanation for recommendation"""
        try:
            reasons = []
            
            # Interest-based reasons
            if portrait.preferred_subjects:
                project_subjects = project.get('subjects', [])
                overlap = set(portrait.preferred_subjects) & set(project_subjects)
                if overlap:
                    reasons.append(f"与您感兴趣的{', '.join(overlap)}相关")
            
            # Skill development reasons
            project_skills = project.get('skills', [])
            user_skills = portrait.skill_levels or {}
            new_skills = [skill for skill in project_skills if skill not in user_skills]
            if new_skills:
                reasons.append(f"可以学习{', '.join(new_skills[:2])}等新技能")
            
            # Difficulty match reasons
            project_difficulty = project.get('difficulty', 'medium')
            user_pace = portrait.learning_pace or 'medium'
            if project_difficulty == user_pace:
                reasons.append("难度适合您的学习节奏")
            
            # Learning style reasons
            user_style = portrait.learning_style or 'mixed'
            if user_style == 'kinesthetic' and project.get('category') == 'robotics':
                reasons.append("适合动手实践的学习风格")
            elif user_style == 'visual' and project.get('category') == 'electronics':
                reasons.append("适合视觉化学习的特点")
            
            if not reasons:
                reasons.append("根据您的学习模式推荐")
            
            return "；".join(reasons[:3])  # Limit to 3 reasons
            
        except Exception as e:
            logger.error(f"Error generating recommendation reason: {str(e)}")
            return "基于AI分析推荐"
    
    def _save_recommendations(self, user_id, recommendations):
        """Save recommendations to database"""
        try:
            # Clear existing recommendations
            self.db.session.query(ProjectRecommendation).filter_by(user_id=user_id).delete()
            
            # Save new recommendations
            for rec in recommendations:
                recommendation = ProjectRecommendation(
                    user_id=user_id,
                    project_id=rec['project_id'],
                    project_title=rec['project_title'],
                    recommendation_score=rec['recommendation_score'],
                    recommendation_reason=rec['recommendation_reason'],
                    difficulty_match=rec['difficulty_match'],
                    interest_match=rec['interest_match'],
                    skill_development=rec['skill_development']
                )
                self.db.session.add(recommendation)
            
            self.db.session.commit()
            
        except Exception as e:
            self.db.session.rollback()
            logger.error(f"Error saving recommendations: {str(e)}")
    
    def get_user_recommendations(self, user_id):
        """Get saved recommendations for user"""
        try:
            recommendations = self.db.session.query(ProjectRecommendation).filter_by(
                user_id=user_id
            ).order_by(ProjectRecommendation.recommendation_score.desc()).all()
            
            return True, [rec.to_dict() for rec in recommendations]
            
        except Exception as e:
            logger.error(f"Error getting user recommendations: {str(e)}")
            return False, str(e)
    
    def update_recommendation_status(self, user_id, project_id, status_type, value=True):
        """Update recommendation status (viewed, started, completed)"""
        try:
            recommendation = self.db.session.query(ProjectRecommendation).filter_by(
                user_id=user_id,
                project_id=project_id
            ).first()
            
            if not recommendation:
                return False, "Recommendation not found"
            
            if status_type == 'viewed':
                recommendation.is_viewed = value
            elif status_type == 'started':
                recommendation.is_started = value
            elif status_type == 'completed':
                recommendation.is_completed = value
            else:
                return False, "Invalid status type"
            
            self.db.session.commit()
            return True, "Status updated"
            
        except Exception as e:
            self.db.session.rollback()
            logger.error(f"Error updating recommendation status: {str(e)}")
            return False, str(e)
