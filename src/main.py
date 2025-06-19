"""
Main entry point for the Alethea Flask application
"""

import sys
import os
import json
import secrets
from flask import Flask, render_template, send_from_directory, request, jsonify
from flask_sqlalchemy import SQLAlchemy

# Ensure proper import paths
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from routes.llm_routes import llm_bp
from routes.user import user_bp
from routes.analytics_routes import analytics_bp
from routes.project_routes import project_bp
from routes.experiment_routes import experiment_bp
from routes.personal_knowledge_routes import personal_knowledge_bp
from routes.realtime_analytics import realtime_bp
from models.llm_models import initialize_llm_providers
from models.user import initialize_user_system, db
from models.user_analytics import UserAnalyticsManager

# Create Flask app
app = Flask(__name__)

# Configure app
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'alethea-demo-secret-key-2024')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///alethea.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

# Store database instance in app context
app.db = db

# Load configuration
def load_config():
    """Load configuration from environment or config file"""
    # Default configuration with all providers
    config = {
        'openai': {
            'api_key': os.getenv('OPENAI_API_KEY', ''),
            'default_model': os.getenv('OPENAI_DEFAULT_MODEL', 'gpt-4o')
        },
        'deepseek': {
            'api_key': os.getenv('DEEPSEEK_API_KEY', ''),
            'default_model': os.getenv('DEEPSEEK_DEFAULT_MODEL', 'deepseek-chat')
        },
        'volces_deepseek': {
            'api_key': os.getenv('VOLCES_DEEPSEEK_API_KEY', ''),
            'base_url': os.getenv('VOLCES_DEEPSEEK_BASE_URL', 'https://ark.cn-beijing.volces.com/api/v3/chat/completions'),
            'default_model': os.getenv('VOLCES_DEEPSEEK_DEFAULT_MODEL', 'deepseek-r1-250528'),
            'max_tokens': int(os.getenv('VOLCES_DEEPSEEK_MAX_TOKENS', '16191'))
        },
        'ollama_deepseek': {
            'base_url': os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434'),
            'default_model': os.getenv('OLLAMA_DEFAULT_MODEL', 'deepseek-r1:7b')
        },
        'qianwen': {
            'api_key': os.getenv('QIANWEN_API_KEY', ''),
            'secret_key': os.getenv('QIANWEN_SECRET_KEY', ''),
            'default_model': os.getenv('QIANWEN_DEFAULT_MODEL', 'ERNIE-Bot-4')
        },
        'ali_qwen': {
            'api_key': os.getenv('ALI_QWEN_API_KEY', ''),
            'base_url': os.getenv('ALI_QWEN_BASE_URL', 'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions'),
            'default_model': os.getenv('ALI_QWEN_DEFAULT_MODEL', 'qwen-plus-2025-04-28'),
            'max_tokens': int(os.getenv('ALI_QWEN_MAX_TOKENS', '16191'))
        },
        'claude': {
            'api_key': os.getenv('CLAUDE_API_KEY', ''),
            'default_model': os.getenv('CLAUDE_DEFAULT_MODEL', 'claude-3-sonnet-20240229')
        },
        'gemini': {
            'api_key': os.getenv('GEMINI_API_KEY', ''),
            'default_model': os.getenv('GEMINI_DEFAULT_MODEL', 'gemini-1.5-flash')
        },
        'llama': {
            'api_key': os.getenv('LLAMA_API_KEY', ''),
            'default_model': os.getenv('LLAMA_DEFAULT_MODEL', 'llama-3-70b')
        },
        'default_provider': os.getenv('DEFAULT_LLM_PROVIDER', 'gemini')
    }
    
    # For development, try to load from config file if exists
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                file_config = json.load(f)
                print(f"Loading configuration from {config_path}")
                
                # Completely replace config with file values
                for key, value in file_config.items():
                    if isinstance(value, dict) and key in config and isinstance(config[key], dict):
                        # Merge dictionaries
                        config[key].update(value)
                    else:
                        # Replace value completely
                        config[key] = value
                
                print(f"Configuration loaded successfully. Default provider: {config.get('default_provider', 'not set')}")
                
                # Debug: Print which providers have API keys
                for provider_name, provider_config in config.items():
                    if isinstance(provider_config, dict) and 'api_key' in provider_config:
                        has_key = bool(provider_config['api_key'] and provider_config['api_key'].strip())
                        print(f"Provider {provider_name}: {'✓' if has_key else '✗'} API key configured")
                        
        except Exception as e:
            print(f"Error loading config file: {e}")
    else:
        print(f"Config file not found at {config_path}, using environment variables only")
    
    return config

# Initialize application
def initialize_app():
    """Initialize all application components"""
    # Load configuration
    config = load_config()
    
    # Initialize LLM providers
    initialize_llm_providers(config)
    
    # Create database tables
    with app.app_context():
        db.create_all()
        
        # Initialize user management system
        user_managers = initialize_user_system(app, db)
        
        # Initialize analytics manager
        analytics_manager = UserAnalyticsManager(db)
        user_managers['analytics_manager'] = analytics_manager
        
        # Store managers in app context
        app.user_managers = user_managers
        
        print("Database tables created and managers initialized")

# Register blueprints
app.register_blueprint(llm_bp)
app.register_blueprint(user_bp)
app.register_blueprint(analytics_bp)
app.register_blueprint(project_bp)
app.register_blueprint(experiment_bp)
app.register_blueprint(personal_knowledge_bp)
app.register_blueprint(realtime_bp)

# Routes
@app.route('/')
def index():
    """Serve the main application page"""
    return send_from_directory('static', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serve static files"""
    return send_from_directory('static', path)

@app.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files with explicit static prefix"""
    return send_from_directory('static', filename)

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'message': 'Alethea API is running',
        'features': {
            'user_management': True,
            'analytics': True,
            'digital_portrait': True,
            'project_recommendations': True
        }
    })

@app.route('/api/status')
def status():
    """Get system status"""
    try:
        # Check database connection
        with app.app_context():
            db.session.execute('SELECT 1')
        
        # Check if managers are initialized
        managers_status = {
            'user_manager': hasattr(app, 'user_managers') and 'user_manager' in app.user_managers,
            'analytics_manager': hasattr(app, 'user_managers') and 'analytics_manager' in app.user_managers,
            'role_manager': hasattr(app, 'user_managers') and 'role_manager' in app.user_managers,
            'subject_manager': hasattr(app, 'user_managers') and 'subject_manager' in app.user_managers,
            'question_manager': hasattr(app, 'user_managers') and 'question_manager' in app.user_managers
        }
        
        return jsonify({
            'status': 'ok',
            'database': 'connected',
            'managers': managers_status
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

# Enable CORS for development
@app.after_request
def add_cors_headers(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Session-ID')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Handle preflight requests
@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = jsonify()
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "Content-Type,Authorization,X-Session-ID")
        response.headers.add('Access-Control-Allow-Methods', "GET,PUT,POST,DELETE,OPTIONS")
        return response

# Error handlers
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500

# Run the application
if __name__ == '__main__':
    # Initialize the application
    initialize_app()
    
    # For development
    print("Starting Alethea Enhanced Platform...")
    print("Features enabled:")
    print("- AI Question Answering")
    print("- User Management & Authentication")
    print("- Digital Portrait Generation")
    print("- Learning Analytics")
    print("- Personalized Project Recommendations")
    print("- Knowledge Graph Tracking")
    print("\nAccess the application at: http://localhost:8083")
    
    app.run(host='0.0.0.0', port=8083, debug=True)
