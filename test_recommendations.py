"""
测试项目推荐功能
"""

import sys
import os
import json

# 添加路径以便导入模块
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from flask import Flask
from models.user import db, User
from models.user_analytics import UserAnalyticsManager

def create_app():
    """创建Flask应用"""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///alethea.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'test-key'
    
    db.init_app(app)
    return app

def test_recommendations():
    """测试项目推荐功能"""
    app = create_app()
    
    with app.app_context():
        # 获取测试用户
        test_user = User.query.filter_by(username='demo_student').first()
        if not test_user:
            print("测试用户不存在，请先运行 generate_test_data.py")
            return
        
        print(f"为用户 {test_user.username} (ID: {test_user.id}) 生成项目推荐...")
        
        # 创建分析管理器
        analytics_manager = UserAnalyticsManager(db)
        
        # 生成项目推荐
        success, recommendations = analytics_manager.generate_project_recommendations(test_user.id)
        
        if success:
            print(f"\n成功生成 {len(recommendations)} 个项目推荐：")
            for i, rec in enumerate(recommendations, 1):
                print(f"\n{i}. {rec['project_title']}")
                print(f"   推荐分数: {rec['recommendation_score']:.2f}")
                print(f"   推荐理由: {rec['recommendation_reason']}")
                print(f"   难度匹配: {rec['difficulty_match']:.2f}")
                print(f"   兴趣匹配: {rec['interest_match']:.2f}")
                print(f"   技能发展: {', '.join(rec['skill_development'])}")
        else:
            print(f"生成推荐失败: {recommendations}")
        
        # 获取保存的推荐
        success, saved_recs = analytics_manager.get_user_recommendations(test_user.id)
        if success:
            print(f"\n数据库中保存了 {len(saved_recs)} 个推荐")
        
        print("\n测试完成！")

if __name__ == '__main__':
    test_recommendations()
