@echo off
chcp 65001 >nul

echo 🚀 WorkLog Pro 部署脚本
echo ========================

REM 检查Git状态
echo 📋 检查Git状态...
git status --porcelain >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  有未提交的更改，请先提交更改
    git status
    pause
    exit /b 1
)

REM 推送到GitHub
echo 📤 推送到GitHub...
git push origin master

if %errorlevel% equ 0 (
    echo ✅ 代码推送成功！
    echo.
    echo 📋 下一步操作：
    echo 1. 访问 Railway: https://railway.app/
    echo 2. 连接您的 GitHub 仓库
    echo 3. 选择 worklog 目录作为部署目录
    echo 4. 配置环境变量
    echo 5. 添加 MySQL 数据库服务
    echo.
    echo 📖 详细部署指南请参考：
    echo - worklog/QUICK_DEPLOY.md
    echo - worklog/RAILWAY_DEPLOYMENT.md
) else (
    echo ❌ 代码推送失败，请检查网络连接
    pause
    exit /b 1
)

pause
