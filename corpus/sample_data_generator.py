#!/usr/bin/env python3
"""
语料库示例数据生成器
用于创建电工电子学科的示例知识点、多媒体资源和评估数据
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any

def generate_electrical_engineering_domain() -> Dict[str, Any]:
    """生成电工电子工程领域数据"""
    return {
        'domain_key': 'electrical_engineering',
        'name': '电工电子工程',
        'description': '电工电子技术相关知识体系，包括基础概念、电路分析、电子技术和控制系统',
        'subdirectory': 'electrical_engineering',
        'difficulty_levels': ['beginner', 'intermediate', 'advanced'],
        'assessment_types': ['theoretical', 'practical', 'simulation'],
        'metadata': {
            'version': '1.0.0',
            'created_by': 'system',
            'language': 'zh-CN',
            'target_audience': ['undergraduate', 'graduate', 'professional'],
            'prerequisites': ['mathematics', 'physics']
        }
    }

def generate_basic_concepts_knowledge_points() -> List[Dict[str, Any]]:
    """生成基础概念知识点"""
    knowledge_points = [
        {
            'title': '欧姆定律',
            'description': '描述电压、电流和电阻之间关系的基本定律',
            'difficulty_level': 'beginner',
            'bloom_level': 'understand',
            'estimated_duration_minutes': 45,
            'learning_objectives': [
                '理解欧姆定律的基本概念',
                '掌握欧姆定律的数学表达式',
                '能够应用欧姆定律解决简单电路问题',
                '理解电阻、电压、电流的关系'
            ],
            'prerequisites': ['基本数学运算', '电路基础概念'],
            'key_concepts': [
                '电压 (Voltage)',
                '电流 (Current)', 
                '电阻 (Resistance)',
                '线性关系',
                '比例常数'
            ],
            'formulas': [
                {
                    'name': '欧姆定律基本形式',
                    'expression': 'V = I × R',
                    'variables': {
                        'V': '电压 (伏特)',
                        'I': '电流 (安培)',
                        'R': '电阻 (欧姆)'
                    },
                    'description': '电压等于电流与电阻的乘积'
                },
                {
                    'name': '电流计算',
                    'expression': 'I = V / R',
                    'description': '已知电压和电阻，计算电流'
                },
                {
                    'name': '电阻计算',
                    'expression': 'R = V / I',
                    'description': '已知电压和电流，计算电阻'
                }
            ],
            'examples': [
                {
                    'title': '基础计算示例',
                    'problem': '一个电阻器的阻值为100Ω，通过的电流为0.5A，求电阻器两端的电压。',
                    'solution': '根据欧姆定律：V = I × R = 0.5A × 100Ω = 50V',
                    'explanation': '直接应用欧姆定律的基本形式进行计算'
                },
                {
                    'title': 'LED电路设计',
                    'problem': '设计一个LED驱动电路，LED正向电压3.3V，工作电流20mA，电源电压5V，求限流电阻。',
                    'solution': '限流电阻上的电压：5V - 3.3V = 1.7V\n限流电阻：R = 1.7V / 0.02A = 85Ω',
                    'explanation': '实际电路设计中的欧姆定律应用'
                }
            ],
            'applications': [
                '电路分析与设计',
                '电子设备故障诊断',
                '电力系统计算',
                '传感器电路设计',
                '功率计算'
            ],
            'content_modules': {
                'theory': {
                    'sections': [
                        {
                            'title': '历史背景',
                            'content': '欧姆定律由德国物理学家格奥尔格·西蒙·欧姆在1827年提出，是电学的基本定律之一。'
                        },
                        {
                            'title': '物理意义',
                            'content': '欧姆定律揭示了导体中电流与电压成正比，与电阻成反比的关系。'
                        },
                        {
                            'title': '适用条件',
                            'content': '欧姆定律适用于线性电阻元件，在一定温度和条件下成立。'
                        }
                    ]
                },
                'examples': {
                    'basic_examples': '基础计算练习',
                    'advanced_examples': '复杂电路分析',
                    'real_world_applications': '实际工程应用'
                },
                'practice': {
                    'difficulty_levels': ['easy', 'medium', 'hard'],
                    'question_types': ['calculation', 'analysis', 'design']
                },
                'simulation': {
                    'type': 'circuit_simulator',
                    'parameters': ['voltage', 'resistance'],
                    'outputs': ['current', 'power']
                }
            },
            'simulation_config': {
                'type': 'ohms_law_simulator',
                'parameters': [
                    {
                        'name': 'voltage',
                        'display_name': '电压',
                        'unit': 'V',
                        'min': 1,
                        'max': 12,
                        'default': 5,
                        'step': 0.1
                    },
                    {
                        'name': 'resistance',
                        'display_name': '电阻',
                        'unit': 'Ω',
                        'min': 10,
                        'max': 1000,
                        'default': 100,
                        'step': 10
                    }
                ],
                'outputs': [
                    {
                        'name': 'current',
                        'display_name': '电流',
                        'unit': 'A',
                        'formula': 'voltage / resistance'
                    },
                    {
                        'name': 'power',
                        'display_name': '功率',
                        'unit': 'W',
                        'formula': 'voltage * current'
                    }
                ],
                'visualization': {
                    'circuit_diagram': True,
                    'real_time_calculation': True,
                    'parameter_sliders': True
                }
            },
            'practice_questions': [
                {
                    'id': 1,
                    'type': 'multiple_choice',
                    'question': '一个电阻器的阻值为220Ω，通过的电流为50mA，求电阻器两端的电压。',
                    'options': [
                        {'id': 'a', 'text': '11V', 'correct': True},
                        {'id': 'b', 'text': '11mV', 'correct': False},
                        {'id': 'c', 'text': '110V', 'correct': False},
                        {'id': 'd', 'text': '1.1V', 'correct': False}
                    ],
                    'explanation': 'V = I × R = 0.05A × 220Ω = 11V',
                    'difficulty': 'easy',
                    'bloom_level': 'apply'
                },
                {
                    'id': 2,
                    'type': 'calculation',
                    'question': '在一个串联电路中，电源电压为12V，电阻R1=100Ω，R2=200Ω，求通过电路的电流和各电阻上的电压。',
                    'solution': {
                        'total_resistance': '300Ω',
                        'current': '0.04A',
                        'voltage_r1': '4V',
                        'voltage_r2': '8V'
                    },
                    'difficulty': 'medium',
                    'bloom_level': 'analyze'
                }
            ],
            'tags': ['基础电学', '欧姆定律', '电路分析', '电阻', '电压', '电流'],
            'accessibility_features': {
                'screen_reader_support': True,
                'high_contrast_mode': True,
                'keyboard_navigation': True,
                'audio_descriptions': True
            },
            'cultural_context': {
                'language': 'zh-CN',
                'educational_system': 'chinese',
                'measurement_units': 'metric'
            }
        },
        {
            'title': '基尔霍夫定律',
            'description': '描述电路中电流和电压分布规律的基本定律',
            'difficulty_level': 'intermediate',
            'bloom_level': 'analyze',
            'estimated_duration_minutes': 60,
            'learning_objectives': [
                '理解基尔霍夫电流定律(KCL)',
                '理解基尔霍夫电压定律(KVL)',
                '能够应用KCL和KVL分析复杂电路',
                '掌握节点分析和回路分析方法'
            ],
            'prerequisites': ['欧姆定律', '电路基本概念', '串并联电路'],
            'key_concepts': [
                '节点 (Node)',
                '回路 (Loop)',
                '电流守恒',
                '电压守恒',
                '支路电流'
            ],
            'formulas': [
                {
                    'name': '基尔霍夫电流定律 (KCL)',
                    'expression': '∑I_in = ∑I_out',
                    'description': '流入节点的电流总和等于流出节点的电流总和'
                },
                {
                    'name': '基尔霍夫电压定律 (KVL)',
                    'expression': '∑V = 0',
                    'description': '沿任意闭合回路，电压降的代数和为零'
                }
            ],
            'examples': [
                {
                    'title': '节点分析示例',
                    'problem': '在一个三支路节点中，已知流入电流I1=2A，I2=1.5A，流出电流I3=？',
                    'solution': '根据KCL：I1 + I2 = I3，所以 I3 = 2A + 1.5A = 3.5A',
                    'explanation': '电流守恒定律的直接应用'
                }
            ],
            'applications': [
                '复杂电路分析',
                '电网分析',
                '电子电路设计',
                '故障诊断'
            ],
            'tags': ['基尔霍夫定律', 'KCL', 'KVL', '电路分析', '节点分析', '回路分析']
        },
        {
            'title': '电容器原理',
            'description': '电容器的基本原理、特性和应用',
            'difficulty_level': 'intermediate',
            'bloom_level': 'understand',
            'estimated_duration_minutes': 50,
            'learning_objectives': [
                '理解电容器的基本结构和工作原理',
                '掌握电容的定义和计算方法',
                '了解不同类型电容器的特点',
                '能够分析电容器在电路中的作用'
            ],
            'prerequisites': ['电场概念', '欧姆定律', '基本电路知识'],
            'key_concepts': [
                '电容 (Capacitance)',
                '电介质 (Dielectric)',
                '充电过程',
                '放电过程',
                '时间常数'
            ],
            'formulas': [
                {
                    'name': '电容定义',
                    'expression': 'C = Q / V',
                    'variables': {
                        'C': '电容 (法拉)',
                        'Q': '电荷量 (库仑)',
                        'V': '电压 (伏特)'
                    }
                },
                {
                    'name': '平行板电容器',
                    'expression': 'C = ε₀εᵣA / d',
                    'variables': {
                        'ε₀': '真空介电常数',
                        'εᵣ': '相对介电常数',
                        'A': '极板面积',
                        'd': '极板间距'
                    }
                }
            ],
            'tags': ['电容器', '电容', '充放电', '时间常数', '电介质']
        }
    ]
    
    return knowledge_points

def generate_circuit_analysis_knowledge_points() -> List[Dict[str, Any]]:
    """生成电路分析知识点"""
    return [
        {
            'title': '串联电路分析',
            'description': '串联电路的特点、分析方法和应用',
            'difficulty_level': 'beginner',
            'bloom_level': 'apply',
            'estimated_duration_minutes': 40,
            'learning_objectives': [
                '理解串联电路的基本特点',
                '掌握串联电路中电流、电压、电阻的关系',
                '能够计算串联电路的各项参数',
                '了解串联电路的实际应用'
            ],
            'prerequisites': ['欧姆定律', '电路基本概念'],
            'key_concepts': [
                '串联连接',
                '总电阻',
                '电压分配',
                '电流相等',
                '功率分配'
            ],
            'formulas': [
                {
                    'name': '串联总电阻',
                    'expression': 'R_total = R₁ + R₂ + R₃ + ...',
                    'description': '串联电路中总电阻等于各电阻之和'
                },
                {
                    'name': '电压分配',
                    'expression': 'V_i = V_total × (R_i / R_total)',
                    'description': '各电阻上的电压与其阻值成正比'
                }
            ],
            'tags': ['串联电路', '电阻串联', '电压分配', '电路分析']
        },
        {
            'title': '并联电路分析',
            'description': '并联电路的特点、分析方法和应用',
            'difficulty_level': 'beginner',
            'bloom_level': 'apply',
            'estimated_duration_minutes': 40,
            'learning_objectives': [
                '理解并联电路的基本特点',
                '掌握并联电路中电流、电压、电阻的关系',
                '能够计算并联电路的各项参数',
                '了解并联电路的实际应用'
            ],
            'prerequisites': ['欧姆定律', '串联电路'],
            'key_concepts': [
                '并联连接',
                '等效电阻',
                '电流分配',
                '电压相等',
                '功率分配'
            ],
            'formulas': [
                {
                    'name': '并联等效电阻',
                    'expression': '1/R_total = 1/R₁ + 1/R₂ + 1/R₃ + ...',
                    'description': '并联电路中总电阻的倒数等于各电阻倒数之和'
                },
                {
                    'name': '电流分配',
                    'expression': 'I_i = I_total × (R_total / R_i)',
                    'description': '各支路电流与其电阻成反比'
                }
            ],
            'tags': ['并联电路', '电阻并联', '电流分配', '等效电阻']
        }
    ]

def generate_multimedia_resources() -> List[Dict[str, Any]]:
    """生成多媒体资源数据"""
    return [
        {
            'filename': 'ohms_law_introduction.mp4',
            'original_filename': '欧姆定律介绍.mp4',
            'resource_type': 'video',
            'title': '欧姆定律基础介绍',
            'description': '通过动画演示欧姆定律的基本概念和应用',
            'duration_seconds': 300,
            'resolution': '1920x1080',
            'quality_level': '1080p',
            'learning_objectives': [
                '理解欧姆定律的基本概念',
                '观察电压、电流、电阻的关系'
            ],
            'difficulty_level': 'beginner',
            'bloom_level': 'understand',
            'timestamps': [
                {'time': 0, 'title': '开场介绍', 'description': '欧姆定律的重要性'},
                {'time': 30, 'title': '基本概念', 'description': '电压、电流、电阻的定义'},
                {'time': 120, 'title': '数学表达', 'description': 'V=IR公式推导'},
                {'time': 180, 'title': '实例演示', 'description': '简单电路计算'},
                {'time': 240, 'title': '总结回顾', 'description': '要点总结'}
            ],
            'captions': [
                {'language': 'zh-CN', 'file': 'ohms_law_zh.srt'},
                {'language': 'en-US', 'file': 'ohms_law_en.srt'}
            ],
            'alt_text': '欧姆定律教学视频，包含动画演示和公式推导',
            'transcription': '本视频介绍了欧姆定律的基本概念...',
            'copyright_info': {
                'owner': 'Alethea教育平台',
                'year': 2025,
                'license': 'Educational Use'
            },
            'license_type': 'educational',
            'attribution': 'Alethea教育团队制作'
        },
        {
            'filename': 'circuit_simulator.html',
            'original_filename': '电路仿真器.html',
            'resource_type': 'simulation',
            'title': '交互式电路仿真器',
            'description': '可调节参数的电路仿真工具，支持实时计算',
            'learning_objectives': [
                '通过交互操作理解电路原理',
                '观察参数变化对电路的影响'
            ],
            'difficulty_level': 'intermediate',
            'bloom_level': 'apply',
            'interactive_hotspots': [
                {'x': 100, 'y': 50, 'type': 'voltage_source', 'description': '可调节电压源'},
                {'x': 200, 'y': 50, 'type': 'resistor', 'description': '可调节电阻'},
                {'x': 300, 'y': 50, 'type': 'ammeter', 'description': '电流表显示'}
            ],
            'alt_text': '交互式电路仿真器，包含可调节的电压源和电阻',
            'license_type': 'educational'
        },
        {
            'filename': 'kirchhoff_laws_diagram.png',
            'original_filename': '基尔霍夫定律图解.png',
            'resource_type': 'image',
            'title': '基尔霍夫定律图解',
            'description': '基尔霍夫电流定律和电压定律的图形化说明',
            'resolution': '1200x800',
            'learning_objectives': [
                '直观理解KCL和KVL',
                '识别电路中的节点和回路'
            ],
            'difficulty_level': 'intermediate',
            'bloom_level': 'understand',
            'alt_text': '基尔霍夫定律示意图，显示节点电流和回路电压',
            'annotations': [
                {'x': 150, 'y': 100, 'text': '节点A：电流汇聚点'},
                {'x': 300, 'y': 200, 'text': '回路1：电压环路'},
                {'x': 450, 'y': 150, 'text': '回路2：电压环路'}
            ],
            'license_type': 'educational'
        }
    ]

def generate_assessments() -> List[Dict[str, Any]]:
    """生成评估数据"""
    return [
        {
            'title': '欧姆定律基础测试',
            'description': '测试学生对欧姆定律基本概念和计算的掌握程度',
            'assessment_type': 'theoretical',
            'difficulty_level': 'beginner',
            'bloom_level': 'apply',
            'competency_level': 'competent',
            'estimated_duration_minutes': 30,
            'max_attempts': 3,
            'passing_score': 70.0,
            'questions': [
                {
                    'id': 1,
                    'type': 'multiple_choice',
                    'question': '欧姆定律的数学表达式是？',
                    'options': [
                        {'id': 'a', 'text': 'V = I × R'},
                        {'id': 'b', 'text': 'V = I / R'},
                        {'id': 'c', 'text': 'V = I + R'},
                        {'id': 'd', 'text': 'V = I - R'}
                    ],
                    'correct_answer': 'a',
                    'points': 10,
                    'explanation': '欧姆定律表明电压等于电流与电阻的乘积'
                },
                {
                    'id': 2,
                    'type': 'calculation',
                    'question': '一个100Ω的电阻通过2A的电流，求电阻两端的电压。',
                    'correct_answer': '200V',
                    'points': 15,
                    'solution_steps': [
                        '应用欧姆定律：V = I × R',
                        '代入数值：V = 2A × 100Ω',
                        '计算结果：V = 200V'
                    ]
                },
                {
                    'id': 3,
                    'type': 'multiple_choice',
                    'question': '在欧姆定律中，如果电压增加一倍，电阻不变，电流会？',
                    'options': [
                        {'id': 'a', 'text': '增加一倍'},
                        {'id': 'b', 'text': '减少一半'},
                        {'id': 'c', 'text': '保持不变'},
                        {'id': 'd', 'text': '增加四倍'}
                    ],
                    'correct_answer': 'a',
                    'points': 10,
                    'explanation': '根据I=V/R，电压增加一倍，电流也增加一倍'
                }
            ],
            'rubrics': {
                'excellent': {'min_score': 90, 'description': '优秀：完全掌握欧姆定律概念和应用'},
                'good': {'min_score': 80, 'description': '良好：基本掌握欧姆定律，能解决简单问题'},
                'satisfactory': {'min_score': 70, 'description': '及格：理解基本概念，需要更多练习'},
                'needs_improvement': {'min_score': 0, 'description': '需要改进：概念理解不足，需要重新学习'}
            },
            'feedback_templates': {
                'correct': '回答正确！{explanation}',
                'incorrect': '回答错误。正确答案是{correct_answer}。{explanation}',
                'partial': '部分正确。{feedback}'
            }
        },
        {
            'title': '电路分析综合测试',
            'description': '测试学生对串并联电路分析的综合能力',
            'assessment_type': 'practical',
            'difficulty_level': 'intermediate',
            'bloom_level': 'analyze',
            'competency_level': 'proficient',
            'estimated_duration_minutes': 45,
            'max_attempts': 2,
            'passing_score': 75.0,
            'questions': [
                {
                    'id': 1,
                    'type': 'circuit_analysis',
                    'question': '分析给定的串并联混合电路，计算各支路电流和电压。',
                    'circuit_diagram': 'mixed_circuit_1.png',
                    'given_values': {
                        'V_source': '12V',
                        'R1': '100Ω',
                        'R2': '200Ω',
                        'R3': '150Ω'
                    },
                    'required_answers': [
                        'total_current',
                        'voltage_across_R1',
                        'current_through_R2',
                        'current_through_R3'
                    ],
                    'points': 25
                }
            ]
        }
    ]

def save_sample_data():
    """保存示例数据到文件"""
    # 创建输出目录
    output_dir = 'knowledge_base/electrical_engineering'
    os.makedirs(output_dir, exist_ok=True)
    
    # 生成领域数据
    domain_data = generate_electrical_engineering_domain()
    with open(f'{output_dir}/domain.json', 'w', encoding='utf-8') as f:
        json.dump(domain_data, f, ensure_ascii=False, indent=2)
    
    # 生成知识点数据
    basic_concepts = generate_basic_concepts_knowledge_points()
    circuit_analysis = generate_circuit_analysis_knowledge_points()
    
    all_knowledge_points = basic_concepts + circuit_analysis
    
    with open(f'{output_dir}/knowledge_points.json', 'w', encoding='utf-8') as f:
        json.dump(all_knowledge_points, f, ensure_ascii=False, indent=2)
    
    # 生成多媒体资源数据
    multimedia_resources = generate_multimedia_resources()
    with open(f'{output_dir}/multimedia_resources.json', 'w', encoding='utf-8') as f:
        json.dump(multimedia_resources, f, ensure_ascii=False, indent=2)
    
    # 生成评估数据
    assessments = generate_assessments()
    with open(f'{output_dir}/assessments.json', 'w', encoding='utf-8') as f:
        json.dump(assessments, f, ensure_ascii=False, indent=2)
    
    # 生成完整的导入数据包
    import_package = {
        'domain': domain_data,
        'knowledge_points': all_knowledge_points,
        'multimedia_resources': multimedia_resources,
        'assessments': assessments,
        'metadata': {
            'generated_at': datetime.now().isoformat(),
            'version': '1.0.0',
            'description': '电工电子工程示例数据包',
            'total_knowledge_points': len(all_knowledge_points),
            'total_multimedia_resources': len(multimedia_resources),
            'total_assessments': len(assessments)
        }
    }
    
    with open('electrical_engineering_sample_data.json', 'w', encoding='utf-8') as f:
        json.dump(import_package, f, ensure_ascii=False, indent=2)
    
    print(f"示例数据已生成：")
    print(f"- 知识领域: 1个")
    print(f"- 知识点: {len(all_knowledge_points)}个")
    print(f"- 多媒体资源: {len(multimedia_resources)}个")
    print(f"- 评估: {len(assessments)}个")
    print(f"- 完整数据包: electrical_engineering_sample_data.json")

if __name__ == '__main__':
    save_sample_data()
