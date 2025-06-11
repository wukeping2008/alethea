"""
API routes for user analytics and digital portrait in Alethea Platform
"""

from flask import Blueprint, request, jsonify, current_app
from functools import wraps
import logging
from src.models.user_analytics import UserAnalyticsManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create blueprint
analytics_bp = Blueprint('analytics', __name__, url_prefix='/api/analytics')

# Get managers from app context
def get_managers():
    return current_app.user_managers

# Authentication decorator (reuse from user routes)
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Get token from header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        # Verify token
        user_manager = get_managers()['user_manager']
        success, user_or_error = user_manager.verify_token(token)
        
        if not success:
            return jsonify({'error': user_or_error}), 401
        
        # Add user to request context
        kwargs['current_user'] = user_or_error
        return f(*args, **kwargs)
    
    return decorated

# Routes

@analytics_bp.route('/track', methods=['POST'])
@token_required
def track_behavior(current_user):
    """Track user behavior"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if 'action_type' not in data:
            return jsonify({'error': 'Missing action_type'}), 400
        
        # Get analytics manager
        analytics_manager = get_managers().get('analytics_manager')
        if not analytics_manager:
            return jsonify({'error': 'Analytics manager not available'}), 500
        
        # Get additional data from request
        session_id = request.headers.get('X-Session-ID')
        ip_address = request.remote_addr
        user_agent = request.headers.get('User-Agent')
        
        # Track behavior
        success, result = analytics_manager.track_behavior(
            user_id=current_user.id,
            action_type=data['action_type'],
            action_data=data.get('action_data'),
            subject_id=data.get('subject_id'),
            session_id=session_id,
            ip_address=ip_address,
            user_agent=user_agent,
            duration=data.get('duration')
        )
        
        if not success:
            return jsonify({'error': result}), 400
        
        return jsonify({'message': 'Behavior tracked successfully', 'behavior_id': result}), 201
        
    except Exception as e:
        logger.error(f"Error in track_behavior: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@analytics_bp.route('/dashboard', methods=['GET'])
@token_required
def get_user_dashboard(current_user):
    """Get user analytics dashboard data"""
    try:
        # Get query parameters
        days = request.args.get('days', 30, type=int)
        
        # Get analytics manager
        analytics_manager = get_managers().get('analytics_manager')
        if not analytics_manager:
            return jsonify({'error': 'Analytics manager not available'}), 500
        
        # Get user analytics
        success, analytics = analytics_manager.get_user_analytics(current_user.id, days)
        
        if not success:
            return jsonify({'error': analytics}), 400
        
        return jsonify(analytics), 200
        
    except Exception as e:
        logger.error(f"Error in get_user_dashboard: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@analytics_bp.route('/portrait', methods=['GET'])
@token_required
def get_digital_portrait(current_user):
    """Get user's digital portrait"""
    try:
        # Get analytics manager
        analytics_manager = get_managers().get('analytics_manager')
        if not analytics_manager:
            return jsonify({'error': 'Analytics manager not available'}), 500
        
        # Get existing portrait from database
        from src.models.user_analytics import UserDigitalPortrait
        db = current_app.db
        
        portrait = db.session.query(UserDigitalPortrait).filter_by(user_id=current_user.id).first()
        
        if not portrait:
            return jsonify({'error': 'Digital portrait not found. Please generate one first.'}), 404
        
        return jsonify(portrait.to_dict()), 200
        
    except Exception as e:
        logger.error(f"Error in get_digital_portrait: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@analytics_bp.route('/portrait/generate', methods=['POST'])
@token_required
def generate_digital_portrait(current_user):
    """Generate or update user's digital portrait"""
    try:
        # Get analytics manager
        analytics_manager = get_managers().get('analytics_manager')
        if not analytics_manager:
            return jsonify({'error': 'Analytics manager not available'}), 500
        
        # Generate digital portrait
        success, portrait = analytics_manager.generate_digital_portrait(current_user.id)
        
        if not success:
            return jsonify({'error': portrait}), 400
        
        return jsonify({
            'message': 'Digital portrait generated successfully',
            'portrait': portrait
        }), 200
        
    except Exception as e:
        logger.error(f"Error in generate_digital_portrait: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@analytics_bp.route('/recommendations', methods=['GET'])
@token_required
def get_project_recommendations(current_user):
    """Get personalized project recommendations"""
    try:
        # Get analytics manager
        analytics_manager = get_managers().get('analytics_manager')
        if not analytics_manager:
            return jsonify({'error': 'Analytics manager not available'}), 500
        
        # Get saved recommendations
        success, recommendations = analytics_manager.get_user_recommendations(current_user.id)
        
        if not success:
            return jsonify({'error': recommendations}), 400
        
        return jsonify(recommendations), 200
        
    except Exception as e:
        logger.error(f"Error in get_project_recommendations: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@analytics_bp.route('/recommendations/generate', methods=['POST'])
@token_required
def generate_project_recommendations(current_user):
    """Generate new project recommendations"""
    try:
        # Get analytics manager
        analytics_manager = get_managers().get('analytics_manager')
        if not analytics_manager:
            return jsonify({'error': 'Analytics manager not available'}), 500
        
        # Generate recommendations
        success, recommendations = analytics_manager.generate_project_recommendations(current_user.id)
        
        if not success:
            return jsonify({'error': recommendations}), 400
        
        return jsonify({
            'message': 'Project recommendations generated successfully',
            'recommendations': recommendations
        }), 200
        
    except Exception as e:
        logger.error(f"Error in generate_project_recommendations: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@analytics_bp.route('/recommendations/<project_id>/status', methods=['PUT'])
@token_required
def update_recommendation_status(current_user, project_id):
    """Update recommendation status (viewed, started, completed)"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if 'status_type' not in data:
            return jsonify({'error': 'Missing status_type'}), 400
        
        # Get analytics manager
        analytics_manager = get_managers().get('analytics_manager')
        if not analytics_manager:
            return jsonify({'error': 'Analytics manager not available'}), 500
        
        # Update status
        success, result = analytics_manager.update_recommendation_status(
            user_id=current_user.id,
            project_id=project_id,
            status_type=data['status_type'],
            value=data.get('value', True)
        )
        
        if not success:
            return jsonify({'error': result}), 400
        
        return jsonify({'message': result}), 200
        
    except Exception as e:
        logger.error(f"Error in update_recommendation_status: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@analytics_bp.route('/knowledge-points', methods=['GET'])
@token_required
def get_knowledge_points(current_user):
    """Get user's knowledge points and mastery levels"""
    try:
        # Get database from app context
        db = current_app.db
        
        # Get knowledge points
        from src.models.user_analytics import UserKnowledgePoint
        knowledge_points = db.session.query(UserKnowledgePoint).filter_by(
            user_id=current_user.id
        ).order_by(UserKnowledgePoint.mastery_level.desc()).all()
        
        # Convert to dict and group by subject
        result = {}
        for kp in knowledge_points:
            subject_name = kp.subject.name if kp.subject else 'Unknown'
            if subject_name not in result:
                result[subject_name] = []
            result[subject_name].append(kp.to_dict())
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error in get_knowledge_points: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@analytics_bp.route('/learning-sessions', methods=['GET'])
@token_required
def get_learning_sessions(current_user):
    """Get user's learning sessions"""
    try:
        # Get query parameters
        days = request.args.get('days', 30, type=int)
        
        # Get database from app context
        db = current_app.db
        
        # Get learning sessions
        from src.models.user_analytics import LearningSession
        from datetime import datetime, timedelta
        
        start_date = datetime.utcnow() - timedelta(days=days)
        sessions = db.session.query(LearningSession).filter(
            LearningSession.user_id == current_user.id,
            LearningSession.start_time >= start_date
        ).order_by(LearningSession.start_time.desc()).all()
        
        # Convert to dict
        session_list = [session.to_dict() for session in sessions]
        
        return jsonify(session_list), 200
        
    except Exception as e:
        logger.error(f"Error in get_learning_sessions: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@analytics_bp.route('/insights', methods=['GET'])
@token_required
def get_ai_insights(current_user):
    """Get AI-generated insights about user's learning"""
    try:
        # Get analytics manager
        analytics_manager = get_managers().get('analytics_manager')
        if not analytics_manager:
            return jsonify({'error': 'Analytics manager not available'}), 500
        
        # Get user analytics
        success, analytics = analytics_manager.get_user_analytics(current_user.id, days=90)
        if not success:
            return jsonify({'error': analytics}), 400
        
        # Get digital portrait for AI insights
        from src.models.user_analytics import UserDigitalPortrait
        db = current_app.db
        
        portrait = db.session.query(UserDigitalPortrait).filter_by(user_id=current_user.id).first()
        
        insights = {
            'engagement_insights': self._generate_engagement_insights(analytics),
            'learning_insights': self._generate_learning_insights(analytics),
            'recommendation_insights': self._generate_recommendation_insights(analytics),
            'ai_insights': portrait.ai_insights if portrait else None
        }
        
        return jsonify(insights), 200
        
    except Exception as e:
        logger.error(f"Error in get_ai_insights: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

def _generate_engagement_insights(analytics):
    """Generate insights about user engagement"""
    insights = []
    engagement = analytics['engagement_metrics']
    
    if engagement['consistency_score'] > 0.8:
        insights.append("您的学习一致性很高，保持了良好的学习习惯！")
    elif engagement['consistency_score'] < 0.3:
        insights.append("建议您建立更规律的学习计划，提高学习的一致性。")
    
    if engagement['avg_session_duration'] > 1800:  # 30 minutes
        insights.append("您的学习专注度很好，能够进行深度学习。")
    elif engagement['avg_session_duration'] < 600:  # 10 minutes
        insights.append("尝试延长每次学习的时间，这样能够更深入地理解知识点。")
    
    if engagement['engagement_score'] > 0.7:
        insights.append("您的整体学习参与度很高，继续保持！")
    
    return insights

def _generate_learning_insights(analytics):
    """Generate insights about learning patterns"""
    insights = []
    
    # Analyze subject interests
    if analytics['subject_interests']:
        top_subject = max(analytics['subject_interests'], key=analytics['subject_interests'].get)
        insights.append(f"您对{top_subject}表现出最大的兴趣。")
    
    # Analyze action patterns
    action_breakdown = analytics['action_breakdown']
    if action_breakdown.get('ask_question', 0) > 10:
        insights.append("您善于提问，这是很好的学习习惯。")
    
    if action_breakdown.get('view_project', 0) > 5:
        insights.append("您对项目学习很感兴趣，这有助于实践技能的提升。")
    
    return insights

def _generate_recommendation_insights(analytics):
    """Generate insights for recommendations"""
    insights = []
    
    # Analyze learning style
    action_breakdown = analytics['action_breakdown']
    total_actions = sum(action_breakdown.values())
    
    if total_actions > 0:
        practical_ratio = (action_breakdown.get('start_project', 0) + action_breakdown.get('simulation', 0)) / total_actions
        if practical_ratio > 0.4:
            insights.append("您偏向实践型学习，建议多参与动手项目。")
        
        question_ratio = action_breakdown.get('ask_question', 0) / total_actions
        if question_ratio > 0.3:
            insights.append("您善于思考和提问，适合探索性学习。")
    
    return insights

@analytics_bp.route('/profile/<int:user_id>', methods=['GET'])
def get_user_profile_public(user_id):
    """Get user's digital portrait (public endpoint for testing)"""
    try:
        # Get analytics manager
        analytics_manager = get_managers().get('analytics_manager')
        if not analytics_manager:
            return jsonify({'error': 'Analytics manager not available'}), 500
        
        # Get existing portrait from database
        from src.models.user_analytics import UserDigitalPortrait
        db = current_app.db
        
        portrait = db.session.query(UserDigitalPortrait).filter_by(user_id=user_id).first()
        
        if not portrait:
            return jsonify({'error': 'Digital portrait not found. Please generate one first.'}), 404
        
        return jsonify(portrait.to_dict()), 200
        
    except Exception as e:
        logger.error(f"Error in get_user_profile_public: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@analytics_bp.route('/learning-analysis/<int:user_id>', methods=['GET'])
def get_learning_analysis_public(user_id):
    """Get user learning analysis (public endpoint for testing)"""
    try:
        # Get analytics manager
        analytics_manager = get_managers().get('analytics_manager')
        if not analytics_manager:
            return jsonify({'error': 'Analytics manager not available'}), 500
        
        # Get user analytics
        days = request.args.get('days', 30, type=int)
        success, analytics = analytics_manager.get_user_analytics(user_id, days)
        
        if not success:
            return jsonify({'error': analytics}), 400
        
        return jsonify(analytics), 200
        
    except Exception as e:
        logger.error(f"Error in get_learning_analysis_public: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@analytics_bp.route('/export', methods=['GET'])
@token_required
def export_user_data(current_user):
    """Export user's learning data"""
    try:
        # Get analytics manager
        analytics_manager = get_managers().get('analytics_manager')
        if not analytics_manager:
            return jsonify({'error': 'Analytics manager not available'}), 500
        
        # Get comprehensive user data
        success, analytics = analytics_manager.get_user_analytics(current_user.id, days=365)  # Full year
        if not success:
            return jsonify({'error': analytics}), 400
        
        # Get digital portrait
        from src.models.user_analytics import UserDigitalPortrait
        db = current_app.db
        
        portrait = db.session.query(UserDigitalPortrait).filter_by(user_id=current_user.id).first()
        
        # Get recommendations
        success, recommendations = analytics_manager.get_user_recommendations(current_user.id)
        if not success:
            recommendations = []
        
        export_data = {
            'user_info': current_user.to_dict(),
            'analytics': analytics,
            'digital_portrait': portrait.to_dict() if portrait else None,
            'recommendations': recommendations,
            'export_date': datetime.utcnow().isoformat()
        }
        
        return jsonify(export_data), 200
        
    except Exception as e:
        logger.error(f"Error in export_user_data: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
