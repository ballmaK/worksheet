#!/usr/bin/env python3
"""
测试加入团队请求管理功能
"""

import requests
import json

# 配置
BASE_URL = "http://localhost:8000/api/v1"
HEADERS = {
    "Content-Type": "application/json"
}

def test_join_requests_management():
    """测试加入请求管理功能"""
    print("🧪 测试加入团队请求管理功能")
    print("=" * 50)
    
    # 测试1: 获取团队加入申请列表
    print("1. 测试获取团队加入申请列表...")
    try:
        # 这里需要替换为实际的团队ID
        team_id = 1
        response = requests.get(f"{BASE_URL}/teams/{team_id}/join-requests", headers=HEADERS)
        
        if response.status_code == 200:
            requests_list = response.json()
            print(f"   ✅ 获取成功，找到 {len(requests_list)} 个申请")
            for req in requests_list:
                print(f"   📋 申请ID: {req['id']}, 用户: {req['username']}, 状态: {req['status']}")
        elif response.status_code == 403:
            print("   ⚠️  权限不足，需要团队管理员权限")
        else:
            print(f"   ❌ 获取失败: {response.status_code}")
            print(f"   📝 响应: {response.text}")
    except Exception as e:
        print(f"   ❌ 获取异常: {e}")
    
    # 测试2: 批准加入申请
    print("\n2. 测试批准加入申请...")
    try:
        # 这里需要替换为实际的团队ID和申请ID
        team_id = 1
        request_id = 1
        response = requests.put(f"{BASE_URL}/teams/{team_id}/join-requests/{request_id}/approve", headers=HEADERS)
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ 批准成功: {result['message']}")
        elif response.status_code == 403:
            print("   ⚠️  权限不足，需要团队管理员权限")
        elif response.status_code == 404:
            print("   ⚠️  申请不存在")
        else:
            print(f"   ❌ 批准失败: {response.status_code}")
            print(f"   📝 响应: {response.text}")
    except Exception as e:
        print(f"   ❌ 批准异常: {e}")
    
    # 测试3: 拒绝加入申请
    print("\n3. 测试拒绝加入申请...")
    try:
        # 这里需要替换为实际的团队ID和申请ID
        team_id = 1
        request_id = 2
        response = requests.put(f"{BASE_URL}/teams/{team_id}/join-requests/{request_id}/reject", headers=HEADERS)
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ 拒绝成功: {result['message']}")
        elif response.status_code == 403:
            print("   ⚠️  权限不足，需要团队管理员权限")
        elif response.status_code == 404:
            print("   ⚠️  申请不存在")
        else:
            print(f"   ❌ 拒绝失败: {response.status_code}")
            print(f"   📝 响应: {response.text}")
    except Exception as e:
        print(f"   ❌ 拒绝异常: {e}")
    
    print("\n✅ 加入请求管理功能测试完成")
    print("\n📋 API端点清单:")
    print("   ✅ GET /teams/{team_id}/join-requests - 获取加入申请列表")
    print("   ✅ PUT /teams/{team_id}/join-requests/{request_id}/approve - 批准申请")
    print("   ✅ PUT /teams/{team_id}/join-requests/{request_id}/reject - 拒绝申请")

if __name__ == "__main__":
    try:
        test_join_requests_management()
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请确保后端服务正在运行")
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
    
    print("\n🎉 测试完成！")
    print("\n💡 使用说明:")
    print("1. 确保后端服务正在运行")
    print("2. 确保有团队管理员权限")
    print("3. 替换脚本中的团队ID和申请ID为实际值")
    print("4. 在团队管理页面查看加入申请")
