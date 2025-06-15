"""
实验仿真路由
Experiment Simulation Routes
"""

from flask import Blueprint, request, jsonify, session
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from models.llm_models import llm_manager
import json
import logging
from datetime import datetime

# 创建蓝图
experiment_bp = Blueprint('experiment', __name__)

# 设置日志
logger = logging.getLogger(__name__)

# 实验模板数据
EXPERIMENT_TEMPLATES = {
    'circuit_ohm': {
        'title': '欧姆定律验证实验',
        'subject': '电路分析',
        'objectives': [
            '理解欧姆定律的基本原理',
            '掌握电压、电流、电阻之间的关系',
            '学会使用万用表测量电路参数',
            '验证理论计算与实际测量的一致性'
        ],
        'theory': '欧姆定律是电路分析的基础定律，表述为：在恒定温度下，通过导体的电流与导体两端的电压成正比，与导体的电阻成反比。数学表达式为：V = I × R，其中V为电压(伏特)，I为电流(安培)，R为电阻(欧姆)。',
        'steps': [
            '准备实验器材：直流电源、电阻器、万用表、导线',
            '搭建基本电路：将电阻器与电源串联',
            '设置电源电压为3V，记录电阻值',
            '使用万用表测量电路中的电流',
            '改变电阻值，重复测量电流',
            '改变电源电压，观察电流变化',
            '记录所有测量数据并分析'
        ],
        'expected_results': '通过实验验证，电压与电流的比值等于电阻值，证明欧姆定律的正确性。当电阻固定时，电流与电压成正比；当电压固定时，电流与电阻成反比。',
        'simulation_type': 'circuit',
        'simulation_url': '/static/simulations/circuit-simulator.html'
    },
    'circuit_rc': {
        'title': 'RC电路充放电实验',
        'subject': '电路分析',
        'objectives': [
            '理解RC电路的充放电过程',
            '掌握时间常数τ=RC的概念',
            '观察电容电压的指数变化规律',
            '学会分析一阶电路的暂态响应'
        ],
        'theory': 'RC电路是由电阻R和电容C组成的一阶电路。充电时，电容电压按指数规律上升：Vc(t) = V(1-e^(-t/RC))；放电时，电容电压按指数规律下降：Vc(t) = V₀e^(-t/RC)。时间常数τ=RC决定了充放电的快慢。',
        'steps': [
            '搭建RC充放电电路',
            '设置方波信号源，频率为1/(10RC)',
            '连接示波器观察电容电压波形',
            '测量充电时间常数τ₁',
            '测量放电时间常数τ₂',
            '改变R或C值，观察时间常数变化',
            '记录波形并分析充放电特性'
        ],
        'expected_results': '观察到电容电压呈指数变化，充电时渐近接近电源电压，放电时指数衰减到零。时间常数τ=RC，当t=τ时，充电达到63.2%，放电剩余36.8%。',
        'simulation_type': 'circuit',
        'simulation_url': '/static/simulations/general-simulator.html'
    },
    'digital_gates': {
        'title': '逻辑门特性测试实验',
        'subject': '数字电路',
        'objectives': [
            '掌握基本逻辑门的真值表',
            '理解TTL和CMOS逻辑门的特性',
            '学会测量逻辑门的电气参数',
            '验证布尔代数的基本运算'
        ],
        'theory': '逻辑门是数字电路的基本单元，实现布尔代数运算。基本逻辑门包括：与门(AND)、或门(OR)、非门(NOT)、与非门(NAND)、或非门(NOR)、异或门(XOR)等。每种门都有特定的真值表和逻辑功能。',
        'steps': [
            '准备各种逻辑门芯片(74LS系列)',
            '搭建测试电路，连接电源和地',
            '使用逻辑开关提供输入信号',
            '用LED指示灯显示输出状态',
            '逐一测试每种逻辑门的真值表',
            '测量高低电平的电压值',
            '记录所有测试结果并验证'
        ],
        'expected_results': '各逻辑门的输出完全符合理论真值表。TTL逻辑门的高电平约为3.5V，低电平约为0.3V。验证了布尔代数的基本运算规律。',
        'simulation_type': 'digital',
        'simulation_url': '/static/simulations/general-simulator.html'
    },
    'analog_opamp': {
        'title': '运算放大器基本电路实验',
        'subject': '模拟电路',
        'objectives': [
            '理解运算放大器的工作原理',
            '掌握反相和同相放大器的设计',
            '学会计算放大倍数和输入阻抗',
            '分析运放电路的频率响应'
        ],
        'theory': '运算放大器是高增益差分放大器，具有高输入阻抗、低输出阻抗的特点。在负反馈条件下，运放工作在线性区，满足"虚短"和"虚断"的理想化条件。反相放大器增益Av=-Rf/Ri，同相放大器增益Av=1+Rf/Ri。',
        'steps': [
            '选择合适的运放芯片(如LM741)',
            '搭建反相放大器电路',
            '设置输入信号，测量输出波形',
            '计算实际放大倍数',
            '搭建同相放大器电路',
            '比较两种电路的性能差异',
            '测试电路的频率响应特性'
        ],
        'expected_results': '反相放大器实现信号放大和相位反转，同相放大器实现同相位放大。实际增益与理论计算基本一致，频率响应呈低通特性，带宽受增益带宽积限制。',
        'simulation_type': 'analog',
        'simulation_url': '/static/simulations/general-simulator.html'
    },
    'signal_fourier': {
        'title': '傅里叶变换分析实验',
        'subject': '信号与系统',
        'objectives': [
            '理解傅里叶变换的物理意义',
            '掌握信号频谱分析方法',
            '学会使用MATLAB进行频谱分析',
            '分析不同信号的频域特性'
        ],
        'theory': '傅里叶变换是信号分析的重要工具，将时域信号转换为频域表示。连续傅里叶变换：F(ω)=∫f(t)e^(-jωt)dt，离散傅里叶变换(DFT)用于数字信号处理。频谱显示了信号在各个频率分量上的幅度和相位分布。',
        'steps': [
            '生成标准测试信号(正弦波、方波、三角波)',
            '使用MATLAB计算信号的FFT',
            '绘制幅度谱和相位谱',
            '分析周期信号的频谱特点',
            '研究窗函数对频谱的影响',
            '比较理论频谱与实际计算结果',
            '分析频谱泄漏和栅栏效应'
        ],
        'expected_results': '正弦波频谱为单一频率分量，方波频谱包含奇次谐波，三角波频谱谐波衰减更快。窗函数会影响频谱分辨率和泄漏，验证了傅里叶变换理论。',
        'simulation_type': 'signal',
        'simulation_url': '/static/simulations/general-simulator.html'
    },
    'comm_am': {
        'title': 'AM调制解调实验',
        'subject': '通信原理',
        'objectives': [
            '理解幅度调制的基本原理',
            '掌握AM调制器和解调器的设计',
            '分析调制信号的频谱特性',
            '学会计算调制度和频谱效率'
        ],
        'theory': 'AM调制是将低频信号调制到高频载波上的过程。AM信号表达式：s(t)=[A+m(t)]cos(ωct)，其中A为载波幅度，m(t)为调制信号，ωc为载波频率。调制度ma=|m(t)|max/A，过调制会产生失真。',
        'steps': [
            '搭建AM调制电路',
            '设置载波频率和调制信号',
            '观察调制信号的时域波形',
            '分析AM信号的频谱',
            '搭建包络检波解调电路',
            '比较解调信号与原始信号',
            '测试不同调制度的影响'
        ],
        'expected_results': 'AM信号包含载波和上下边带，频谱宽度为调制信号带宽的两倍。包络检波能正确恢复调制信号，调制度过大会产生失真。验证了AM调制解调的基本原理。',
        'simulation_type': 'communication',
        'simulation_url': '/static/simulations/general-simulator.html'
    },
    'embedded_gpio': {
        'title': 'STM32 GPIO控制实验',
        'subject': '嵌入式系统',
        'objectives': [
            '掌握STM32微控制器的GPIO配置',
            '学会控制LED和读取按键状态',
            '理解GPIO的工作模式',
            '编写基本的嵌入式程序'
        ],
        'theory': 'GPIO(General Purpose Input/Output)是微控制器的通用输入输出端口。STM32的GPIO具有多种工作模式：输入模式(浮空、上拉、下拉)、输出模式(推挽、开漏)、复用功能模式等。通过配置相应寄存器可以控制GPIO的行为。',
        'steps': [
            '创建STM32CubeMX工程',
            '配置GPIO引脚为输出模式(LED)',
            '配置GPIO引脚为输入模式(按键)',
            '编写LED闪烁程序',
            '编写按键检测程序',
            '实现按键控制LED的功能',
            '下载程序到开发板验证'
        ],
        'expected_results': 'LED能够按程序控制闪烁，按键能够正确检测并控制LED状态。掌握了GPIO的基本配置和使用方法，为后续复杂应用打下基础。',
        'simulation_type': 'embedded',
        'simulation_url': '/static/simulations/general-simulator.html'
    },
    # 新增实验模板
    'circuit_thevenin': {
        'title': '戴维南等效电路实验',
        'subject': '电路分析',
        'objectives': [
            '理解戴维南定理的基本原理',
            '掌握等效电路的求解方法',
            '学会测量等效电阻和等效电压',
            '验证复杂电路的等效简化'
        ],
        'theory': '戴维南定理指出：任何线性有源二端网络，对外电路而言，都可以用一个电压源Vth与一个电阻Rth的串联组合来等效替代。其中Vth为开路电压，Rth为从端口看进去的等效电阻。',
        'steps': [
            '搭建复杂线性电路',
            '断开负载，测量开路电压Vth',
            '将所有独立电源置零，测量等效电阻Rth',
            '用Vth和Rth构建等效电路',
            '连接不同负载，验证等效性',
            '比较原电路与等效电路的输出',
            '分析误差并总结规律'
        ],
        'expected_results': '验证戴维南等效电路与原电路在负载端具有相同的电压电流特性，等效电路大大简化了复杂电路的分析过程。',
        'simulation_type': 'circuit',
        'simulation_url': '/static/simulations/circuit-simulator.html'
    },
    'circuit_rlc': {
        'title': 'RLC谐振电路实验',
        'subject': '电路分析',
        'objectives': [
            '理解RLC串联谐振的基本原理',
            '掌握谐振频率和品质因数的计算',
            '观察谐振时的电压电流特性',
            '分析频率响应和选择性'
        ],
        'theory': 'RLC串联电路在特定频率下发生谐振，此时感抗等于容抗，电路呈纯阻性。谐振频率f0=1/(2π√LC)，品质因数Q=ωL/R，决定了电路的选择性。',
        'steps': [
            '搭建RLC串联谐振电路',
            '设置正弦信号源，调节频率',
            '测量不同频率下的电流幅值',
            '找到谐振频率点',
            '测量谐振时各元件电压',
            '绘制频率响应曲线',
            '计算品质因数和带宽'
        ],
        'expected_results': '在谐振频率处电流达到最大值，电感和电容上的电压可能远大于电源电压，验证了RLC谐振的选择性和放大特性。',
        'simulation_type': 'circuit',
        'simulation_url': '/static/simulations/circuit-simulator.html'
    },
    # 数字电路实验
    'digital_combinational': {
        'title': '组合逻辑设计实验',
        'subject': '数字电路',
        'objectives': [
            '掌握组合逻辑电路的设计方法',
            '学会使用多路选择器实现逻辑函数',
            '理解编码器和译码器的工作原理',
            '验证组合逻辑的功能正确性'
        ],
        'theory': '组合逻辑电路的输出只取决于当前输入，不依赖于电路的历史状态。常用的组合逻辑器件包括多路选择器、编码器、译码器等。设计时需要根据真值表或逻辑表达式选择合适的器件。',
        'steps': [
            '分析设计要求，列出真值表',
            '选择合适的组合逻辑器件',
            '设计电路连接图',
            '搭建实验电路',
            '输入各种组合，测试输出',
            '验证电路功能正确性',
            '分析电路的延迟特性'
        ],
        'expected_results': '组合逻辑电路能够正确实现预期的逻辑功能，输出与真值表完全一致，验证了组合逻辑设计的正确性。',
        'simulation_type': 'digital',
        'simulation_url': '/static/simulations/digital-simulator.html'
    },
    'digital_counter': {
        'title': '计数器设计实验',
        'subject': '数字电路',
        'objectives': [
            '理解同步计数器的工作原理',
            '掌握计数器的设计和实现方法',
            '学会分析计数器的状态转换',
            '验证计数器的计数功能'
        ],
        'theory': '计数器是重要的时序逻辑电路，能够按照一定规律进行计数。同步计数器的所有触发器由同一时钟信号控制，具有较好的同步性。设计时需要确定状态转换图和激励函数。',
        'steps': [
            '确定计数器的计数范围',
            '画出状态转换图',
            '选择触发器类型',
            '求解激励函数',
            '搭建计数器电路',
            '输入时钟信号，观察计数过程',
            '验证计数器的功能'
        ],
        'expected_results': '计数器能够按照预定的规律进行计数，状态转换正确，验证了时序逻辑设计的有效性。',
        'simulation_type': 'digital',
        'simulation_url': '/static/simulations/digital-simulator.html'
    },
    'digital_flipflop': {
        'title': '触发器应用实验',
        'subject': '数字电路',
        'objectives': [
            '理解各种触发器的工作原理',
            '掌握触发器的特性和应用',
            '学会分析触发器的时序关系',
            '验证触发器的逻辑功能'
        ],
        'theory': '触发器是构成时序逻辑电路的基本单元，具有记忆功能。常见的触发器有RS触发器、JK触发器、D触发器和T触发器，每种都有特定的逻辑功能和应用场合。',
        'steps': [
            '搭建各种触发器电路',
            '输入不同的控制信号',
            '观察触发器的状态变化',
            '测试触发器的建立时间和保持时间',
            '分析时钟边沿的影响',
            '验证触发器的逻辑功能',
            '比较不同触发器的特点'
        ],
        'expected_results': '各种触发器都能正确响应输入信号，状态转换符合逻辑功能，验证了触发器的工作原理和应用特性。',
        'simulation_type': 'digital',
        'simulation_url': '/static/simulations/digital-simulator.html'
    }
}

