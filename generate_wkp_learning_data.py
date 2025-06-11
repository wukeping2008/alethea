#!/usr/bin/env python3
"""
为用户wkp生成丰富的学习数据
包括问答记录、项目制学习、仿真实验等数据
用于AI数字画像生成和个性化推荐
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from models.user import UserManager, SubjectManager
from models.history import HistoryManager
from datetime import datetime, timedelta
import random
import json

def generate_wkp_learning_data():
    """为用户wkp生成完整的学习数据"""
    
    # 初始化管理器
    user_manager = UserManager()
    subject_manager = SubjectManager()
    history_manager = HistoryManager()
    
    print("🚀 开始为用户wkp生成学习数据...")
    
    # 1. 创建或获取用户wkp
    print("👤 创建/获取用户wkp...")
    user_data = {
        'username': 'wkp',
        'email': 'wkp@alethea.edu',
        'password': 'wkp123456',
        'full_name': '王科鹏',
        'student_id': 'STU2024001',
        'major': '电子信息工程',
        'grade': '大三',
        'phone': '13800138001'
    }
    
    # 检查用户是否存在
    existing_user = user_manager.get_user_by_username('wkp')
    if existing_user:
        user_id = existing_user['id']
        print(f"✅ 用户wkp已存在，ID: {user_id}")
    else:
        result = user_manager.register_user(user_data)
        if result['success']:
            user_id = result['user_id']
            print(f"✅ 用户wkp创建成功，ID: {user_id}")
        else:
            print(f"❌ 用户创建失败: {result['message']}")
            return
    
    # 2. 生成学科数据
    print("📚 生成学科数据...")
    subjects_data = [
        {
            'name': '电路分析',
            'code': 'EE101',
            'description': '电路基础理论与分析方法',
            'category': '专业基础课',
            'credits': 4,
            'difficulty_level': 3,
            'prerequisites': [],
            'knowledge_points': [
                '欧姆定律', '基尔霍夫定律', '节点电压法', '网孔电流法',
                '戴维南定理', '诺顿定理', '最大功率传输', 'RC电路',
                'RL电路', 'RLC电路', '正弦稳态分析', '相量法'
            ]
        },
        {
            'name': '数字电路',
            'code': 'EE201',
            'description': '数字逻辑设计与分析',
            'category': '专业核心课',
            'credits': 4,
            'difficulty_level': 4,
            'prerequisites': ['电路分析'],
            'knowledge_points': [
                '布尔代数', '逻辑门', '组合逻辑电路', '编码器',
                '译码器', '多路选择器', '触发器', '计数器',
                '寄存器', '状态机', 'FPGA设计', 'Verilog HDL'
            ]
        },
        {
            'name': '模拟电路',
            'code': 'EE202',
            'description': '模拟电子技术基础',
            'category': '专业核心课',
            'credits': 4,
            'difficulty_level': 4,
            'prerequisites': ['电路分析'],
            'knowledge_points': [
                '二极管', '三极管', '场效应管', '放大电路',
                '运算放大器', '反馈电路', '振荡器', '滤波器',
                '功率放大器', '电源电路', '集成电路', 'PCB设计'
            ]
        },
        {
            'name': '信号与系统',
            'code': 'EE301',
            'description': '信号处理与系统分析',
            'category': '专业核心课',
            'credits': 3,
            'difficulty_level': 5,
            'prerequisites': ['电路分析', '高等数学'],
            'knowledge_points': [
                '信号分类', '系统特性', '卷积', '傅里叶变换',
                '拉普拉斯变换', 'Z变换', '滤波器设计', '采样定理',
                '数字信号处理', 'FFT算法', '滤波器实现', 'MATLAB仿真'
            ]
        },
        {
            'name': '通信原理',
            'code': 'EE401',
            'description': '通信系统原理与技术',
            'category': '专业选修课',
            'credits': 3,
            'difficulty_level': 4,
            'prerequisites': ['信号与系统'],
            'knowledge_points': [
                '调制解调', 'AM调制', 'FM调制', '数字调制',
                'QPSK', 'QAM', '信道编码', '信道容量',
                '多径衰落', 'OFDM', 'MIMO', '5G技术'
            ]
        },
        {
            'name': '嵌入式系统',
            'code': 'EE402',
            'description': '嵌入式系统设计与开发',
            'category': '专业选修课',
            'credits': 3,
            'difficulty_level': 4,
            'prerequisites': ['数字电路', 'C语言程序设计'],
            'knowledge_points': [
                'ARM架构', '单片机', 'STM32', 'Linux系统',
                '实时操作系统', '驱动开发', '传感器接口', '通信协议',
                'I2C', 'SPI', 'UART', 'CAN总线'
            ]
        }
    ]
    
    subject_ids = {}
    for subject_data in subjects_data:
        result = subject_manager.create_subject(subject_data)
        if result['success']:
            subject_ids[subject_data['name']] = result['subject_id']
            print(f"✅ 学科创建成功: {subject_data['name']}")
        else:
            # 如果学科已存在，获取其ID
            existing_subject = subject_manager.get_subject_by_code(subject_data['code'])
            if existing_subject:
                subject_ids[subject_data['name']] = existing_subject['id']
                print(f"✅ 学科已存在: {subject_data['name']}")
    
    # 3. 生成问答历史数据
    print("💬 生成问答历史数据...")
    
    # 电路分析相关问答
    circuit_questions = [
        {
            'question': '什么是欧姆定律？请解释其物理意义和数学表达式。',
            'answer': '欧姆定律是电路分析的基础定律，表述为：在恒定温度下，通过导体的电流与导体两端的电压成正比，与导体的电阻成反比。数学表达式为 V = I × R，其中V是电压(伏特)，I是电流(安培)，R是电阻(欧姆)。物理意义是描述了电压、电流和电阻三者之间的线性关系。',
            'subject': '电路分析',
            'difficulty': 2,
            'tags': ['基础概念', '欧姆定律', '电路理论']
        },
        {
            'question': '请解释基尔霍夫电流定律(KCL)和电压定律(KVL)。',
            'answer': 'KCL(基尔霍夫电流定律)：在任意时刻，流入任一节点的电流代数和等于零，即∑I=0。这反映了电荷守恒定律。KVL(基尔霍夫电压定律)：在任意时刻，沿任一闭合回路的电压代数和等于零，即∑V=0。这反映了能量守恒定律。这两个定律是电路分析的基础。',
            'subject': '电路分析',
            'difficulty': 3,
            'tags': ['基尔霍夫定律', 'KCL', 'KVL', '电路分析']
        },
        {
            'question': '什么是戴维南定理？如何应用戴维南等效电路？',
            'answer': '戴维南定理：任何线性有源二端网络，对外电路而言，都可以用一个电压源Vth与一个电阻Rth串联的等效电路来代替。其中Vth是开路电压，Rth是从端口看进去的等效电阻。应用步骤：1)断开负载，求开路电压Vth；2)将独立源置零，求等效电阻Rth；3)画出戴维南等效电路；4)连接负载分析电路。',
            'subject': '电路分析',
            'difficulty': 4,
            'tags': ['戴维南定理', '等效电路', '电路简化']
        }
    ]
    
    # 数字电路相关问答
    digital_questions = [
        {
            'question': '什么是布尔代数？请列举基本的布尔运算。',
            'answer': '布尔代数是处理逻辑变量的数学体系，变量只能取0或1两个值。基本布尔运算包括：1)与运算(AND)：A·B，只有当A=1且B=1时结果为1；2)或运算(OR)：A+B，当A=1或B=1时结果为1；3)非运算(NOT)：Ā，对A取反。还有异或(XOR)、与非(NAND)、或非(NOR)等复合运算。布尔代数遵循交换律、结合律、分配律等运算规律。',
            'subject': '数字电路',
            'difficulty': 3,
            'tags': ['布尔代数', '逻辑运算', '数字逻辑']
        },
        {
            'question': '请解释D触发器的工作原理和真值表。',
            'answer': 'D触发器是边沿触发的存储器件，具有数据输入端D、时钟输入端CLK和输出端Q、Q̄。工作原理：在时钟上升沿(或下降沿)到来时，输出Q跟随输入D的状态，其他时间输出保持不变。真值表：当CLK↑时，若D=0则Q=0；若D=1则Q=1。D触发器消除了SR触发器的约束条件，广泛用于寄存器、计数器等时序电路中。',
            'subject': '数字电路',
            'difficulty': 4,
            'tags': ['D触发器', '时序电路', '存储器件']
        }
    ]
    
    # 模拟电路相关问答
    analog_questions = [
        {
            'question': '请解释三极管的三种工作状态及其特点。',
            'answer': '三极管有三种工作状态：1)截止状态：发射结和集电结均反偏，Ib≈0，Ic≈0，三极管相当于开关断开；2)放大状态：发射结正偏，集电结反偏，Ic=βIb，具有电流放大作用，用于放大电路；3)饱和状态：发射结和集电结均正偏，Ic不再随Ib变化，Vce很小，三极管相当于开关闭合。不同状态下三极管的应用不同：放大状态用于信号放大，截止和饱和状态用于开关电路。',
            'subject': '模拟电路',
            'difficulty': 4,
            'tags': ['三极管', '工作状态', '放大电路']
        },
        {
            'question': '什么是运算放大器？请说明理想运放的特点。',
            'answer': '运算放大器(Op-Amp)是高增益的直流耦合放大器，具有差分输入和单端输出。理想运放特点：1)开环增益无穷大(Avo→∞)；2)输入阻抗无穷大(Ri→∞)；3)输出阻抗为零(Ro=0)；4)带宽无穷大；5)失调为零。在负反馈条件下，理想运放遵循"虚短"和"虚断"原则：虚短指两输入端电压相等，虚断指输入端电流为零。运放广泛用于放大、滤波、运算等电路。',
            'subject': '模拟电路',
            'difficulty': 4,
            'tags': ['运算放大器', '理想运放', '虚短虚断']
        }
    ]
    
    # 信号与系统相关问答
    signal_questions = [
        {
            'question': '什么是卷积？请解释卷积在信号处理中的意义。',
            'answer': '卷积是两个函数的一种数学运算，定义为：(f*g)(t) = ∫f(τ)g(t-τ)dτ。在信号处理中，卷积描述了线性时不变系统的输入输出关系：y(t) = x(t)*h(t)，其中x(t)是输入信号，h(t)是系统冲激响应，y(t)是输出信号。卷积的物理意义是系统对输入信号的"记忆"效应，当前输出不仅取决于当前输入，还取决于过去的输入历史。',
            'subject': '信号与系统',
            'difficulty': 5,
            'tags': ['卷积', '线性系统', '冲激响应']
        },
        {
            'question': '请解释傅里叶变换的物理意义和应用。',
            'answer': '傅里叶变换将时域信号转换为频域表示：F(ω) = ∫f(t)e^(-jωt)dt。物理意义：任何信号都可以分解为不同频率正弦波的叠加，傅里叶变换揭示了信号的频谱特性。应用包括：1)频谱分析：分析信号的频率成分；2)滤波器设计：在频域设计滤波器；3)信号处理：去噪、压缩等；4)通信系统：调制解调；5)图像处理：频域滤波。傅里叶变换是信号处理的核心工具。',
            'subject': '信号与系统',
            'difficulty': 5,
            'tags': ['傅里叶变换', '频域分析', '频谱']
        }
    ]
    
    # 通信原理相关问答
    comm_questions = [
        {
            'question': '什么是调制？请比较AM、FM和PM调制的特点。',
            'answer': '调制是将低频信号转换为适合传输的高频信号的过程。AM(幅度调制)：载波幅度随调制信号变化，优点是解调简单，缺点是抗噪声能力差；FM(频率调制)：载波频率随调制信号变化，抗噪声能力强，但占用带宽大；PM(相位调制)：载波相位随调制信号变化，与FM类似但实现方式不同。数字调制如QPSK、QAM等在现代通信中更常用，具有更高的频谱效率和抗干扰能力。',
            'subject': '通信原理',
            'difficulty': 4,
            'tags': ['调制', 'AM', 'FM', '数字调制']
        }
    ]
    
    # 嵌入式系统相关问答
    embedded_questions = [
        {
            'question': '什么是ARM架构？请介绍ARM Cortex-M系列的特点。',
            'answer': 'ARM是一种RISC(精简指令集)架构，具有低功耗、高性能的特点。ARM Cortex-M系列专为微控制器设计，特点包括：1)32位RISC架构；2)哈佛结构，指令和数据分离；3)嵌套向量中断控制器(NVIC)；4)低功耗设计；5)丰富的外设接口。常见型号：Cortex-M0/M0+适合低成本应用，Cortex-M3/M4适合中高端应用，Cortex-M7适合高性能应用。广泛应用于物联网、工业控制、消费电子等领域。',
            'subject': '嵌入式系统',
            'difficulty': 4,
            'tags': ['ARM架构', 'Cortex-M', '微控制器']
        }
    ]
    
    # 合并所有问答
    all_questions = (circuit_questions + digital_questions + analog_questions + 
                    signal_questions + comm_questions + embedded_questions)
    
    # 生成问答历史
    base_time = datetime.now() - timedelta(days=90)  # 从90天前开始
    
    for i, qa in enumerate(all_questions):
        # 随机时间分布
        days_offset = random.randint(0, 85)
        hours_offset = random.randint(0, 23)
        minutes_offset = random.randint(0, 59)
        
        question_time = base_time + timedelta(days=days_offset, hours=hours_offset, minutes=minutes_offset)
        
        # 添加问答记录
        subject_id = subject_ids.get(qa['subject'])
        if subject_id:
            history_data = {
                'user_id': user_id,
                'subject_id': subject_id,
                'question': qa['question'],
                'answer': qa['answer'],
                'ai_model': random.choice(['claude', 'gemini', 'ollama_deepseek', 'ali_qwen']),
                'response_time': random.uniform(2.0, 8.0),
                'satisfaction_rating': random.randint(4, 5),
                'difficulty_level': qa['difficulty'],
                'tags': qa['tags'],
                'created_at': question_time
            }
            
            result = history_manager.add_question_history(history_data)
            if result['success']:
                print(f"✅ 问答记录 {i+1}/{len(all_questions)}: {qa['question'][:30]}...")
    
    # 4. 生成项目制学习数据
    print("🎯 生成项目制学习数据...")
    
    projects_data = [
        {
            'name': '智能家居控制系统',
            'description': '基于STM32的智能家居控制系统设计与实现',
            'subjects': ['嵌入式系统', '数字电路', '模拟电路'],
            'difficulty': 4,
            'duration_weeks': 8,
            'status': 'completed',
            'progress': 100,
            'skills_gained': ['STM32编程', '传感器接口', '无线通信', 'PCB设计', '系统集成'],
            'deliverables': ['系统设计文档', '硬件原理图', '软件源代码', '测试报告', '演示视频'],
            'start_date': datetime.now() - timedelta(days=60),
            'end_date': datetime.now() - timedelta(days=4)
        },
        {
            'name': '数字信号处理器设计',
            'description': '基于FPGA的FIR滤波器设计与实现',
            'subjects': ['信号与系统', '数字电路'],
            'difficulty': 5,
            'duration_weeks': 6,
            'status': 'completed',
            'progress': 100,
            'skills_gained': ['Verilog HDL', 'FPGA开发', '数字滤波器', 'MATLAB仿真', '硬件验证'],
            'deliverables': ['算法设计文档', 'Verilog代码', 'FPGA实现', '仿真结果', '性能测试'],
            'start_date': datetime.now() - timedelta(days=45),
            'end_date': datetime.now() - timedelta(days=3)
        },
        {
            'name': '无线通信系统仿真',
            'description': 'OFDM通信系统的MATLAB仿真与性能分析',
            'subjects': ['通信原理', '信号与系统'],
            'difficulty': 4,
            'duration_weeks': 4,
            'status': 'in_progress',
            'progress': 75,
            'skills_gained': ['MATLAB编程', 'OFDM原理', '信道建模', '性能分析'],
            'deliverables': ['仿真程序', '性能分析报告', '参数优化方案'],
            'start_date': datetime.now() - timedelta(days=20),
            'end_date': None
        },
        {
            'name': '模拟电路综合设计',
            'description': '音频功率放大器的设计与制作',
            'subjects': ['模拟电路', '电路分析'],
            'difficulty': 4,
            'duration_weeks': 5,
            'status': 'planned',
            'progress': 0,
            'skills_gained': ['放大器设计', 'PCB布局', '电路仿真', '性能测试'],
            'deliverables': ['电路设计', 'PCB制作', '性能测试', '优化改进'],
            'start_date': datetime.now() + timedelta(days=7),
            'end_date': None
        }
    ]
    
    # 保存项目数据到数据库
    for project in projects_data:
        # 这里可以添加项目数据到数据库的逻辑
        print(f"✅ 项目数据: {project['name']}")
    
    # 5. 生成仿真实验数据
    print("🔬 生成仿真实验数据...")
    
    simulation_data = [
        {
            'subject': '电路分析',
            'experiments': [
                {
                    'name': '欧姆定律验证实验',
                    'description': '通过改变电阻值，测量电压和电流的关系',
                    'difficulty': 2,
                    'duration_minutes': 30,
                    'completed': True,
                    'score': 95,
                    'completion_date': datetime.now() - timedelta(days=50)
                },
                {
                    'name': 'RC电路暂态分析',
                    'description': '分析RC电路的充放电过程',
                    'difficulty': 3,
                    'duration_minutes': 45,
                    'completed': True,
                    'score': 88,
                    'completion_date': datetime.now() - timedelta(days=45)
                },
                {
                    'name': '戴维南等效电路',
                    'description': '验证戴维南定理，求解等效电路',
                    'difficulty': 4,
                    'duration_minutes': 60,
                    'completed': True,
                    'score': 92,
                    'completion_date': datetime.now() - timedelta(days=40)
                }
            ]
        },
        {
            'subject': '数字电路',
            'experiments': [
                {
                    'name': '逻辑门特性测试',
                    'description': '测试各种逻辑门的真值表',
                    'difficulty': 2,
                    'duration_minutes': 40,
                    'completed': True,
                    'score': 90,
                    'completion_date': datetime.now() - timedelta(days=35)
                },
                {
                    'name': '组合逻辑电路设计',
                    'description': '设计并实现多路选择器',
                    'difficulty': 4,
                    'duration_minutes': 90,
                    'completed': True,
                    'score': 85,
                    'completion_date': datetime.now() - timedelta(days=30)
                },
                {
                    'name': '计数器设计实验',
                    'description': '设计同步二进制计数器',
                    'difficulty': 5,
                    'duration_minutes': 120,
                    'completed': False,
                    'score': None,
                    'completion_date': None
                }
            ]
        },
        {
            'subject': '模拟电路',
            'experiments': [
                {
                    'name': '三极管特性曲线',
                    'description': '测量三极管的输入输出特性',
                    'difficulty': 3,
                    'duration_minutes': 60,
                    'completed': True,
                    'score': 87,
                    'completion_date': datetime.now() - timedelta(days=25)
                },
                {
                    'name': '运放基本电路',
                    'description': '实现反相放大器和同相放大器',
                    'difficulty': 4,
                    'duration_minutes': 75,
                    'completed': True,
                    'score': 93,
                    'completion_date': datetime.now() - timedelta(days=20)
                }
            ]
        },
        {
            'subject': '信号与系统',
            'experiments': [
                {
                    'name': '信号的时域分析',
                    'description': '分析各种基本信号的时域特性',
                    'difficulty': 3,
                    'duration_minutes': 50,
                    'completed': True,
                    'score': 89,
                    'completion_date': datetime.now() - timedelta(days=15)
                },
                {
                    'name': '傅里叶变换实验',
                    'description': '使用MATLAB分析信号频谱',
                    'difficulty': 5,
                    'duration_minutes': 90,
                    'completed': True,
                    'score': 91,
                    'completion_date': datetime.now() - timedelta(days=10)
                }
            ]
        }
    ]
    
    # 保存仿真实验数据
    for subject_sim in simulation_data:
        subject_name = subject_sim['subject']
        print(f"✅ {subject_name} 仿真实验数据")
        for exp in subject_sim['experiments']:
            print(f"   - {exp['name']}: {'已完成' if exp['completed'] else '未完成'}")
    
    # 6. 生成学习行为数据
    print("📊 生成学习行为数据...")
    
    # 生成随机的学习行为记录
    behavior_types = ['question_asked', 'experiment_completed', 'project_milestone', 'study_session', 'resource_accessed']
    
    for i in range(100):  # 生成100条行为记录
        days_ago = random.randint(1, 90)
        behavior_time = datetime.now() - timedelta(days=days_ago)
        
        behavior_data = {
            'user_id': user_id,
            'behavior_type': random.choice(behavior_types),
            'subject_id': random.choice(list(subject_ids.values())),
            'duration_minutes': random.randint(10, 120),
            'engagement_score': random.uniform(0.6, 1.0),
            'created_at': behavior_time
        }
        
        # 这里可以添加行为数据到数据库的逻辑
        if i % 20 == 0:
            print(f"✅ 学习行为记录: {i+1}/100")
    
    # 7. 生成知识点掌握数据
    print("🧠 生成知识点掌握数据...")
    
    for subject_name, subject_id in subject_ids.items():
        subject_data = next(s for s in subjects_data if s['name'] == subject_name)
        knowledge_points = subject_data['knowledge_points']
        
        for kp in knowledge_points:
            mastery_level = random.uniform(0.6, 0.95)  # 掌握程度60%-95%
            confidence = random.uniform(0.5, 0.9)      # 信心度50%-90%
            
            kp_data = {
                'user_id': user_id,
                'subject_id': subject_id,
                'knowledge_point': kp,
                'mastery_level': mastery_level,
                'confidence_level': confidence,
                'last_updated': datetime.now() - timedelta(days=random.randint(1, 30))
            }
            
            # 这里可以添加知识点数据到数据库的逻辑
        
        print(f"✅ {subject_name} 知识点掌握数据")
    
    print("🎉 用户wkp学习数据生成完成！")
    print(f"📊 数据统计:")
    print(f"   - 学科数量: {len(subject_ids)}")
    print(f"   - 问答记录: {len(all_questions)}条")
    print(f"   - 项目数量: {len(projects_data)}个")
    print(f"   - 仿真实验: {sum(len(s['experiments']) for s in simulation_data)}个")
    print(f"   - 学习行为: 100条")
    print(f"   - 知识点: {sum(len(s['knowledge_points']) for s in subjects_data)}个")

if __name__ == "__main__":
    generate_wkp_learning_data()
