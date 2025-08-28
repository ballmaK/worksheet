#!/usr/bin/env python3
"""
测试完整的团队邀请流程（包括验证码验证）
"""
import requests
import json
import time

# 配置
BASE_URL = "http://localhost:8000/api/v1"
TEST_EMAIL = "test_invite_new@example.com"

def test_complete_invite_flow():
    """测试完整的邀请流程"""
    print("=== 开始测试完整团队邀请流程 ===\n")
    
    # 1. 登录获取token
    print("1. 登录获取token...")
    login_data = {
        "username": "ballmaAdmin",
        "password": "123456"
    }
    
    response = requests.post(f"{BASE_URL}/users/token", data=login_data)
    if response.status_code != 200:
        print(f"登录失败: {response.status_code} - {response.text}")
        return
    
    token_data = response.json()
    access_token = token_data["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    print("登录成功，获取到token\n")
    
    # 2. 获取团队列表
    print("2. 获取团队列表...")
    response = requests.get(f"{BASE_URL}/teams", headers=headers)
    if response.status_code != 200:
        print(f"获取团队列表失败: {response.status_code} - {response.text}")
        return
    
    teams = response.json()
    if not teams:
        print("没有找到团队，请先创建团队")
        return
    
    team_id = teams[0]["id"]
    team_name = teams[0]["name"]
    print(f"找到团队: {team_name} (ID: {team_id})\n")
    
    # 3. 发送邀请
    print("3. 发送邀请...")
    invite_data = {
        "email": TEST_EMAIL,
        "role": "team_member"
    }
    
    response = requests.post(f"{BASE_URL}/teams/{team_id}/invite", 
                           json=invite_data, headers=headers)
    
    if response.status_code == 400 and "已有未过期的邀请" in response.text:
        print("该邮箱已有未过期的邀请，尝试重新发送...")
        
        # 获取邀请列表
        response = requests.get(f"{BASE_URL}/teams/{team_id}/invites", headers=headers)
        if response.status_code == 200:
            invites = response.json()
            for invite in invites:
                if invite["email"] == TEST_EMAIL and invite["status"] == "pending":
                    # 重新发送邀请
                    response = requests.post(f"{BASE_URL}/teams/invite/{invite['id']}/resend", 
                                           headers=headers)
                    if response.status_code == 200:
                        print("重新发送邀请成功")
                        break
    elif response.status_code == 200:
        print("发送邀请成功")
    else:
        print(f"发送邀请失败: {response.status_code} - {response.text}")
        return
    
    # 4. 获取邀请列表，找到验证码
    print("\n4. 获取邀请列表...")
    response = requests.get(f"{BASE_URL}/teams/{team_id}/invites", headers=headers)
    if response.status_code == 200:
        invites = response.json()
        for invite in invites:
            if invite["email"] == TEST_EMAIL and invite["status"] == "pending":
                verification_code = invite["token"]  # 验证码存储在token字段中
                print(f"找到邀请，验证码: {verification_code}")
                break
        else:
            print("未找到对应的邀请记录")
            return
    else:
        print(f"获取邀请列表失败: {response.status_code}")
        return
    
    # 5. 测试验证邀请（模拟新用户）
    print("\n5. 测试验证邀请（新用户）...")
    verify_data = {
        "email": TEST_EMAIL,
        "verification_code": verification_code,
        "username": "testuser_new",
        "password": "123456"
    }
    
    response = requests.post(f"{BASE_URL}/teams/invite/verify", json=verify_data)
    if response.status_code == 200:
        result = response.json()
        print(f"验证成功: {result['message']}")
        print(f"用户创建: {result['user_created']}")
        print(f"团队成员ID: {result['team_member_id']}")
    else:
        print(f"验证失败: {response.status_code} - {response.text}")
    
    print("\n=== 邀请流程测试完成 ===")
    print("请检查邮箱中的验证码邮件")
    print("然后在前端验证邀请页面测试完整流程")

if __name__ == "__main__":
    test_complete_invite_flow() 