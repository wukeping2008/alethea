import os
import json
import shutil
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
from werkzeug.utils import secure_filename
import hashlib
import mimetypes
from pathlib import Path

from src.models.corpus_models import (
    KnowledgeDomain, EnhancedKnowledgePoint, MultimediaResource,
    Assessment, AssessmentAttempt, MultimediaUsageLog, ContentVersion,
    EnhancedKnowledgeInteraction, DifficultyLevel, BloomLevel,
    MultimediaType, AssessmentType, CompetencyLevel
)
from src.models.user import User
from src.models.learning_analytics import LearningSession

class CorpusService:
    """语料库管理服务"""
    
    def __init__(self, db: Session, corpus_root: str = "corpus"):
        self.db = db
        self.corpus_root = corpus_root
        self.config = self._load_corpus_config()
        
    def _load_corpus_config(self) -> Dict:
        """加载语料库配置"""
        config_path = os.path.join(self.corpus_root, "corpus_config.json")
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    # ==================== 知识领域管理 ====================
    
    def create_knowledge_domain(self, domain_data: Dict[str, Any]) -> KnowledgeDomain:
        """创建知识领域"""
        domain = KnowledgeDomain(
            domain_key=domain_data.get('domain_key'),
            name=domain_data.get('name'),
            description=domain_data.get('description'),
            parent_domain_id=domain_data.get('parent_domain_id'),
            subdirectory=domain_data.get('subdirectory'),
            difficulty_levels=domain_data.get('difficulty_levels', []),
            assessment_types=domain_data.get('assessment_types', []),
            metadata=domain_data.get('metadata', {})
        )
        
        self.db.add(domain)
        self.db.commit()
        self.db.refresh(domain)
        
        # 创建对应的文件系统目录
        self._create_domain_directory(domain)
        
        return domain
    
    def _create_domain_directory(self, domain: KnowledgeDomain):
        """为知识领域创建文件系统目录"""
        domain_path = os.path.join(
            self.corpus_root, 
            "knowledge_base", 
            domain.domain_key
        )
        
        if domain.subdirectory:
            domain_path = os.path.join(domain_path, domain.subdirectory)
        
        os.makedirs(domain_path, exist_ok=True)
        
        # 创建子目录
        subdirs = ['content', 'assessments', 'multimedia', 'metadata']
        for subdir in subdirs:
            os.makedirs(os.path.join(domain_path, subdir), exist_ok=True)
    
    def get_knowledge_domains(self, parent_id: Optional[int] = None) -> List[KnowledgeDomain]:
        """获取知识领域列表"""
        query = self.db.query(KnowledgeDomain).filter(
            KnowledgeDomain.is_active == True
        )
        
        if parent_id is not None:
            query = query.filter(KnowledgeDomain.parent_domain_id == parent_id)
        else:
            query = query.filter(KnowledgeDomain.parent_domain_id.is_(None))
        
        return query.order_by(KnowledgeDomain.name).all()
    
    # ==================== 知识点管理 ====================
    
    def create_knowledge_point(self, kp_data: Dict[str, Any]) -> EnhancedKnowledgePoint:
        """创建增强知识点"""
        knowledge_point = EnhancedKnowledgePoint(
            title=kp_data.get('title'),
            description=kp_data.get('description'),
            domain_id=kp_data.get('domain_id'),
            parent_id=kp_data.get('parent_id'),
            order_index=kp_data.get('order_index', 0),
            depth_level=kp_data.get('depth_level', 0),
            difficulty_level=DifficultyLevel(kp_data.get('difficulty_level', 'intermediate')),
            bloom_level=BloomLevel(kp_data.get('bloom_level', 'understand')),
            estimated_duration_minutes=kp_data.get('estimated_duration_minutes'),
            learning_objectives=kp_data.get('learning_objectives', []),
            prerequisites=kp_data.get('prerequisites', []),
            related_points=kp_data.get('related_points', []),
            key_concepts=kp_data.get('key_concepts', []),
            formulas=kp_data.get('formulas', []),
            examples=kp_data.get('examples', []),
            applications=kp_data.get('applications', []),
            content_modules=kp_data.get('content_modules', {}),
            multimedia_resources=kp_data.get('multimedia_resources', []),
            interactive_elements=kp_data.get('interactive_elements', {}),
            simulation_config=kp_data.get('simulation_config', {}),
            assessment_criteria=kp_data.get('assessment_criteria', {}),
            practice_questions=kp_data.get('practice_questions', []),
            competency_indicators=kp_data.get('competency_indicators', []),
            tags=kp_data.get('tags', []),
            language=kp_data.get('language', 'zh-CN'),
            accessibility_features=kp_data.get('accessibility_features', {}),
            cultural_context=kp_data.get('cultural_context', {})
        )
        
        self.db.add(knowledge_point)
        self.db.commit()
        self.db.refresh(knowledge_point)
        
        # 创建初始版本
        self._create_content_version(knowledge_point, "1.0.0", "Initial version")
        
        return knowledge_point
    
    def update_knowledge_point(self, kp_id: int, update_data: Dict[str, Any], 
                             user_id: Optional[int] = None) -> EnhancedKnowledgePoint:
        """更新知识点"""
        knowledge_point = self.db.query(EnhancedKnowledgePoint).filter(
            EnhancedKnowledgePoint.id == kp_id
        ).first()
        
        if not knowledge_point:
            raise ValueError(f"Knowledge point {kp_id} not found")
        
        # 保存更新前的状态用于版本控制
        old_content = self._serialize_knowledge_point(knowledge_point)
        
        # 更新字段
        for field, value in update_data.items():
            if hasattr(knowledge_point, field):
                setattr(knowledge_point, field, value)
        
        knowledge_point.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(knowledge_point)
        
        # 创建新版本
        new_version = self._increment_version(knowledge_point.content_version)
        self._create_content_version(
            knowledge_point, 
            new_version, 
            "Content update",
            old_content=old_content,
            created_by=user_id
        )
        
        return knowledge_point
    
    def get_knowledge_points(self, domain_id: Optional[int] = None, 
                           parent_id: Optional[int] = None,
                           difficulty_level: Optional[str] = None,
                           tags: Optional[List[str]] = None,
                           search_query: Optional[str] = None,
                           limit: int = 50, offset: int = 0) -> Tuple[List[EnhancedKnowledgePoint], int]:
        """获取知识点列表"""
        query = self.db.query(EnhancedKnowledgePoint)
        
        # 过滤条件
        if domain_id:
            query = query.filter(EnhancedKnowledgePoint.domain_id == domain_id)
        
        if parent_id is not None:
            query = query.filter(EnhancedKnowledgePoint.parent_id == parent_id)
        
        if difficulty_level:
            query = query.filter(EnhancedKnowledgePoint.difficulty_level == difficulty_level)
        
        if tags:
            for tag in tags:
                query = query.filter(EnhancedKnowledgePoint.tags.contains([tag]))
        
        if search_query:
            search_filter = or_(
                EnhancedKnowledgePoint.title.contains(search_query),
                EnhancedKnowledgePoint.description.contains(search_query)
            )
            query = query.filter(search_filter)
        
        # 获取总数
        total_count = query.count()
        
        # 分页和排序
        knowledge_points = query.order_by(
            EnhancedKnowledgePoint.order_index,
            EnhancedKnowledgePoint.title
        ).offset(offset).limit(limit).all()
        
        return knowledge_points, total_count
    
    def get_knowledge_point_hierarchy(self, domain_id: int) -> Dict[str, Any]:
        """获取知识点层级结构"""
        knowledge_points = self.db.query(EnhancedKnowledgePoint).filter(
            EnhancedKnowledgePoint.domain_id == domain_id
        ).order_by(
            EnhancedKnowledgePoint.depth_level,
            EnhancedKnowledgePoint.order_index
        ).all()
        
        # 构建层级结构
        hierarchy = {}
        point_map = {}
        
        for kp in knowledge_points:
            point_data = {
                'id': kp.id,
                'title': kp.title,
                'description': kp.description,
                'difficulty_level': kp.difficulty_level.value if kp.difficulty_level else None,
                'bloom_level': kp.bloom_level.value if kp.bloom_level else None,
                'estimated_duration_minutes': kp.estimated_duration_minutes,
                'children': []
            }
            
            point_map[kp.id] = point_data
            
            if kp.parent_id is None:
                hierarchy[kp.id] = point_data
            else:
                if kp.parent_id in point_map:
                    point_map[kp.parent_id]['children'].append(point_data)
        
        return hierarchy
    
    # ==================== 多媒体资源管理 ====================
    
    def upload_multimedia_resource(self, file_data: Dict[str, Any], 
                                 knowledge_point_id: Optional[int] = None) -> MultimediaResource:
        """上传多媒体资源"""
        # 文件安全检查
        filename = secure_filename(file_data.get('filename', ''))
        if not filename:
            raise ValueError("Invalid filename")
        
        # 确定资源类型
        mime_type = file_data.get('mime_type') or mimetypes.guess_type(filename)[0]
        resource_type = self._determine_resource_type(mime_type)
        
        # 生成文件路径
        file_path = self._generate_file_path(filename, resource_type, knowledge_point_id)
        
        # 创建目录
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # 保存文件
        if 'file_content' in file_data:
            with open(file_path, 'wb') as f:
                f.write(file_data['file_content'])
        elif 'source_path' in file_data:
            shutil.copy2(file_data['source_path'], file_path)
        
        # 计算文件哈希
        file_hash = self._calculate_file_hash(file_path)
        file_size = os.path.getsize(file_path)
        
        # 创建数据库记录
        resource = MultimediaResource(
            knowledge_point_id=knowledge_point_id,
            filename=filename,
            original_filename=file_data.get('original_filename', filename),
            file_path=file_path,
            file_size=file_size,
            file_format=Path(filename).suffix.lower(),
            mime_type=mime_type,
            resource_type=resource_type,
            title=file_data.get('title', filename),
            description=file_data.get('description'),
            duration_seconds=file_data.get('duration_seconds'),
            resolution=file_data.get('resolution'),
            quality_level=file_data.get('quality_level'),
            timestamps=file_data.get('timestamps', []),
            captions=file_data.get('captions', []),
            annotations=file_data.get('annotations', []),
            interactive_hotspots=file_data.get('interactive_hotspots', []),
            learning_objectives=file_data.get('learning_objectives', []),
            difficulty_level=DifficultyLevel(file_data.get('difficulty_level', 'intermediate')),
            bloom_level=BloomLevel(file_data.get('bloom_level', 'understand')),
            usage_context=file_data.get('usage_context', {}),
            alt_text=file_data.get('alt_text'),
            transcription=file_data.get('transcription'),
            copyright_info=file_data.get('copyright_info', {}),
            license_type=file_data.get('license_type', 'educational'),
            attribution=file_data.get('attribution'),
            usage_rights=file_data.get('usage_rights', {}),
            processing_status="completed"
        )
        
        self.db.add(resource)
        self.db.commit()
        self.db.refresh(resource)
        
        # 生成缩略图和预览（如果需要）
        self._generate_thumbnails(resource)
        
        return resource
    
    def _determine_resource_type(self, mime_type: str) -> MultimediaType:
        """根据MIME类型确定资源类型"""
        if not mime_type:
            return MultimediaType.DOCUMENT
        
        if mime_type.startswith('video/'):
            return MultimediaType.VIDEO
        elif mime_type.startswith('audio/'):
            return MultimediaType.AUDIO
        elif mime_type.startswith('image/'):
            if mime_type in ['image/gif']:
                return MultimediaType.ANIMATION
            return MultimediaType.IMAGE
        elif mime_type in ['application/pdf', 'application/msword', 'text/html']:
            return MultimediaType.DOCUMENT
        elif mime_type in ['application/javascript', 'text/html']:
            return MultimediaType.SIMULATION
        else:
            return MultimediaType.DOCUMENT
    
    def _generate_file_path(self, filename: str, resource_type: MultimediaType, 
                          knowledge_point_id: Optional[int] = None) -> str:
        """生成文件存储路径"""
        # 基础路径
        base_path = os.path.join(self.corpus_root, "multimedia_resources")
        
        # 按类型分类
        type_path = os.path.join(base_path, resource_type.value + "s")
        
        # 按知识点分组（如果有）
        if knowledge_point_id:
            type_path = os.path.join(type_path, f"kp_{knowledge_point_id}")
        
        # 按日期分组
        date_path = datetime.now().strftime("%Y/%m")
        type_path = os.path.join(type_path, date_path)
        
        # 生成唯一文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        name, ext = os.path.splitext(filename)
        unique_filename = f"{timestamp}_{name}{ext}"
        
        return os.path.join(type_path, unique_filename)
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """计算文件哈希值"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def _generate_thumbnails(self, resource: MultimediaResource):
        """生成缩略图和预览"""
        # 这里可以集成图像/视频处理库来生成缩略图
        # 例如使用PIL、OpenCV、FFmpeg等
        pass
    
    def get_multimedia_resources(self, knowledge_point_id: Optional[int] = None,
                               resource_type: Optional[str] = None,
                               limit: int = 50, offset: int = 0) -> Tuple[List[MultimediaResource], int]:
        """获取多媒体资源列表"""
        query = self.db.query(MultimediaResource)
        
        if knowledge_point_id:
            query = query.filter(MultimediaResource.knowledge_point_id == knowledge_point_id)
        
        if resource_type:
            query = query.filter(MultimediaResource.resource_type == resource_type)
        
        total_count = query.count()
        
        resources = query.order_by(
            desc(MultimediaResource.created_at)
        ).offset(offset).limit(limit).all()
        
        return resources, total_count
    
    def log_multimedia_usage(self, resource_id: int, user_id: int, 
                           usage_data: Dict[str, Any]) -> MultimediaUsageLog:
        """记录多媒体资源使用"""
        usage_log = MultimediaUsageLog(
            resource_id=resource_id,
            user_id=user_id,
            session_id=usage_data.get('session_id'),
            action_type=usage_data.get('action_type', 'view'),
            start_time=usage_data.get('start_time', datetime.utcnow()),
            end_time=usage_data.get('end_time'),
            duration_seconds=usage_data.get('duration_seconds'),
            playback_position=usage_data.get('playback_position'),
            playback_speed=usage_data.get('playback_speed', 1.0),
            volume_level=usage_data.get('volume_level'),
            quality_setting=usage_data.get('quality_setting'),
            interactions=usage_data.get('interactions', []),
            annotations_made=usage_data.get('annotations_made', []),
            bookmarks=usage_data.get('bookmarks', []),
            notes=usage_data.get('notes'),
            device_type=usage_data.get('device_type'),
            browser_info=usage_data.get('browser_info'),
            screen_resolution=usage_data.get('screen_resolution'),
            network_quality=usage_data.get('network_quality'),
            comprehension_rating=usage_data.get('comprehension_rating'),
            engagement_score=usage_data.get('engagement_score'),
            completion_percentage=usage_data.get('completion_percentage')
        )
        
        self.db.add(usage_log)
        self.db.commit()
        self.db.refresh(usage_log)
        
        # 更新资源使用统计
        self._update_resource_statistics(resource_id)
        
        return usage_log
    
    def _update_resource_statistics(self, resource_id: int):
        """更新资源使用统计"""
        resource = self.db.query(MultimediaResource).filter(
            MultimediaResource.id == resource_id
        ).first()
        
        if resource:
            # 更新查看次数
            view_count = self.db.query(MultimediaUsageLog).filter(
                MultimediaUsageLog.resource_id == resource_id,
                MultimediaUsageLog.action_type == 'view'
            ).count()
            
            # 更新下载次数
            download_count = self.db.query(MultimediaUsageLog).filter(
                MultimediaUsageLog.resource_id == resource_id,
                MultimediaUsageLog.action_type == 'download'
            ).count()
            
            # 计算平均评分
            avg_rating = self.db.query(func.avg(MultimediaUsageLog.comprehension_rating)).filter(
                MultimediaUsageLog.resource_id == resource_id,
                MultimediaUsageLog.comprehension_rating.isnot(None)
            ).scalar() or 0.0
            
            resource.view_count = view_count
            resource.download_count = download_count
            resource.average_rating = float(avg_rating)
            
            self.db.commit()
    
    # ==================== 评估管理 ====================
    
    def create_assessment(self, assessment_data: Dict[str, Any]) -> Assessment:
        """创建评估"""
        assessment = Assessment(
            knowledge_point_id=assessment_data.get('knowledge_point_id'),
            title=assessment_data.get('title'),
            description=assessment_data.get('description'),
            assessment_type=AssessmentType(assessment_data.get('assessment_type', 'theoretical')),
            difficulty_level=DifficultyLevel(assessment_data.get('difficulty_level', 'intermediate')),
            bloom_level=BloomLevel(assessment_data.get('bloom_level', 'understand')),
            competency_level=CompetencyLevel(assessment_data.get('competency_level', 'competent')),
            estimated_duration_minutes=assessment_data.get('estimated_duration_minutes'),
            max_attempts=assessment_data.get('max_attempts', 3),
            passing_score=assessment_data.get('passing_score', 60.0),
            questions=assessment_data.get('questions', []),
            rubrics=assessment_data.get('rubrics', {}),
            answer_key=assessment_data.get('answer_key', {}),
            feedback_templates=assessment_data.get('feedback_templates', {}),
            adaptive_rules=assessment_data.get('adaptive_rules', {}),
            difficulty_adjustment=assessment_data.get('difficulty_adjustment', {}),
            personalization_config=assessment_data.get('personalization_config', {}),
            randomize_questions=assessment_data.get('randomize_questions', False),
            randomize_options=assessment_data.get('randomize_options', False),
            show_correct_answers=assessment_data.get('show_correct_answers', True),
            immediate_feedback=assessment_data.get('immediate_feedback', True)
        )
        
        self.db.add(assessment)
        self.db.commit()
        self.db.refresh(assessment)
        
        return assessment
    
    def record_assessment_attempt(self, attempt_data: Dict[str, Any]) -> AssessmentAttempt:
        """记录评估尝试"""
        # 计算尝试次数
        attempt_number = self.db.query(AssessmentAttempt).filter(
            AssessmentAttempt.assessment_id == attempt_data.get('assessment_id'),
            AssessmentAttempt.user_id == attempt_data.get('user_id')
        ).count() + 1
        
        attempt = AssessmentAttempt(
            assessment_id=attempt_data.get('assessment_id'),
            user_id=attempt_data.get('user_id'),
            session_id=attempt_data.get('session_id'),
            attempt_number=attempt_number,
            start_time=attempt_data.get('start_time', datetime.utcnow()),
            end_time=attempt_data.get('end_time'),
            duration_seconds=attempt_data.get('duration_seconds'),
            responses=attempt_data.get('responses', {}),
            score=attempt_data.get('score'),
            percentage=attempt_data.get('percentage'),
            is_passed=attempt_data.get('is_passed', False),
            question_analysis=attempt_data.get('question_analysis', {}),
            competency_scores=attempt_data.get('competency_scores', {}),
            bloom_level_scores=attempt_data.get('bloom_level_scores', {}),
            time_per_question=attempt_data.get('time_per_question', {}),
            automated_feedback=attempt_data.get('automated_feedback', {}),
            completion_status=attempt_data.get('completion_status', 'completed'),
            submission_ip=attempt_data.get('submission_ip'),
            user_agent=attempt_data.get('user_agent')
        )
        
        self.db.add(attempt)
        self.db.commit()
        self.db.refresh(attempt)
        
        # 更新评估统计
        self._update_assessment_statistics(attempt_data.get('assessment_id'))
        
        return attempt
    
    def _update_assessment_statistics(self, assessment_id: int):
        """更新评估统计信息"""
        assessment = self.db.query(Assessment).filter(
            Assessment.id == assessment_id
        ).first()
        
        if assessment:
            attempts = self.db.query(AssessmentAttempt).filter(
                AssessmentAttempt.assessment_id == assessment_id,
                AssessmentAttempt.completion_status == 'completed'
            ).all()
            
            if attempts:
                assessment.total_attempts = len(attempts)
                assessment.average_score = sum(a.score for a in attempts if a.score) / len(attempts)
                assessment.completion_rate = len([a for a in attempts if a.is_passed]) / len(attempts) * 100
                assessment.average_duration = sum(a.duration_seconds for a in attempts if a.duration_seconds) / len(attempts)
                
                self.db.commit()
    
    # ==================== 版本控制 ====================
    
    def _create_content_version(self, knowledge_point: EnhancedKnowledgePoint, 
                              version_number: str, change_summary: str,
                              old_content: Optional[Dict] = None,
                              created_by: Optional[int] = None):
        """创建内容版本"""
        # 序列化当前内容
        current_content = self._serialize_knowledge_point(knowledge_point)
        
        # 计算差异
        diff_from_previous = {}
        if old_content:
            diff_from_previous = self._calculate_content_diff(old_content, current_content)
        
        version = ContentVersion(
            knowledge_point_id=knowledge_point.id,
            version_number=version_number,
            version_type=self._determine_version_type(version_number),
            change_summary=change_summary,
            content_snapshot=current_content,
            diff_from_previous=diff_from_previous,
            created_by=created_by,
            is_current=True
        )
        
        # 将之前的版本标记为非当前版本
        self.db.query(ContentVersion).filter(
            ContentVersion.knowledge_point_id == knowledge_point.id,
            ContentVersion.is_current == True
        ).update({'is_current': False})
        
        self.db.add(version)
        
        # 更新知识点的版本号
        knowledge_point.content_version = version_number
        
        self.db.commit()
    
    def _serialize_knowledge_point(self, kp: EnhancedKnowledgePoint) -> Dict:
        """序列化知识点内容"""
        return {
            'title': kp.title,
            'description': kp.description,
            'difficulty_level': kp.difficulty_level.value if kp.difficulty_level else None,
            'bloom_level': kp.bloom_level.value if kp.bloom_level else None,
            'estimated_duration_minutes': kp.estimated_duration_minutes,
            'learning_objectives': kp.learning_objectives,
            'prerequisites': kp.prerequisites,
            'related_points': kp.related_points,
            'key_concepts': kp.key_concepts,
            'formulas': kp.formulas,
            'examples': kp.examples,
            'applications': kp.applications,
            'content_modules': kp.content_modules,
            'interactive_elements': kp.interactive_elements,
            'simulation_config': kp.simulation_config,
            'assessment_criteria': kp.assessment_criteria,
            'practice_questions': kp.practice_questions,
            'competency_indicators': kp.competency_indicators,
            'tags': kp.tags,
            'accessibility_features': kp.accessibility_features,
            'cultural_context': kp.cultural_context
        }
    
    def _calculate_content_diff(self, old_content: Dict, new_content: Dict) -> Dict:
        """计算内容差异"""
        diff = {}
        
        for key in set(old_content.keys()) | set(new_content.keys()):
            old_value = old_content.get(key)
            new_value = new_content.get(key)
            
            if old_value != new_value:
                diff[key] = {
                    'old': old_value,
                    'new': new_value
                }
        
        return diff
    
    def _increment_version(self, current_version: str) -> str:
        """递增版本号"""
        try:
            parts = current_version.split('.')
            if len(parts) == 3:
                major, minor, patch = map(int, parts)
                return f"{major}.{minor}.{patch + 1}"
            else:
                return "1.0.1"
        except:
            return "1.0.1"
    
    def _determine_version_type(self, version_number: str) -> str:
        """确定版本类型"""
        try:
            parts = version_number.split('.')
            if len(parts) == 3:
                major, minor, patch = map(int, parts)
                if patch > 0:
                    return "patch"
                elif minor > 0:
                    return "minor"
                else:
                    return "major"
        except:
            pass
        return "patch"
    
    # ==================== 搜索和推荐 ====================
    
    def search_content(self, query: str, content_types: Optional[List[str]] = None,
                      domain_ids: Optional[List[int]] = None,
                      difficulty_levels: Optional[List[str]] = None,
                      limit: int = 20) -> Dict[str, List]:
        """搜索内容"""
        results = {
            'knowledge_points': [],
            'multimedia_resources': [],
            'assessments': []
        }
        
        # 搜索知识点
        if not content_types or 'knowledge_points' in content_types:
            kp_query = self.db.query(EnhancedKnowledgePoint)
            
            # 文本搜索
            search_filter = or_(
                EnhancedKnowledgePoint.title.contains(query),
                EnhancedKnowledgePoint.description.contains(query)
            )
            kp_query = kp_query.filter(search_filter)
            
            # 领域过滤
            if domain_ids:
                kp_query = kp_query.filter(EnhancedKnowledgePoint.domain_id.in_(domain_ids))
            
            # 难度过滤
            if difficulty_levels:
                kp_query = kp_query.filter(EnhancedKnowledgePoint.difficulty_level.in_(difficulty_levels))
            
            results['knowledge_points'] = kp_query.limit(limit).all()
        
        # 搜索多媒体资源
        if not content_types or 'multimedia_resources' in content_types:
            mr_query = self.db.query(MultimediaResource)
            
            # 文本搜索
            search_filter = or_(
                MultimediaResource.title.contains(query),
                MultimediaResource.description.contains(query),
                MultimediaResource.filename.contains(query)
            )
            mr_query = mr_query.filter(search_filter)
            
            results['multimedia_resources'] = mr_query.limit(limit).all()
        
        # 搜索评估
        if not content_types or 'assessments' in content_types:
            assess_query = self.db.query(Assessment)
            
            # 文本搜索
            search_filter = or_(
                Assessment.title.contains(query),
                Assessment.description.contains(query)
            )
            assess_query = assess_query.filter(search_filter)
            
            results['assessments'] = assess_query.limit(limit).all()
        
        return results
    
    def get_content_recommendations(self, user_id: int, 
                                  based_on_history: bool = True,
                                  limit: int = 10) -> Dict[str, List]:
        """获取内容推荐"""
        recommendations = {
            'knowledge_points': [],
            'multimedia_resources': [],
            'assessments': []
        }
        
        if based_on_history:
            # 基于用户历史行为推荐
            user_interactions = self.db.query(EnhancedKnowledgeInteraction).filter(
                EnhancedKnowledgeInteraction.user_id == user_id
            ).order_by(desc(EnhancedKnowledgeInteraction.created_at)).limit(50).all()
            
            # 分析用户偏好
            preferred_domains = {}
            preferred_difficulty = {}
            
            for interaction in user_interactions:
                if interaction.knowledge_point:
                    domain_id = interaction.knowledge_point.domain_id
                    difficulty = interaction.knowledge_point.difficulty_level
                    
                    preferred_domains[domain_id] = preferred_domains.get(domain_id, 0) + 1
                    if difficulty:
                        preferred_difficulty[difficulty.value] = preferred_difficulty.get(difficulty.value, 0) + 1
            
            # 获取推荐的知识点
            if preferred_domains:
                top_domain = max(preferred_domains.keys(), key=lambda k: preferred_domains[k])
                
                recommended_kps = self.db.query(EnhancedKnowledgePoint).filter(
                    EnhancedKnowledgePoint.domain_id == top_domain,
                    ~EnhancedKnowledgePoint.id.in_([i.knowledge_point_id for i in user_interactions])
                ).order_by(desc(EnhancedKnowledgePoint.average_rating)).limit(limit).all()
                
                recommendations['knowledge_points'] = recommended_kps
        
        return recommendations
    
    # ==================== 数据导入导出 ====================
    
    def export_knowledge_domain(self, domain_id: int, include_multimedia: bool = True) -> Dict[str, Any]:
        """导出知识领域数据"""
        domain = self.db.query(KnowledgeDomain).filter(
            KnowledgeDomain.id == domain_id
        ).first()
        
        if not domain:
            raise ValueError(f"Domain {domain_id} not found")
        
        # 获取知识点
        knowledge_points = self.db.query(EnhancedKnowledgePoint).filter(
            EnhancedKnowledgePoint.domain_id == domain_id
        ).all()
        
        export_data = {
            'domain': {
                'domain_key': domain.domain_key,
                'name': domain.name,
                'description': domain.description,
                'subdirectory': domain.subdirectory,
                'difficulty_levels': domain.difficulty_levels,
                'assessment_types': domain.assessment_types,
                'metadata': domain.metadata
            },
            'knowledge_points': [],
            'multimedia_resources': [],
            'assessments': []
        }
        
        for kp in knowledge_points:
            kp_data = self._serialize_knowledge_point(kp)
            kp_data['id'] = kp.id
            kp_data['parent_id'] = kp.parent_id
            kp_data['order_index'] = kp.order_index
            kp_data['depth_level'] = kp.depth_level
            export_data['knowledge_points'].append(kp_data)
            
            if include_multimedia:
                # 获取相关多媒体资源
                multimedia_resources = self.db.query(MultimediaResource).filter(
                    MultimediaResource.knowledge_point_id == kp.id
                ).all()
                
                for resource in multimedia_resources:
                    resource_data = {
                        'knowledge_point_id': resource.knowledge_point_id,
                        'filename': resource.filename,
                        'original_filename': resource.original_filename,
                        'file_format': resource.file_format,
                        'resource_type': resource.resource_type.value,
                        'title': resource.title,
                        'description': resource.description,
                        'duration_seconds': resource.duration_seconds,
                        'resolution': resource.resolution,
                        'quality_level': resource.quality_level,
                        'timestamps': resource.timestamps,
                        'captions': resource.captions,
                        'annotations': resource.annotations,
                        'learning_objectives': resource.learning_objectives,
                        'difficulty_level': resource.difficulty_level.value if resource.difficulty_level else None,
                        'bloom_level': resource.bloom_level.value if resource.bloom_level else None,
                        'alt_text': resource.alt_text,
                        'transcription': resource.transcription,
                        'copyright_info': resource.copyright_info,
                        'license_type': resource.license_type,
                        'attribution': resource.attribution
                    }
                    export_data['multimedia_resources'].append(resource_data)
            
            # 获取相关评估
            assessments = self.db.query(Assessment).filter(
                Assessment.knowledge_point_id == kp.id
            ).all()
            
            for assessment in assessments:
                assessment_data = {
                    'knowledge_point_id': assessment.knowledge_point_id,
                    'title': assessment.title,
                    'description': assessment.description,
                    'assessment_type': assessment.assessment_type.value,
                    'difficulty_level': assessment.difficulty_level.value if assessment.difficulty_level else None,
                    'bloom_level': assessment.bloom_level.value if assessment.bloom_level else None,
                    'competency_level': assessment.competency_level.value if assessment.competency_level else None,
                    'estimated_duration_minutes': assessment.estimated_duration_minutes,
                    'max_attempts': assessment.max_attempts,
                    'passing_score': assessment.passing_score,
                    'questions': assessment.questions,
                    'rubrics': assessment.rubrics,
                    'answer_key': assessment.answer_key,
                    'feedback_templates': assessment.feedback_templates
                }
                export_data['assessments'].append(assessment_data)
        
        return export_data
    
    def import_knowledge_domain(self, import_data: Dict[str, Any], 
                              user_id: Optional[int] = None) -> KnowledgeDomain:
        """导入知识领域数据"""
        # 创建或更新知识领域
        domain_data = import_data.get('domain', {})
        
        existing_domain = self.db.query(KnowledgeDomain).filter(
            KnowledgeDomain.domain_key == domain_data.get('domain_key')
        ).first()
        
        if existing_domain:
            # 更新现有领域
            for key, value in domain_data.items():
                if hasattr(existing_domain, key):
                    setattr(existing_domain, key, value)
            domain = existing_domain
        else:
            # 创建新领域
            domain = self.create_knowledge_domain(domain_data)
        
        # 导入知识点
        knowledge_points_map = {}  # 旧ID到新ID的映射
        
        for kp_data in import_data.get('knowledge_points', []):
            old_id = kp_data.pop('id', None)
            old_parent_id = kp_data.pop('parent_id', None)
            
            kp_data['domain_id'] = domain.id
            
            # 暂时设置parent_id为None，稍后更新
            kp_data['parent_id'] = None
            
            new_kp = self.create_knowledge_point(kp_data)
            
            if old_id:
                knowledge_points_map[old_id] = new_kp.id
        
        # 更新父子关系
        for kp_data in import_data.get('knowledge_points', []):
            old_id = kp_data.get('id')
            old_parent_id = kp_data.get('parent_id')
            
            if old_id and old_parent_id and old_parent_id in knowledge_points_map:
                new_kp_id = knowledge_points_map[old_id]
                new_parent_id = knowledge_points_map[old_parent_id]
                
                kp = self.db.query(EnhancedKnowledgePoint).filter(
                    EnhancedKnowledgePoint.id == new_kp_id
                ).first()
                
                if kp:
                    kp.parent_id = new_parent_id
        
        self.db.commit()
        
        return domain
    
    # ==================== 统计和分析 ====================
    
    def get_corpus_statistics(self) -> Dict[str, Any]:
        """获取语料库统计信息"""
        stats = {}
        
        # 知识领域统计
        stats['domains'] = {
            'total': self.db.query(KnowledgeDomain).filter(KnowledgeDomain.is_active == True).count(),
            'by_type': {}
        }
        
        # 知识点统计
        stats['knowledge_points'] = {
            'total': self.db.query(EnhancedKnowledgePoint).count(),
            'by_difficulty': {},
            'by_bloom_level': {},
            'by_domain': {}
        }
        
        # 按难度统计知识点
        for difficulty in DifficultyLevel:
            count = self.db.query(EnhancedKnowledgePoint).filter(
                EnhancedKnowledgePoint.difficulty_level == difficulty
            ).count()
            stats['knowledge_points']['by_difficulty'][difficulty.value] = count
        
        # 按布鲁姆层级统计知识点
        for bloom_level in BloomLevel:
            count = self.db.query(EnhancedKnowledgePoint).filter(
                EnhancedKnowledgePoint.bloom_level == bloom_level
            ).count()
            stats['knowledge_points']['by_bloom_level'][bloom_level.value] = count
        
        # 多媒体资源统计
        stats['multimedia_resources'] = {
            'total': self.db.query(MultimediaResource).count(),
            'by_type': {},
            'total_size_mb': 0
        }
        
        # 按类型统计多媒体资源
        for resource_type in MultimediaType:
            count = self.db.query(MultimediaResource).filter(
                MultimediaResource.resource_type == resource_type
            ).count()
            stats['multimedia_resources']['by_type'][resource_type.value] = count
        
        # 计算总文件大小
        total_size = self.db.query(func.sum(MultimediaResource.file_size)).scalar() or 0
        stats['multimedia_resources']['total_size_mb'] = round(total_size / (1024 * 1024), 2)
        
        # 评估统计
        stats['assessments'] = {
            'total': self.db.query(Assessment).filter(Assessment.is_active == True).count(),
            'by_type': {},
            'total_attempts': self.db.query(AssessmentAttempt).count()
        }
        
        # 按类型统计评估
        for assessment_type in AssessmentType:
            count = self.db.query(Assessment).filter(
                Assessment.assessment_type == assessment_type,
                Assessment.is_active == True
            ).count()
            stats['assessments']['by_type'][assessment_type.value] = count
        
        # 使用统计
        stats['usage'] = {
            'total_multimedia_views': self.db.query(MultimediaUsageLog).filter(
                MultimediaUsageLog.action_type == 'view'
            ).count(),
            'total_knowledge_interactions': self.db.query(EnhancedKnowledgeInteraction).count(),
            'active_users_last_30_days': self.db.query(EnhancedKnowledgeInteraction.user_id.distinct()).filter(
                EnhancedKnowledgeInteraction.created_at >= datetime.utcnow() - timedelta(days=30)
            ).count()
        }
        
        return stats
    
    def get_quality_metrics(self) -> Dict[str, Any]:
        """获取内容质量指标"""
        metrics = {}
        
        # 知识点质量
        avg_kp_quality = self.db.query(func.avg(EnhancedKnowledgePoint.quality_score)).scalar() or 0.0
        metrics['knowledge_points'] = {
            'average_quality_score': round(avg_kp_quality, 2),
            'reviewed_percentage': 0,
            'approved_percentage': 0
        }
        
        # 计算审核和批准比例
        total_kps = self.db.query(EnhancedKnowledgePoint).count()
        if total_kps > 0:
            reviewed_kps = self.db.query(EnhancedKnowledgePoint).filter(
                EnhancedKnowledgePoint.review_status.in_(['reviewed', 'approved'])
            ).count()
            approved_kps = self.db.query(EnhancedKnowledgePoint).filter(
                EnhancedKnowledgePoint.review_status == 'approved'
            ).count()
            
            metrics['knowledge_points']['reviewed_percentage'] = round(reviewed_kps / total_kps * 100, 2)
            metrics['knowledge_points']['approved_percentage'] = round(approved_kps / total_kps * 100, 2)
        
        # 多媒体资源质量
        avg_mr_quality = self.db.query(func.avg(MultimediaResource.quality_score)).scalar() or 0.0
        avg_mr_rating = self.db.query(func.avg(MultimediaResource.average_rating)).scalar() or 0.0
        
        metrics['multimedia_resources'] = {
            'average_quality_score': round(avg_mr_quality, 2),
            'average_user_rating': round(avg_mr_rating, 2),
            'processing_success_rate': 0
        }
        
        # 计算处理成功率
        total_resources = self.db.query(MultimediaResource).count()
        if total_resources > 0:
            completed_resources = self.db.query(MultimediaResource).filter(
                MultimediaResource.processing_status == 'completed'
            ).count()
            metrics['multimedia_resources']['processing_success_rate'] = round(
                completed_resources / total_resources * 100, 2
            )
        
        # 评估质量
        avg_assessment_quality = self.db.query(func.avg(Assessment.quality_score)).scalar() or 0.0
        avg_completion_rate = self.db.query(func.avg(Assessment.completion_rate)).scalar() or 0.0
        
        metrics['assessments'] = {
            'average_quality_score': round(avg_assessment_quality, 2),
            'average_completion_rate': round(avg_completion_rate, 2),
            'average_score': 0
        }
        
        # 计算平均分数
        avg_score = self.db.query(func.avg(AssessmentAttempt.score)).filter(
            AssessmentAttempt.completion_status == 'completed'
        ).scalar() or 0.0
        metrics['assessments']['average_score'] = round(avg_score, 2)
        
        return metrics
