import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pytest
import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000/api/v1"

# 使用时间戳生成唯一的用户名和邮箱
TS = int(time.time())
TEST_USERNAME = f"testuser_api_{TS}"
TEST_EMAIL = f"testuser_api_{TS}@example.com"
TEST_PASSWORD = "testpassword123456"

@pytest.fixture(scope="module")
def admin_token():
    """获取管理员token"""
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    response = requests.post(f"{BASE_URL}/users/login", data=login_data)
    assert response.status_code == 200, f"管理员登录失败: {response.text}"
    return response.json()["access_token"]

@pytest.fixture(scope="module")
def test_user():
    """注册测试用户"""
    register_data = {
        "username": TEST_USERNAME,
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    response = requests.post(f"{BASE_URL}/users/register", json=register_data)
    assert response.status_code == 200, f"测试用户注册失败: {response.text}"
    return response.json()

@pytest.fixture(scope="module")
def test_user_token(test_user):
    """获取测试用户token"""
    login_data = {
        "username": TEST_USERNAME,
        "password": TEST_PASSWORD
    }
    response = requests.post(f"{BASE_URL}/users/login", data=login_data)
    assert response.status_code == 200, f"测试用户登录失败: {response.text}"
    return response.json()["access_token"]

@pytest.fixture(scope="module")
def test_team(test_user_token):
    """创建测试团队"""
    team_data = {
        "name": f"测试团队_{TS}",
        "description": "这是一个测试团队"
    }
    headers = {"Authorization": f"Bearer {test_user_token}"}
    response = requests.post(f"{BASE_URL}/teams", headers=headers, json=team_data)
    assert response.status_code == 200, f"创建团队失败: {response.text}"
    return response.json()

def test_admin_login(admin_token):
    """测试管理员登录"""
    assert admin_token, "未获取到管理员token"

def test_user_register(test_user):
    """测试用户注册"""
    assert test_user["username"] == TEST_USERNAME
    assert test_user["email"] == TEST_EMAIL

def test_user_login(test_user_token):
    """测试用户登录"""
    assert test_user_token, "未获取到用户token"

def test_create_team(test_team):
    """测试创建团队"""
    assert test_team["name"].startswith("测试团队_")
    assert test_team["description"] == "这是一个测试团队"

def test_get_team(test_user_token, test_team):
    """测试获取团队信息"""
    headers = {"Authorization": f"Bearer {test_user_token}"}
    response = requests.get(f"{BASE_URL}/teams/{test_team['id']}", headers=headers)
    assert response.status_code == 200, f"获取团队信息失败: {response.text}"
    team = response.json()
    assert team["id"] == test_team["id"]
    assert team["name"] == test_team["name"]
    assert team["description"] == test_team["description"]

def test_update_team(test_user_token, test_team):
    """测试更新团队信息"""
    headers = {"Authorization": f"Bearer {test_user_token}"}
    update_data = {
        "name": f"更新后的团队_{TS}",
        "description": "这是更新后的团队描述"
    }
    response = requests.put(
        f"{BASE_URL}/teams/{test_team['id']}",
        headers=headers,
        json=update_data
    )
    assert response.status_code == 200, f"更新团队信息失败: {response.text}"
    updated_team = response.json()
    assert updated_team["name"] == update_data["name"]
    assert updated_team["description"] == update_data["description"]

def test_delete_team(test_user_token, test_team):
    """测试删除团队"""
    headers = {"Authorization": f"Bearer {test_user_token}"}
    response = requests.delete(f"{BASE_URL}/teams/{test_team['id']}", headers=headers)
    assert response.status_code == 200, f"删除团队失败: {response.text}"

def test_get_nonexistent_team(test_user_token):
    """测试获取不存在的团队"""
    headers = {"Authorization": f"Bearer {test_user_token}"}
    response = requests.get(f"{BASE_URL}/teams/nonexistent_id", headers=headers)
    assert response.status_code == 404, "应该返回404错误"

def test_create_team_without_auth():
    """测试未授权创建团队"""
    team_data = {
        "name": "未授权团队",
        "description": "这是一个未授权创建的团队"
    }
    response = requests.post(f"{BASE_URL}/teams", json=team_data)
    assert response.status_code == 401, "应该返回401错误"

def test_create_team_with_invalid_data(test_user_token):
    """测试使用无效数据创建团队"""
    headers = {"Authorization": f"Bearer {test_user_token}"}
    invalid_data = {
        "name": "",  # 空名称
        "description": "这是一个无效的团队"
    }
    response = requests.post(f"{BASE_URL}/teams", headers=headers, json=invalid_data)
    assert response.status_code == 422, "应该返回422错误"
    error_detail = response.json()
    assert "name" in error_detail["detail"][0]["loc"], "错误信息应该包含name字段"
    assert error_detail["detail"][0]["msg"] == "String should have at least 1 characters", "错误信息应该说明名称不能为空"

if __name__ == "__main__":
    pytest.main(["-v", "test_api.py"]) 