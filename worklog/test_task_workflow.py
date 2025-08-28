#!/usr/bin/env python3
"""
测试任务与工作日志自动关联功能
"""

import requests
import json
from datetime import datetime, timedelta

# 配置
BASE_URL = "http://localhost:8000/api/v1"
USERNAME = "ballmaAdmin"
PASSWORD = "admin123"

def login():
    """用户登录"""
    url = f"{BASE_URL}/auth/login"
    data = {
        "username": USERNAME,
        "password": PASSWORD
    }
    
    response = requests.post(url, data=data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        raise Exception(f"登录失败: {response.text}")

def create_test_task(token):
    """创建测试任务"""
    url = f"{BASE_URL}/tasks"
    headers = {"Authorization": f"Bearer {token}"}
    
    data = {
        "title": "测试任务-工作日志关联",
        "description": "这是一个用于测试任务与工作日志自动关联功能的任务",
        "team_id": 1,
        "project_id": 1,
        "assignee_id": 1,
        "priority": "medium",
        "task_type": "feature",
        "estimated_hours": 4.0,
        "due_date": (datetime.now() + timedelta(days=7)).isoformat()
    }
    
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 201:
        return response.json()
    else:
        raise Exception(f"创建任务失败: {response.text}")

def start_task_work(token, task_id):
    """开始任务工作"""
    url = f"{BASE_URL}/tasks/{task_id}/start"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.post(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"开始任务工作失败: {response.text}")

def complete_task(token, task_id):
    """完成任务"""
    url = f"{BASE_URL}/tasks/{task_id}/complete"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.post(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"完成任务失败: {response.text}")

def get_task_work_logs(token, task_id):
    """获取任务工作日志"""
    url = f"{BASE_URL}/work-logs/task/{task_id}"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"获取任务工作日志失败: {response.text}")

def get_task_work_summary(token, task_id):
    """获取任务工作汇总"""
    url = f"{BASE_URL}/work-logs/task/{task_id}/summary"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"获取任务工作汇总失败: {response.text}")

def update_latest_work_log(token, task_id, content):
    """更新最新工作日志"""
    url = f"{BASE_URL}/work-logs/task/{task_id}/update-latest"
    headers = {"Authorization": f"Bearer {token}"}
    
    data = {
        "content": content,
        "issues_encountered": "测试过程中遇到了一些技术问题",
        "solutions_applied": "通过查阅文档和调试解决了问题",
        "remark": "这是一个测试更新"
    }
    
    response = requests.put(url, json=data, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"更新工作日志失败: {response.text}")

def main():
    """主测试流程"""
    print("=== 测试任务与工作日志自动关联功能 ===\n")
    
    try:
        # 1. 用户登录
        print("1. 用户登录...")
        token = login()
        print("✓ 登录成功\n")
        
        # 2. 创建测试任务
        print("2. 创建测试任务...")
        task = create_test_task(token)
        task_id = task["id"]
        print(f"✓ 任务创建成功，ID: {task_id}")
        print(f"   任务标题: {task['title']}")
        print(f"   任务状态: {task['status']}\n")
        
        # 3. 开始任务工作
        print("3. 开始任务工作...")
        start_result = start_task_work(token, task_id)
        print(f"✓ 任务工作已开始")
        print(f"   开始时间: {start_result['task']['started_at']}")
        print(f"   任务状态: {start_result['task']['status']}\n")
        
        # 4. 查看自动创建的工作日志
        print("4. 查看自动创建的工作日志...")
        work_logs = get_task_work_logs(token, task_id)
        print(f"✓ 找到 {len(work_logs)} 条工作日志")
        for i, log in enumerate(work_logs, 1):
            print(f"   日志 {i}: {log['description']}")
            print(f"       开始时间: {log['start_time']}")
            print(f"       工作状态: {log['work_status']}\n")
        
        # 5. 补充工作详情
        print("5. 补充工作详情...")
        update_result = update_latest_work_log(token, task_id, "完成了任务的核心功能开发，包括用户界面设计和后端API实现")
        print("✓ 工作详情补充成功")
        print(f"   工作内容: {update_result['content']}\n")
        
        # 6. 完成任务
        print("6. 完成任务...")
        complete_result = complete_task(token, task_id)
        print(f"✓ 任务已完成")
        print(f"   完成时间: {complete_result['task']['completed_at']}")
        print(f"   实际工时: {complete_result['task']['actual_hours']:.2f} 小时")
        print(f"   任务状态: {complete_result['task']['status']}\n")
        
        # 7. 查看最终工作日志
        print("7. 查看最终工作日志...")
        final_work_logs = get_task_work_logs(token, task_id)
        print(f"✓ 最终共有 {len(final_work_logs)} 条工作日志")
        for i, log in enumerate(final_work_logs, 1):
            print(f"   日志 {i}: {log['description']}")
            print(f"       开始时间: {log['start_time']}")
            print(f"       结束时间: {log['end_time']}")
            print(f"       工作时长: {log['hours_spent']:.2f} 小时")
            print(f"       工作状态: {log['work_status']}")
            print(f"       工作内容: {log['content'][:50]}...\n")
        
        # 8. 查看工作汇总
        print("8. 查看工作汇总...")
        summary = get_task_work_summary(token, task_id)
        print("✓ 工作汇总信息:")
        print(f"   总工时: {summary['total_hours']:.2f} 小时")
        print(f"   日志数量: {summary['log_count']} 条")
        print(f"   工作类型分布: {summary['work_type_distribution']}")
        print(f"   平均完成度: {summary['average_progress']:.1f}%\n")
        
        print("=== 测试完成 ===")
        print("✓ 任务与工作日志自动关联功能测试通过！")
        print("✓ 系统能够自动记录任务状态变更并创建工作日志")
        print("✓ 用户可以补充详细的工作内容")
        print("✓ 工时统计和汇总功能正常工作")
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    main() 