@experiment_bp.route('/api/experiments/generate', methods=['POST'])
def generate_experiment():
    """AI生成实验内容"""
    try:
        data = request.get_json()
        
        experiment_id = data.get('experiment_id')
        title = data.get('title', '')
        description = data.get('description', '')
        subject = data.get('subject', '')
        language = data.get('language', 'zh')
        
        # 检查是否有预定义模板
        if experiment_id in EXPERIMENT_TEMPLATES:
            template = EXPERIMENT_TEMPLATES[experiment_id]
            return jsonify({
                'success': True,
                'experiment': template
            })
        
        # 构建AI生成提示
        prompt = f"""
作为一个专业的实验教学AI助手，请为以下实验生成详细的实验内容：

实验信息：
- 实验ID: {experiment_id}
- 实验标题: {title}
- 实验描述: {description}
- 学科领域: {subject}
- 语言: 中文

请生成包含以下内容的完整实验方案：

1. 实验概览 (overview)
2. 实验目标 (objectives) - 3-4个具体目标
3. 理论基础 (theory) - 详细的理论知识
4. 实验步骤 (steps) - 6-8个详细步骤
5. 预期结果 (expected_results) - 实验预期达到的效果

请确保内容：
- 科学准确，符合教学要求
- 步骤清晰，易于操作
- 理论联系实际
- 适合本科生水平

请以JSON格式返回，包含以上所有字段。
"""

        # 调用LLM生成实验内容
        import asyncio
        response = asyncio.run(llm_manager.generate_response(prompt))
        
        # 检查响应格式
        if isinstance(response, dict) and 'content' in response:
            response_content = response['content']
        else:
            response_content = str(response)
        
        try:
            # 尝试解析JSON响应
            experiment_data = json.loads(response_content)
            
            # 验证必要字段
            required_fields = ['overview', 'objectives', 'theory', 'steps', 'expected_results']
            if all(field in experiment_data for field in required_fields):
                return jsonify({
                    'success': True,
                    'experiment': experiment_data
                })
            else:
                # 字段不完整，使用备用方案
                return generate_fallback_experiment(experiment_id, title, description, subject)
                
        except json.JSONDecodeError:
            # JSON解析失败，使用备用方案
            logger.warning("无法解析AI生成的实验内容，使用备用方案")
            return generate_fallback_experiment(experiment_id, title, description, subject)
            
    except Exception as e:
        logger.error(f"生成实验内容错误: {e}")
        return jsonify({
            'success': False,
            'error': '实验生成服务暂时不可用'
        }), 500

