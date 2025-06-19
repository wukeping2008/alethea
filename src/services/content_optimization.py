"""
内容优化服务模块
提供AI内容生成的优化功能，包括缓存、质量验证、个性化等
"""

import os
import json
import hashlib
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import requests

logger = logging.getLogger(__name__)

@dataclass
class ContentCacheItem:
    """缓存项数据结构"""
    content: Dict[str, Any]
    timestamp: datetime
    provider: str
    quality_score: float
    user_id: Optional[int] = None

@dataclass
class UserProfile:
    """用户画像数据结构"""
    user_id: int
    interests: List[str]
    knowledge_level: str
    preferred_difficulty: str
    question_history: List[str]
    last_updated: datetime

class ContentCache:
    """智能内容缓存系统"""
    
    def __init__(self, cache_duration_hours: int = 24):
        self.cache = {}
        self.cache_duration = timedelta(hours=cache_duration_hours)
        self.max_cache_size = 1000
        self.hit_count = 0
        self.miss_count = 0
    
    def get_cache_key(self, question: str, answer: str, user_id: Optional[int] = None) -> str:
        """生成缓存键"""
        content = f"{question}_{answer}"
        if user_id:
            content += f"_user_{user_id}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def get_cached_content(self, question: str, answer: str, user_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """获取缓存内容"""
        key = self.get_cache_key(question, answer, user_id)
        
        if key in self.cache:
            cached_item = self.cache[key]
            
            # 检查缓存是否过期
            if datetime.now() - cached_item.timestamp < self.cache_duration:
                self.hit_count += 1
                logger.info(f"Cache hit for key: {key[:8]}...")
                return cached_item.content
            else:
                # 删除过期缓存
                del self.cache[key]
                logger.info(f"Cache expired for key: {key[:8]}...")
        
        self.miss_count += 1
        logger.info(f"Cache miss for key: {key[:8]}...")
        return None
    
    def cache_content(self, question: str, answer: str, content: Dict[str, Any], 
                     provider: str, quality_score: float, user_id: Optional[int] = None):
        """缓存内容"""
        key = self.get_cache_key(question, answer, user_id)
        
        # 如果缓存已满，删除最旧的项
        if len(self.cache) >= self.max_cache_size:
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k].timestamp)
            del self.cache[oldest_key]
            logger.info(f"Cache full, removed oldest item: {oldest_key[:8]}...")
        
        self.cache[key] = ContentCacheItem(
            content=content,
            timestamp=datetime.now(),
            provider=provider,
            quality_score=quality_score,
            user_id=user_id
        )
        
        logger.info(f"Cached content for key: {key[:8]}... (quality: {quality_score})")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        total_requests = self.hit_count + self.miss_count
        hit_rate = (self.hit_count / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'cache_size': len(self.cache),
            'hit_count': self.hit_count,
            'miss_count': self.miss_count,
            'hit_rate': round(hit_rate, 2),
            'max_cache_size': self.max_cache_size
        }
    
    def clear_cache(self):
        """清空缓存"""
        self.cache.clear()
        self.hit_count = 0
        self.miss_count = 0
        logger.info("Cache cleared")

class ContentQualityValidator:
    """内容质量验证器"""
    
    def __init__(self):
        self.min_quality_score = 70
        self.validation_rules = {
            'knowledge_points': {
                'min_count': 3,
                'max_count': 6,
                'min_description_length': 10,
                'required_fields': ['title', 'description']
            },
            'experiments': {
                'min_count': 3,
                'max_count': 6,
                'required_fields': ['title', 'description', 'type'],
                'optional_fields': ['equipment', 'steps', 'simulation_url']
            },
            'simulation': {
                'required_fields': ['title', 'type', 'description'],
                'optional_fields': ['parameters', 'outputs', 'third_party_platform']
            }
        }
    
    def validate_content(self, content: Dict[str, Any]) -> Tuple[bool, float, List[str]]:
        """
        验证内容质量
        返回: (是否通过, 质量分数, 问题列表)
        """
        score = 0
        max_score = 100
        issues = []
        
        # 验证知识点
        if 'knowledge_points' in content:
            kp_score, kp_issues = self._validate_knowledge_points(content['knowledge_points'])
            score += kp_score
            issues.extend(kp_issues)
        else:
            issues.append("缺少知识点内容")
        
        # 验证实验
        if 'experiments' in content:
            exp_score, exp_issues = self._validate_experiments(content['experiments'])
            score += exp_score
            issues.extend(exp_issues)
        else:
            issues.append("缺少实验内容")
        
        # 验证仿真
        if 'simulation' in content:
            sim_score, sim_issues = self._validate_simulation(content['simulation'])
            score += sim_score
            issues.extend(sim_issues)
        else:
            issues.append("缺少仿真内容")
        
        # 验证整体结构
        structure_score = self._validate_structure(content)
        score += structure_score
        
        is_valid = score >= self.min_quality_score
        
        logger.info(f"Content validation: score={score}/{max_score}, valid={is_valid}")
        if issues:
            logger.warning(f"Validation issues: {issues}")
        
        return is_valid, score, issues
    
    def _validate_knowledge_points(self, knowledge_points: List[Dict]) -> Tuple[float, List[str]]:
        """验证知识点"""
        score = 0
        issues = []
        rules = self.validation_rules['knowledge_points']
        
        # 检查数量
        count = len(knowledge_points)
        if count < rules['min_count']:
            issues.append(f"知识点数量不足: {count} < {rules['min_count']}")
        elif count > rules['max_count']:
            issues.append(f"知识点数量过多: {count} > {rules['max_count']}")
        else:
            score += 25
        
        # 检查每个知识点的质量
        valid_points = 0
        for i, kp in enumerate(knowledge_points):
            point_valid = True
            
            # 检查必需字段
            for field in rules['required_fields']:
                if field not in kp or not kp[field]:
                    issues.append(f"知识点{i+1}缺少{field}字段")
                    point_valid = False
            
            # 检查描述长度
            if 'description' in kp and len(kp['description']) < rules['min_description_length']:
                issues.append(f"知识点{i+1}描述过短")
                point_valid = False
            
            if point_valid:
                valid_points += 1
        
        # 根据有效知识点比例计算分数
        if knowledge_points:
            score += (valid_points / len(knowledge_points)) * 25
        
        return score, issues
    
    def _validate_experiments(self, experiments: List[Dict]) -> Tuple[float, List[str]]:
        """验证实验"""
        score = 0
        issues = []
        rules = self.validation_rules['experiments']
        
        # 检查数量
        count = len(experiments)
        if count < rules['min_count']:
            issues.append(f"实验数量不足: {count} < {rules['min_count']}")
        elif count > rules['max_count']:
            issues.append(f"实验数量过多: {count} > {rules['max_count']}")
        else:
            score += 25
        
        # 检查每个实验的质量
        valid_experiments = 0
        for i, exp in enumerate(experiments):
            exp_valid = True
            
            # 检查必需字段
            for field in rules['required_fields']:
                if field not in exp or not exp[field]:
                    issues.append(f"实验{i+1}缺少{field}字段")
                    exp_valid = False
            
            # 检查仿真URL有效性
            if 'simulation_url' in exp and exp['simulation_url']:
                if not self._validate_url(exp['simulation_url']):
                    issues.append(f"实验{i+1}仿真URL无效")
            
            if exp_valid:
                valid_experiments += 1
        
        # 根据有效实验比例计算分数
        if experiments:
            score += (valid_experiments / len(experiments)) * 25
        
        return score, issues
    
    def _validate_simulation(self, simulation: Dict) -> Tuple[float, List[str]]:
        """验证仿真"""
        score = 0
        issues = []
        rules = self.validation_rules['simulation']
        
        # 检查必需字段
        missing_fields = []
        for field in rules['required_fields']:
            if field not in simulation or not simulation[field]:
                missing_fields.append(field)
        
        if missing_fields:
            issues.append(f"仿真缺少必需字段: {missing_fields}")
        else:
            score += 25
        
        # 检查第三方平台URL
        if 'platform_url' in simulation and simulation['platform_url']:
            if not self._validate_url(simulation['platform_url']):
                issues.append("仿真平台URL无效")
            else:
                score += 10
        
        # 检查参数配置
        if 'parameters' in simulation and isinstance(simulation['parameters'], list):
            if len(simulation['parameters']) > 0:
                score += 10
        
        # 检查输出配置
        if 'outputs' in simulation and isinstance(simulation['outputs'], list):
            if len(simulation['outputs']) > 0:
                score += 5
        
        return score, issues
    
    def _validate_structure(self, content: Dict) -> float:
        """验证整体结构"""
        score = 0
        
        # 检查是否有success标志
        if content.get('success', False):
            score += 5
        
        # 检查是否有生成来源标识
        if 'generated_by' in content:
            score += 5
        
        return score
    
    def _validate_url(self, url: str) -> bool:
        """验证URL有效性"""
        try:
            # 简单的URL格式检查
            if not url.startswith(('http://', 'https://')):
                return False
            
            # 可以添加更复杂的URL验证逻辑
            # 比如实际请求检查URL是否可访问
            return True
        except Exception:
            return False

class UserProfileManager:
    """用户画像管理器"""
    
    def __init__(self):
        self.profiles = {}
        self.interest_keywords = {
            'electronics': ['电路', '电子', '电压', '电流', '电阻', '电容', '晶体管', '运放'],
            'physics': ['物理', '力学', '热力学', '光学', '量子', '波动', '能量'],
            'mathematics': ['数学', '函数', '微积分', '线性代数', '概率', '统计'],
            'chemistry': ['化学', '分子', '原子', '反应', '催化', '有机', '无机'],
            'computer_science': ['编程', '算法', '数据结构', '软件', '计算机', '代码'],
            'biology': ['生物', '细胞', '基因', 'DNA', '蛋白质', '生态', '进化'],
            'control': ['控制', 'PID', '系统', '反馈', '自动化', '调节'],
            'ai': ['人工智能', '机器学习', '深度学习', '神经网络', 'AI']
        }
    
    def get_user_profile(self, user_id: int) -> Optional[UserProfile]:
        """获取用户画像"""
        return self.profiles.get(user_id)
    
    def update_user_profile(self, user_id: int, question: str, answer: str):
        """更新用户画像"""
        if user_id not in self.profiles:
            self.profiles[user_id] = UserProfile(
                user_id=user_id,
                interests=[],
                knowledge_level='beginner',
                preferred_difficulty='medium',
                question_history=[],
                last_updated=datetime.now()
            )
        
        profile = self.profiles[user_id]
        
        # 更新问题历史
        profile.question_history.append(question)
        if len(profile.question_history) > 50:  # 保留最近50个问题
            profile.question_history = profile.question_history[-50:]
        
        # 分析兴趣领域
        interests = self._analyze_interests(profile.question_history)
        profile.interests = interests
        
        # 分析知识水平
        profile.knowledge_level = self._analyze_knowledge_level(profile.question_history)
        
        # 更新时间戳
        profile.last_updated = datetime.now()
        
        logger.info(f"Updated profile for user {user_id}: interests={interests}, level={profile.knowledge_level}")
    
    def _analyze_interests(self, question_history: List[str]) -> List[str]:
        """分析用户兴趣领域"""
        interest_scores = {}
        
        for domain, keywords in self.interest_keywords.items():
            score = 0
            for question in question_history:
                question_lower = question.lower()
                for keyword in keywords:
                    if keyword in question_lower:
                        score += 1
            interest_scores[domain] = score
        
        # 返回得分最高的前3个领域
        sorted_interests = sorted(interest_scores.items(), key=lambda x: x[1], reverse=True)
        return [domain for domain, score in sorted_interests[:3] if score > 0]
    
    def _analyze_knowledge_level(self, question_history: List[str]) -> str:
        """分析用户知识水平"""
        if len(question_history) < 5:
            return 'beginner'
        
        # 简单的启发式规则
        advanced_keywords = ['高级', '复杂', '深入', '原理', '推导', '证明', '优化']
        intermediate_keywords = ['应用', '设计', '分析', '计算', '实现']
        beginner_keywords = ['什么是', '如何', '基础', '入门', '简单']
        
        advanced_count = sum(1 for q in question_history for kw in advanced_keywords if kw in q)
        intermediate_count = sum(1 for q in question_history for kw in intermediate_keywords if kw in q)
        beginner_count = sum(1 for q in question_history for kw in beginner_keywords if kw in q)
        
        total_questions = len(question_history)
        
        if advanced_count / total_questions > 0.3:
            return 'advanced'
        elif intermediate_count / total_questions > 0.4:
            return 'intermediate'
        else:
            return 'beginner'
    
    def get_personalized_context(self, user_id: int) -> str:
        """获取个性化上下文"""
        profile = self.get_user_profile(user_id)
        if not profile:
            return ""
        
        context_parts = []
        
        if profile.interests:
            context_parts.append(f"用户兴趣领域: {', '.join(profile.interests)}")
        
        context_parts.append(f"用户知识水平: {profile.knowledge_level}")
        context_parts.append(f"推荐难度: {profile.preferred_difficulty}")
        
        # 分析最近的问题趋势
        if len(profile.question_history) >= 3:
            recent_questions = profile.question_history[-3:]
            context_parts.append(f"最近关注: {self._extract_recent_topics(recent_questions)}")
        
        return "\n".join(context_parts)
    
    def _extract_recent_topics(self, recent_questions: List[str]) -> str:
        """提取最近关注的话题"""
        # 简单的关键词提取
        all_text = " ".join(recent_questions).lower()
        
        # 提取高频词汇
        words = all_text.split()
        word_freq = {}
        for word in words:
            if len(word) > 2 and word not in ['什么', '如何', '为什么', '怎么', '请问']:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # 返回频率最高的3个词
        top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:3]
        return ", ".join([word for word, freq in top_words])

class MultimediaContentEnhancer:
    """多媒体内容增强器"""
    
    def __init__(self):
        self.domain_enhancers = {
            'electronics': self._enhance_electronics_content,
            'physics': self._enhance_physics_content,
            'mathematics': self._enhance_mathematics_content,
            'chemistry': self._enhance_chemistry_content,
            'computer_science': self._enhance_cs_content
        }
    
    def enhance_content(self, content: Dict[str, Any], domain: str) -> Dict[str, Any]:
        """增强内容的多媒体元素"""
        if domain in self.domain_enhancers:
            enhanced_content = self.domain_enhancers[domain](content.copy())
            logger.info(f"Enhanced content for domain: {domain}")
            return enhanced_content
        
        return content
    
    def _enhance_electronics_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """增强电子学内容"""
        # 添加电路图配置
        content['circuit_diagrams'] = {
            'enabled': True,
            'components': ['resistor', 'capacitor', 'inductor', 'voltage_source'],
            'simulation_tools': ['CircuitJS', 'LTSpice', 'Multisim']
        }
        
        # 添加仿真参数
        if 'simulation' in content:
            content['simulation']['enhanced_parameters'] = [
                {'name': '电压', 'type': 'slider', 'min': 0, 'max': 12, 'default': 5, 'unit': 'V'},
                {'name': '频率', 'type': 'slider', 'min': 1, 'max': 1000, 'default': 100, 'unit': 'Hz'},
                {'name': '电阻', 'type': 'slider', 'min': 100, 'max': 10000, 'default': 1000, 'unit': 'Ω'}
            ]
        
        return content
    
    def _enhance_physics_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """增强物理学内容"""
        # 添加物理仿真配置
        content['physics_simulations'] = {
            'enabled': True,
            'types': ['mechanics', 'waves', 'thermodynamics', 'electromagnetism'],
            'visualization_tools': ['PhET', 'Algodoo', 'Interactive Physics']
        }
        
        # 添加公式渲染
        content['formula_rendering'] = {
            'enabled': True,
            'engine': 'MathJax',
            'common_formulas': ['F=ma', 'E=mc²', 'v=fλ', 'PV=nRT']
        }
        
        return content
    
    def _enhance_mathematics_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """增强数学内容"""
        # 添加图形绘制配置
        content['interactive_plots'] = {
            'enabled': True,
            'plot_types': ['function', 'parametric', 'polar', '3d'],
            'tools': ['Desmos', 'GeoGebra', 'Wolfram Alpha']
        }
        
        # 添加数学符号支持
        content['math_symbols'] = {
            'enabled': True,
            'categories': ['calculus', 'algebra', 'geometry', 'statistics']
        }
        
        return content
    
    def _enhance_chemistry_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """增强化学内容"""
        # 添加分子模型配置
        content['molecular_models'] = {
            'enabled': True,
            'viewers': ['MolView', 'ChemSketch', 'Avogadro'],
            'formats': ['2D', '3D', 'ball_and_stick', 'space_filling']
        }
        
        # 添加反应动画
        content['reaction_animations'] = {
            'enabled': True,
            'types': ['acid_base', 'redox', 'organic', 'equilibrium']
        }
        
        return content
    
    def _enhance_cs_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """增强计算机科学内容"""
        # 添加代码示例
        content['code_examples'] = {
            'enabled': True,
            'languages': ['python', 'javascript', 'java', 'c++'],
            'interactive_editors': ['CodePen', 'JSFiddle', 'Repl.it']
        }
        
        # 添加算法可视化
        content['algorithm_visualization'] = {
            'enabled': True,
            'types': ['sorting', 'searching', 'graph', 'tree'],
            'tools': ['VisuAlgo', 'Algorithm Visualizer']
        }
        
        return content

class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self.metrics = {
            'response_times': [],
            'success_rates': {},
            'quality_scores': [],
            'cache_performance': {},
            'user_satisfaction': []
        }
        self.start_time = datetime.now()
    
    def log_generation_time(self, start_time: datetime, end_time: datetime, 
                          provider: str, success: bool, quality_score: float = 0):
        """记录生成时间"""
        duration = (end_time - start_time).total_seconds()
        
        self.metrics['response_times'].append({
            'duration': duration,
            'provider': provider,
            'success': success,
            'quality_score': quality_score,
            'timestamp': end_time
        })
        
        # 更新成功率统计
        if provider not in self.metrics['success_rates']:
            self.metrics['success_rates'][provider] = {'success': 0, 'total': 0}
        
        self.metrics['success_rates'][provider]['total'] += 1
        if success:
            self.metrics['success_rates'][provider]['success'] += 1
        
        # 记录质量分数
        if quality_score > 0:
            self.metrics['quality_scores'].append({
                'score': quality_score,
                'provider': provider,
                'timestamp': end_time
            })
        
        logger.info(f"Performance logged: {provider}, {duration:.2f}s, success={success}, quality={quality_score}")
    
    def log_cache_performance(self, cache_stats: Dict[str, Any]):
        """记录缓存性能"""
        self.metrics['cache_performance'] = {
            **cache_stats,
            'timestamp': datetime.now()
        }
    
    def log_user_satisfaction(self, user_id: int, rating: int, feedback: str = ""):
        """记录用户满意度"""
        self.metrics['user_satisfaction'].append({
            'user_id': user_id,
            'rating': rating,
            'feedback': feedback,
            'timestamp': datetime.now()
        })
    
    def get_performance_report(self) -> Dict[str, Any]:
        """生成性能报告"""
        report = {
            'monitoring_duration': (datetime.now() - self.start_time).total_seconds() / 3600,  # 小时
            'total_requests': len(self.metrics['response_times']),
            'average_response_time': 0,
            'provider_performance': {},
            'quality_analysis': {},
            'cache_efficiency': self.metrics['cache_performance'],
            'user_satisfaction_avg': 0
        }
        
        # 计算平均响应时间
        if self.metrics['response_times']:
            total_time = sum(item['duration'] for item in self.metrics['response_times'])
            report['average_response_time'] = total_time / len(self.metrics['response_times'])
        
        # 分析提供商性能
        for provider, stats in self.metrics['success_rates'].items():
            success_rate = (stats['success'] / stats['total'] * 100) if stats['total'] > 0 else 0
            
            # 计算该提供商的平均响应时间
            provider_times = [item['duration'] for item in self.metrics['response_times'] 
                            if item['provider'] == provider]
            avg_time = sum(provider_times) / len(provider_times) if provider_times else 0
            
            report['provider_performance'][provider] = {
                'success_rate': round(success_rate, 2),
                'total_requests': stats['total'],
                'average_response_time': round(avg_time, 2)
            }
        
        # 分析质量分数
        if self.metrics['quality_scores']:
            scores = [item['score'] for item in self.metrics['quality_scores']]
            report['quality_analysis'] = {
                'average_score': round(sum(scores) / len(scores), 2),
                'min_score': min(scores),
                'max_score': max(scores),
                'total_evaluations': len(scores)
            }
        
        # 计算用户满意度
        if self.metrics['user_satisfaction']:
            ratings = [item['rating'] for item in self.metrics['user_satisfaction']]
            report['user_satisfaction_avg'] = round(sum(ratings) / len(ratings), 2)
        
        return report
    
    def get_optimization_suggestions(self) -> List[str]:
        """生成优化建议"""
        suggestions = []
        report = self.get_performance_report()
        
        # 响应时间建议
        if report['average_response_time'] > 5:
            suggestions.append("平均响应时间较长，建议优化AI模型选择或增加缓存")
        
        # 成功率建议
        for provider, stats in report['provider_performance'].items():
            if stats['success_rate'] < 90:
                suggestions.append(f"{provider}提供商成功率较低({stats['success_rate']}%)，建议检查配置")
        
        # 质量分数建议
        if 'quality_analysis' in report and report['quality_analysis']['average_score'] < 75:
            suggestions.append("内容质量分数较低，建议优化提示词或验证规则")
        
        # 缓存效率建议
        cache_stats = report.get('cache_efficiency', {})
        if cache_stats.get('hit_rate', 0) < 30:
            suggestions.append("缓存命中率较低，建议调整缓存策略或增加缓存时间")
        
        return suggestions

# 全局实例
content_cache = ContentCache()
quality_validator = ContentQualityValidator()
user_profile_manager = UserProfileManager()
multimedia_enhancer = MultimediaContentEnhancer()
performance_monitor = PerformanceMonitor()

def get_optimization_services():
    """获取所有优化服务实例"""
    return {
        'cache': content_cache,
        'validator': quality_validator,
        'profile_manager': user_profile_manager,
        'multimedia_enhancer': multimedia_enhancer,
        'performance_monitor': performance_monitor
    }
