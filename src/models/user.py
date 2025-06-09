"""
User Management Module for Alethea Platform
Supports multiple user roles and permissions
"""

import os
import json
import logging
import hashlib
import secrets
import re
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union, Tuple
import jwt
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Table
from sqlalchemy.orm import relationship

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize SQLAlchemy
db = SQLAlchemy()

# Define association tables for many-to-many relationships
role_permission = Table(
    'role_permission', 
    db.metadata,
    Column('role_id', Integer, ForeignKey('roles.id')),
    Column('permission_id', Integer, ForeignKey('permissions.id'))
)

user_subject = Table(
    'user_subject', 
    db.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('subject_id', Integer, ForeignKey('subjects.id'))
)

class Permission(db.Model):
    """Permission model for defining access rights"""
    __tablename__ = 'permissions'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Permission {self.name}>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }


class Role(db.Model):
    """Role model for user roles (student, teacher, admin)"""
    __tablename__ = 'roles'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    permissions = relationship('Permission', secondary=role_permission, backref='roles')
    users = relationship('User', backref='role')
    
    def __repr__(self):
        return f"<Role {self.name}>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'permissions': [p.name for p in self.permissions]
        }


class Subject(db.Model):
    """Subject model for academic subjects"""
    __tablename__ = 'subjects'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    category = Column(String(50))  # e.g., "engineering", "science", "math"
    description = Column(Text)
    icon = Column(String(100))  # Icon class or path
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    questions = relationship('Question', backref='subject')
    
    def __repr__(self):
        return f"<Subject {self.name}>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'description': self.description,
            'icon': self.icon
        }