def generate_fallback_experiment(experiment_id, title, description, subject):
    """生成备用实验内容"""
    fallback_data = {
        'overview': f'这是一个关于{title}的实验。{description}',
        'objectives': [
            f'理解{title}的基本原理',
            f'掌握{subject}相关的实验技能',
            '学会分析实验现象和数据',
            '培养科学实验的思维方法'
        ],
        'theory': f'本实验涉及{subject}领域的重要理论知识。通过实际操作，学生可以深入理解相关概念，并将理论知识与实践相结合。',
        'steps': [
            '准备实验器材和设备',
            '按照电路图搭建实验电路',
            '检查电路连接是否正确',
            '设置实验参数',
            '进行实验测量',
            '记录实验数据',
            '分析实验结果'
        ],
        'expected_results': f'通过本实验，学生将掌握{title}的实际应用，理解相关理论知识，并获得宝贵的实践经验。',
        'simulation_type': get_simulation_type(subject)
    }
    
    return jsonify({
        'success': True,
        'experiment': fallback_data,
        'fallback': True
    })

def get_simulation_type(subject):
    """根据学科获取仿真类型"""
    simulation_types = {
        'circuit': 'circuit',
        'digital': 'digital', 
        'analog': 'analog',
        'signal': 'signal',
        'communication': 'communication',
        'embedded': 'embedded'
    }
    return simulation_types.get(subject, 'general')

