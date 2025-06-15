"""
Subject Classification and Engineering Knowledge Module for Alethea Platform
Focuses on engineering subjects, especially electrical and electronic experiments
"""

import os
import json
import logging
import re
from datetime import datetime
from typing import Dict, Any, List, Optional, Union, Tuple
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Float, Table
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from src.models.user import Base, Subject

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define association tables for many-to-many relationships
knowledge_point_tag = Table(
    'knowledge_point_tag', 
    Base.metadata,
    Column('knowledge_point_id', Integer, ForeignKey('knowledge_points.id')),
    Column('tag_id', Integer, ForeignKey('tags.id'))
)

class Tag(Base):
    """Tag model for categorizing knowledge points"""
    __tablename__ = 'tags'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    category = Column(String(50))  # e.g., "component", "theory", "experiment"
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Tag {self.name}>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category
        }


class KnowledgePoint(Base):
    """Knowledge point model for storing subject-specific knowledge"""
    __tablename__ = 'knowledge_points'
    
    id = Column(Integer, primary_key=True)
    subject_id = Column(Integer, ForeignKey('subjects.id'))
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    difficulty_level = Column(Integer)  # 1-5, where 5 is most difficult
    importance_level = Column(Integer)  # 1-5, where 5 is most important
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tags = relationship('Tag', secondary=knowledge_point_tag, backref='knowledge_points')
    examples = relationship('Example', backref='knowledge_point')
    simulations = relationship('Simulation', backref='knowledge_point')
    
    def __repr__(self):
        return f"<KnowledgePoint {self.title}>"
    
    def to_dict(self, include_related=False):
        data = {
            'id': self.id,
            'subject_id': self.subject_id,
            'title': self.title,
            'content': self.content,
            'difficulty_level': self.difficulty_level,
            'importance_level': self.importance_level,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'tags': [tag.name for tag in self.tags]
        }
        
        if include_related:
            data['examples'] = [example.to_dict() for example in self.examples]
            data['simulations'] = [simulation.to_dict() for simulation in self.simulations]
        
        return data


class Example(Base):
    """Example model for storing practical examples of knowledge points"""
    __tablename__ = 'examples'
    
    id = Column(Integer, primary_key=True)
    knowledge_point_id = Column(Integer, ForeignKey('knowledge_points.id'))
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    code = Column(Text)  # For code examples or formulas
    image_path = Column(String(255))  # Path to example image
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Example {self.title}>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'knowledge_point_id': self.knowledge_point_id,
            'title': self.title,
            'description': self.description,
            'code': self.code,
            'image_path': self.image_path,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Component(Base):
    """Electronic component model for simulations"""
    __tablename__ = 'components'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    type = Column(String(50), nullable=False)  # e.g., "resistor", "capacitor", "transistor"
    symbol = Column(String(100))  # Path to component symbol image
    description = Column(Text)
    properties = Column(Text)  # JSON string of component properties
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    simulation_components = relationship('SimulationComponent', backref='component')
    
    def __repr__(self):
        return f"<Component {self.name}>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'symbol': self.symbol,
            'description': self.description,
            'properties': json.loads(self.properties) if self.properties else {},
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Simulation(Base):
    """Simulation model for electronic circuit simulations"""
    __tablename__ = 'simulations'
    
    id = Column(Integer, primary_key=True)
    knowledge_point_id = Column(Integer, ForeignKey('knowledge_points.id'))
    title = Column(String(200), nullable=False)
    description = Column(Text)
    circuit_json = Column(Text)  # JSON representation of the circuit
    thumbnail_path = Column(String(255))  # Path to simulation thumbnail
    is_public = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    components = relationship('SimulationComponent', backref='simulation')
    results = relationship('SimulationResult', backref='simulation')
    
    def __repr__(self):
        return f"<Simulation {self.title}>"
    
    def to_dict(self, include_results=False):
        data = {
            'id': self.id,
            'knowledge_point_id': self.knowledge_point_id,
            'title': self.title,
            'description': self.description,
            'circuit_json': json.loads(self.circuit_json) if self.circuit_json else {},
            'thumbnail_path': self.thumbnail_path,
            'is_public': self.is_public,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'components': [comp.to_dict() for comp in self.components]
        }
        
        if include_results:
            data['results'] = [result.to_dict() for result in self.results]
        
        return data


