import os
import sys
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import time
import uuid

# 修正：将项目根目录加入sys.path，确保app模块能被正确导入
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import app
from app.core.config import settings

client = TestClient(app)

@pytest.fixture
def test_user():
    """创建测试用户并返回用户信息"""
    unique = str(int(time.time()))
    username = f"testuser_{unique}"
    email = f"test_{unique}@example.com"
    password = "testpassword123"
    
    register_data = {
        "username": username,
        "email": email,
        "password": password,
        "full_name": "Test User",
        "department": "测试部门",
        "position": "测试工程师"
    }
    response = client.post("/api/v1/users/register", json=register_data)
    assert response.status_code == 200
    return {"username": username, "password": password}

@pytest.fixture
def test_user_token(test_user):
    """获取测试用户的token"""
    login_data = {
        "username": test_user["username"],
        "password": test_user["password"]
    }
    response = client.post("/api/v1/users/login", data=login_data)
    assert response.status_code == 200
    return response.json()["access_token"]

@pytest.fixture
def test_work_log(test_user_token):
    """创建测试工作日志并返回工作日志信息"""
    headers = {"Authorization": f"Bearer {test_user_token}"}
    start_time = datetime.now()
    end_time = start_time + timedelta(hours=8)
    work_log_data = {
        "work_type": "dev",
        "content": "这是一条测试工作日志的内容",
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "duration": 8.0,
        "remark": "这是一些额外的备注信息",
        "tags": "测试,开发",
        "attachments": ""
    }
    response = client.post("/api/v1/work-logs", json=work_log_data, headers=headers)
    assert response.status_code == 200
    return response.json()

def test_create_work_log(test_user_token):
    """测试创建工作日志"""
    headers = {"Authorization": f"Bearer {test_user_token}"}
    start_time = datetime.now()
    end_time = start_time + timedelta(hours=8)
    work_log_data = {
        "work_type": "dev",
        "content": "这是一条测试工作日志的内容",
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "duration": 8.0,
        "remark": "这是一些额外的备注信息",
        "tags": "测试,开发",
        "attachments": ""
    }
    response = client.post("/api/v1/work-logs", json=work_log_data, headers=headers)
    assert response.status_code == 200
    work_log = response.json()
    assert work_log["work_type"] == work_log_data["work_type"]
    assert work_log["content"] == work_log_data["content"]
    assert abs(work_log["duration"] - work_log_data["duration"]) < 0.01
    assert work_log["remark"] == work_log_data["remark"]
    assert work_log["tags"] == work_log_data["tags"]

def test_get_work_logs(test_user_token, test_work_log):
    """测试获取工作日志列表"""
    headers = {"Authorization": f"Bearer {test_user_token}"}
    response = client.get("/api/v1/work-logs", headers=headers)
    assert response.status_code == 200
    work_logs = response.json()
    assert isinstance(work_logs, list)
    assert len(work_logs) > 0
    
    work_log = work_logs[0]
    required_fields = [
        "id", "work_type", "content", "start_time", "end_time",
        "duration", "remark", "tags", "attachments", "user_id",
        "created_at", "updated_at"
    ]
    for field in required_fields:
        assert field in work_log

def test_update_work_log(test_user_token, test_work_log):
    """测试更新工作日志"""
    headers = {"Authorization": f"Bearer {test_user_token}"}
    work_log_id = test_work_log["id"]
    
    start_time = datetime.now()
    end_time = start_time + timedelta(hours=6)
    update_data = {
        "work_type": "test",
        "content": "这是更新后的工作日志内容",
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "duration": 6.0,
        "remark": "这是更新后的备注信息",
        "tags": "更新,测试",
        "attachments": ""
    }
    response = client.put(f"/api/v1/work-logs/{work_log_id}", json=update_data, headers=headers)
    assert response.status_code == 200
    updated_work_log = response.json()
    assert updated_work_log["work_type"] == update_data["work_type"]
    assert updated_work_log["content"] == update_data["content"]
    assert abs(updated_work_log["duration"] - update_data["duration"]) < 0.01
    assert updated_work_log["remark"] == update_data["remark"]
    assert updated_work_log["tags"] == update_data["tags"]

def test_delete_work_log(test_user_token, test_work_log):
    """测试删除工作日志"""
    headers = {"Authorization": f"Bearer {test_user_token}"}
    work_log_id = test_work_log["id"]
    
    response = client.delete(f"/api/v1/work-logs/{work_log_id}", headers=headers)
    assert response.status_code == 200
    
    response = client.get(f"/api/v1/work-logs/{work_log_id}", headers=headers)
    assert response.status_code == 404 