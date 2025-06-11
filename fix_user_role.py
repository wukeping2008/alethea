"""
修复wkp用户角色的脚本
"""

import sys
import os

# 添加路径以便导入模块
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from flask import Flask
from models.user import db, User, Role

def create_app():
    """创建Flask应用"""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///alethea.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'demo-key'
    
    db.init_app(app)
    return app

def fix_user_role():
    """修复用户角色"""
    
    # 查找wkp用户
    user = db.session.query(User).filter_by(username='wkp').first()
    if not user:
        print("用户wkp不存在")
        return False
    
    print(f"用户: {user.username}")
    print(f"当前角色ID: {user.role_id}")
    print(f"当前角色: {user.role.name if user.role else '无角色'}")
    
    # 查找student角色
    student_role = db.session.query(Role).filter_by(name='student').first()
    if not student_role:
        print("student角色不存在")
        return False
    
    # 分配角色
    user.role_id = student_role.id
    db.session.commit()
    
    print(f"已将用户{user.username}的角色设置为: {student_role.name}")
    return True

def main():
    """主函数"""
    app = create_app()
    
    with app.app_context():
        success = fix_user_role()
        if success:
            print("用户角色修复完成")
        else:
            print("用户角色修复失败")

if __name__ == '__main__':
    main()
