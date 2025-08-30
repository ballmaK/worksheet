#!/usr/bin/env python3
"""
测试团队API的脚本
"""
import requests
import json

# 配置
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

def test_team_api():
    """测试团队API"""
    print("=== 测试团队API ===")
    
    # 1. 测试获取团队列表
    print("\n1. 测试获取团队列表...")
    try:
        response = requests.get(f"{API_BASE}/teams")
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            teams = response.json()
            print(f"团队数量: {len(teams)}")
            for team in teams:
                print(f"  - 团队ID: {team['id']}, 名称: {team['name']}")
        else:
            print(f"错误: {response.text}")
    except Exception as e:
        print(f"请求失败: {e}")
    
    # 2. 测试获取团队详情（需要认证）
    print("\n2. 测试获取团队详情...")
    print("注意: 这个测试需要有效的认证token")
    
    # 这里可以添加认证逻辑
    # headers = {"Authorization": f"Bearer {token}"}
    # response = requests.get(f"{API_BASE}/teams/1", headers=headers)
    
    print("请手动测试团队详情API")

if __name__ == "__main__":
    test_team_api()
