"""
Enhanced logging system for Alethea Platform
Provides structured logging with different levels and formatters
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime
from typing import Optional


class ColoredFormatter(logging.Formatter):
    """Colored formatter for console output"""
    
    # Color codes
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'      # Reset
    }
    
    def format(self, record):
        # Add color to levelname
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}"
        
        # Format the message
        formatted = super().format(record)
        
        # Reset levelname for other formatters
        record.levelname = levelname
        
        return formatted


class AlethearLogger:
    """Enhanced logger for Alethea Platform"""
    
    def __init__(self, name: str = "alethea", log_level: str = "INFO"):
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # Prevent duplicate handlers
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup console and file handlers"""
        
        # Console handler with colors
        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = ColoredFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(logging.INFO)
        
        # File handler
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        file_handler = logging.handlers.RotatingFileHandler(
            os.path.join(log_dir, f"{self.name}.log"),
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(logging.DEBUG)
        
        # Error file handler
        error_handler = logging.handlers.RotatingFileHandler(
            os.path.join(log_dir, f"{self.name}_error.log"),
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        error_handler.setFormatter(file_formatter)
        error_handler.setLevel(logging.ERROR)
        
        # Add handlers
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(error_handler)
    
    def debug(self, message: str, **kwargs):
        """Log debug message"""
        self.logger.debug(message, extra=kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message"""
        self.logger.info(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self.logger.warning(message, extra=kwargs)
    
    def error(self, message: str, exception: Optional[Exception] = None, **kwargs):
        """Log error message"""
        if exception:
            self.logger.error(f"{message}: {str(exception)}", exc_info=True, extra=kwargs)
        else:
            self.logger.error(message, extra=kwargs)
    
    def critical(self, message: str, exception: Optional[Exception] = None, **kwargs):
        """Log critical message"""
        if exception:
            self.logger.critical(f"{message}: {str(exception)}", exc_info=True, extra=kwargs)
        else:
            self.logger.critical(message, extra=kwargs)
    
    def log_request(self, method: str, path: str, status_code: int, duration: float, user_id: Optional[int] = None):
        """Log HTTP request"""
        self.info(
            f"{method} {path} - {status_code} - {duration:.3f}s",
            method=method,
            path=path,
            status_code=status_code,
            duration=duration,
            user_id=user_id
        )
    
    def log_user_action(self, user_id: int, action: str, details: Optional[dict] = None):
        """Log user action"""
        message = f"User {user_id} performed action: {action}"
        if details:
            message += f" - Details: {details}"
        
        self.info(
            message,
            user_id=user_id,
            action=action,
            details=details
        )
    
    def log_ai_request(self, provider: str, model: str, prompt_length: int, response_length: int, duration: float):
        """Log AI model request"""
        self.info(
            f"AI Request - Provider: {provider}, Model: {model}, "
            f"Prompt: {prompt_length} chars, Response: {response_length} chars, "
            f"Duration: {duration:.3f}s",
            provider=provider,
            model=model,
            prompt_length=prompt_length,
            response_length=response_length,
            duration=duration
        )
    
    def log_database_operation(self, operation: str, table: str, duration: float, success: bool = True):
        """Log database operation"""
        status = "SUCCESS" if success else "FAILED"
        self.info(
            f"DB {operation} on {table} - {status} - {duration:.3f}s",
            operation=operation,
            table=table,
            duration=duration,
            success=success
        )


# Global logger instance
logger = AlethearLogger()

# Convenience functions
def get_logger(name: str = "alethea") -> AlethearLogger:
    """Get logger instance"""
    return AlethearLogger(name)

def setup_logging(log_level: str = "INFO"):
    """Setup global logging configuration"""
    global logger
    logger = AlethearLogger("alethea", log_level)
    return logger