class SimulationComponent(Base):
    """Association model between simulations and components"""
    __tablename__ = 'simulation_components'
    
    id = Column(Integer, primary_key=True)
    simulation_id = Column(Integer, ForeignKey('simulations.id'))
    component_id = Column(Integer, ForeignKey('components.id'))
    position_x = Column(Float)  # X position in the circuit
    position_y = Column(Float)  # Y position in the circuit
    rotation = Column(Float, default=0)  # Rotation in degrees
    properties = Column(Text)  # JSON string of component instance properties
    
    def __repr__(self):
        return f"<SimulationComponent {self.id}>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'simulation_id': self.simulation_id,
            'component_id': self.component_id,
            'component_name': self.component.name if self.component else None,
            'component_type': self.component.type if self.component else None,
            'position_x': self.position_x,
            'position_y': self.position_y,
            'rotation': self.rotation,
            'properties': json.loads(self.properties) if self.properties else {}
        }


class SimulationResult(Base):
    """Model for storing simulation results"""
    __tablename__ = 'simulation_results'
    
    id = Column(Integer, primary_key=True)
    simulation_id = Column(Integer, ForeignKey('simulations.id'))
    result_type = Column(String(50))  # e.g., "voltage", "current", "frequency"
    data = Column(Text)  # JSON string of result data
    graph_path = Column(String(255))  # Path to result graph image
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<SimulationResult {self.id}>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'simulation_id': self.simulation_id,
            'result_type': self.result_type,
            'data': json.loads(self.data) if self.data else {},
            'graph_path': self.graph_path,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class KnowledgePointManager:
    """Manager class for knowledge point operations"""
    
    def __init__(self, db_instance):
        """Initialize knowledge point manager with database instance"""
        self.db = db_instance
    
    def create_knowledge_point(self, subject_id, title, content, difficulty_level=3, importance_level=3, tags=None):
        """Create a new knowledge point"""
        try:
            # Check if subject exists
            subject = self.db.session.query(Subject).filter_by(id=subject_id).first()
            if not subject:
                return False, "Subject not found"
            
            # Create knowledge point
            knowledge_point = KnowledgePoint(
                subject_id=subject_id,
                title=title,
                content=content,
                difficulty_level=difficulty_level,
                importance_level=importance_level
            )
            
            self.db.session.add(knowledge_point)
            
            # Add tags if provided
            if tags:
                for tag_name in tags:
                    # Get or create tag
                    tag = self.db.session.query(Tag).filter_by(name=tag_name).first()
                    if not tag:
                        tag = Tag(name=tag_name)
                        self.db.session.add(tag)
                    
                    knowledge_point.tags.append(tag)
            
            self.db.session.commit()
            
            return True, knowledge_point.id
            
        except Exception as e:
            self.db.session.rollback()
            logger.error(f"Error creating knowledge point: {str(e)}")
            return False, str(e)
    
    def get_knowledge_point(self, knowledge_point_id, include_related=False):
        """Get knowledge point by ID"""
        try:
            knowledge_point = self.db.session.query(KnowledgePoint).filter_by(id=knowledge_point_id).first()
            if not knowledge_point:
                return False, "Knowledge point not found"
            
            return True, knowledge_point.to_dict(include_related=include_related)
            
        except Exception as e:
            logger.error(f"Error getting knowledge point: {str(e)}")
            return False, str(e)
    
    def get_knowledge_points_by_subject(self, subject_id):
        """Get knowledge points for a specific subject"""
        try:
            knowledge_points = self.db.session.query(KnowledgePoint).filter_by(subject_id=subject_id).all()
            return True, [kp.to_dict() for kp in knowledge_points]
            
        except Exception as e:
            logger.error(f"Error getting knowledge points by subject: {str(e)}")
            return False, str(e)
    
    def search_knowledge_points(self, query, subject_id=None, tags=None):
        """Search knowledge points by query string, optionally filtered by subject and tags"""
        try:
            # Build base query
            base_query = self.db.session.query(KnowledgePoint)
            
            # Filter by subject if provided
            if subject_id:
                base_query = base_query.filter(KnowledgePoint.subject_id == subject_id)
            
            # Filter by search query in title or content
            if query:
                search_filter = (
                    KnowledgePoint.title.ilike(f"%{query}%") | 
                    KnowledgePoint.content.ilike(f"%{query}%")
                )
                base_query = base_query.filter(search_filter)
            
            # Filter by tags if provided
            if tags:
                for tag_name in tags:
                    tag = self.db.session.query(Tag).filter_by(name=tag_name).first()
                    if tag:
                        base_query = base_query.filter(KnowledgePoint.tags.contains(tag))
            
            # Execute query
            knowledge_points = base_query.all()
            
            return True, [kp.to_dict() for kp in knowledge_points]
            
        except Exception as e:
            logger.error(f"Error searching knowledge points: {str(e)}")
            return False, str(e)
    
    def add_example(self, knowledge_point_id, title, description, code=None, image_path=None):
        """Add an example to a knowledge point"""
        try:
            # Check if knowledge point exists
            knowledge_point = self.db.session.query(KnowledgePoint).filter_by(id=knowledge_point_id).first()
            if not knowledge_point:
                return False, "Knowledge point not found"
            
            # Create example
            example = Example(
                knowledge_point_id=knowledge_point_id,
                title=title,
                description=description,
                code=code,
                image_path=image_path
            )
            
            self.db.session.add(example)
            self.db.session.commit()
            
            return True, example.id
            
        except Exception as e:
            self.db.session.rollback()
            logger.error(f"Error adding example: {str(e)}")
            return False, str(e)


