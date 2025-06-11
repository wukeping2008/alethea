"""
Enhanced error handling system for Alethea Platform
Provides centralized error handling and user-friendly error responses
"""

import traceback
from functools import wraps
from typing import Dict, Any, Optional, Tuple
from flask import jsonify, request
from werkzeug.exceptions import HTTPException
from utils.logger import get_logger

logger = get_logger("error_handler")


class AlethearError(Exception):
    """Base exception class for Alethea Platform"""
    
    def __init__(self, message: str, error_code: str = "GENERAL_ERROR", status_code: int = 500, details: Optional[Dict] = None):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for JSON response"""
        return {
            'error': True,
            'error_code': self.error_code,
            'message': self.message,
            'details': self.details,
            'status_code': self.status_code
        }


class ValidationError(AlethearError):
    """Validation error"""
    
    def __init__(self, message: str, field: Optional[str] = None, details: Optional[Dict] = None):
        error_details = details or {}
        if field:
            error_details['field'] = field
        
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            status_code=400,
            details=error_details
        )


class AuthenticationError(AlethearError):
    """Authentication error"""
    
    def __init__(self, message: str = "Authentication required", details: Optional[Dict] = None):
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_ERROR",
            status_code=401,
            details=details
        )


class AuthorizationError(AlethearError):
    """Authorization error"""
    
    def __init__(self, message: str = "Insufficient permissions", details: Optional[Dict] = None):
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_ERROR",
            status_code=403,
            details=details
        )


class NotFoundError(AlethearError):
    """Resource not found error"""
    
    def __init__(self, message: str = "Resource not found", resource_type: Optional[str] = None, details: Optional[Dict] = None):
        error_details = details or {}
        if resource_type:
            error_details['resource_type'] = resource_type
        
        super().__init__(
            message=message,
            error_code="NOT_FOUND_ERROR",
            status_code=404,
            details=error_details
        )


class DatabaseError(AlethearError):
    """Database operation error"""
    
    def __init__(self, message: str = "Database operation failed", operation: Optional[str] = None, details: Optional[Dict] = None):
        error_details = details or {}
        if operation:
            error_details['operation'] = operation
        
        super().__init__(
            message=message,
            error_code="DATABASE_ERROR",
            status_code=500,
            details=error_details
        )


class AIProviderError(AlethearError):
    """AI provider error"""
    
    def __init__(self, message: str = "AI provider error", provider: Optional[str] = None, details: Optional[Dict] = None):
        error_details = details or {}
        if provider:
            error_details['provider'] = provider
        
        super().__init__(
            message=message,
            error_code="AI_PROVIDER_ERROR",
            status_code=502,
            details=error_details
        )


class RateLimitError(AlethearError):
    """Rate limit exceeded error"""
    
    def __init__(self, message: str = "Rate limit exceeded", limit: Optional[int] = None, details: Optional[Dict] = None):
        error_details = details or {}
        if limit:
            error_details['limit'] = limit
        
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_ERROR",
            status_code=429,
            details=error_details
        )


def handle_error(error: Exception) -> Tuple[Dict[str, Any], int]:
    """Handle different types of errors and return appropriate response"""
    
    # Log the error
    logger.error(
        f"Error occurred: {str(error)}",
        exception=error,
        path=request.path if request else None,
        method=request.method if request else None,
        user_agent=request.headers.get('User-Agent') if request else None
    )
    
    # Handle Alethea custom errors
    if isinstance(error, AlethearError):
        return error.to_dict(), error.status_code
    
    # Handle HTTP exceptions
    if isinstance(error, HTTPException):
        return {
            'error': True,
            'error_code': 'HTTP_ERROR',
            'message': error.description or 'HTTP error occurred',
            'status_code': error.code
        }, error.code
    
    # Handle generic exceptions
    error_response = {
        'error': True,
        'error_code': 'INTERNAL_ERROR',
        'message': 'An internal error occurred',
        'status_code': 500
    }
    
    # In development, include traceback
    import os
    if os.getenv('FLASK_ENV') == 'development':
        error_response['traceback'] = traceback.format_exc()
        error_response['details'] = {'original_error': str(error)}
    
    return error_response, 500


def error_handler_decorator(f):
    """Decorator to handle errors in route functions"""
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            error_response, status_code = handle_error(e)
            return jsonify(error_response), status_code
    
    return decorated_function


def safe_execute(func, *args, **kwargs):
    """Safely execute a function and return result or error"""
    try:
        result = func(*args, **kwargs)
        return True, result
    except Exception as e:
        logger.error(f"Error in safe_execute: {str(e)}", exception=e)
        return False, str(e)


def validate_required_fields(data: Dict[str, Any], required_fields: list) -> None:
    """Validate that required fields are present in data"""
    missing_fields = []
    
    for field in required_fields:
        if field not in data or data[field] is None or data[field] == '':
            missing_fields.append(field)
    
    if missing_fields:
        raise ValidationError(
            f"Missing required fields: {', '.join(missing_fields)}",
            details={'missing_fields': missing_fields}
        )


def validate_field_types(data: Dict[str, Any], field_types: Dict[str, type]) -> None:
    """Validate field types in data"""
    invalid_fields = []
    
    for field, expected_type in field_types.items():
        if field in data and data[field] is not None:
            if not isinstance(data[field], expected_type):
                invalid_fields.append({
                    'field': field,
                    'expected_type': expected_type.__name__,
                    'actual_type': type(data[field]).__name__
                })
    
    if invalid_fields:
        raise ValidationError(
            "Invalid field types",
            details={'invalid_fields': invalid_fields}
        )


def register_error_handlers(app):
    """Register error handlers with Flask app"""
    
    @app.errorhandler(AlethearError)
    def handle_alethea_error(error):
        response, status_code = handle_error(error)
        return jsonify(response), status_code
    
    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        response, status_code = handle_error(error)
        return jsonify(response), status_code
    
    @app.errorhandler(Exception)
    def handle_generic_error(error):
        response, status_code = handle_error(error)
        return jsonify(response), status_code
    
    logger.info("Error handlers registered successfully")


# Context manager for safe operations
class SafeOperation:
    """Context manager for safe operations with automatic error handling"""
    
    def __init__(self, operation_name: str, reraise: bool = False):
        self.operation_name = operation_name
        self.reraise = reraise
        self.success = False
        self.error = None
        self.result = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.error = exc_val
            logger.error(f"Error in {self.operation_name}: {str(exc_val)}", exception=exc_val)
            
            if self.reraise:
                return False  # Re-raise the exception
            return True  # Suppress the exception
        else:
            self.success = True
            return True
    
    def set_result(self, result):
        """Set the result of the operation"""
        self.result = result
