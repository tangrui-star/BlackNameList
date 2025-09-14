@echo off
echo 🚀 启动黑名单管理系统后端服务
echo ========================================

cd /d "%~dp0\blacklist-backend"

echo 📁 当前目录: %CD%
echo 🌐 服务地址: http://127.0.0.1:8000
echo 📚 API文档: http://127.0.0.1:8000/docs
echo ⏹️  按 Ctrl+C 停止服务
echo ========================================

python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

pause