class TagManager:
    """Manager class for tag operations"""
    
    def __init__(self, db_instance):
        """Initialize tag manager with database instance"""
        self.db = db_instance
    
    def create_tag(self, name, category=None):
        """Create a new tag"""
        try:
            # Check if tag already exists
            existing = self.db.session.query(Tag).filter_by(name=name).first()
            if existing:
                return False, "Tag already exists"
            
            # Create tag
            tag = Tag(name=name, category=category)
            self.db.session.add(tag)
            self.db.session.commit()
            
            return True, tag.id
            
        except Exception as e:
            self.db.session.rollback()
            logger.error(f"Error creating tag: {str(e)}")
            return False, str(e)
    
    def get_tags_by_category(self, category):
        """Get tags by category"""
        try:
            tags = self.db.session.query(Tag).filter_by(category=category).all()
            return True, [tag.to_dict() for tag in tags]
            
        except Exception as e:
            logger.error(f"Error getting tags by category: {str(e)}")
            return False, str(e)
    
    def get_all_tags(self):
        """Get all tags"""
        try:
            tags = self.db.session.query(Tag).all()
            return True, [tag.to_dict() for tag in tags]
            
        except Exception as e:
            logger.error(f"Error getting all tags: {str(e)}")
            return False, str(e)


class ComponentManager:
    """Manager class for component operations"""
    
    def __init__(self, db_instance):
        """Initialize component manager with database instance"""
        self.db = db_instance
    
    def create_component(self, name, type, description=None, symbol=None, properties=None):
        """Create a new component"""
        try:
            # Check if component already exists
            existing = self.db.session.query(Component).filter_by(name=name, type=type).first()
            if existing:
                return False, "Component already exists"
            
            # Create component
            component = Component(
                name=name,
                type=type,
                description=description,
                symbol=symbol,
                properties=json.dumps(properties) if properties else None
            )
            
            self.db.session.add(component)
            self.db.session.commit()
            
            return True, component.id
            
        except Exception as e:
            self.db.session.rollback()
            logger.error(f"Error creating component: {str(e)}")
            return False, str(e)
    
    def get_component(self, component_id):
        """Get component by ID"""
        try:
            component = self.db.session.query(Component).filter_by(id=component_id).first()
            if not component:
                return False, "Component not found"
            
            return True, component.to_dict()
            
        except Exception as e:
            logger.error(f"Error getting component: {str(e)}")
            return False, str(e)
    
    def get_components_by_type(self, type):
        """Get components by type"""
        try:
            components = self.db.session.query(Component).filter_by(type=type).all()
            return True, [component.to_dict() for component in components]
            
        except Exception as e:
            logger.error(f"Error getting components by type: {str(e)}")
            return False, str(e)
    
    def get_all_components(self):
        """Get all components"""
        try:
            components = self.db.session.query(Component).all()
            return True, [component.to_dict() for component in components]
            
        except Exception as e:
            logger.error(f"Error getting all components: {str(e)}")
            return False, str(e)