@experiment_bp.route('/api/experiments/progress', methods=['POST'])
def update_experiment_progress():
    """更新实验进度"""
    try:
        data = request.get_json()
        experiment_id = data.get('experiment_id')
        step = data.get('step', 0)
        progress = data.get('progress', 0)
        
        # 这里应该保存到数据库
        # 暂时使用session存储
        if 'experiment_progress' not in session:
            session['experiment_progress'] = {}
        
        session['experiment_progress'][experiment_id] = {
            'step': step,
            'progress': progress,
            'updated_at': str(datetime.utcnow())
        }
        
        return jsonify({
            'success': True,
            'message': '实验进度已更新'
        })
        
    except Exception as e:
        logger.error(f"更新实验进度错误: {e}")
        return jsonify({
            'success': False,
            'error': '更新失败'
        }), 500

@experiment_bp.route('/api/experiments/progress/<experiment_id>', methods=['GET'])
def get_experiment_progress(experiment_id):
    """获取实验进度"""
    try:
        progress_data = session.get('experiment_progress', {}).get(experiment_id, {
            'step': 0,
            'progress': 0
        })
        
        return jsonify({
            'success': True,
            'progress': progress_data
        })
        
    except Exception as e:
        logger.error(f"获取实验进度错误: {e}")
        return jsonify({
            'success': False,
            'error': '获取失败'
        }), 500