class User(db.Model):
    """User model with role-based permissions"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    full_name = Column(String(100))
    role_id = Column(Integer, ForeignKey('roles.id'))
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    questions = relationship('Question', backref='user')
    favorite_subjects = relationship('Subject', secondary=user_subject, backref='interested_users')
    
    def __repr__(self):
        return f"<User {self.username}>"
    
    def set_password(self, password):
        """Set password hash"""
        self.password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    def check_password(self, password):
        """Check password against hash"""
        return self.password_hash == hashlib.sha256(password.encode()).hexdigest()
    
    def has_permission(self, permission_name):
        """Check if user has specific permission"""
        if not self.role:
            return False
        
        for permission in self.role.permissions:
            if permission.name == permission_name:
                return True
        
        return False
    
    def to_dict(self, include_sensitive=False):
        """Convert user to dictionary, optionally including sensitive data"""
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'role': self.role.name if self.role else None,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'favorite_subjects': [s.name for s in self.favorite_subjects]
        }
        
        if include_sensitive:
            data['permissions'] = [p.name for p in self.role.permissions] if self.role else []
        
        return data


class Question(db.Model):
    """Question model for storing user questions and AI responses"""
    __tablename__ = 'questions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    subject_id = Column(Integer, ForeignKey('subjects.id'))
    content = Column(Text, nullable=False)
    response = Column(Text)
    provider = Column(String(50))  # AI provider used
    model = Column(String(50))     # Specific model used
    is_favorite = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Question {self.id}>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'subject_id': self.subject_id,
            'subject_name': self.subject.name if self.subject else None,
            'content': self.content,
            'response': self.response,
            'provider': self.provider,
            'model': self.model,
            'is_favorite': self.is_favorite,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class UserManager:
    """Manager class for user operations"""
    
    def __init__(self, db_instance, secret_key):
        """Initialize user manager with database instance"""
        self.db = db_instance
        self.secret_key = secret_key
    
    def create_user(self, username, email, password, full_name=None, role_name="student"):
        """Create a new user"""
        try:
            # Validate input
            if not self._validate_username(username):
                return False, "Invalid username format"
            
            if not self._validate_email(email):
                return False, "Invalid email format"
            
            if not self._validate_password(password):
                return False, "Password does not meet requirements"
            
            # Check if username or email already exists
            existing_user = self.db.session.query(User).filter(
                (User.username == username) | (User.email == email)
            ).first()
            
            if existing_user:
                return False, "Username or email already exists"
            
            # Get role
            role = self.db.session.query(Role).filter_by(name=role_name).first()
            if not role:
                return False, f"Role '{role_name}' not found"
            
            # Create user
            user = User(
                username=username,
                email=email,
                full_name=full_name,
                role_id=role.id
            )
            user.set_password(password)
            
            self.db.session.add(user)
            self.db.session.commit()
            
            return True, user.id
            
        except Exception as e:
            self.db.session.rollback()
            logger.error(f"Error creating user: {str(e)}")
            return False, str(e)
    
    def authenticate_user(self, username_or_email, password):
        """Authenticate user and return JWT token"""
        try:
            # Find user by username or email
            user = self.db.session.query(User).filter(
                (User.username == username_or_email) | (User.email == username_or_email)
            ).first()
            
            if not user:
                return False, "User not found"
            
            if not user.is_active:
                return False, "User account is inactive"
            
            if not user.check_password(password):
                return False, "Invalid password"
            
            # Update last login time
            user.last_login = datetime.utcnow()
            self.db.session.commit()
            
            # Generate JWT token
            token = self._generate_token(user)
            
            return True, {
                'token': token,
                'user': user.to_dict()
            }
            
        except Exception as e:
            logger.error(f"Error authenticating user: {str(e)}")
            return False, str(e)
    
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        try:
            user = self.db.session.query(User).filter_by(id=user_id).first()
            if not user:
                return False, "User not found"
            
            return True, user
            
        except Exception as e:
            logger.error(f"Error getting user: {str(e)}")
            return False, str(e)
    
    def update_user(self, user_id, data):
        """Update user information"""
        try:
            user = self.db.session.query(User).filter_by(id=user_id).first()
            if not user:
                return False, "User not found"
            
            # Update fields
            if 'full_name' in data:
                user.full_name = data['full_name']
            
            if 'email' in data:
                if not self._validate_email(data['email']):
                    return False, "Invalid email format"
                
                # Check if email is already used by another user
                existing = self.db.session.query(User).filter(
                    User.email == data['email'], 
                    User.id != user_id
                ).first()
                
                if existing:
                    return False, "Email already in use"
                
                user.email = data['email']
            
            if 'password' in data:
                if not self._validate_password(data['password']):
                    return False, "Password does not meet requirements"
                
                user.set_password(data['password'])
            
            if 'is_active' in data and isinstance(data['is_active'], bool):
                user.is_active = data['is_active']
            
            self.db.session.commit()
            return True, user.id
            
        except Exception as e:
            self.db.session.rollback()
            logger.error(f"Error updating user: {str(e)}")
            return False, str(e)
    
    def delete_user(self, user_id):
        """Delete a user"""
        try:
            user = self.db.session.query(User).filter_by(id=user_id).first()
            if not user:
                return False, "User not found"
            
            self.db.session.delete(user)
            self.db.session.commit()
            return True, "User deleted successfully"
            
        except Exception as e:
            self.db.session.rollback()
            logger.error(f"Error deleting user: {str(e)}")
            return False, str(e)
    
    def change_user_role(self, user_id, role_name):
        """Change user role"""
        try:
            user = self.db.session.query(User).filter_by(id=user_id).first()
            if not user:
                return False, "User not found"
            
            role = self.db.session.query(Role).filter_by(name=role_name).first()
            if not role:
                return False, f"Role '{role_name}' not found"
            
            user.role_id = role.id
            self.db.session.commit()
            return True, "User role updated successfully"
            
        except Exception as e:
            self.db.session.rollback()
            logger.error(f"Error changing user role: {str(e)}")
            return False, str(e)
    
    def verify_token(self, token):
        """Verify JWT token and return user"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            user_id = payload.get("sub")
            
            if not user_id:
                return False, "Invalid token"
            
            # Check token expiration
            exp = payload.get("exp")
            if not exp or datetime.utcnow() > datetime.fromtimestamp(exp):
                return False, "Token expired"
            
            # Get user
            success, user_or_error = self.get_user_by_id(user_id)
            if not success:
                return False, user_or_error
            
            return True, user_or_error
            
        except jwt.InvalidTokenError:
            return False, "Invalid token"
        except Exception as e:
            logger.error(f"Error verifying token: {str(e)}")
            return False, str(e)
    
    def _generate_token(self, user):
        """Generate JWT token for user"""
        payload = {
            "sub": user.id,
            "username": user.username,
            "role": user.role.name if user.role else None,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(days=1)  # Token expires in 1 day
        }
        
        return jwt.encode(payload, self.secret_key, algorithm="HS256")
    
    def _validate_username(self, username):
        """Validate username format"""
        if not username or len(username) < 3 or len(username) > 50:
            return False
        
        # Username should contain only alphanumeric characters and underscores
        return bool(re.match(r'^[a-zA-Z0-9_]+$', username))
    
    def _validate_email(self, email):
        """Validate email format"""
        if not email or len(email) > 100:
            return False
        
        # Simple email validation
        return bool(re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email))
    
    def _validate_password(self, password):
        """Validate password strength"""
        if not password or len(password) < 3:
            return False
        
        # For demo purposes, just require minimum length
        return True


