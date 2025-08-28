import pytest
import requests
import time
from datetime import datetime

# API基础URL
BASE_URL = "http://127.0.0.1:8000/api/v1"

# 使用时间戳生成唯一的用户名和邮箱
TS = int(time.time())
TEST_USERNAME = f"testuser_auto_{TS}"
TEST_EMAIL = f"testuser_auto_{TS}@example.com"
TEST_PASSWORD = "testpassword123456"
MEMBER_USERNAME = f"member_auto_{TS}"
MEMBER_EMAIL = f"member_auto_{TS}@example.com"
MEMBER_PASSWORD = "memberpassword123456"

@pytest.fixture(scope="module")
def test_user():
    """注册测试用户并返回用户信息"""
    url = f"{BASE_URL}/users/register"
    data = {
        "username": TEST_USERNAME,
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    response = requests.post(url, json=data)
    assert response.status_code == 200, f"用户注册失败: {response.text}"
    return response.json()

@pytest.fixture(scope="module")
def test_user_token(test_user):
    """获取测试用户的token"""
    url = f"{BASE_URL}/users/token"
    data = {
        "username": TEST_USERNAME,
        "password": TEST_PASSWORD
    }
    response = requests.post(url, data=data)
    assert response.status_code == 200, f"用户登录失败: {response.text}"
    return response.json()["access_token"]

@pytest.fixture(scope="module")
def test_member():
    """注册测试成员并返回成员信息"""
    url = f"{BASE_URL}/users/register"
    data = {
        "username": MEMBER_USERNAME,
        "email": MEMBER_EMAIL,
        "password": MEMBER_PASSWORD
    }
    response = requests.post(url, json=data)
    assert response.status_code == 200, f"成员注册失败: {response.text}"
    return response.json()

@pytest.fixture(scope="module")
def test_member_token(test_member):
    """获取测试成员的token"""
    url = f"{BASE_URL}/users/token"
    data = {
        "username": MEMBER_USERNAME,
        "password": MEMBER_PASSWORD
    }
    response = requests.post(url, data=data)
    assert response.status_code == 200, f"成员登录失败: {response.text}"
    return response.json()["access_token"]

def test_create_team(test_user_token):
    """测试创建团队"""
    url = f"{BASE_URL}/teams"
    headers = {"Authorization": f"Bearer {test_user_token}"}
    data = {
        "name": f"测试团队_auto_{TS}",
        "description": "这是一个测试团队"
    }
    response = requests.post(url, json=data, headers=headers)
    assert response.status_code == 200, f"创建团队失败: {response.text}"
    data = response.json()
    assert data["name"] == f"测试团队_auto_{TS}"
    assert data["description"] == "这是一个测试团队"
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data
    assert len(data["members"]) == 1  # 创建者自动成为管理员
    return data

def test_create_team_duplicate_name(test_user_token):
    """测试创建重复名称的团队"""
    # 先创建一个团队
    url = f"{BASE_URL}/teams"
    headers = {"Authorization": f"Bearer {test_user_token}"}
    data = {
        "name": f"重复团队_auto_{TS}",
        "description": "这是一个测试团队"
    }
    response = requests.post(url, json=data, headers=headers)
    assert response.status_code == 200
    
    # 尝试创建同名团队
    response = requests.post(url, json=data, headers=headers)
    assert response.status_code == 400
    assert "团队名称已存在" in response.json()["detail"]

def test_get_teams(test_user_token):
    """测试获取团队列表"""
    # 创建两个团队
    url = f"{BASE_URL}/teams"
    headers = {"Authorization": f"Bearer {test_user_token}"}
    
    # 创建第一个团队
    data1 = {
        "name": f"测试团队1_auto_{TS}",
        "description": "这是测试团队1"
    }
    response = requests.post(url, json=data1, headers=headers)
    assert response.status_code == 200
    
    # 创建第二个团队
    data2 = {
        "name": f"测试团队2_auto_{TS}",
        "description": "这是测试团队2"
    }
    response = requests.post(url, json=data2, headers=headers)
    assert response.status_code == 200
    
    # 获取团队列表
    response = requests.get(url, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2
    team_names = [team["name"] for team in data]
    assert f"测试团队1_auto_{TS}" in team_names
    assert f"测试团队2_auto_{TS}" in team_names

def test_get_team(test_user_token):
    """测试获取单个团队"""
    # 创建一个团队
    url = f"{BASE_URL}/teams"
    headers = {"Authorization": f"Bearer {test_user_token}"}
    data = {
        "name": f"测试团队_auto_{TS}",
        "description": "这是一个测试团队"
    }
    create_response = requests.post(url, json=data, headers=headers)
    assert create_response.status_code == 200
    team_id = create_response.json()["id"]
    
    # 获取团队详情
    response = requests.get(f"{url}/{team_id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == f"测试团队_auto_{TS}"
    assert data["description"] == "这是一个测试团队"
    assert data["id"] == team_id

def test_update_team(test_user_token):
    """测试更新团队"""
    # 创建一个团队
    url = f"{BASE_URL}/teams"
    headers = {"Authorization": f"Bearer {test_user_token}"}
    data = {
        "name": f"测试团队_auto_{TS}",
        "description": "这是一个测试团队"
    }
    create_response = requests.post(url, json=data, headers=headers)
    assert create_response.status_code == 200
    team_id = create_response.json()["id"]
    
    # 更新团队
    update_data = {
        "name": f"更新后的团队_auto_{TS}",
        "description": "这是更新后的团队"
    }
    response = requests.put(f"{url}/{team_id}", json=update_data, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == f"更新后的团队_auto_{TS}"
    assert data["description"] == "这是更新后的团队"

def test_delete_team(test_user_token):
    """测试删除团队"""
    # 创建一个团队
    url = f"{BASE_URL}/teams"
    headers = {"Authorization": f"Bearer {test_user_token}"}
    data = {
        "name": f"测试团队_auto_{TS}",
        "description": "这是一个测试团队"
    }
    create_response = requests.post(url, json=data, headers=headers)
    assert create_response.status_code == 200
    team_id = create_response.json()["id"]
    
    # 删除团队
    response = requests.delete(f"{url}/{team_id}", headers=headers)
    assert response.status_code == 200
    
    # 验证团队已被删除
    response = requests.get(f"{url}/{team_id}", headers=headers)
    assert response.status_code == 404

def test_add_team_member(test_user_token, test_member):
    """测试添加团队成员"""
    # 创建一个团队
    url = f"{BASE_URL}/teams"
    headers = {"Authorization": f"Bearer {test_user_token}"}
    data = {
        "name": f"测试团队_auto_{TS}",
        "description": "这是一个测试团队"
    }
    create_response = requests.post(url, json=data, headers=headers)
    assert create_response.status_code == 200
    team_id = create_response.json()["id"]
    
    # 添加团队成员
    response = requests.post(
        f"{url}/{team_id}/members",
        headers=headers,
        json={
            "user_id": test_member["id"],
            "role": "member"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == test_member["id"]
    assert data["role"] == "member"

def test_remove_team_member(test_user_token, test_member):
    """测试移除团队成员"""
    # 创建一个团队
    url = f"{BASE_URL}/teams"
    headers = {"Authorization": f"Bearer {test_user_token}"}
    data = {
        "name": f"测试团队_auto_{TS}",
        "description": "这是一个测试团队"
    }
    create_response = requests.post(url, json=data, headers=headers)
    assert create_response.status_code == 200
    team_id = create_response.json()["id"]
    
    # 添加团队成员
    response = requests.post(
        f"{url}/{team_id}/members",
        headers=headers,
        json={
            "user_id": test_member["id"],
            "role": "member"
        }
    )
    assert response.status_code == 200
    
    # 移除团队成员
    response = requests.delete(
        f"{url}/{team_id}/members/{test_member['id']}",
        headers=headers
    )
    assert response.status_code == 200
    
    # 验证成员已被移除
    response = requests.get(f"{url}/{team_id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data["members"]) == 1  # 只剩下创建者

def test_team_permissions(test_user_token, test_member_token):
    """测试团队权限"""
    # 创建一个团队
    url = f"{BASE_URL}/teams"
    headers = {"Authorization": f"Bearer {test_user_token}"}
    data = {
        "name": f"测试团队_auto_{TS}",
        "description": "这是一个测试团队"
    }
    create_response = requests.post(url, json=data, headers=headers)
    assert create_response.status_code == 200
    team_id = create_response.json()["id"]
    
    # 普通成员尝试更新团队
    member_headers = {"Authorization": f"Bearer {test_member_token}"}
    response = requests.put(
        f"{url}/{team_id}",
        headers=member_headers,
        json={
            "name": "未授权的更新",
            "description": "这是未授权的更新"
        }
    )
    assert response.status_code == 403
    
    # 普通成员尝试删除团队
    response = requests.delete(
        f"{url}/{team_id}",
        headers=member_headers
    )
    assert response.status_code == 403

if __name__ == "__main__":
    pytest.main(["-v", "test_team.py"]) 