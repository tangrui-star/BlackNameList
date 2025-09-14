#!/bin/bash

echo "启动黑名单管理系统后端服务..."
echo

# 设置环境变量
export PYTHONPATH="$(dirname "$0")"

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3，请先安装Python3"
    exit 1
fi

# 检查依赖是否安装
echo "检查依赖包..."
if ! python3 -c "import uvicorn, fastapi" &> /dev/null; then
    echo "正在安装依赖包..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "错误: 依赖包安装失败"
        exit 1
    fi
fi

# 启动服务
echo "启动服务..."
echo "服务地址: http://127.0.0.1:8000"
echo "API文档: http://127.0.0.1:8000/docs"
echo "按 Ctrl+C 停止服务"
echo

python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