class RoleManager:
    """Manager class for role operations"""
    
    def __init__(self, db_instance):
        """Initialize role manager with database instance"""
        self.db = db_instance
    
    def create_role(self, name, description=None):
        """Create a new role"""
        try:
            # Check if role already exists
            existing = self.db.session.query(Role).filter_by(name=name).first()
            if existing:
                return False, "Role already exists"
            
            # Create role
            role = Role(name=name, description=description)
            self.db.session.add(role)
            self.db.session.commit()
            
            return True, role.id
            
        except Exception as e:
            self.db.session.rollback()
            logger.error(f"Error creating role: {str(e)}")
            return False, str(e)
    
    def get_role_by_name(self, name):
        """Get role by name"""
        try:
            role = self.db.session.query(Role).filter_by(name=name).first()
            if not role:
                return False, "Role not found"
            
            return True, role
            
        except Exception as e:
            logger.error(f"Error getting role: {str(e)}")
            return False, str(e)
    
    def add_permission_to_role(self, role_name, permission_name):
        """Add permission to role"""
        try:
            # Get role
            role = self.db.session.query(Role).filter_by(name=role_name).first()
            if not role:
                return False, f"Role '{role_name}' not found"
            
            # Get permission
            permission = self.db.session.query(Permission).filter_by(name=permission_name).first()
            if not permission:
                return False, f"Permission '{permission_name}' not found"
            
            # Check if permission already assigned
            if permission in role.permissions:
                return True, "Permission already assigned to role"
            
            # Add permission to role
            role.permissions.append(permission)
            self.db.session.commit()
            
            return True, "Permission added to role"
            
        except Exception as e:
            self.db.session.rollback()
            logger.error(f"Error adding permission to role: {str(e)}")
            return False, str(e)
    
    def remove_permission_from_role(self, role_name, permission_name):
        """Remove permission from role"""
        try:
            # Get role
            role = self.db.session.query(Role).filter_by(name=role_name).first()
            if not role:
                return False, f"Role '{role_name}' not found"
            
            # Get permission
            permission = self.db.session.query(Permission).filter_by(name=permission_name).first()
            if not permission:
                return False, f"Permission '{permission_name}' not found"
            
            # Check if permission is assigned
            if permission not in role.permissions:
                return True, "Permission not assigned to role"
            
            # Remove permission from role
            role.permissions.remove(permission)
            self.db.session.commit()
            
            return True, "Permission removed from role"
            
        except Exception as e:
            self.db.session.rollback()
            logger.error(f"Error removing permission from role: {str(e)}")
            return False, str(e)


class PermissionManager:
    """Manager class for permission operations"""
    
    def __init__(self, db_instance):
        """Initialize permission manager with database instance"""
        self.db = db_instance
    
    def create_permission(self, name, description=None):
        """Create a new permission"""
        try:
            # Check if permission already exists
            existing = self.db.session.query(Permission).filter_by(name=name).first()
            if existing:
                return False, "Permission already exists"
            
            # Create permission
            permission = Permission(name=name, description=description)
            self.db.session.add(permission)
            self.db.session.commit()
            
            return True, permission.id
            
        except Exception as e:
            self.db.session.rollback()
            logger.error(f"Error creating permission: {str(e)}")
            return False, str(e)
    
    def get_permission_by_name(self, name):
        """Get permission by name"""
        try:
            permission = self.db.session.query(Permission).filter_by(name=name).first()
            if not permission:
                return False, "Permission not found"
            
            return True, permission
            
        except Exception as e:
            logger.error(f"Error getting permission: {str(e)}")
            return False, str(e)


