#!/usr/bin/env python3
"""
黑名单管理系统后端启动脚本
"""
import os
import sys
import subprocess
from pathlib import Path

def main():
    """启动后端服务"""
    # 获取脚本所在目录
    script_dir = Path(__file__).parent.absolute()
    
    # 设置环境变量
    os.environ['PYTHONPATH'] = str(script_dir)
    
    print("🚀 启动黑名单管理系统后端服务...")
    print(f"📁 工作目录: {script_dir}")
    print(f"🌐 服务地址: http://127.0.0.1:8000")
    print(f"📚 API文档: http://127.0.0.1:8000/docs")
    print("⏹️  按 Ctrl+C 停止服务")
    print("-" * 50)
    
    try:
        # 启动uvicorn服务
        cmd = [
            sys.executable, "-m", "uvicorn",
            "app.main:app",
            "--host", "127.0.0.1",
            "--port", "8000",
            "--reload"
        ]
        
        subprocess.run(cmd, cwd=script_dir)
        
    except KeyboardInterrupt:
        print("\n👋 服务已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
