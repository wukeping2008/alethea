from flask import Blueprint, request, jsonify, current_app
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from typing import Dict, Any, Optional
import json
import os

from src.services.corpus_service import CorpusService
from src.models.corpus_models import (
    KnowledgeDomain, EnhancedKnowledgePoint, MultimediaResource,
    Assessment, AssessmentAttempt, DifficultyLevel, BloomLevel,
    MultimediaType, AssessmentType, CompetencyLevel
)
from src.utils.error_handler import handle_error
from src.utils.logger import get_logger

# 创建蓝图
corpus_bp = Blueprint('corpus', __name__, url_prefix='/api/corpus')
logger = get_logger(__name__)

def get_corpus_service() -> CorpusService:
    """获取语料库服务实例"""
    # 这里应该从应用配置中获取数据库连接
    # 暂时使用简单的实现
    engine = create_engine('sqlite:///instance/alethea.db')
    Session = sessionmaker(bind=engine)
    db = Session()
    return CorpusService(db)

# ==================== 知识领域管理 ====================

@corpus_bp.route('/domains', methods=['GET'])
def get_domains():
    """获取知识领域列表"""
    try:
        corpus_service = get_corpus_service()
        parent_id = request.args.get('parent_id', type=int)
        
        domains = corpus_service.get_knowledge_domains(parent_id=parent_id)
        
        result = []
        for domain in domains:
            result.append({
                'id': domain.id,
                'domain_key': domain.domain_key,
                'name': domain.name,
                'description': domain.description,
                'parent_domain_id': domain.parent_domain_id,
                'subdirectory': domain.subdirectory,
                'difficulty_levels': domain.difficulty_levels,
                'assessment_types': domain.assessment_types,
                'metadata': domain.metadata,
                'created_at': domain.created_at.isoformat(),
                'updated_at': domain.updated_at.isoformat()
            })
        
        return jsonify({
            'success': True,
            'data': result,
            'total': len(result)
        })
        
    except Exception as e:
        logger.error(f"Error getting domains: {str(e)}")
        return handle_error(e)

