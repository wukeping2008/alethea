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
        required_fields = ['username', 'email', 'password', 'full_name']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Get role name (default to 'student')
        role_name = data.get('role_name', 'student')
        
        # Validate teacher-specific fields if role is teacher
        if role_name == 'teacher':
            teacher_data = data.get('teacher_data', {})
            teacher_required_fields = ['institution', 'teacher_id', 'phone']
            
            for field in teacher_required_fields:
                if field not in teacher_data or not teacher_data[field].strip():
                    return jsonify({'error': f'教师注册需要提供{field}信息'}), 400
            
            # Validate phone format
            phone = teacher_data['phone'].strip()
            import re
            if not re.match(r'^1[3-9]\d{9}$', phone):
                return jsonify({'error': '请输入有效的手机号码'}), 400
        
        # Get user manager
        user_manager = get_managers()['user_manager']
        
        # Create user
        success, result = user_manager.create_user(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            full_name=data['full_name'],
            role_name=role_name
        )
        
        if not success:
            return jsonify({'error': result}), 400
        
        # If teacher registration, store additional data and set pending status
        if role_name == 'teacher':
            try:
                # Get database from app context
                db = current_app.db
                
                # Update user with teacher data and pending status
                user = db.session.query(User).filter_by(id=result).first()
                if user:
                    # Store teacher data in user profile (you might want to create a separate table)
                    teacher_info = {
                        'institution': teacher_data['institution'],
                        'teacher_id': teacher_data['teacher_id'],
                        'phone': teacher_data['phone'],
                        'subjects': teacher_data.get('subjects', ''),
                        'status': 'pending_approval'
                    }
                    
                    # For now, store in a JSON field or create additional fields
                    # This is a simplified approach - in production, consider a separate teacher_profiles table
                    user.teacher_data = str(teacher_info)  # Store as string for now
                    user.is_active = False  # Deactivate until approved
                    
                    db.session.commit()
                    
                    return jsonify({
                        'message': 'Teacher registration submitted successfully. Please wait for admin approval.',
                        'user_id': result,
                        'status': 'pending_approval'
                    }), 201
                    
            except Exception as e:
                logger.error(f"Error storing teacher data: {str(e)}")
                # Continue with normal registration if teacher data storage fails
        
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
        if 'username' not in data or 'password' not in data:
            return jsonify({'success': False, 'error': 'Missing username or password'}), 400
        
        # Get user manager
        user_manager = get_managers()['user_manager']
        
        # Authenticate user
        success, result = user_manager.authenticate_user(
            username_or_email=data['username'],
            password=data['password']
        )
        
        if not success:
            return jsonify({'success': False, 'error': result}), 401
        
        # Add success flag and include permissions
        user_data = result['user']
        
        return jsonify({
            'success': True,
            'token': result['token'],
            'user': user_data
        }), 200
        
    except Exception as e:
        logger.error(f"Error in login: {str(e)}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

@user_bp.route('/verify', methods=['POST'])
def verify_token():
    """Verify authentication token"""
    try:
        token = None
        
        # Get token from header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'success': False, 'error': 'Token is missing'}), 401
        
        # Get user manager
        user_manager = get_managers()['user_manager']
        
        # Verify token
        success, user_or_error = user_manager.verify_token(token)
        
        if not success:
            return jsonify({'success': False, 'error': user_or_error}), 401
        
        # Include permissions in user data
        user_data = user_or_error.to_dict(include_sensitive=True)
        
        return jsonify({
            'success': True,
            'user': user_data
        }), 200
        
    except Exception as e:
        logger.error(f"Error in verify_token: {str(e)}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

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
        
        # Get database from app context
        db = current_app.db
        
        # Get the user to be updated
        user = db.session.query(User).filter_by(id=user_id).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Special handling for teacher approval
        if data['role_name'] == 'teacher' and data.get('approve', False):
            # Approve teacher application
            user.is_active = True
            
            # Log the approval
            logger.info(f"Teacher application approved for user {user.username} by admin {current_user.username}")
            
            db.session.commit()
            
            return jsonify({'message': 'Teacher application approved successfully'}), 200
        
        # Get user manager for regular role changes
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

# Admin panel specific routes

@user_bp.route('/admin/stats', methods=['GET'])
@token_required
@role_required('admin')
def get_admin_stats(current_user):
    """Get admin dashboard statistics"""
    try:
        # Get database from app context
        db = current_app.db
        
        # Count total users
        total_users = db.session.query(User).count()
        
        # Count pending teachers (inactive users with teacher role)
        pending_teachers = db.session.query(User).join(Role).filter(
            Role.name == 'teacher',
            User.is_active == False
        ).count()
        
        # Count active teachers
        active_teachers = db.session.query(User).join(Role).filter(
            Role.name == 'teacher',
            User.is_active == True
        ).count()
        
        # Count students
        students = db.session.query(User).join(Role).filter(
            Role.name == 'student'
        ).count()
        
        stats = {
            'total_users': total_users,
            'pending_teachers': pending_teachers,
            'active_teachers': active_teachers,
            'students': students
        }
        
        return jsonify(stats), 200
        
    except Exception as e:
        logger.error(f"Error in get_admin_stats: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@user_bp.route('/admin/pending-teachers', methods=['GET'])
@token_required
@role_required('admin')
def get_pending_teachers(current_user):
    """Get pending teacher applications"""
    try:
        # Get database from app context
        db = current_app.db
        
        # Query pending teachers
        pending_teachers = db.session.query(User).join(Role).filter(
            Role.name == 'teacher',
            User.is_active == False
        ).order_by(User.created_at.desc()).all()
        
        # Convert to dict with teacher data
        teacher_list = []
        for teacher in pending_teachers:
            teacher_dict = teacher.to_dict()
            
            # Parse teacher data if exists
            if hasattr(teacher, 'teacher_data') and teacher.teacher_data:
                try:
                    import ast
                    teacher_info = ast.literal_eval(teacher.teacher_data)
                    teacher_dict['teacher_info'] = teacher_info
                except:
                    teacher_dict['teacher_info'] = {}
            else:
                teacher_dict['teacher_info'] = {}
            
            teacher_list.append(teacher_dict)
        
        return jsonify(teacher_list), 200
        
    except Exception as e:
        logger.error(f"Error in get_pending_teachers: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@user_bp.route('/admin/approve-teacher/<int:user_id>', methods=['POST'])
@token_required
@role_required('admin')
def approve_teacher(current_user, user_id):
    """Approve teacher application"""
    try:
        # Get database from app context
        db = current_app.db
        
        # Get the teacher user
        teacher = db.session.query(User).filter_by(id=user_id).first()
        if not teacher:
            return jsonify({'error': 'Teacher not found'}), 404
        
        # Check if user has teacher role
        if not teacher.role or teacher.role.name != 'teacher':
            return jsonify({'error': 'User is not a teacher'}), 400
        
        # Approve the teacher
        teacher.is_active = True
        db.session.commit()
        
        logger.info(f"Teacher {teacher.username} approved by admin {current_user.username}")
        
        return jsonify({'message': 'Teacher approved successfully'}), 200
        
    except Exception as e:
        logger.error(f"Error in approve_teacher: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@user_bp.route('/admin/reject-teacher/<int:user_id>', methods=['POST'])
@token_required
@role_required('admin')
def reject_teacher(current_user, user_id):
    """Reject teacher application"""
    try:
        # Get database from app context
        db = current_app.db
        
        # Get the teacher user
        teacher = db.session.query(User).filter_by(id=user_id).first()
        if not teacher:
            return jsonify({'error': 'Teacher not found'}), 404
        
        # Check if user has teacher role
        if not teacher.role or teacher.role.name != 'teacher':
            return jsonify({'error': 'User is not a teacher'}), 400
        
        # Delete the rejected application
        db.session.delete(teacher)
        db.session.commit()
        
        logger.info(f"Teacher application {teacher.username} rejected by admin {current_user.username}")
        
        return jsonify({'message': 'Teacher application rejected'}), 200
        
    except Exception as e:
        logger.error(f"Error in reject_teacher: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
