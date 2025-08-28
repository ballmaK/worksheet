import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import asyncio
import requests
import json
import time
import pytest

BASE_URL = "http://localhost:8000/api/v1"

# 使用时间戳生成唯一的用户名
TS = int(time.time())
USERNAME_A = f"testuserA_{TS}"
EMAIL_A = f"testuserA_{TS}@example.com"
USERNAME_B = f"testuserB_{TS}"
EMAIL_B = f"testuserB_{TS}@example.com"
PASSWORD = "test12345678"

def cleanup_test_data():
    """清理测试数据"""
    try:
        # 1. 登录获取token
        login_data = {
            "username": USERNAME_A,
            "password": PASSWORD
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        response = requests.post(f"{BASE_URL}/users/login", data=login_data, headers=headers)
        if response.status_code != 200:
            print("清理数据时登录失败，可能是用户不存在")
            return
        token = response.json().get("access_token")
        if not token:
            print("清理数据时未获取到token")
            return
        headers = {"Authorization": f"Bearer {token}"}

        # 2. 获取所有团队
        response = requests.get(f"{BASE_URL}/teams", headers=headers)
        if response.status_code != 200:
            print("获取团队列表失败")
            return
        teams = response.json()
        
        # 3. 删除所有测试团队
        for team in teams:
            if team["name"].startswith("测试团队"):
                response = requests.delete(f"{BASE_URL}/teams/{team['id']}", headers=headers)
                if response.status_code != 200:
                    print(f"删除团队 {team['name']} 失败")
    except Exception as e:
        print(f"清理数据时发生错误: {str(e)}")

@pytest.fixture(scope="module")
def user_a_token():
    """注册并登录用户A，返回token"""
    # 注册用户A
    register_data_a = {
        "username": USERNAME_A,
        "email": EMAIL_A,
        "password": PASSWORD
    }
    response = requests.post(f"{BASE_URL}/users/register", json=register_data_a)
    assert response.status_code == 200, f"用户A注册失败，错误信息: {response.json().get('detail', '未知错误')}"

    # 登录A获取token
    login_data_a = {
        "username": USERNAME_A,
        "password": PASSWORD
    }
    headers_a = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(f"{BASE_URL}/users/login", data=login_data_a, headers=headers_a)
    assert response.status_code == 200, f"用户A登录失败，错误信息: {response.json().get('detail', '未知错误')}"
    token_a = response.json().get("access_token")
    assert token_a, "用户A未获取到token"
    return token_a

@pytest.fixture(scope="module")
def user_b_token():
    """注册并登录用户B，返回token"""
    # 注册用户B
    register_data_b = {
        "username": USERNAME_B,
        "email": EMAIL_B,
        "password": PASSWORD
    }
    response = requests.post(f"{BASE_URL}/users/register", json=register_data_b)
    assert response.status_code == 200, f"用户B注册失败，错误信息: {response.json().get('detail', '未知错误')}"

    # 登录B获取token
    login_data_b = {
        "username": USERNAME_B,
        "password": PASSWORD
    }
    headers_b = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(f"{BASE_URL}/users/login", data=login_data_b, headers=headers_b)
    assert response.status_code == 200, f"用户B登录失败，错误信息: {response.json().get('detail', '未知错误')}"
    token_b = response.json().get("access_token")
    assert token_b, "用户B未获取到token"
    return token_b

@pytest.fixture(scope="module")
def user_a_id(user_a_token):
    """获取用户A的ID"""
    headers_a = {"Authorization": f"Bearer {user_a_token}"}
    response = requests.get(f"{BASE_URL}/users/me", headers=headers_a)
    assert response.status_code == 200, f"获取用户A信息失败，错误信息: {response.json().get('detail', '未知错误')}"
    user_a = response.json()
    user_id_a = user_a.get("id")
    assert user_id_a, "未获取到用户A ID"
    return user_id_a

@pytest.fixture(scope="module")
def user_b_id(user_b_token):
    """获取用户B的ID"""
    headers_b = {"Authorization": f"Bearer {user_b_token}"}
    response = requests.get(f"{BASE_URL}/users/me", headers=headers_b)
    assert response.status_code == 200, f"获取用户B信息失败，错误信息: {response.json().get('detail', '未知错误')}"
    user_b = response.json()
    user_id_b = user_b.get("id")
    assert user_id_b, "未获取到用户B ID"
    return user_id_b

@pytest.fixture(scope="module")
def team_id(user_a_token):
    """创建测试团队，返回团队ID"""
    team_name = f"测试团队_{TS}"
    team_data = {
        "name": team_name,
        "description": "用于测试的团队"
    }
    headers_a = {"Authorization": f"Bearer {user_a_token}"}
    response = requests.post(f"{BASE_URL}/teams", json=team_data, headers=headers_a)
    assert response.status_code == 200, f"创建团队失败，错误信息: {response.json().get('detail', '未知错误')}"
    team_id = response.json().get("id")
    assert team_id, "未获取到团队ID"
    return team_id

def test_register_user_a():
    """测试注册用户A"""
    register_data_a = {
        "username": USERNAME_A,
        "email": EMAIL_A,
        "password": PASSWORD
    }
    response = requests.post(f"{BASE_URL}/users/register", json=register_data_a)
    assert response.status_code == 200, f"用户A注册失败，错误信息: {response.json().get('detail', '未知错误')}"

def test_register_user_b():
    """测试注册用户B"""
    register_data_b = {
        "username": USERNAME_B,
        "email": EMAIL_B,
        "password": PASSWORD
    }
    response = requests.post(f"{BASE_URL}/users/register", json=register_data_b)
    assert response.status_code == 200, f"用户B注册失败，错误信息: {response.json().get('detail', '未知错误')}"

def test_login_user_a(user_a_token):
    """测试用户A登录"""
    assert user_a_token, "用户A登录失败，未获取到token"

def test_login_user_b(user_b_token):
    """测试用户B登录"""
    assert user_b_token, "用户B登录失败，未获取到token"

def test_get_user_a_info(user_a_id):
    """测试获取用户A信息"""
    assert user_a_id, "未获取到用户A ID"

def test_get_user_b_info(user_b_id):
    """测试获取用户B信息"""
    assert user_b_id, "未获取到用户B ID"

def test_create_team(team_id):
    """测试创建团队"""
    assert team_id, "未获取到团队ID"

def test_invite_registered_user(user_a_token, team_id, user_b_id):
    """测试邀请已注册用户B"""
    headers_a = {"Authorization": f"Bearer {user_a_token}"}
    member_data = {
        "user_id": user_b_id,
        "role": "member"
    }
    response = requests.post(
        f"{BASE_URL}/teams/{team_id}/members",
        json=member_data,
        headers=headers_a
    )
    assert response.status_code == 200, f"邀请已注册用户B失败，错误信息: {response.json().get('detail', '未知错误')}"

def test_invite_unregistered_user(user_a_token, team_id):
    """测试邀请未注册用户"""
    headers_a = {"Authorization": f"Bearer {user_a_token}"}
    member_data = {
        "email": "378975390@qq.com",
        "role": "member"
    }
    response = requests.post(
        f"{BASE_URL}/teams/{team_id}/members",
        json=member_data,
        headers=headers_a
    )
    assert response.status_code == 200, f"邀请未注册用户失败，错误信息: {response.json().get('detail', '未知错误')}"

if __name__ == "__main__":
    pytest.main(["-v", "test_team_invite.py"]) 