class SimulationManager:
    """Manager class for simulation operations"""
    
    def __init__(self, db_instance):
        """Initialize simulation manager with database instance"""
        self.db = db_instance
    
    def create_simulation(self, title, knowledge_point_id, description=None, circuit_json=None, created_by=None, is_public=True):
        """Create a new simulation"""
        try:
            # Check if knowledge point exists
            if knowledge_point_id:
                knowledge_point = self.db.session.query(KnowledgePoint).filter_by(id=knowledge_point_id).first()
                if not knowledge_point:
                    return False, "Knowledge point not found"
            
            # Create simulation
            simulation = Simulation(
                title=title,
                knowledge_point_id=knowledge_point_id,
                description=description,
                circuit_json=json.dumps(circuit_json) if circuit_json else None,
                created_by=created_by,
                is_public=is_public
            )
            
            self.db.session.add(simulation)
            self.db.session.commit()
            
            return True, simulation.id
            
        except Exception as e:
            self.db.session.rollback()
            logger.error(f"Error creating simulation: {str(e)}")
            return False, str(e)
    
    def get_simulation(self, simulation_id, include_results=False):
        """Get simulation by ID"""
        try:
            simulation = self.db.session.query(Simulation).filter_by(id=simulation_id).first()
            if not simulation:
                return False, "Simulation not found"
            
            return True, simulation.to_dict(include_results=include_results)
            
        except Exception as e:
            logger.error(f"Error getting simulation: {str(e)}")
            return False, str(e)
    
    def get_simulations_by_knowledge_point(self, knowledge_point_id):
        """Get simulations for a specific knowledge point"""
        try:
            simulations = self.db.session.query(Simulation).filter_by(knowledge_point_id=knowledge_point_id).all()
            return True, [simulation.to_dict() for simulation in simulations]
            
        except Exception as e:
            logger.error(f"Error getting simulations by knowledge point: {str(e)}")
            return False, str(e)
    
    def get_simulations_by_user(self, user_id):
        """Get simulations created by a specific user"""
        try:
            simulations = self.db.session.query(Simulation).filter_by(created_by=user_id).all()
            return True, [simulation.to_dict() for simulation in simulations]
            
        except Exception as e:
            logger.error(f"Error getting simulations by user: {str(e)}")
            return False, str(e)
    
    def add_component_to_simulation(self, simulation_id, component_id, position_x, position_y, rotation=0, properties=None):
        """Add a component to a simulation"""
        try:
            # Check if simulation exists
            simulation = self.db.session.query(Simulation).filter_by(id=simulation_id).first()
            if not simulation:
                return False, "Simulation not found"
            
            # Check if component exists
            component = self.db.session.query(Component).filter_by(id=component_id).first()
            if not component:
                return False, "Component not found"
            
            # Create simulation component
            sim_component = SimulationComponent(
                simulation_id=simulation_id,
                component_id=component_id,
                position_x=position_x,
                position_y=position_y,
                rotation=rotation,
                properties=json.dumps(properties) if properties else None
            )
            
            self.db.session.add(sim_component)
            self.db.session.commit()
            
            return True, sim_component.id
            
        except Exception as e:
            self.db.session.rollback()
            logger.error(f"Error adding component to simulation: {str(e)}")
            return False, str(e)
    
    def save_simulation_result(self, simulation_id, result_type, data, graph_path=None):
        """Save simulation result"""
        try:
            # Check if simulation exists
            simulation = self.db.session.query(Simulation).filter_by(id=simulation_id).first()
            if not simulation:
                return False, "Simulation not found"
            
            # Create simulation result
            result = SimulationResult(
                simulation_id=simulation_id,
                result_type=result_type,
                data=json.dumps(data) if data else None,
                graph_path=graph_path
            )
            
            self.db.session.add(result)
            self.db.session.commit()
            
            return True, result.id
            
        except Exception as e:
            self.db.session.rollback()
            logger.error(f"Error saving simulation result: {str(e)}")
            return False, str(e)


