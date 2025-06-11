"""
History and Record Management Module for Alethea Platform
Supports question history, favorites, and sharing
"""

import os
import json
import logging
import re
from datetime import datetime
from typing import Dict, Any, List, Optional, Union, Tuple
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Table
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from src.models.user import Base, User, Question, Subject

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define association tables for many-to-many relationships
question_tag = Table(
    'question_tag', 
    Base.metadata,
    Column('question_id', Integer, ForeignKey('questions.id')),
    Column('tag_id', Integer, ForeignKey('tags.id'))
)

class QuestionHistory(Base):
    """Model for tracking user question history"""
    __tablename__ = 'question_history'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    question_id = Column(Integer, ForeignKey('questions.id'))
    viewed_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    question = relationship('Question')
    
    def __repr__(self):
        return f"<QuestionHistory {self.id}>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'question_id': self.question_id,
            'viewed_at': self.viewed_at.isoformat() if self.viewed_at else None,
            'question': self.question.to_dict() if self.question else None
        }


class QuestionCollection(Base):
    """Model for user-created collections of questions"""
    __tablename__ = 'question_collections'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    name = Column(String(100), nullable=False)
    description = Column(Text)
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    questions = relationship('CollectionQuestion', backref='collection')
    
    def __repr__(self):
        return f"<QuestionCollection {self.name}>"
    
    def to_dict(self, include_questions=False):
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'description': self.description,
            'is_public': self.is_public,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'question_count': len(self.questions)
        }
        
        if include_questions:
            data['questions'] = [cq.to_dict() for cq in self.questions]
        
        return data


class CollectionQuestion(Base):
    """Association model between collections and questions"""
    __tablename__ = 'collection_questions'
    
    id = Column(Integer, primary_key=True)
    collection_id = Column(Integer, ForeignKey('question_collections.id'))
    question_id = Column(Integer, ForeignKey('questions.id'))
    added_at = Column(DateTime, default=datetime.utcnow)
    note = Column(Text)  # Optional note about why this question is in the collection
    
    # Relationships
    question = relationship('Question')
    
    def __repr__(self):
        return f"<CollectionQuestion {self.id}>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'collection_id': self.collection_id,
            'question_id': self.question_id,
            'added_at': self.added_at.isoformat() if self.added_at else None,
            'note': self.note,
            'question': self.question.to_dict() if self.question else None
        }


class QuestionShare(Base):
    """Model for shared questions"""
    __tablename__ = 'question_shares'
    
    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, ForeignKey('questions.id'))
    user_id = Column(Integer, ForeignKey('users.id'))  # User who shared
    share_token = Column(String(64), unique=True, nullable=False)  # Unique token for sharing
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime)  # Optional expiration date
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    question = relationship('Question')
    user = relationship('User')
    
    def __repr__(self):
        return f"<QuestionShare {self.share_token}>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'question_id': self.question_id,
            'user_id': self.user_id,
            'share_token': self.share_token,
            'is_active': self.is_active,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'question': self.question.to_dict() if self.question else None
        }


