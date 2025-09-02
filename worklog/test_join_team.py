#!/usr/bin/env python3
"""
测试加入团队功能
"""

import requests
import json

# 配置
BASE_URL = "http://localhost:8000/api/v1"
HEADERS = {
    "Content-Type": "application/json"
}

def test_search_teams():
    """测试搜索公开团队"""
    print("🔍 测试搜索公开团队...")
    
    # 搜索所有团队
    response = requests.get(f"{BASE_URL}/teams/search/public", headers=HEADERS)
    
    if response.status_code == 200:
        teams = response.json()
        print(f"✅ 搜索成功，找到 {len(teams)} 个团队")
        for team in teams:
            print(f"  - {team['name']}: {team['description']}")
            print(f"    成员: {team['member_count']}, 项目: {team['project_count']}")
    else:
        print(f"❌ 搜索失败: {response.status_code}")
        print(response.text)

def test_join_team():
    """测试申请加入团队"""
    print("\n🚀 测试申请加入团队...")
    
    # 先搜索团队
    response = requests.get(f"{BASE_URL}/teams/search/public", headers=HEADERS)
    if response.status_code != 200:
        print("❌ 无法获取团队列表")
        return
    
    teams = response.json()
    if not teams:
        print("❌ 没有可加入的团队")
        return
    
    # 选择第一个团队进行测试
    team = teams[0]
    print(f"选择团队: {team['name']}")
    
    # 申请加入
    join_data = {
        "message": "我想加入这个团队，因为我对团队的项目很感兴趣，希望能贡献自己的力量。"
    }
    
    response = requests.post(
        f"{BASE_URL}/teams/{team['id']}/join",
        headers=HEADERS,
        json=join_data
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ 申请成功: {result['message']}")
        if result.get('application_id'):
            print(f"申请ID: {result['application_id']}")
    else:
        print(f"❌ 申请失败: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    print("🧪 加入团队功能测试")
    print("=" * 50)
    
    try:
        test_search_teams()
        test_join_team()
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请确保后端服务正在运行")
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
    
    print("\n✅ 测试完成")