class SubjectManager:
    """Manager class for subject operations"""
    
    def __init__(self, db_instance):
        """Initialize subject manager with database instance"""
        self.db = db_instance
    
    def create_subject(self, name, category, description=None, icon=None):
        """Create a new subject"""
        try:
            # Check if subject already exists
            existing = self.db.session.query(Subject).filter_by(name=name).first()
            if existing:
                return False, "Subject already exists"
            
            # Create subject
            subject = Subject(
                name=name,
                category=category,
                description=description,
                icon=icon
            )
            self.db.session.add(subject)
            self.db.session.commit()
            
            return True, subject.id
            
        except Exception as e:
            self.db.session.rollback()
            logger.error(f"Error creating subject: {str(e)}")
            return False, str(e)
    
    def get_subject_by_name(self, name):
        """Get subject by name"""
        try:
            subject = self.db.session.query(Subject).filter_by(name=name).first()
            if not subject:
                return False, "Subject not found"
            
            return True, subject
            
        except Exception as e:
            logger.error(f"Error getting subject: {str(e)}")
            return False, str(e)
    
    def get_subjects_by_category(self, category):
        """Get subjects by category"""
        try:
            subjects = self.db.session.query(Subject).filter_by(category=category).all()
            return True, subjects
            
        except Exception as e:
            logger.error(f"Error getting subjects by category: {str(e)}")
            return False, str(e)
    
    def get_all_subjects(self):
        """Get all subjects"""
        try:
            subjects = self.db.session.query(Subject).all()
            return True, subjects
            
        except Exception as e:
            logger.error(f"Error getting all subjects: {str(e)}")
            return False, str(e)


class QuestionManager:
    """Manager class for question operations"""
    
    def __init__(self, db_instance):
        """Initialize question manager with database instance"""
        self.db = db_instance
    
    def create_question(self, user_id, content, subject_id=None):
        """Create a new question"""
        try:
            # Check if user exists
            user = self.db.session.query(User).filter_by(id=user_id).first()
            if not user:
                return False, "User not found"
            
            # Check if subject exists (if provided)
            if subject_id:
                subject = self.db.session.query(Subject).filter_by(id=subject_id).first()
                if not subject:
                    return False, "Subject not found"
            
            # Create question
            question = Question(
                user_id=user_id,
                subject_id=subject_id,
                content=content
            )
            self.db.session.add(question)
            self.db.session.commit()
            
            return True, question.id
            
        except Exception as e:
            self.db.session.rollback()
            logger.error(f"Error creating question: {str(e)}")
            return False, str(e)
    
    def save_response(self, question_id, response, provider, model):
        """Save AI response to question"""
        try:
            # Get question
            question = self.db.session.query(Question).filter_by(id=question_id).first()
            if not question:
                return False, "Question not found"
            
            # Update question with response
            question.response = response
            question.provider = provider
            question.model = model
            
            self.db.session.commit()
            
            return True, question.id
            
        except Exception as e:
            self.db.session.rollback()
            logger.error(f"Error saving response: {str(e)}")
            return False, str(e)
    
    def toggle_favorite(self, question_id, user_id):
        """Toggle favorite status of a question"""
        try:
            # Get question
            question = self.db.session.query(Question).filter_by(id=question_id).first()
            if not question:
                return False, "Question not found"
            
            # Check if user owns the question
            if question.user_id != user_id:
                return False, "Not authorized to modify this question"
            
            # Toggle favorite status
            question.is_favorite = not question.is_favorite
            self.db.session.commit()
            
            return True, question.is_favorite
            
        except Exception as e:
            self.db.session.rollback()
            logger.error(f"Error toggling favorite: {str(e)}")
            return False, str(e)
    
    def get_user_questions(self, user_id, include_favorites_only=False, subject_id=None):
        """Get questions for a specific user"""
        try:
            # Build query
            query = self.db.session.query(Question).filter_by(user_id=user_id)
            
            # Filter by favorite status if requested
            if include_favorites_only:
                query = query.filter_by(is_favorite=True)
            
            # Filter by subject if provided
            if subject_id:
                query = query.filter_by(subject_id=subject_id)
            
            # Order by creation date (newest first)
            query = query.order_by(Question.created_at.desc())
            
            questions = query.all()
            return True, questions
            
        except Exception as e:
            logger.error(f"Error getting user questions: {str(e)}")
            return False, str(e)


