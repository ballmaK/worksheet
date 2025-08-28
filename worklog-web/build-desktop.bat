@echo off
echo 构建 WorkLog 桌面客户端安装包...
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
echo 正在构建桌面客户端...
echo.

REM 构建桌面客户端
npm run electron:build

echo.
echo 构建完成！
echo 安装包位置: dist_electron/
echo.

pause 