"""
调试JWT token的脚本
"""

import requests
import json
import jwt
from datetime import datetime

# 使用与应用相同的SECRET_KEY
SECRET_KEY = 'alethea-demo-secret-key-2024'

def test_token_details():
    # 登录获取token
    url = 'http://localhost:8083/api/user/login'
    data = {
        'username_or_email': 'wkp',
        'password': 'wkp123'
    }
    
    response = requests.post(url, json=data)
    print(f"登录状态: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        token = result['token']
        print(f"获得token: {token}")
        
        # 解码token查看内容（不验证签名）
        try:
            decoded = jwt.decode(token, options={"verify_signature": False})
            print(f"Token内容: {json.dumps(decoded, indent=2)}")
            
            # 检查过期时间
            exp = decoded.get('exp')
            if exp:
                exp_time = datetime.fromtimestamp(exp)
                now = datetime.utcnow()
                print(f"Token过期时间: {exp_time}")
                print(f"当前时间: {now}")
                print(f"Token是否过期: {now > exp_time}")
            
        except Exception as e:
            print(f"解码token失败: {e}")
        
        # 测试用户profile API
        headers = {'Authorization': f'Bearer {token}'}
        profile_url = 'http://localhost:8083/api/user/profile'
        profile_response = requests.get(profile_url, headers=headers)
        print(f"\nProfile API状态: {profile_response.status_code}")
        if profile_response.status_code == 200:
            print("Profile API成功")
        else:
            print(f"Profile API错误: {profile_response.text}")
        
        # 测试analytics API
        analytics_url = 'http://localhost:8083/api/analytics/dashboard?days=30'
        analytics_response = requests.get(analytics_url, headers=headers)
        print(f"\nAnalytics API状态: {analytics_response.status_code}")
        if analytics_response.status_code != 200:
            print(f"Analytics API错误: {analytics_response.text}")
        
    else:
        print(f"登录失败: {response.text}")

if __name__ == '__main__':
    test_token_details()
