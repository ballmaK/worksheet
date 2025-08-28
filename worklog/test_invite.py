#!/usr/bin/env python3
"""
测试团队邀请功能（验证码方式）
"""
import requests
import json

def test_team_invite():
    # 后端服务地址
    base_url = "http://localhost:8000"
    
    # 测试数据
    login_data = {
        "username": "ballmaAdmin",
        "password": "123456"
    }
    
    team_id = 1  # 假设团队ID为1
    
    try:
        # 1. 登录获取token
        print("1. 登录获取token...")
        login_response = requests.post(
            f"{base_url}/api/v1/users/token",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if login_response.status_code != 200:
            print(f"登录失败: {login_response.status_code}")
            print(f"响应: {login_response.text}")
            return
        
        token_data = login_response.json()
        access_token = token_data["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}
        
        print(f"登录成功，用户: {token_data['user']['username']}")
        
        # 2. 获取团队详情
        print("\n2. 获取团队详情...")
        team_response = requests.get(
            f"{base_url}/api/v1/teams/{team_id}",
            headers=headers
        )
        
        if team_response.status_code == 200:
            team_data = team_response.json()
            print(f"团队信息: {team_data['name']} - {team_data['description']}")
        else:
            print(f"获取团队失败: {team_response.status_code}")
            print(f"响应: {team_response.text}")
        
        # 3. 获取团队成员
        print("\n3. 获取团队成员...")
        members_response = requests.get(
            f"{base_url}/api/v1/teams/{team_id}/members",
            headers=headers
        )
        
        if members_response.status_code == 200:
            members_data = members_response.json()
            print(f"团队成员数量: {len(members_data)}")
            for member in members_data:
                print(f"  - {member['username']} ({member['role']})")
        else:
            print(f"获取成员失败: {members_response.status_code}")
            print(f"响应: {members_response.text}")
        
        # 4. 获取团队邀请
        print("\n4. 获取团队邀请...")
        invites_response = requests.get(
            f"{base_url}/api/v1/teams/{team_id}/invites",
            headers=headers
        )
        
        if invites_response.status_code == 200:
            invites_data = invites_response.json()
            print(f"团队邀请数量: {len(invites_data)}")
            for invite in invites_data:
                print(f"  - {invite['email']} ({invite['status']}) - 验证码: {invite['token']}")
        else:
            print(f"获取邀请失败: {invites_response.status_code}")
            print(f"响应: {invites_response.text}")
        
        # 5. 发送邀请（验证码方式）
        print("\n5. 发送邀请（验证码方式）...")
        invite_data = {
            "email": "test@example.com",
            "role": "team_member"
        }
        
        invite_response = requests.post(
            f"{base_url}/api/v1/teams/{team_id}/invite",
            json=invite_data,
            headers=headers
        )
        
        if invite_response.status_code == 200:
            invite_result = invite_response.json()
            print(f"邀请发送成功: {invite_result}")
            print(f"验证码: {invite_result.get('token', 'N/A')}")
        else:
            print(f"发送邀请失败: {invite_response.status_code}")
            print(f"响应: {invite_response.text}")
        
        # 6. 测试验证邀请码（需要另一个用户登录）
        print("\n6. 测试验证邀请码...")
        print("注意：验证邀请码需要被邀请的用户登录后操作")
        print("验证API: POST /api/v1/teams/invite/verify")
        print("参数: {email: 'test@example.com', verification_code: '123456'}")
        
    except Exception as e:
        print(f"测试过程中发生错误: {str(e)}")

if __name__ == "__main__":
    test_team_invite() 