@corpus_bp.route('/domains', methods=['POST'])
def create_domain():
    """创建知识领域"""
    try:
        corpus_service = get_corpus_service()
        data = request.get_json()
        
        # 验证必需字段
        required_fields = ['domain_key', 'name']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        domain = corpus_service.create_knowledge_domain(data)
        
        return jsonify({
            'success': True,
            'data': {
                'id': domain.id,
                'domain_key': domain.domain_key,
                'name': domain.name,
                'description': domain.description,
                'created_at': domain.created_at.isoformat()
            }
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating domain: {str(e)}")
        return handle_error(e)

# ==================== 知识点管理 ====================

@corpus_bp.route('/knowledge-points', methods=['GET'])
def get_knowledge_points():
    """获取知识点列表"""
    try:
        corpus_service = get_corpus_service()
        
        # 获取查询参数
        domain_id = request.args.get('domain_id', type=int)
        parent_id = request.args.get('parent_id', type=int)
        difficulty_level = request.args.get('difficulty_level')
        tags = request.args.getlist('tags')
        search_query = request.args.get('search')
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        knowledge_points, total_count = corpus_service.get_knowledge_points(
            domain_id=domain_id,
            parent_id=parent_id,
            difficulty_level=difficulty_level,
            tags=tags if tags else None,
            search_query=search_query,
            limit=limit,
            offset=offset
        )
        
        result = []
        for kp in knowledge_points:
            result.append({
                'id': kp.id,
                'title': kp.title,
                'description': kp.description,
                'domain_id': kp.domain_id,
                'parent_id': kp.parent_id,
                'order_index': kp.order_index,
                'depth_level': kp.depth_level,
                'difficulty_level': kp.difficulty_level.value if kp.difficulty_level else None,
                'bloom_level': kp.bloom_level.value if kp.bloom_level else None,
                'estimated_duration_minutes': kp.estimated_duration_minutes,
                'learning_objectives': kp.learning_objectives,
                'key_concepts': kp.key_concepts,
                'tags': kp.tags,
                'content_version': kp.content_version,
                'quality_score': kp.quality_score,
                'review_status': kp.review_status,
                'view_count': kp.view_count,
                'completion_rate': kp.completion_rate,
                'average_rating': kp.average_rating,
                'created_at': kp.created_at.isoformat(),
                'updated_at': kp.updated_at.isoformat()
            })
        
        return jsonify({
            'success': True,
            'data': result,
            'total': total_count,
            'limit': limit,
            'offset': offset
        })
        
    except Exception as e:
        logger.error(f"Error getting knowledge points: {str(e)}")
        return handle_error(e)

@corpus_bp.route('/knowledge-points', methods=['POST'])
def create_knowledge_point():
    """创建知识点"""
    try:
        corpus_service = get_corpus_service()
        data = request.get_json()
        
        # 验证必需字段
        required_fields = ['title', 'domain_id']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        knowledge_point = corpus_service.create_knowledge_point(data)
        
        return jsonify({
            'success': True,
            'data': {
                'id': knowledge_point.id,
                'title': knowledge_point.title,
                'description': knowledge_point.description,
                'domain_id': knowledge_point.domain_id,
                'difficulty_level': knowledge_point.difficulty_level.value if knowledge_point.difficulty_level else None,
                'content_version': knowledge_point.content_version,
                'created_at': knowledge_point.created_at.isoformat()
            }
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating knowledge point: {str(e)}")
        return handle_error(e)

@corpus_bp.route('/knowledge-points/<int:kp_id>', methods=['GET'])
def get_knowledge_point(kp_id: int):
    """获取单个知识点详情"""
    try:
        corpus_service = get_corpus_service()
        
        # 这里需要添加获取单个知识点的方法
        # 暂时返回基本信息
        return jsonify({
            'success': True,
            'data': {
                'id': kp_id,
                'message': 'Knowledge point details endpoint - to be implemented'
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting knowledge point {kp_id}: {str(e)}")
        return handle_error(e)

@corpus_bp.route('/knowledge-points/<int:kp_id>', methods=['PUT'])
def update_knowledge_point(kp_id: int):
    """更新知识点"""
    try:
        corpus_service = get_corpus_service()
        data = request.get_json()
        user_id = request.headers.get('X-User-ID', type=int)  # 从请求头获取用户ID
        
        knowledge_point = corpus_service.update_knowledge_point(
            kp_id=kp_id,
            update_data=data,
            user_id=user_id
        )
        
        return jsonify({
            'success': True,
            'data': {
                'id': knowledge_point.id,
                'title': knowledge_point.title,
                'content_version': knowledge_point.content_version,
                'updated_at': knowledge_point.updated_at.isoformat()
            }
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404
    except Exception as e:
        logger.error(f"Error updating knowledge point {kp_id}: {str(e)}")
        return handle_error(e)

@corpus_bp.route('/knowledge-points/<int:domain_id>/hierarchy', methods=['GET'])
def get_knowledge_point_hierarchy(domain_id: int):
    """获取知识点层级结构"""
    try:
        corpus_service = get_corpus_service()
        hierarchy = corpus_service.get_knowledge_point_hierarchy(domain_id)
        
        return jsonify({
            'success': True,
            'data': hierarchy
        })
        
    except Exception as e:
        logger.error(f"Error getting knowledge point hierarchy for domain {domain_id}: {str(e)}")
        return handle_error(e)

# ==================== 多媒体资源管理 ====================

@corpus_bp.route('/multimedia-resources', methods=['GET'])
def get_multimedia_resources():
    """获取多媒体资源列表"""
    try:
        corpus_service = get_corpus_service()
        
        knowledge_point_id = request.args.get('knowledge_point_id', type=int)
        resource_type = request.args.get('resource_type')
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        resources, total_count = corpus_service.get_multimedia_resources(
            knowledge_point_id=knowledge_point_id,
            resource_type=resource_type,
            limit=limit,
            offset=offset
        )
        
        result = []
        for resource in resources:
            result.append({
                'id': resource.id,
                'knowledge_point_id': resource.knowledge_point_id,
                'filename': resource.filename,
                'original_filename': resource.original_filename,
                'file_path': resource.file_path,
                'file_size': resource.file_size,
                'file_format': resource.file_format,
                'mime_type': resource.mime_type,
                'resource_type': resource.resource_type.value,
                'title': resource.title,
                'description': resource.description,
                'duration_seconds': resource.duration_seconds,
                'resolution': resource.resolution,
                'quality_level': resource.quality_level,
                'difficulty_level': resource.difficulty_level.value if resource.difficulty_level else None,
                'bloom_level': resource.bloom_level.value if resource.bloom_level else None,
                'processing_status': resource.processing_status,
                'quality_score': resource.quality_score,
                'review_status': resource.review_status,
                'view_count': resource.view_count,
                'download_count': resource.download_count,
                'average_rating': resource.average_rating,
                'created_at': resource.created_at.isoformat(),
                'updated_at': resource.updated_at.isoformat()
            })
        
        return jsonify({
            'success': True,
            'data': result,
            'total': total_count,
            'limit': limit,
            'offset': offset
        })
        
    except Exception as e:
        logger.error(f"Error getting multimedia resources: {str(e)}")
        return handle_error(e)

@corpus_bp.route('/multimedia-resources/upload', methods=['POST'])
def upload_multimedia_resource():
    """上传多媒体资源"""
    try:
        corpus_service = get_corpus_service()
        
        # 获取文件和元数据
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        # 获取其他参数
        knowledge_point_id = request.form.get('knowledge_point_id', type=int)
        title = request.form.get('title', file.filename)
        description = request.form.get('description', '')
        difficulty_level = request.form.get('difficulty_level', 'intermediate')
        bloom_level = request.form.get('bloom_level', 'understand')
        
        # 准备文件数据
        file_data = {
            'filename': file.filename,
            'original_filename': file.filename,
            'file_content': file.read(),
            'mime_type': file.mimetype,
            'title': title,
            'description': description,
            'difficulty_level': difficulty_level,
            'bloom_level': bloom_level
        }
        
        resource = corpus_service.upload_multimedia_resource(
            file_data=file_data,
            knowledge_point_id=knowledge_point_id
        )
        
        return jsonify({
            'success': True,
            'data': {
                'id': resource.id,
                'filename': resource.filename,
                'title': resource.title,
                'resource_type': resource.resource_type.value,
                'file_size': resource.file_size,
                'processing_status': resource.processing_status,
                'created_at': resource.created_at.isoformat()
            }
        }), 201
        
    except Exception as e:
        logger.error(f"Error uploading multimedia resource: {str(e)}")
        return handle_error(e)

@corpus_bp.route('/multimedia-resources/<int:resource_id>/usage', methods=['POST'])
def log_multimedia_usage(resource_id: int):
    """记录多媒体资源使用"""
    try:
        corpus_service = get_corpus_service()
        data = request.get_json()
        user_id = request.headers.get('X-User-ID', type=int)
        
        if not user_id:
            return jsonify({
                'success': False,
                'error': 'User ID required'
            }), 400
        
        usage_log = corpus_service.log_multimedia_usage(
            resource_id=resource_id,
            user_id=user_id,
            usage_data=data
        )
        
        return jsonify({
            'success': True,
            'data': {
                'id': usage_log.id,
                'action_type': usage_log.action_type,
                'duration_seconds': usage_log.duration_seconds,
                'created_at': usage_log.created_at.isoformat()
            }
        }), 201
        
    except Exception as e:
        logger.error(f"Error logging multimedia usage for resource {resource_id}: {str(e)}")
        return handle_error(e)

# ==================== 评估管理 ====================

@corpus_bp.route('/assessments', methods=['POST'])
def create_assessment():
    """创建评估"""
    try:
        corpus_service = get_corpus_service()
        data = request.get_json()
        
        # 验证必需字段
        required_fields = ['title', 'assessment_type']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        assessment = corpus_service.create_assessment(data)
        
        return jsonify({
            'success': True,
            'data': {
                'id': assessment.id,
                'title': assessment.title,
                'assessment_type': assessment.assessment_type.value,
                'difficulty_level': assessment.difficulty_level.value if assessment.difficulty_level else None,
                'estimated_duration_minutes': assessment.estimated_duration_minutes,
                'max_attempts': assessment.max_attempts,
                'passing_score': assessment.passing_score,
                'created_at': assessment.created_at.isoformat()
            }
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating assessment: {str(e)}")
        return handle_error(e)

@corpus_bp.route('/assessments/<int:assessment_id>/attempts', methods=['POST'])
def record_assessment_attempt(assessment_id: int):
    """记录评估尝试"""
    try:
        corpus_service = get_corpus_service()
        data = request.get_json()
        user_id = request.headers.get('X-User-ID', type=int)
        
        if not user_id:
            return jsonify({
                'success': False,
                'error': 'User ID required'
            }), 400
        
        data['assessment_id'] = assessment_id
        data['user_id'] = user_id
        
        attempt = corpus_service.record_assessment_attempt(data)
        
        return jsonify({
            'success': True,
            'data': {
                'id': attempt.id,
                'attempt_number': attempt.attempt_number,
                'score': attempt.score,
                'percentage': attempt.percentage,
                'is_passed': attempt.is_passed,
                'duration_seconds': attempt.duration_seconds,
                'completion_status': attempt.completion_status,
                'created_at': attempt.created_at.isoformat()
            }
        }), 201
        
    except Exception as e:
        logger.error(f"Error recording assessment attempt for assessment {assessment_id}: {str(e)}")
        return handle_error(e)

# ==================== 搜索和推荐 ====================

@corpus_bp.route('/search', methods=['GET'])
def search_content():
    """搜索内容"""
    try:
        corpus_service = get_corpus_service()
        
        query = request.args.get('q', '')
        if not query:
            return jsonify({
                'success': False,
                'error': 'Search query required'
            }), 400
        
        content_types = request.args.getlist('content_types')
        domain_ids = request.args.getlist('domain_ids', type=int)
        difficulty_levels = request.args.getlist('difficulty_levels')
        limit = request.args.get('limit', 20, type=int)
        
        results = corpus_service.search_content(
            query=query,
            content_types=content_types if content_types else None,
            domain_ids=domain_ids if domain_ids else None,
            difficulty_levels=difficulty_levels if difficulty_levels else None,
            limit=limit
        )
        
        # 格式化搜索结果
        formatted_results = {}
        for content_type, items in results.items():
            formatted_items = []
            for item in items:
                if content_type == 'knowledge_points':
                    formatted_items.append({
                        'id': item.id,
                        'title': item.title,
                        'description': item.description,
                        'difficulty_level': item.difficulty_level.value if item.difficulty_level else None,
                        'tags': item.tags,
                        'type': 'knowledge_point'
                    })
                elif content_type == 'multimedia_resources':
                    formatted_items.append({
                        'id': item.id,
                        'title': item.title,
                        'description': item.description,
                        'resource_type': item.resource_type.value,
                        'filename': item.filename,
                        'type': 'multimedia_resource'
                    })
                elif content_type == 'assessments':
                    formatted_items.append({
                        'id': item.id,
                        'title': item.title,
                        'description': item.description,
                        'assessment_type': item.assessment_type.value,
                        'difficulty_level': item.difficulty_level.value if item.difficulty_level else None,
                        'type': 'assessment'
                    })
            formatted_results[content_type] = formatted_items
        
        return jsonify({
            'success': True,
            'query': query,
            'results': formatted_results,
            'total_results': sum(len(items) for items in formatted_results.values())
        })
        
    except Exception as e:
        logger.error(f"Error searching content: {str(e)}")
        return handle_error(e)

@corpus_bp.route('/recommendations', methods=['GET'])
def get_recommendations():
    """获取内容推荐"""
    try:
        corpus_service = get_corpus_service()
        user_id = request.headers.get('X-User-ID', type=int)
        
        if not user_id:
            return jsonify({
                'success': False,
                'error': 'User ID required'
            }), 400
        
        based_on_history = request.args.get('based_on_history', 'true').lower() == 'true'
        limit = request.args.get('limit', 10, type=int)
        
        recommendations = corpus_service.get_content_recommendations(
            user_id=user_id,
            based_on_history=based_on_history,
            limit=limit
        )
        
        # 格式化推荐结果
        formatted_recommendations = {}
        for content_type, items in recommendations.items():
            formatted_items = []
            for item in items:
                if content_type == 'knowledge_points':
                    formatted_items.append({
                        'id': item.id,
                        'title': item.title,
                        'description': item.description,
                        'difficulty_level': item.difficulty_level.value if item.difficulty_level else None,
                        'estimated_duration_minutes': item.estimated_duration_minutes,
                        'average_rating': item.average_rating
                    })
            formatted_recommendations[content_type] = formatted_items
        
        return jsonify({
            'success': True,
            'recommendations': formatted_recommendations,
            'based_on_history': based_on_history
        })
        
    except Exception as e:
        logger.error(f"Error getting recommendations: {str(e)}")
        return handle_error(e)

# ==================== 数据导入导出 ====================

@corpus_bp.route('/domains/<int:domain_id>/export', methods=['GET'])
def export_domain(domain_id: int):
    """导出知识领域数据"""
    try:
        corpus_service = get_corpus_service()
        include_multimedia = request.args.get('include_multimedia', 'true').lower() == 'true'
        
        export_data = corpus_service.export_knowledge_domain(
            domain_id=domain_id,
            include_multimedia=include_multimedia
        )
        
        return jsonify({
            'success': True,
            'data': export_data
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404
    except Exception as e:
        logger.error(f"Error exporting domain {domain_id}: {str(e)}")
        return handle_error(e)

@corpus_bp.route('/domains/import', methods=['POST'])
def import_domain():
    """导入知识领域数据"""
    try:
        corpus_service = get_corpus_service()
        data = request.get_json()
        user_id = request.headers.get('X-User-ID', type=int)
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Import data required'
            }), 400
        
        domain = corpus_service.import_knowledge_domain(
            import_data=data,
            user_id=user_id
        )
        
        return jsonify({
            'success': True,
            'data': {
                'id': domain.id,
                'domain_key': domain.domain_key,
                'name': domain.name,
                'created_at': domain.created_at.isoformat()
            }
        }), 201
        
    except Exception as e:
        logger.error(f"Error importing domain: {str(e)}")
        return handle_error(e)

# ==================== 统计和分析 ====================

@corpus_bp.route('/statistics', methods=['GET'])
def get_statistics():
    """获取语料库统计信息"""
    try:
        corpus_service = get_corpus_service()
        stats = corpus_service.get_corpus_statistics()
        
        return jsonify({
            'success': True,
            'data': stats
        })
        
    except Exception as e:
        logger.error(f"Error getting corpus statistics: {str(e)}")
        return handle_error(e)

@corpus_bp.route('/quality-metrics', methods=['GET'])
def get_quality_metrics():
    """获取内容质量指标"""
    try:
        corpus_service = get_corpus_service()
        metrics = corpus_service.get_quality_metrics()
        
        return jsonify({
            'success': True,
            'data': metrics
        })
        
    except Exception as e:
        logger.error(f"Error getting quality metrics: {str(e)}")
        return handle_error(e)

# ==================== 配置和元数据 ====================

@corpus_bp.route('/config', methods=['GET'])
def get_corpus_config():
    """获取语料库配置"""
    try:
        corpus_service = get_corpus_service()
        config = corpus_service.config
        
        return jsonify({
            'success': True,
            'data': config
        })
        
    except Exception as e:
        logger.error(f"Error getting corpus config: {str(e)}")
        return handle_error(e)

@corpus_bp.route('/enums', methods=['GET'])
def get_enums():
    """获取枚举值定义"""
    try:
        enums = {
            'difficulty_levels': [level.value for level in DifficultyLevel],
            'bloom_levels': [level.value for level in BloomLevel],
            'multimedia_types': [type_.value for type_ in MultimediaType],
            'assessment_types': [type_.value for type_ in AssessmentType],
            'competency_levels': [level.value for level in CompetencyLevel]
        }
        
        return jsonify({
            'success': True,
            'data': enums
        })
        
    except Exception as e:
        logger.error(f"Error getting enums: {str(e)}")
        return handle_error(e)

# 错误处理
@corpus_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Resource not found'
    }), 404

@corpus_bp.errorhandler(400)
def bad_request(error):
    return jsonify({
        'success': False,
        'error': 'Bad request'
    }), 400

@corpus_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500