# Initialize managers
def initialize_subject_system(app, db_instance):
    """Initialize subject classification system"""
    # Create managers
    knowledge_point_manager = KnowledgePointManager(db_instance)
    tag_manager = TagManager(db_instance)
    component_manager = ComponentManager(db_instance)
    simulation_manager = SimulationManager(db_instance)
    
    # Create default tags if they don't exist
    _create_default_tags(tag_manager)
    
    # Create default components if they don't exist
    _create_default_components(component_manager)
    
    # Create default knowledge points if they don't exist
    _create_default_knowledge_points(knowledge_point_manager, tag_manager)
    
    return {
        'knowledge_point_manager': knowledge_point_manager,
        'tag_manager': tag_manager,
        'component_manager': component_manager,
        'simulation_manager': simulation_manager
    }


def _create_default_tags(tag_manager):
    """Create default tags"""
    tags = [
        # Component categories
        {'name': '电阻', 'category': 'component'},
        {'name': '电容', 'category': 'component'},
        {'name': '电感', 'category': 'component'},
        {'name': '二极管', 'category': 'component'},
        {'name': '晶体管', 'category': 'component'},
        {'name': '运算放大器', 'category': 'component'},
        {'name': '逻辑门', 'category': 'component'},
        {'name': '微控制器', 'category': 'component'},
        
        # Theory categories
        {'name': '电路分析', 'category': 'theory'},
        {'name': '模拟电路', 'category': 'theory'},
        {'name': '数字电路', 'category': 'theory'},
        {'name': '信号处理', 'category': 'theory'},
        {'name': '控制系统', 'category': 'theory'},
        {'name': '电磁学', 'category': 'theory'},
        
        # Experiment categories
        {'name': '基础实验', 'category': 'experiment'},
        {'name': '电路测量', 'category': 'experiment'},
        {'name': '信号生成', 'category': 'experiment'},
        {'name': '放大器设计', 'category': 'experiment'},
        {'name': '滤波器设计', 'category': 'experiment'},
        {'name': '数字逻辑', 'category': 'experiment'},
        {'name': '微控制器编程', 'category': 'experiment'},
        {'name': '电源设计', 'category': 'experiment'}
    ]
    
    for tag_data in tags:
        tag_manager.create_tag(name=tag_data['name'], category=tag_data['category'])


