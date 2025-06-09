"""
创建wkp用户的脚本，设置正确的密码
"""

import sys
import os

# 添加路径以便导入模块
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from flask import Flask
from models.user import db, User

def create_app():
    """创建Flask应用"""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///alethea.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'demo-key'
    
    db.init_app(app)
    return app

def create_wkp_user():
    """创建wkp用户并设置密码"""
    
    # 检查用户是否已存在
    existing_user = User.query.filter_by(username='wkp').first()
    if existing_user:
        print("用户wkp已存在，更新密码...")
        # 设置密码为 'wkp123'
        existing_user.set_password('wkp123')
        db.session.commit()
        print("密码已更新为: wkp123")
        return existing_user.id
    else:
        print("用户wkp不存在，请先运行generate_demo_user_data.py创建用户")
        return None

def main():
    """主函数"""
    app = create_app()
    
    with app.app_context():
        user_id = create_wkp_user()
        if user_id:
            print(f"\n用户wkp (ID: {user_id}) 密码设置完成")
            print("登录信息:")
            print("用户名: wkp")
            print("密码: wkp123")
        else:
            print("操作失败")

if __name__ == '__main__':
    main()