# Initialize managers
def initialize_user_system(app, db_instance):
    """Initialize user management system"""
    # Generate secret key if not provided
    if not app.config.get('SECRET_KEY'):
        app.config['SECRET_KEY'] = secrets.token_hex(32)
    
    # Create managers
    user_manager = UserManager(db_instance, app.config['SECRET_KEY'])
    role_manager = RoleManager(db_instance)
    permission_manager = PermissionManager(db_instance)
    subject_manager = SubjectManager(db_instance)
    question_manager = QuestionManager(db_instance)
    
    # Create default roles and permissions if they don't exist
    _create_default_roles_and_permissions(role_manager, permission_manager)
    
    # Create default subjects if they don't exist
    _create_default_subjects(subject_manager)
    
    return {
        'user_manager': user_manager,
        'role_manager': role_manager,
        'permission_manager': permission_manager,
        'subject_manager': subject_manager,
        'question_manager': question_manager
    }


def _create_default_roles_and_permissions(role_manager, permission_manager):
    """Create default roles and permissions"""
    # Create default permissions
    permissions = {
        'ask_questions': 'Can ask questions to AI models',
        'view_history': 'Can view own question history',
        'create_users': 'Can create new user accounts',
        'manage_users': 'Can manage user accounts',
        'manage_roles': 'Can manage roles and permissions',
        'view_analytics': 'Can view system analytics',
        'manage_subjects': 'Can manage subjects and categories',
        'view_all_questions': 'Can view all users\' questions',
        'create_simulations': 'Can create and run simulations',
        'manage_simulations': 'Can manage all simulations'
    }
    
    for name, description in permissions.items():
        permission_manager.create_permission(name, description)
    
    # Create default roles
    roles = {
        'student': 'Regular student user',
        'teacher': 'Teacher with additional privileges',
        'admin': 'Administrator with full access'
    }
    
    for name, description in roles.items():
        role_manager.create_role(name, description)
    
    # Assign permissions to roles
    role_permissions = {
        'student': ['ask_questions', 'view_history'],
        'teacher': ['ask_questions', 'view_history', 'create_users', 'view_analytics', 
                   'view_all_questions', 'create_simulations', 'manage_simulations'],
        'admin': ['ask_questions', 'view_history', 'create_users', 'manage_users', 
                 'manage_roles', 'view_analytics', 'manage_subjects', 
                 'view_all_questions', 'create_simulations', 'manage_simulations']
    }
    
    for role_name, permission_list in role_permissions.items():
        for permission_name in permission_list:
            role_manager.add_permission_to_role(role_name, permission_name)


def _create_default_subjects(subject_manager):
    """Create default subjects"""
    subjects = [
        {
            'name': '电工电子实验',
            'category': 'engineering',
            'description': '电工电子实验课程，包括电路分析、模拟电路、数字电路等实验内容',
            'icon': 'fa-bolt'
        },
        {
            'name': '电路分析',
            'category': 'engineering',
            'description': '电路理论与分析方法，包括直流电路、交流电路、三相电路等',
            'icon': 'fa-project-diagram'
        },
        {
            'name': '模拟电子技术',
            'category': 'engineering',
            'description': '模拟电子电路的分析与设计，包括放大器、滤波器、振荡器等',
            'icon': 'fa-wave-square'
        },
        {
            'name': '数字电子技术',
            'category': 'engineering',
            'description': '数字电路与系统的分析与设计，包括逻辑门、触发器、计数器等',
            'icon': 'fa-microchip'
        },
        {
            'name': '电力电子技术',
            'category': 'engineering',
            'description': '电力电子器件与电路的分析与应用，包括整流器、逆变器、变频器等',
            'icon': 'fa-plug'
        },
        {
            'name': '自动控制原理',
            'category': 'engineering',
            'description': '自动控制系统的分析与设计，包括时域分析、频域分析、状态空间分析等',
            'icon': 'fa-sliders-h'
        },
        {
            'name': '信号与系统',
            'category': 'engineering',
            'description': '信号与系统的分析与处理，包括时域分析、频域分析、Z变换等',
            'icon': 'fa-signal'
        },
        {
            'name': '微机原理与接口技术',
            'category': 'engineering',
            'description': '微处理器原理与接口设计，包括汇编语言、中断系统、I/O接口等',
            'icon': 'fa-microchip'
        }
    ]
    
    for subject_data in subjects:
        subject_manager.create_subject(
            name=subject_data['name'],
            category=subject_data['category'],
            description=subject_data['description'],
            icon=subject_data['icon']
        )