class QuestionComment(Base):
    """Model for comments on questions"""
    __tablename__ = 'question_comments'
    
    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, ForeignKey('questions.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    question = relationship('Question')
    user = relationship('User')
    
    def __repr__(self):
        return f"<QuestionComment {self.id}>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'question_id': self.question_id,
            'user_id': self.user_id,
            'user_name': self.user.username if self.user else None,
            'content': self.content,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class QuestionRating(Base):
    """Model for rating questions and responses"""
    __tablename__ = 'question_ratings'
    
    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, ForeignKey('questions.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    rating = Column(Integer)  # 1-5 stars
    feedback = Column(Text)  # Optional feedback
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    question = relationship('Question')
    user = relationship('User')
    
    def __repr__(self):
        return f"<QuestionRating {self.id}>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'question_id': self.question_id,
            'user_id': self.user_id,
            'rating': self.rating,
            'feedback': self.feedback,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class HistoryManager:
    """Manager class for question history operations"""
    
    def __init__(self, db_instance):
        """Initialize history manager with database instance"""
        self.db = db_instance
    
    def record_question_view(self, user_id, question_id):
        """Record that a user viewed a question"""
        try:
            # Check if user exists
            user = self.db.session.query(User).filter_by(id=user_id).first()
            if not user:
                return False, "User not found"
            
            # Check if question exists
            question = self.db.session.query(Question).filter_by(id=question_id).first()
            if not question:
                return False, "Question not found"
            
            # Create history record
            history = QuestionHistory(
                user_id=user_id,
                question_id=question_id
            )
            
            self.db.session.add(history)
            self.db.session.commit()
            
            return True, history.id
            
        except Exception as e:
            self.db.session.rollback()
            logger.error(f"Error recording question view: {str(e)}")
            return False, str(e)
    
    def get_user_history(self, user_id, limit=50, offset=0):
        """Get question history for a user"""
        try:
            # Check if user exists
            user = self.db.session.query(User).filter_by(id=user_id).first()
            if not user:
                return False, "User not found"
            
            # Get history records
            history_records = self.db.session.query(QuestionHistory)\
                .filter_by(user_id=user_id)\
                .order_by(QuestionHistory.viewed_at.desc())\
                .limit(limit).offset(offset).all()
            
            return True, [record.to_dict() for record in history_records]
            
        except Exception as e:
            logger.error(f"Error getting user history: {str(e)}")
            return False, str(e)
    
    def clear_user_history(self, user_id):
        """Clear all history for a user"""
        try:
            # Check if user exists
            user = self.db.session.query(User).filter_by(id=user_id).first()
            if not user:
                return False, "User not found"
            
            # Delete history records
            self.db.session.query(QuestionHistory).filter_by(user_id=user_id).delete()
            self.db.session.commit()
            
            return True, "History cleared successfully"
            
        except Exception as e:
            self.db.session.rollback()
            logger.error(f"Error clearing user history: {str(e)}")
            return False, str(e)


class CollectionManager:
    """Manager class for question collection operations"""
    
    def __init__(self, db_instance):
        """Initialize collection manager with database instance"""
        self.db = db_instance
    
    def create_collection(self, user_id, name, description=None, is_public=False):
        """Create a new question collection"""
        try:
            # Check if user exists
            user = self.db.session.query(User).filter_by(id=user_id).first()
            if not user:
                return False, "User not found"
            
            # Create collection
            collection = QuestionCollection(
                user_id=user_id,
                name=name,
                description=description,
                is_public=is_public
            )
            
            self.db.session.add(collection)
            self.db.session.commit()
            
            return True, collection.id
            
        except Exception as e:
            self.db.session.rollback()
            logger.error(f"Error creating collection: {str(e)}")
            return False, str(e)
    
    def get_collection(self, collection_id, include_questions=False):
        """Get collection by ID"""
        try:
            collection = self.db.session.query(QuestionCollection).filter_by(id=collection_id).first()
            if not collection:
                return False, "Collection not found"
            
            return True, collection.to_dict(include_questions=include_questions)
            
        except Exception as e:
            logger.error(f"Error getting collection: {str(e)}")
            return False, str(e)
    
    def get_user_collections(self, user_id):
        """Get all collections for a user"""
        try:
            # Check if user exists
            user = self.db.session.query(User).filter_by(id=user_id).first()
            if not user:
                return False, "User not found"
            
            # Get collections
            collections = self.db.session.query(QuestionCollection).filter_by(user_id=user_id).all()
            
            return True, [collection.to_dict() for collection in collections]
            
        except Exception as e:
            logger.error(f"Error getting user collections: {str(e)}")
            return False, str(e)
    
    def add_question_to_collection(self, collection_id, question_id, note=None):
        """Add a question to a collection"""
        try:
            # Check if collection exists
            collection = self.db.session.query(QuestionCollection).filter_by(id=collection_id).first()
            if not collection:
                return False, "Collection not found"
            
            # Check if question exists
            question = self.db.session.query(Question).filter_by(id=question_id).first()
            if not question:
                return False, "Question not found"
            
            # Check if question is already in collection
            existing = self.db.session.query(CollectionQuestion).filter_by(
                collection_id=collection_id,
                question_id=question_id
            ).first()
            
            if existing:
                return False, "Question already in collection"
            
            # Add question to collection
            collection_question = CollectionQuestion(
                collection_id=collection_id,
                question_id=question_id,
                note=note
            )
            
            self.db.session.add(collection_question)
            self.db.session.commit()
            
            return True, collection_question.id
            
        except Exception as e:
            self.db.session.rollback()
            logger.error(f"Error adding question to collection: {str(e)}")
            return False, str(e)
    
    def remove_question_from_collection(self, collection_id, question_id):
        """Remove a question from a collection"""
        try:
            # Check if collection exists
            collection = self.db.session.query(QuestionCollection).filter_by(id=collection_id).first()
            if not collection:
                return False, "Collection not found"
            
            # Delete collection question
            result = self.db.session.query(CollectionQuestion).filter_by(
                collection_id=collection_id,
                question_id=question_id
            ).delete()
            
            if result == 0:
                return False, "Question not found in collection"
            
            self.db.session.commit()
            
            return True, "Question removed from collection"
            
        except Exception as e:
            self.db.session.rollback()
            logger.error(f"Error removing question from collection: {str(e)}")
            return False, str(e)
    
    def delete_collection(self, collection_id, user_id):
        """Delete a collection (only by owner)"""
        try:
            # Check if collection exists and belongs to user
            collection = self.db.session.query(QuestionCollection).filter_by(
                id=collection_id,
                user_id=user_id
            ).first()
            
            if not collection:
                return False, "Collection not found or not owned by user"
            
            # Delete all collection questions first
            self.db.session.query(CollectionQuestion).filter_by(collection_id=collection_id).delete()
            
            # Delete collection
            self.db.session.delete(collection)
            self.db.session.commit()
            
            return True, "Collection deleted successfully"
            
        except Exception as e:
            self.db.session.rollback()
            logger.error(f"Error deleting collection: {str(e)}")
            return False, str(e)


class ShareManager:
    """Manager class for question sharing operations"""
    
    def __init__(self, db_instance):
        """Initialize share manager with database instance"""
        self.db = db_instance
    
    def create_share(self, question_id, user_id, expires_in_days=None):
        """Create a new share for a question"""
        try:
            # Check if question exists
            question = self.db.session.query(Question).filter_by(id=question_id).first()
            if not question:
                return False, "Question not found"
            
            # Check if user exists
            user = self.db.session.query(User).filter_by(id=user_id).first()
            if not user:
                return False, "User not found"
            
            # Check if user owns the question or has permission to share
            if question.user_id != user_id and not user.has_permission('view_all_questions'):
                return False, "Not authorized to share this question"
            
            # Generate unique token
            import secrets
            share_token = secrets.token_hex(16)
            
            # Calculate expiration date if provided
            expires_at = None
            if expires_in_days:
                from datetime import datetime, timedelta
                expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
            
            # Create share
            share = QuestionShare(
                question_id=question_id,
                user_id=user_id,
                share_token=share_token,
                expires_at=expires_at
            )
            
            self.db.session.add(share)
            self.db.session.commit()
            
            return True, {
                'share_id': share.id,
                'share_token': share_token,
                'expires_at': expires_at.isoformat() if expires_at else None
            }
            
        except Exception as e:
            self.db.session.rollback()
            logger.error(f"Error creating share: {str(e)}")
            return False, str(e)
    
    def get_shared_question(self, share_token):
        """Get a shared question by token"""
        try:
            # Get share
            share = self.db.session.query(QuestionShare).filter_by(share_token=share_token).first()
            if not share:
                return False, "Share not found"
            
            # Check if share is active
            if not share.is_active:
                return False, "Share is inactive"
            
            # Check if share has expired
            if share.expires_at and datetime.utcnow() > share.expires_at:
                return False, "Share has expired"
            
            # Get question
            question = self.db.session.query(Question).filter_by(id=share.question_id).first()
            if not question:
                return False, "Question not found"
            
            return True, question.to_dict()
            
        except Exception as e:
            logger.error(f"Error getting shared question: {str(e)}")
            return False, str(e)
    
    def deactivate_share(self, share_id, user_id):
        """Deactivate a share (only by owner)"""
        try:
            # Check if share exists and belongs to user
            share = self.db.session.query(QuestionShare).filter_by(
                id=share_id,
                user_id=user_id
            ).first()
            
            if not share:
                return False, "Share not found or not owned by user"
            
            # Deactivate share
            share.is_active = False
            self.db.session.commit()
            
            return True, "Share deactivated successfully"
            
        except Exception as e:
            self.db.session.rollback()
            logger.error(f"Error deactivating share: {str(e)}")
            return False, str(e)


class CommentManager:
    """Manager class for question comment operations"""
    
    def __init__(self, db_instance):
        """Initialize comment manager with database instance"""
        self.db = db_instance
    
    def add_comment(self, question_id, user_id, content):
        """Add a comment to a question"""
        try:
            # Check if question exists
            question = self.db.session.query(Question).filter_by(id=question_id).first()
            if not question:
                return False, "Question not found"
            
            # Check if user exists
            user = self.db.session.query(User).filter_by(id=user_id).first()
            if not user:
                return False, "User not found"
            
            # Create comment
            comment = QuestionComment(
                question_id=question_id,
                user_id=user_id,
                content=content
            )
            
            self.db.session.add(comment)
            self.db.session.commit()
            
            return True, comment.id
            
        except Exception as e:
            self.db.session.rollback()
            logger.error(f"Error adding comment: {str(e)}")
            return False, str(e)
    
    def get_question_comments(self, question_id):
        """Get all comments for a question"""
        try:
            # Check if question exists
            question = self.db.session.query(Question).filter_by(id=question_id).first()
            if not question:
                return False, "Question not found"
            
            # Get comments
            comments = self.db.session.query(QuestionComment)\
                .filter_by(question_id=question_id)\
                .order_by(QuestionComment.created_at.asc())\
                .all()
            
            return True, [comment.to_dict() for comment in comments]
            
        except Exception as e:
            logger.error(f"Error getting question comments: {str(e)}")
            return False, str(e)
    
    def update_comment(self, comment_id, user_id, content):
        """Update a comment (only by owner)"""
        try:
            # Check if comment exists and belongs to user
            comment = self.db.session.query(QuestionComment).filter_by(
                id=comment_id,
                user_id=user_id
            ).first()
            
            if not comment:
                return False, "Comment not found or not owned by user"
            
            # Update comment
            comment.content = content
            self.db.session.commit()
            
            return True, comment.id
            
        except Exception as e:
            self.db.session.rollback()
            logger.error(f"Error updating comment: {str(e)}")
            return False, str(e)
    
    def delete_comment(self, comment_id, user_id):
        """Delete a comment (only by owner or admin)"""
        try:
            # Get comment
            comment = self.db.session.query(QuestionComment).filter_by(id=comment_id).first()
            if not comment:
                return False, "Comment not found"
            
            # Check if user is owner or has admin permission
            user = self.db.session.query(User).filter_by(id=user_id).first()
            if not user:
                return False, "User not found"
            
            if comment.user_id != user_id and not user.has_permission('manage_users'):
                return False, "Not authorized to delete this comment"
            
            # Delete comment
            self.db.session.delete(comment)
            self.db.session.commit()
            
            return True, "Comment deleted successfully"
            
        except Exception as e:
            self.db.session.rollback()
            logger.error(f"Error deleting comment: {str(e)}")
            return False, str(e)


class RatingManager:
    """Manager class for question rating operations"""
    
    def __init__(self, db_instance):
        """Initialize rating manager with database instance"""
        self.db = db_instance
    
    def rate_question(self, question_id, user_id, rating, feedback=None):
        """Rate a question"""
        try:
            # Check if question exists
            question = self.db.session.query(Question).filter_by(id=question_id).first()
            if not question:
                return False, "Question not found"
            
            # Check if user exists
            user = self.db.session.query(User).filter_by(id=user_id).first()
            if not user:
                return False, "User not found"
            
            # Check if rating is valid
            if rating < 1 or rating > 5:
                return False, "Rating must be between 1 and 5"
            
            # Check if user has already rated this question
            existing_rating = self.db.session.query(QuestionRating).filter_by(
                question_id=question_id,
                user_id=user_id
            ).first()
            
            if existing_rating:
                # Update existing rating
                existing_rating.rating = rating
                existing_rating.feedback = feedback
                self.db.session.commit()
                return True, existing_rating.id
            
            # Create new rating
            new_rating = QuestionRating(
                question_id=question_id,
                user_id=user_id,
                rating=rating,
                feedback=feedback
            )
            
            self.db.session.add(new_rating)
            self.db.session.commit()
            
            return True, new_rating.id
            
        except Exception as e:
            self.db.session.rollback()
            logger.error(f"Error rating question: {str(e)}")
            return False, str(e)
    
    def get_question_ratings(self, question_id):
        """Get all ratings for a question"""
        try:
            # Check if question exists
            question = self.db.session.query(Question).filter_by(id=question_id).first()
            if not question:
                return False, "Question not found"
            
            # Get ratings
            ratings = self.db.session.query(QuestionRating).filter_by(question_id=question_id).all()
            
            # Calculate average rating
            total_ratings = len(ratings)
            if total_ratings > 0:
                avg_rating = sum(r.rating for r in ratings) / total_ratings
            else:
                avg_rating = 0
            
            return True, {
                'ratings': [rating.to_dict() for rating in ratings],
                'average_rating': avg_rating,
                'total_ratings': total_ratings
            }
            
        except Exception as e:
            logger.error(f"Error getting question ratings: {str(e)}")
            return False, str(e)


# Initialize managers
def initialize_history_system(app, db_instance):
    """Initialize history and record management system"""
    # Create managers
    history_manager = HistoryManager(db_instance)
    collection_manager = CollectionManager(db_instance)
    share_manager = ShareManager(db_instance)
    comment_manager = CommentManager(db_instance)
    rating_manager = RatingManager(db_instance)
    
    return {
        'history_manager': history_manager,
        'collection_manager': collection_manager,
        'share_manager': share_manager,
        'comment_manager': comment_manager,
        'rating_manager': rating_manager
    }
