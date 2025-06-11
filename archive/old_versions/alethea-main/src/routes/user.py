"""
API routes for user management in Alethea Platform
"""

from flask import Blueprint, request, jsonify, current_app
from functools import wraps
import logging
from src.models.user import User, Role, Permission, Subject, Question

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create blueprint
user_bp = Blueprint('user', __name__, url_prefix='/api/user')

# Get managers from app context
def get_managers():
    return current_app.user_managers

# Authentication decorator
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

# Permission check decorator
def permission_required(permission_name):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            current_user = kwargs.get('current_user')
            
            if not current_user:
                return jsonify({'error': 'Authentication required'}), 401
            
            if not current_user.has_permission(permission_name):
                return jsonify({'error': 'Permission denied'}), 403
            
            return f(*args, **kwargs)
        
        return decorated
    
    return decorator

# Role check decorator
def role_required(role_name):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            current_user = kwargs.get('current_user')
            
            if not current_user:
                return jsonify({'error': 'Authentication required'}), 401
            
            if not current_user.role or current_user.role.name != role_name:
                return jsonify({'error': 'Role required'}), 403
            
            return f(*args, **kwargs)
        
        return decorated
    
    return decorator

# Routes

@user_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['username', 'email', 'password']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Get user manager
        user_manager = get_managers()['user_manager']
        
        # Create user (default role is 'student')
        success, result = user_manager.create_user(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            full_name=data.get('full_name'),
            role_name=data.get('role_name', 'student')
        )
        
        if not success:
            return jsonify({'error': result}), 400
        
        return jsonify({'message': 'User registered successfully', 'user_id': result}), 201
        
    except Exception as e:
        logger.error(f"Error in register: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@user_bp.route('/login', methods=['POST'])
def login():
    """Login and get authentication token"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if 'username_or_email' not in data or 'password' not in data:
            return jsonify({'error': 'Missing username/email or password'}), 400
        
        # Get user manager
        user_manager = get_managers()['user_manager']
        
        # Authenticate user
        success, result = user_manager.authenticate_user(
            username_or_email=data['username_or_email'],
            password=data['password']
        )
        
        if not success:
            return jsonify({'error': result}), 401
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error in login: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@user_bp.route('/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    """Get current user profile"""
    try:
        return jsonify(current_user.to_dict()), 200
        
    except Exception as e:
        logger.error(f"Error in get_profile: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@user_bp.route('/profile', methods=['PUT'])
@token_required
def update_profile(current_user):
    """Update current user profile"""
    try:
        data = request.get_json()
        
        # Get user manager
        user_manager = get_managers()['user_manager']
        
        # Update user
        success, result = user_manager.update_user(current_user.id, data)
        
        if not success:
            return jsonify({'error': result}), 400
        
        return jsonify({'message': 'Profile updated successfully'}), 200
        
    except Exception as e:
        logger.error(f"Error in update_profile: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@user_bp.route('/users', methods=['GET'])
@token_required
@permission_required('manage_users')
def get_users(current_user):
    """Get all users (admin only)"""
    try:
        # Get database from app context
        db = current_app.db
        
        # Query all users
        users = db.session.query(User).all()
        
        # Convert to dict
        user_list = [user.to_dict() for user in users]
        
        return jsonify(user_list), 200
        
    except Exception as e:
        logger.error(f"Error in get_users: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@user_bp.route('/users/<int:user_id>', methods=['GET'])
@token_required
@permission_required('manage_users')
def get_user(current_user, user_id):
    """Get user by ID (admin only)"""
    try:
        # Get user manager
        user_manager = get_managers()['user_manager']
        
        # Get user
        success, user_or_error = user_manager.get_user_by_id(user_id)
        
        if not success:
            return jsonify({'error': user_or_error}), 404
        
        return jsonify(user_or_error.to_dict(include_sensitive=True)), 200
        
    except Exception as e:
        logger.error(f"Error in get_user: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@user_bp.route('/users/<int:user_id>/role', methods=['PUT'])
@token_required
@permission_required('manage_users')
def change_user_role(current_user, user_id):
    """Change user role (admin only)"""
    try:
        data = request.get_json()
        
        if 'role_name' not in data:
            return jsonify({'error': 'Missing role_name'}), 400
        
        # Get user manager
        user_manager = get_managers()['user_manager']
        
        # Change user role
        success, result = user_manager.change_user_role(user_id, data['role_name'])
        
        if not success:
            return jsonify({'error': result}), 400
        
        return jsonify({'message': result}), 200
        
    except Exception as e:
        logger.error(f"Error in change_user_role: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
@token_required
@permission_required('manage_users')
def delete_user(current_user, user_id):
    """Delete user (admin only)"""
    try:
        # Get user manager
        user_manager = get_managers()['user_manager']
        
        # Delete user
        success, result = user_manager.delete_user(user_id)
        
        if not success:
            return jsonify({'error': result}), 400
        
        return jsonify({'message': result}), 200
        
    except Exception as e:
        logger.error(f"Error in delete_user: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@user_bp.route('/roles', methods=['GET'])
@token_required
@permission_required('manage_roles')
def get_roles(current_user):
    """Get all roles (admin only)"""
    try:
        # Get database from app context
        db = current_app.db
        
        # Query all roles
        roles = db.session.query(Role).all()
        
        # Convert to dict
        role_list = [role.to_dict() for role in roles]
        
        return jsonify(role_list), 200
        
    except Exception as e:
        logger.error(f"Error in get_roles: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@user_bp.route('/permissions', methods=['GET'])
@token_required
@permission_required('manage_roles')
def get_permissions(current_user):
    """Get all permissions (admin only)"""
    try:
        # Get database from app context
        db = current_app.db
        
        # Query all permissions
        permissions = db.session.query(Permission).all()
        
        # Convert to dict
        permission_list = [permission.to_dict() for permission in permissions]
        
        return jsonify(permission_list), 200
        
    except Exception as e:
        logger.error(f"Error in get_permissions: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@user_bp.route('/subjects', methods=['GET'])
def get_subjects():
    """Get all subjects (public)"""
    try:
        # Get subject manager
        subject_manager = get_managers()['subject_manager']
        
        # Get subjects
        success, subjects = subject_manager.get_all_subjects()
        
        if not success:
            return jsonify({'error': subjects}), 400
        
        # Convert to dict
        subject_list = [subject.to_dict() for subject in subjects]
        
        return jsonify(subject_list), 200
        
    except Exception as e:
        logger.error(f"Error in get_subjects: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@user_bp.route('/subjects/category/<category>', methods=['GET'])
def get_subjects_by_category(category):
    """Get subjects by category (public)"""
    try:
        # Get subject manager
        subject_manager = get_managers()['subject_manager']
        
        # Get subjects
        success, subjects = subject_manager.get_subjects_by_category(category)
        
        if not success:
            return jsonify({'error': subjects}), 400
        
        # Convert to dict
        subject_list = [subject.to_dict() for subject in subjects]
        
        return jsonify(subject_list), 200
        
    except Exception as e:
        logger.error(f"Error in get_subjects_by_category: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@user_bp.route('/subjects', methods=['POST'])
@token_required
@permission_required('manage_subjects')
def create_subject(current_user):
    """Create a new subject (admin only)"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'category']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Get subject manager
        subject_manager = get_managers()['subject_manager']
        
        # Create subject
        success, result = subject_manager.create_subject(
            name=data['name'],
            category=data['category'],
            description=data.get('description'),
            icon=data.get('icon')
        )
        
        if not success:
            return jsonify({'error': result}), 400
        
        return jsonify({'message': 'Subject created successfully', 'subject_id': result}), 201
        
    except Exception as e:
        logger.error(f"Error in create_subject: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@user_bp.route('/questions', methods=['GET'])
@token_required
def get_user_questions(current_user):
    """Get questions for current user"""
    try:
        # Get query parameters
        favorites_only = request.args.get('favorites', 'false').lower() == 'true'
        subject_id = request.args.get('subject_id')
        if subject_id:
            try:
                subject_id = int(subject_id)
            except ValueError:
                return jsonify({'error': 'Invalid subject_id'}), 400
        
        # Get question manager
        question_manager = get_managers()['question_manager']
        
        # Get questions
        success, questions = question_manager.get_user_questions(
            user_id=current_user.id,
            include_favorites_only=favorites_only,
            subject_id=subject_id
        )
        
        if not success:
            return jsonify({'error': questions}), 400
        
        # Convert to dict
        question_list = [question.to_dict() for question in questions]
        
        return jsonify(question_list), 200
        
    except Exception as e:
        logger.error(f"Error in get_user_questions: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@user_bp.route('/questions/<int:question_id>/favorite', methods=['POST'])
@token_required
def toggle_favorite(current_user, question_id):
    """Toggle favorite status of a question"""
    try:
        # Get question manager
        question_manager = get_managers()['question_manager']
        
        # Toggle favorite
        success, result = question_manager.toggle_favorite(question_id, current_user.id)
        
        if not success:
            return jsonify({'error': result}), 400
        
        return jsonify({'is_favorite': result}), 200
        
    except Exception as e:
        logger.error(f"Error in toggle_favorite: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@user_bp.route('/questions/all', methods=['GET'])
@token_required
@permission_required('view_all_questions')
def get_all_questions(current_user):
    """Get all questions (teacher/admin only)"""
    try:
        # Get database from app context
        db = current_app.db
        
        # Query all questions
        questions = db.session.query(Question).order_by(Question.created_at.desc()).all()
        
        # Convert to dict
        question_list = [question.to_dict() for question in questions]
        
        return jsonify(question_list), 200
        
    except Exception as e:
        logger.error(f"Error in get_all_questions: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
