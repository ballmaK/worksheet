@echo off
echo 启动 WorkLog 桌面客户端...
echo.

REM 检查Node.js是否安装
node --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Node.js，请先安装Node.js
    pause
    exit /b 1
)

REM 检查npm是否安装
npm --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到npm，请先安装npm
    pause
    exit /b 1
)

echo 正在安装依赖...
npm install

echo.
echo 正在启动桌面客户端...
echo 请确保后端服务已启动 (http://localhost:8000)
echo.

REM 启动桌面客户端
npm run electron:dev

pause 