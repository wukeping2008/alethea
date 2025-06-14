"""
Real-time Analytics Routes for Alethea Platform
Provides real-time user behavior tracking and dashboard updates
"""

import json
import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify, session
from models.user_analytics import UserAnalyticsManager, UserBehavior, LearningSession
from models.user import db, User, Subject

realtime_bp = Blueprint('realtime', __name__, url_prefix='/api/realtime')

# Initialize analytics manager
analytics_manager = UserAnalyticsManager(db)

@realtime_bp.route('/track', methods=['POST'])
def track_behavior():
    """Track user behavior in real-time"""
    try:
        data = request.get_json()
        
        # Get or create session ID
        session_id = session.get('session_id')
        if not session_id:
            session_id = str(uuid.uuid4())
            session['session_id'] = session_id
        
        # Extract tracking data
        user_id = data.get('user_id', 1)  # Default demo user
        action_type = data.get('action_type')
        action_data = data.get('action_data', {})
        subject_id = data.get('subject_id')
        duration = data.get('duration')
        
        # Get client info
        ip_address = request.remote_addr
        user_agent = request.headers.get('User-Agent')
        
        # Track the behavior
        success, result = analytics_manager.track_behavior(
            user_id=user_id,
            action_type=action_type,
            action_data=action_data,
            subject_id=subject_id,
            session_id=session_id,
            ip_address=ip_address,
            user_agent=user_agent,
            duration=duration
        )
        
        if success:
            # Update or create learning session
            update_learning_session(user_id, session_id, action_type, action_data)
            
            return jsonify({
                'success': True,
                'behavior_id': result,
                'session_id': session_id
            })
        else:
            return jsonify({
                'success': False,
                'error': result
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@realtime_bp.route('/session/start', methods=['POST'])
def start_session():
    """Start a new learning session"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', 1)
        
        # Generate new session ID
        session_id = str(uuid.uuid4())
        session['session_id'] = session_id
        
        # Create learning session
        learning_session = LearningSession(
            user_id=user_id,
            session_id=session_id,
            start_time=datetime.utcnow(),
            pages_visited=[],
            actions_performed=[],
            subjects_explored=[],
            questions_asked=0,
            projects_viewed=0
        )
        
        db.session.add(learning_session)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'session_id': session_id
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@realtime_bp.route('/session/end', methods=['POST'])
def end_session():
    """End current learning session"""
    try:
        session_id = session.get('session_id')
        if not session_id:
            return jsonify({
                'success': False,
                'error': 'No active session'
            }), 400
        
        # Find and update session
        learning_session = db.session.query(LearningSession).filter_by(
            session_id=session_id
        ).first()
        
        if learning_session:
            learning_session.end_time = datetime.utcnow()
            if learning_session.start_time:
                duration = (learning_session.end_time - learning_session.start_time).total_seconds()
                learning_session.duration = int(duration)
            
            # Calculate engagement score
            learning_session.engagement_score = calculate_engagement_score(learning_session)
            
            db.session.commit()
        
        # Clear session
        session.pop('session_id', None)
        
        return jsonify({
            'success': True,
            'session_duration': learning_session.duration if learning_session else 0
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@realtime_bp.route('/analytics/<int:user_id>', methods=['GET'])
def get_realtime_analytics(user_id):
    """Get real-time analytics for user"""
    try:
        # Get analytics data
        success, analytics = analytics_manager.get_user_analytics(user_id, days=30)
        if not success:
            return jsonify({
                'success': False,
                'error': analytics
            }), 400
        
        # Get current session info
        session_id = session.get('session_id')
        current_session = None
        if session_id:
            current_session = db.session.query(LearningSession).filter_by(
                session_id=session_id
            ).first()
        
        # Format data for dashboard
        dashboard_data = format_dashboard_data(analytics, current_session)
        
        return jsonify({
            'success': True,
            'data': dashboard_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@realtime_bp.route('/dashboard/<int:user_id>', methods=['GET'])
def get_dashboard_data(user_id):
    """Get comprehensive dashboard data"""
    try:
        # Get user info
        user = db.session.query(User).get(user_id)
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        # Get analytics
        success, analytics = analytics_manager.get_user_analytics(user_id, days=30)
        if not success:
            analytics = {
                'total_actions': 0,
                'action_breakdown': {},
                'subject_interests': {},
                'knowledge_points': [],
                'learning_sessions': [],
                'daily_activity': {},
                'engagement_metrics': {
                    'engagement_score': 0.0,
                    'avg_session_duration': 0,
                    'total_time_spent': 0,
                    'consistency_score': 0.0
                }
            }
        
        # Get digital portrait
        portrait_success, portrait = analytics_manager.generate_digital_portrait(user_id)
        if not portrait_success:
            portrait = {}
        
        # Get recommendations
        rec_success, recommendations = analytics_manager.get_user_recommendations(user_id)
        if not rec_success:
            recommendations = []
        
        # Format comprehensive dashboard data
        dashboard_data = {
            'user_info': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'created_at': user.created_at.isoformat() if user.created_at else None
            },
            'statistics': {
                'total_projects': analytics['action_breakdown'].get('view_project', 0) + analytics['action_breakdown'].get('start_project', 0),
                'completed_tests': analytics['action_breakdown'].get('complete_test', 0),
                'study_hours': round(analytics['engagement_metrics']['total_time_spent'] / 3600, 1),
                'knowledge_points': len(analytics['knowledge_points'])
            },
            'progress': {
                'overall_progress': min(100, analytics['engagement_metrics']['engagement_score'] * 100),
                'subjects_studied': len(analytics['subject_interests']),
                'avg_score': 85,  # Mock data
                'completion_rate': min(100, analytics['engagement_metrics']['consistency_score'] * 100)
            },
            'subject_progress': format_subject_progress(analytics['knowledge_points']),
            'learning_analytics': format_learning_analytics(analytics),
            'achievements': generate_achievements(analytics),
            'ai_recommendations': format_ai_recommendations(recommendations[:3]),
            'recent_activities': format_recent_activities(analytics),
            'learning_calendar': generate_learning_calendar(analytics),
            'quick_actions': [
                {'icon': '🤖', 'title': '提问AI助手', 'action': 'ask_question'},
                {'icon': '👥', 'title': '开始新实验', 'action': 'start_experiment'},
                {'icon': '📚', 'title': '复习知识点', 'action': 'review_knowledge'},
                {'icon': '📊', 'title': '查看详细报告', 'action': 'view_report'}
            ],
            'digital_portrait': portrait,
            'real_time_stats': {
                'current_session_duration': get_current_session_duration(),
                'today_actions': get_today_actions(analytics),
                'weekly_streak': calculate_weekly_streak(analytics)
            }
        }
        
        return jsonify({
            'success': True,
            'data': dashboard_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def update_learning_session(user_id, session_id, action_type, action_data):
    """Update learning session with new action"""
    try:
        session_obj = db.session.query(LearningSession).filter_by(
            session_id=session_id
        ).first()
        
        if not session_obj:
            # Create new session if not exists
            session_obj = LearningSession(
                user_id=user_id,
                session_id=session_id,
                start_time=datetime.utcnow(),
                pages_visited=[],
                actions_performed=[],
                subjects_explored=[],
                questions_asked=0,
                projects_viewed=0
            )
            db.session.add(session_obj)
        
        # Update session data
        if not session_obj.actions_performed:
            session_obj.actions_performed = []
        session_obj.actions_performed.append({
            'action': action_type,
            'timestamp': datetime.utcnow().isoformat(),
            'data': action_data
        })
        
        # Update counters
        if action_type == 'ask_question':
            session_obj.questions_asked = (session_obj.questions_asked or 0) + 1
        elif action_type in ['view_project', 'start_project']:
            session_obj.projects_viewed = (session_obj.projects_viewed or 0) + 1
        
        # Update subjects explored
        if action_data and 'subject' in action_data:
            if not session_obj.subjects_explored:
                session_obj.subjects_explored = []
            subject = action_data['subject']
            if subject not in session_obj.subjects_explored:
                session_obj.subjects_explored.append(subject)
        
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        print(f"Error updating learning session: {e}")

def calculate_engagement_score(session):
    """Calculate engagement score for a session"""
    try:
        score = 0.0
        
        # Duration factor (max 30 points)
        if session.duration:
            duration_score = min(30, session.duration / 60)  # 1 point per minute, max 30
            score += duration_score
        
        # Actions factor (max 40 points)
        actions_count = len(session.actions_performed or [])
        actions_score = min(40, actions_count * 2)  # 2 points per action, max 40
        score += actions_score
        
        # Questions factor (max 20 points)
        questions_score = min(20, (session.questions_asked or 0) * 5)  # 5 points per question, max 20
        score += questions_score
        
        # Subject diversity factor (max 10 points)
        subjects_count = len(session.subjects_explored or [])
        subjects_score = min(10, subjects_count * 3)  # 3 points per subject, max 10
        score += subjects_score
        
        # Normalize to 0-1 scale
        return min(1.0, score / 100)
        
    except Exception as e:
        print(f"Error calculating engagement score: {e}")
        return 0.0

def format_dashboard_data(analytics, current_session):
    """Format analytics data for dashboard display"""
    try:
        return {
            'total_actions': analytics['total_actions'],
            'engagement_score': analytics['engagement_metrics']['engagement_score'],
            'session_duration': analytics['engagement_metrics']['avg_session_duration'],
            'consistency_score': analytics['engagement_metrics']['consistency_score'],
            'current_session': {
                'duration': get_session_duration(current_session) if current_session else 0,
                'actions': len(current_session.actions_performed or []) if current_session else 0,
                'questions': current_session.questions_asked or 0 if current_session else 0
            },
            'subject_breakdown': analytics['subject_interests'],
            'daily_activity': analytics['daily_activity'],
            'knowledge_points': len(analytics['knowledge_points'])
        }
    except Exception as e:
        print(f"Error formatting dashboard data: {e}")
        return {}

def format_subject_progress(knowledge_points):
    """Format subject progress data"""
    try:
        subjects = {}
        for kp in knowledge_points:
            subject = kp['subject_name']
            if subject and subject != 'Unknown':
                if subject not in subjects:
                    subjects[subject] = {
                        'name': subject,
                        'progress': 0,
                        'knowledge_points': 0,
                        'mastery_level': 0
                    }
                
                subjects[subject]['knowledge_points'] += 1
                subjects[subject]['mastery_level'] += kp['mastery_level']
        
        # Calculate averages and progress
        for subject in subjects.values():
            if subject['knowledge_points'] > 0:
                subject['mastery_level'] = subject['mastery_level'] / subject['knowledge_points']
                subject['progress'] = int(subject['mastery_level'] * 100)
        
        return list(subjects.values())
        
    except Exception as e:
        print(f"Error formatting subject progress: {e}")
        return []

def format_learning_analytics(analytics):
    """Format learning analytics for charts"""
    try:
        # Daily activity chart data
        daily_data = []
        for date, count in analytics['daily_activity'].items():
            daily_data.append({
                'date': date,
                'actions': count,
                'engagement': min(100, count * 5)  # Normalize engagement
            })
        
        # Sort by date
        daily_data.sort(key=lambda x: x['date'])
        
        return {
            'daily_activity': daily_data,
            'action_breakdown': analytics['action_breakdown'],
            'engagement_trend': generate_engagement_trend(analytics)
        }
        
    except Exception as e:
        print(f"Error formatting learning analytics: {e}")
        return {}

def generate_achievements(analytics):
    """Generate achievement badges based on user activity"""
    try:
        achievements = []
        
        # Question master
        total_questions = analytics['action_breakdown'].get('ask_question', 0)
        if total_questions >= 50:
            achievements.append({
                'icon': '🏆',
                'title': '提问专家',
                'description': f'已提问{total_questions}次，善于思考'
            })
        elif total_questions >= 20:
            achievements.append({
                'icon': '🥇',
                'title': '学习达人',
                'description': f'已提问{total_questions}次，求知欲强'
            })
        elif total_questions >= 5:
            achievements.append({
                'icon': '🌟',
                'title': '知识探索者',
                'description': f'已提问{total_questions}次，开始探索'
            })
        
        # Consistency master
        consistency = analytics['engagement_metrics']['consistency_score']
        if consistency >= 0.8:
            achievements.append({
                'icon': '⏰',
                'title': '坚持不懈',
                'description': '学习习惯优秀，持续性强'
            })
        
        # Knowledge accumulator
        knowledge_count = len(analytics['knowledge_points'])
        if knowledge_count >= 30:
            achievements.append({
                'icon': '🧠',
                'title': '知识大师',
                'description': f'掌握{knowledge_count}个知识点'
            })
        
        return achievements
        
    except Exception as e:
        print(f"Error generating achievements: {e}")
        return []

def format_ai_recommendations(recommendations):
    """Format AI recommendations for display"""
    try:
        formatted = []
        for rec in recommendations:
            formatted.append({
                'icon': '🚀',
                'title': rec['project_title'],
                'description': rec['recommendation_reason'],
                'action': f"开始{rec['project_title']}"
            })
        return formatted
        
    except Exception as e:
        print(f"Error formatting AI recommendations: {e}")
        return []

def format_recent_activities(analytics):
    """Format recent activities"""
    try:
        activities = []
        
        # Get recent behaviors from sessions
        for session in analytics['learning_sessions'][-5:]:  # Last 5 sessions
            if session['actions_performed']:
                for action in session['actions_performed'][-3:]:  # Last 3 actions per session
                    activities.append({
                        'icon': get_action_icon(action.get('action', 'unknown')),
                        'description': get_action_description(action),
                        'time': action.get('timestamp', '')
                    })
        
        return activities[-10:]  # Return last 10 activities
        
    except Exception as e:
        print(f"Error formatting recent activities: {e}")
        return []

def generate_learning_calendar(analytics):
    """Generate learning calendar data"""
    try:
        from datetime import datetime, timedelta
        
        # Get current month data
        today = datetime.now()
        month_start = today.replace(day=1)
        
        calendar_data = {
            'year': today.year,
            'month': today.month,
            'days': []
        }
        
        # Generate days for current month
        for day in range(1, 32):
            try:
                date = today.replace(day=day)
                date_str = date.strftime('%Y-%m-%d')
                
                activity_count = analytics['daily_activity'].get(date_str, 0)
                
                calendar_data['days'].append({
                    'day': day,
                    'has_activity': activity_count > 0,
                    'activity_level': min(3, activity_count // 5),  # 0-3 activity levels
                    'is_today': day == today.day
                })
            except ValueError:
                # Invalid day for month
                break
        
        return calendar_data
        
    except Exception as e:
        print(f"Error generating learning calendar: {e}")
        return {}

def get_action_icon(action_type):
    """Get icon for action type"""
    icons = {
        'ask_question': '❓',
        'search': '🔍',
        'view_project': '📋',
        'start_project': '🚀',
        'complete_project': '✅',
        'browse': '👀',
        'simulation': '⚡',
        'test': '📝'
    }
    return icons.get(action_type, '📌')

def get_action_description(action):
    """Get description for action"""
    action_type = action.get('action', 'unknown')
    data = action.get('data', {})
    
    descriptions = {
        'ask_question': f"提问了关于{data.get('subject', '学习')}的问题",
        'search': f"搜索了'{data.get('query', '相关内容')}'",
        'view_project': f"查看了{data.get('project', '项目')}",
        'start_project': f"开始了{data.get('project', '新项目')}",
        'browse': f"浏览了{data.get('page', '页面')}",
        'simulation': f"运行了{data.get('simulation', '仿真')}实验"
    }
    
    return descriptions.get(action_type, f"执行了{action_type}操作")

def get_current_session_duration():
    """Get current session duration"""
    try:
        session_id = session.get('session_id')
        if not session_id:
            return 0
        
        session_obj = db.session.query(LearningSession).filter_by(
            session_id=session_id
        ).first()
        
        if session_obj and session_obj.start_time:
            duration = (datetime.utcnow() - session_obj.start_time).total_seconds()
            return int(duration)
        
        return 0
        
    except Exception as e:
        print(f"Error getting current session duration: {e}")
        return 0

def get_today_actions(analytics):
    """Get today's action count"""
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        return analytics['daily_activity'].get(today, 0)
        
    except Exception as e:
        print(f"Error getting today's actions: {e}")
        return 0

def calculate_weekly_streak(analytics):
    """Calculate weekly learning streak"""
    try:
        from datetime import datetime, timedelta
        
        today = datetime.now().date()
        streak = 0
        
        # Check each day going backwards
        for i in range(7):
            check_date = today - timedelta(days=i)
            date_str = check_date.strftime('%Y-%m-%d')
            
            if analytics['daily_activity'].get(date_str, 0) > 0:
                streak += 1
            else:
                break
        
        return streak
        
    except Exception as e:
        print(f"Error calculating weekly streak: {e}")
        return 0

def get_session_duration(session_obj):
    """Get session duration in seconds"""
    try:
        if session_obj and session_obj.start_time:
            if session_obj.end_time:
                return int((session_obj.end_time - session_obj.start_time).total_seconds())
            else:
                return int((datetime.utcnow() - session_obj.start_time).total_seconds())
        return 0
    except Exception as e:
        print(f"Error getting session duration: {e}")
        return 0

def generate_engagement_trend(analytics):
    """Generate engagement trend data"""
    try:
        # Simple trend based on daily activity
        daily_activity = analytics['daily_activity']
        trend_data = []
        
        sorted_dates = sorted(daily_activity.keys())
        for date in sorted_dates[-7:]:  # Last 7 days
            count = daily_activity[date]
            engagement = min(100, count * 10)  # Normalize to 0-100
            trend_data.append({
                'date': date,
                'engagement': engagement
            })
        
        return trend_data
        
    except Exception as e:
        print(f"Error generating engagement trend: {e}")
        return []