def _create_default_components(component_manager):
    """Create default components"""
    components = [
        {
            'name': '电阻',
            'type': 'resistor',
            'description': '限制电流的基本元件',
            'symbol': '/static/components/resistor.svg',
            'properties': {
                'resistance': {'unit': 'Ω', 'default': 1000},
                'power': {'unit': 'W', 'default': 0.25},
                'tolerance': {'unit': '%', 'default': 5}
            }
        },
        {
            'name': '电容',
            'type': 'capacitor',
            'description': '储存电荷的基本元件',
            'symbol': '/static/components/capacitor.svg',
            'properties': {
                'capacitance': {'unit': 'F', 'default': 0.000001},
                'voltage': {'unit': 'V', 'default': 50},
                'type': {'options': ['ceramic', 'electrolytic', 'tantalum'], 'default': 'ceramic'}
            }
        },
        {
            'name': '电感',
            'type': 'inductor',
            'description': '储存磁能的基本元件',
            'symbol': '/static/components/inductor.svg',
            'properties': {
                'inductance': {'unit': 'H', 'default': 0.001},
                'current': {'unit': 'A', 'default': 1},
                'type': {'options': ['air core', 'iron core', 'ferrite core'], 'default': 'air core'}
            }
        },
        {
            'name': '二极管',
            'type': 'diode',
            'description': '单向导电的半导体元件',
            'symbol': '/static/components/diode.svg',
            'properties': {
                'forward_voltage': {'unit': 'V', 'default': 0.7},
                'max_current': {'unit': 'A', 'default': 1},
                'type': {'options': ['signal', 'rectifier', 'zener', 'LED'], 'default': 'signal'}
            }
        },
        {
            'name': 'NPN晶体管',
            'type': 'transistor',
            'description': 'NPN型双极性晶体管',
            'symbol': '/static/components/npn.svg',
            'properties': {
                'gain': {'unit': '', 'default': 100},
                'collector_current': {'unit': 'A', 'default': 0.1},
                'model': {'options': ['2N2222', 'BC547', 'TIP31'], 'default': '2N2222'}
            }
        },
        {
            'name': 'PNP晶体管',
            'type': 'transistor',
            'description': 'PNP型双极性晶体管',
            'symbol': '/static/components/pnp.svg',
            'properties': {
                'gain': {'unit': '', 'default': 100},
                'collector_current': {'unit': 'A', 'default': 0.1},
                'model': {'options': ['2N2907', 'BC557', 'TIP32'], 'default': '2N2907'}
            }
        },
        {
            'name': '运算放大器',
            'type': 'opamp',
            'description': '高增益电压放大器',
            'symbol': '/static/components/opamp.svg',
            'properties': {
                'gain': {'unit': '', 'default': 100000},
                'supply_voltage': {'unit': 'V', 'default': 15},
                'model': {'options': ['LM741', 'TL081', 'LM358'], 'default': 'LM741'}
            }
        },
        {
            'name': '电压源',
            'type': 'voltage_source',
            'description': '理想电压源',
            'symbol': '/static/components/voltage_source.svg',
            'properties': {
                'voltage': {'unit': 'V', 'default': 5},
                'type': {'options': ['DC', 'AC', 'pulse'], 'default': 'DC'},
                'frequency': {'unit': 'Hz', 'default': 1000, 'condition': {'type': ['AC', 'pulse']}}
            }
        },
        {
            'name': '电流源',
            'type': 'current_source',
            'description': '理想电流源',
            'symbol': '/static/components/current_source.svg',
            'properties': {
                'current': {'unit': 'A', 'default': 0.01},
                'type': {'options': ['DC', 'AC', 'pulse'], 'default': 'DC'},
                'frequency': {'unit': 'Hz', 'default': 1000, 'condition': {'type': ['AC', 'pulse']}}
            }
        },
        {
            'name': '开关',
            'type': 'switch',
            'description': '电路开关',
            'symbol': '/static/components/switch.svg',
            'properties': {
                'state': {'options': ['open', 'closed'], 'default': 'open'}
            }
        },
        {
            'name': '接地',
            'type': 'ground',
            'description': '电路接地点',
            'symbol': '/static/components/ground.svg',
            'properties': {}
        },
        {
            'name': '与门',
            'type': 'logic_gate',
            'description': '逻辑与门',
            'symbol': '/static/components/and_gate.svg',
            'properties': {
                'inputs': {'unit': '', 'default': 2, 'min': 2, 'max': 8},
                'family': {'options': ['TTL', 'CMOS'], 'default': 'TTL'}
            }
        },
        {
            'name': '或门',
            'type': 'logic_gate',
            'description': '逻辑或门',
            'symbol': '/static/components/or_gate.svg',
            'properties': {
                'inputs': {'unit': '', 'default': 2, 'min': 2, 'max': 8},
                'family': {'options': ['TTL', 'CMOS'], 'default': 'TTL'}
            }
        },
        {
            'name': '非门',
            'type': 'logic_gate',
            'description': '逻辑非门',
            'symbol': '/static/components/not_gate.svg',
            'properties': {
                'family': {'options': ['TTL', 'CMOS'], 'default': 'TTL'}
            }
        },
        {
            'name': '555定时器',
            'type': 'ic',
            'description': '经典的定时器集成电路',
            'symbol': '/static/components/555_timer.svg',
            'properties': {
                'mode': {'options': ['astable', 'monostable', 'bistable'], 'default': 'astable'}
            }
        }
    ]
    
    for comp_data in components:
        component_manager.create_component(
            name=comp_data['name'],
            type=comp_data['type'],
            description=comp_data['description'],
            symbol=comp_data['symbol'],
            properties=comp_data['properties']
        )


