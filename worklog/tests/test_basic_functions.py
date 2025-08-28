import pytest
import requests
import time
from datetime import datetime, timedelta

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
    url = f"{BASE_URL}/users/login"
    data = {
        "username": TEST_USERNAME,
        "password": TEST_PASSWORD
    }
    response = requests.post(url, data=data)
    assert response.status_code == 200, f"用户登录失败: {response.text}"
    return response.json()["access_token"]

@pytest.fixture(scope="module")
def test_team(test_user_token):
    """创建测试团队"""
    url = f"{BASE_URL}/teams"
    headers = {"Authorization": f"Bearer {test_user_token}"}
    data = {
        "name": f"测试团队_auto_{TS}",
        "description": "这是一个自动化测试团队"
    }
    response = requests.post(url, json=data, headers=headers)
    assert response.status_code == 200, f"创建团队失败: {response.text}"
    return response.json()

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

def test_user_register(test_user):
    """测试用户注册"""
    assert test_user["username"] == TEST_USERNAME
    assert test_user["email"] == TEST_EMAIL

def test_user_login(test_user_token):
    """测试用户登录"""
    assert test_user_token, "未获取到token"

def test_create_team(test_team):
    """测试创建团队"""
    assert test_team["name"].startswith("测试团队_auto_")
    assert test_team["description"] == "这是一个自动化测试团队"

def test_invite_unregistered_member(test_user_token, test_team):
    """测试邀请未注册成员"""
    url = f"{BASE_URL}/teams/{test_team['id']}/members"
    headers = {"Authorization": f"Bearer {test_user_token}"}
    data = {
        "email": f"new_member_{TS}@example.com",
        "role": "member"
    }
    response = requests.post(url, json=data, headers=headers)
    assert response.status_code == 200, f"邀请未注册成员失败: {response.text}"

def test_invite_registered_member(test_user_token, test_team, test_member):
    """测试邀请已注册成员"""
    url = f"{BASE_URL}/teams/{test_team['id']}/members"
    headers = {"Authorization": f"Bearer {test_user_token}"}
    data = {
        "user_id": test_member["id"],
        "role": "member"
    }
    response = requests.post(url, json=data, headers=headers)
    assert response.status_code == 200, f"邀请已注册成员失败: {response.text}"

def test_create_work_log(test_user_token, test_team):
    """测试创建工作日志"""
    url = f"{BASE_URL}/work-logs"
    headers = {"Authorization": f"Bearer {test_user_token}"}
    
    start_time = datetime.now()
    end_time = start_time + timedelta(hours=2)
    data = {
        "team_id": test_team["id"],
        "work_type": "development",
        "content": "这是一个测试工作日志",
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "duration": 2.0,
        "remark": "测试备注"
    }
    response = requests.post(url, json=data, headers=headers)
    assert response.status_code == 200, f"创建工作日志失败: {response.text}"
    work_log = response.json()
    assert work_log["work_type"] == "development"
    assert work_log["content"] == "这是一个测试工作日志"
    assert work_log["duration"] == 2.0
    assert work_log["remark"] == "测试备注"

def test_create_work_log_invalid_team(test_user_token):
    """测试在无效团队中创建工作日志"""
    url = f"{BASE_URL}/work-logs"
    headers = {"Authorization": f"Bearer {test_user_token}"}
    
    start_time = datetime.now()
    end_time = start_time + timedelta(hours=2)
    data = {
        "team_id": "invalid_team_id",
        "work_type": "development",
        "content": "这是一个测试工作日志",
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "duration": 2.0,
        "remark": "测试备注"
    }
    response = requests.post(url, json=data, headers=headers)
    assert response.status_code == 404, "应该返回404错误"

def test_create_work_log_invalid_duration(test_user_token, test_team):
    """测试创建无效时长的工作日志"""
    url = f"{BASE_URL}/work-logs"
    headers = {"Authorization": f"Bearer {test_user_token}"}
    
    start_time = datetime.now()
    end_time = start_time + timedelta(hours=2)
    data = {
        "team_id": test_team["id"],
        "work_type": "development",
        "content": "这是一个测试工作日志",
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "duration": -1.0,  # 无效的时长
        "remark": "测试备注"
    }
    response = requests.post(url, json=data, headers=headers)
    assert response.status_code == 422, "应该返回422错误"

if __name__ == "__main__":
    pytest.main(["-v", "test_basic_functions.py"]) 