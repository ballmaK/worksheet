from fastapi import APIRouter, HTTPException
from typing import Dict, List
import os
from datetime import datetime

router = APIRouter()

# 下载信息配置
DOWNLOAD_INFO = {
    "windows": {
        "name": "WorkLog Pro Windows",
        "version": "1.0.0",
        "filename": "WorkLogPro-Setup-1.0.0.exe",
        "size": "45.2 MB",
        "size_bytes": 47349760,  # 45.2 MB in bytes
        "url": "https://download.worklogpro.com/windows/WorkLogPro-Setup-1.0.0.exe",
        "checksum": "sha256:abc123...",  # 实际使用时需要计算真实的校验和
        "requirements": "Windows 10/11",
        "features": [
            "系统托盘运行",
            "全局快捷键",
            "自动同步数据",
            "离线工作模式"
        ],
        "updated_at": "2025-08-31"
    },
    "macos": {
        "name": "WorkLog Pro macOS",
        "version": "1.0.0",
        "filename": "WorkLogPro-1.0.0.dmg",
        "size": "52.8 MB",
        "size_bytes": 55364812,  # 52.8 MB in bytes
        "url": "https://download.worklogpro.com/macos/WorkLogPro-1.0.0.dmg",
        "checksum": "sha256:def456...",
        "requirements": "macOS 11.0+",
        "features": [
            "菜单栏集成",
            "Touch Bar支持",
            "自动同步数据",
            "离线工作模式"
        ],
        "updated_at": "2025-08-31"
    },
    "linux": {
        "name": "WorkLog Pro Linux",
        "version": "1.0.0",
        "filename": "WorkLogPro-1.0.0.AppImage",
        "size": "38.5 MB",
        "size_bytes": 40370176,  # 38.5 MB in bytes
        "url": "https://download.worklogpro.com/linux/WorkLogPro-1.0.0.AppImage",
        "checksum": "sha256:ghi789...",
        "requirements": "Ubuntu 20.04+",
        "features": [
            "系统托盘运行",
            "全局快捷键",
            "自动同步数据",
            "离线工作模式"
        ],
        "updated_at": "2025-08-31"
    }
}

@router.get("/downloads")
async def get_downloads() -> Dict[str, dict]:
    """
    获取所有可用的下载版本信息
    """
    return {
        "status": "success",
        "data": DOWNLOAD_INFO,
        "timestamp": datetime.now().isoformat()
    }

@router.get("/downloads/{platform}")
async def get_download_info(platform: str) -> Dict[str, dict]:
    """
    获取特定平台的下载信息
    
    Args:
        platform: 平台名称 (windows, macos, linux)
    """
    if platform not in DOWNLOAD_INFO:
        raise HTTPException(status_code=404, detail=f"Platform {platform} not found")
    
    return {
        "status": "success",
        "data": DOWNLOAD_INFO[platform],
        "timestamp": datetime.now().isoformat()
    }

@router.get("/downloads/{platform}/download")
async def download_client(platform: str):
    """
    下载客户端文件（重定向到实际下载链接）
    
    Args:
        platform: 平台名称 (windows, macos, linux)
    """
    if platform not in DOWNLOAD_INFO:
        raise HTTPException(status_code=404, detail=f"Platform {platform} not found")
    
    download_info = DOWNLOAD_INFO[platform]
    
    # 在实际部署中，这里应该重定向到真实的文件下载链接
    # 或者提供文件流下载
    from fastapi.responses import RedirectResponse
    
    return RedirectResponse(url=download_info["url"])

@router.get("/downloads/check-updates")
async def check_updates() -> Dict[str, dict]:
    """
    检查客户端更新
    """
    # 这里可以添加检查更新的逻辑
    # 比如从数据库或外部API获取最新版本信息
    return {
        "status": "success",
        "data": {
            "latest_version": "1.0.0",
            "update_available": False,
            "update_url": None,
            "changelog": [],
            "timestamp": datetime.now().isoformat()
        }
    }

@router.get("/downloads/stats")
async def get_download_stats() -> Dict[str, dict]:
    """
    获取下载统计信息
    """
    # 这里可以从数据库获取实际的下载统计
    return {
        "status": "success",
        "data": {
            "total_downloads": 0,
            "platform_stats": {
                "windows": 0,
                "macos": 0,
                "linux": 0
            },
            "recent_downloads": [],
            "timestamp": datetime.now().isoformat()
        }
    }