def _create_default_knowledge_points(knowledge_point_manager, tag_manager):
    """Create default knowledge points"""
    # First get subject ID for "电工电子实验"
    from src.models.user import Subject
    
    # This is just a placeholder - in a real implementation, we would query the database
    # to get the actual subject ID
    subject = Subject.query.filter_by(name='电工电子实验').first()
    if not subject:
        return
    
    subject_id = subject.id
    
    knowledge_points = [
        {
            'title': '欧姆定律',
            'content': '欧姆定律是电路分析的基础，表述为电流与电压成正比，与电阻成反比。数学表达式为 I = V / R，其中 I 是电流（单位：安培），V 是电压（单位：伏特），R 是电阻（单位：欧姆）。',
            'difficulty_level': 1,
            'importance_level': 5,
            'tags': ['电路分析', '基础实验']
        },
        {
            'title': '基尔霍夫电流定律（KCL）',
            'content': '基尔霍夫电流定律（KCL）指出，在任何节点上，流入的电流等于流出的电流。这是电路分析中的基本定律之一，基于电荷守恒原理。',
            'difficulty_level': 2,
            'importance_level': 5,
            'tags': ['电路分析', '基础实验']
        },
        {
            'title': '基尔霍夫电压定律（KVL）',
            'content': '基尔霍夫电压定律（KVL）指出，在任何闭合回路中，电压降的代数和等于零。这是电路分析中的基本定律之一，基于能量守恒原理。',
            'difficulty_level': 2,
            'importance_level': 5,
            'tags': ['电路分析', '基础实验']
        },
        {
            'title': 'RC电路时间常数',
            'content': 'RC电路由电阻和电容组成，其时间常数τ = RC，表示电容充电或放电到达最终值的63.2%所需的时间。这是分析瞬态响应的重要参数。',
            'difficulty_level': 3,
            'importance_level': 4,
            'tags': ['电路分析', '电容', '基础实验']
        },
        {
            'title': 'RL电路时间常数',
            'content': 'RL电路由电阻和电感组成，其时间常数τ = L/R，表示电感中电流达到最终值的63.2%所需的时间。这是分析瞬态响应的重要参数。',
            'difficulty_level': 3,
            'importance_level': 4,
            'tags': ['电路分析', '电感', '基础实验']
        },
        {
            'title': '二极管特性曲线测量',
            'content': '二极管特性曲线显示了二极管在不同电压下的电流响应。正向偏置时，超过阈值电压后电流迅速增加；反向偏置时，只有很小的漏电流，直到击穿电压。',
            'difficulty_level': 2,
            'importance_level': 4,
            'tags': ['二极管', '电路测量', '模拟电路']
        },
        {
            'title': '晶体管放大器设计',
            'content': '晶体管放大器利用晶体管的电流放大特性，将小信号放大为大信号。设计过程包括选择合适的偏置点、计算增益、确定输入输出阻抗等步骤。',
            'difficulty_level': 4,
            'importance_level': 5,
            'tags': ['晶体管', '放大器设计', '模拟电路']
        },
        {
            'title': '运算放大器反相放大器',
            'content': '反相放大器是运算放大器的基本应用电路之一，输出信号与输入信号相位相差180度。增益由反馈电阻和输入电阻的比值决定：Av = -Rf/Rin。',
            'difficulty_level': 3,
            'importance_level': 4,
            'tags': ['运算放大器', '放大器设计', '模拟电路']
        },
        {
            'title': '运算放大器同相放大器',
            'content': '同相放大器是运算放大器的基本应用电路之一，输出信号与输入信号同相位。增益由反馈电阻和接地电阻决定：Av = 1 + Rf/Rg。',
            'difficulty_level': 3,
            'importance_level': 4,
            'tags': ['运算放大器', '放大器设计', '模拟电路']
        },
        {
            'title': '有源低通滤波器设计',
            'content': '有源低通滤波器使用运算放大器和RC网络，可以通过信号的低频部分并衰减高频部分。截止频率由RC时间常数决定：fc = 1/(2πRC)。',
            'difficulty_level': 4,
            'importance_level': 4,
            'tags': ['运算放大器', '滤波器设计', '模拟电路']
        },
        {
            'title': '数字逻辑门电路实验',
            'content': '数字逻辑门是数字电路的基本单元，包括与门、或门、非门等。本实验通过测量不同输入组合下的输出，验证逻辑门的真值表和功能。',
            'difficulty_level': 2,
            'importance_level': 5,
            'tags': ['逻辑门', '数字逻辑', '数字电路']
        },
        {
            'title': '555定时器应用',
            'content': '555定时器是一种多功能集成电路，可用于产生精确的时间延迟或振荡。在多谐振荡器模式下，频率由外部RC网络决定。',
            'difficulty_level': 3,
            'importance_level': 4,
            'tags': ['信号生成', '模拟电路']
        },
        {
            'title': '示波器使用方法',
            'content': '示波器是观察电信号波形的重要仪器。使用方法包括设置时基、电压档位、触发条件等，以及测量频率、幅值、相位等参数。',
            'difficulty_level': 2,
            'importance_level': 5,
            'tags': ['电路测量', '基础实验']
        },
        {
            'title': '数字频率计使用方法',
            'content': '数字频率计用于精确测量信号频率。使用方法包括选择合适的量程、设置门控时间、连接信号源等，以及理解测量误差来源。',
            'difficulty_level': 2,
            'importance_level': 3,
            'tags': ['电路测量', '基础实验']
        },
        {
            'title': '函数信号发生器使用方法',
            'content': '函数信号发生器可产生各种波形的电信号，如正弦波、方波、三角波等。使用方法包括设置频率、幅值、偏置、调制等参数。',
            'difficulty_level': 2,
            'importance_level': 4,
            'tags': ['信号生成', '基础实验']
        }
    ]
    
    for kp_data in knowledge_points:
        knowledge_point_manager.create_knowledge_point(
            subject_id=subject_id,
            title=kp_data['title'],
            content=kp_data['content'],
            difficulty_level=kp_data['difficulty_level'],
            importance_level=kp_data['importance_level'],
            tags=kp_data['tags']
        )
