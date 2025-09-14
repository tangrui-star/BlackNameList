@echo off
echo 启动黑名单管理系统后端服务...
echo.

REM 设置环境变量
set PYTHONPATH=%~dp0

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python
    pause
    exit /b 1
)

REM 检查依赖是否安装
echo 检查依赖包...
python -c "import uvicorn, fastapi" >nul 2>&1
if errorlevel 1 (
    echo 正在安装依赖包...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo 错误: 依赖包安装失败
        pause
        exit /b 1
    )
)

REM 启动服务
echo 启动服务...
echo 服务地址: http://127.0.0.1:8000
echo API文档: http://127.0.0.1:8000/docs
echo 按 Ctrl+C 停止服务
echo.

python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

pause
