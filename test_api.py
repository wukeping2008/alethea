"""
测试API接口的脚本
"""

import requests
import json

# 测试登录
def test_login():
    url = 'http://localhost:8083/api/user/login'
    data = {
        'username_or_email': 'wkp',
        'password': 'wkp123'
    }
    
    response = requests.post(url, json=data)
    print(f"登录状态: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"登录成功: {result['user']['username']}")
        return result['token']
    else:
        print(f"登录失败: {response.text}")
        return None

# 测试分析API
def test_analytics(token):
    headers = {'Authorization': f'Bearer {token}'}
    
    # 测试dashboard
    url = 'http://localhost:8083/api/analytics/dashboard?days=30'
    response = requests.get(url, headers=headers)
    print(f"Dashboard API状态: {response.status_code}")
    if response.status_code != 200:
        print(f"Dashboard错误: {response.text}")
    
    # 测试portrait
    url = 'http://localhost:8083/api/analytics/portrait'
    response = requests.get(url, headers=headers)
    print(f"Portrait API状态: {response.status_code}")
    if response.status_code != 200:
        print(f"Portrait错误: {response.text}")
    
    # 测试recommendations
    url = 'http://localhost:8083/api/analytics/recommendations'
    response = requests.get(url, headers=headers)
    print(f"Recommendations API状态: {response.status_code}")
    if response.status_code != 200:
        print(f"Recommendations错误: {response.text}")
    
    # 测试knowledge points
    url = 'http://localhost:8083/api/analytics/knowledge-points'
    response = requests.get(url, headers=headers)
    print(f"Knowledge Points API状态: {response.status_code}")
    if response.status_code != 200:
        print(f"Knowledge Points错误: {response.text}")

def main():
    print("开始测试API...")
    
    # 测试登录
    token = test_login()
    
    if token:
        print(f"\n获得token: {token[:50]}...")
        
        # 测试分析API
        test_analytics(token)
    else:
        print("无法获得token，停止测试")

if __name__ == '__main__':
    main()