@experiment_bp.route('/api/experiments/simulation/<experiment_id>', methods=['GET'])
def get_simulation_url(experiment_id):
    """获取仿真环境URL"""
    try:
        # 这里可以根据实验ID返回对应的仿真环境URL
        simulation_urls = {
            'circuit_ohm': '/static/simulations/circuit-simulator.html',
            'circuit_rc': '/static/simulations/general-simulator.html',
            'digital_gates': '/static/simulations/general-simulator.html',
            'analog_opamp': '/static/simulations/general-simulator.html',
            'signal_fourier': '/static/simulations/general-simulator.html',
            'comm_am': '/static/simulations/general-simulator.html',
            'embedded_gpio': '/static/simulations/general-simulator.html'
        }
        
        simulation_url = simulation_urls.get(experiment_id, '/static/simulations/general-simulator.html')
        
        return jsonify({
            'success': True,
            'simulation_url': simulation_url,
            'experiment_id': experiment_id
        })
        
    except Exception as e:
        logger.error(f"获取仿真URL错误: {e}")
        return jsonify({
            'success': False,
            'error': '获取仿真环境失败'
        }), 500

@experiment_bp.route('/api/experiments/help', methods=['POST'])
def get_experiment_help():
    """获取实验帮助"""
    try:
        data = request.get_json()
        experiment_id = data.get('experiment_id', '')
        question = data.get('question', '')
        context = data.get('context', '')
        
        # 构建帮助提示
        prompt = f"""
作为一个专业的实验教学助手，请帮助学生解决实验中的问题。

实验信息：
- 实验ID: {experiment_id}
- 学生问题: {question}
- 实验上下文: {context}

请提供：
1. 问题分析
2. 详细解答
3. 操作建议
4. 注意事项

请用中文回答，语言要通俗易懂，适合本科生理解。
"""

        # 调用LLM生成帮助内容
        import asyncio
        response = asyncio.run(llm_manager.generate_response(prompt))
        
        # 检查响应格式
        if isinstance(response, dict) and 'content' in response:
            response_content = response['content']
        else:
            response_content = str(response)
        
        return jsonify({
            'success': True,
            'help': response_content
        })
        
    except Exception as e:
        logger.error(f"获取实验帮助错误: {e}")
        return jsonify({
            'success': False,
            'error': '帮助服务暂时不可用'
        }), 500
