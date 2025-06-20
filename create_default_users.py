#!/usr/bin/env python3
"""
创建默认用户账户的脚本
用于在阿里云部署后初始化教师和管理员账户
"""

import sys
import os
import json

# 添加项目路径
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# 设置工作目录
os.chdir(os.path.dirname(__file__))

from src.main import app, db
from src.models.user import User, Role

def create_default_users():
    """创建默认用户账户"""
    with app.app_context():
        try:
            # 获取用户管理器
            user_manager = app.user_managers['user_manager']
            
            # 检查是否已存在管理员账户
            admin_exists = db.session.query(User).join(Role).filter(Role.name == 'admin').first()
            teacher_exists = db.session.query(User).join(Role).filter(Role.name == 'teacher').first()
            
            created_users = []
            
            # 创建管理员账户
            if not admin_exists:
                print("创建管理员账户...")
                success, result = user_manager.create_user(
                    username='admin',
                    email='admin@alethea.edu',
                    password='admin123',
                    full_name='系统管理员',
                    role_name='admin'
                )
                
                if success:
                    print(f"✓ 管理员账户创建成功 (ID: {result})")
                    created_users.append({
                        'username': 'admin',
                        'password': 'admin123',
                        'role': 'admin',
                        'email': 'admin@alethea.edu'
                    })
                else:
                    print(f"✗ 管理员账户创建失败: {result}")
            else:
                print("✓ 管理员账户已存在")
            
            # 创建教师账户
            if not teacher_exists:
                print("创建教师账户...")
                success, result = user_manager.create_user(
                    username='teacher',
                    email='teacher@alethea.edu',
                    password='teacher123',
                    full_name='教师用户',
                    role_name='teacher'
                )
                
                if success:
                    print(f"✓ 教师账户创建成功 (ID: {result})")
                    created_users.append({
                        'username': 'teacher',
                        'password': 'teacher123',
                        'role': 'teacher',
                        'email': 'teacher@alethea.edu'
                    })
                else:
                    print(f"✗ 教师账户创建失败: {result}")
            else:
                print("✓ 教师账户已存在")
            
            # 创建额外的测试账户
            test_accounts = [
                {
                    'username': 'admin_test',
                    'email': 'admin_test@alethea.edu',
                    'password': 'admin123',
                    'full_name': '测试管理员',
                    'role_name': 'admin'
                },
                {
                    'username': 'teacher_test',
                    'email': 'teacher_test@alethea.edu',
                    'password': 'teacher123',
                    'full_name': '测试教师',
                    'role_name': 'teacher'
                },
                {
                    'username': 'student_test',
                    'email': 'student_test@alethea.edu',
                    'password': 'student123',
                    'full_name': '测试学生',
                    'role_name': 'student'
                }
            ]
            
            for account in test_accounts:
                # 检查用户是否已存在
                existing = db.session.query(User).filter(
                    (User.username == account['username']) | (User.email == account['email'])
                ).first()
                
                if not existing:
                    print(f"创建测试账户: {account['username']}...")
                    success, result = user_manager.create_user(
                        username=account['username'],
                        email=account['email'],
                        password=account['password'],
                        full_name=account['full_name'],
                        role_name=account['role_name']
                    )
                    
                    if success:
                        print(f"✓ 测试账户 {account['username']} 创建成功")
                        created_users.append({
                            'username': account['username'],
                            'password': account['password'],
                            'role': account['role_name'],
                            'email': account['email']
                        })
                    else:
                        print(f"✗ 测试账户 {account['username']} 创建失败: {result}")
                else:
                    print(f"✓ 测试账户 {account['username']} 已存在")
            
            # 输出创建的账户信息
            if created_users:
                print("\n" + "="*60)
                print("新创建的用户账户信息:")
                print("="*60)
                for user in created_users:
                    print(f"用户名: {user['username']}")
                    print(f"密码: {user['password']}")
                    print(f"角色: {user['role']}")
                    print(f"邮箱: {user['email']}")
                    print("-" * 40)
                
                # 保存账户信息到文件
                with open('default_accounts.json', 'w', encoding='utf-8') as f:
                    json.dump(created_users, f, ensure_ascii=False, indent=2)
                print("账户信息已保存到 default_accounts.json")
            
            print("\n✓ 默认用户创建完成!")
            
            # 显示所有用户统计
            total_users = db.session.query(User).count()
            admin_count = db.session.query(User).join(Role).filter(Role.name == 'admin').count()
            teacher_count = db.session.query(User).join(Role).filter(Role.name == 'teacher').count()
            student_count = db.session.query(User).join(Role).filter(Role.name == 'student').count()
            
            print(f"\n当前用户统计:")
            print(f"总用户数: {total_users}")
            print(f"管理员: {admin_count}")
            print(f"教师: {teacher_count}")
            print(f"学生: {student_count}")
            
        except Exception as e:
            print(f"创建默认用户时出错: {str(e)}")
            import traceback
            traceback.print_exc()

def verify_users():
    """验证用户账户是否可以正常登录"""
    with app.app_context():
        try:
            user_manager = app.user_managers['user_manager']
            
            test_accounts = [
                {'username': 'admin', 'password': 'admin123'},
                {'username': 'teacher', 'password': 'teacher123'},
                {'username': 'admin_test', 'password': 'admin123'},
                {'username': 'teacher_test', 'password': 'teacher123'},
                {'username': 'student_test', 'password': 'student123'}
            ]
            
            print("\n" + "="*60)
            print("验证用户登录:")
            print("="*60)
            
            for account in test_accounts:
                success, result = user_manager.authenticate_user(
                    account['username'], 
                    account['password']
                )
                
                if success:
                    user_data = result['user']
                    print(f"✓ {account['username']} - 登录成功 (角色: {user_data.get('role', 'unknown')})")
                else:
                    print(f"✗ {account['username']} - 登录失败: {result}")
            
        except Exception as e:
            print(f"验证用户登录时出错: {str(e)}")

if __name__ == '__main__':
    print("Alethea 默认用户创建脚本")
    print("="*60)
    
    # 初始化应用
    from src.main import initialize_app
    initialize_app()
    
    # 创建默认用户
    create_default_users()
    
    # 验证用户登录
    verify_users()
    
    print("\n脚本执行完成!")
    print("\n重要提示:")
    print("1. 请妥善保管账户信息")
    print("2. 建议在生产环境中修改默认密码")
    print("3. 可以使用这些账户登录系统测试功能")
