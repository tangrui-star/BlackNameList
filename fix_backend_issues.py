#!/usr/bin/env python3
"""
修复后端服务问题
"""
import os
import sys
import subprocess
import time
import requests
from pathlib import Path

def check_python_environment():
    """检查Python环境"""
    print("🐍 检查Python环境...")
    print(f"Python版本: {sys.version}")
    print(f"Python路径: {sys.executable}")
    
    # 检查必要的包
    required_packages = ['fastapi', 'uvicorn', 'sqlalchemy', 'pymysql']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} 已安装")
        except ImportError:
            print(f"❌ {package} 未安装")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n📦 需要安装的包: {', '.join(missing_packages)}")
        print("请运行: pip install -r requirements.txt")
        return False
    
    return True

def check_database_connection():
    """检查数据库连接"""
    print("\n🗄️ 检查数据库连接...")
    
    try:
        from app.core.database import test_connection
        if test_connection():
            print("✅ 数据库连接成功")
            return True
        else:
            print("❌ 数据库连接失败")
            return False
    except Exception as e:
        print(f"❌ 数据库连接错误: {e}")
        return False

def create_env_file():
    """创建环境变量文件"""
    print("\n📝 创建环境变量文件...")
    
    env_content = """# 黑名单管理系统环境变量配置
# 数据库配置
DB_HOST=47.109.97.153
DB_PORT=3306
DB_USER=root
DB_PASSWORD=Root@2025!
DB_DATABASE=blacklist

# Redis配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# JWT配置
JWT_SECRET_KEY=your-secret-key-here-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# 应用配置
APP_NAME=黑名单管理系统
APP_VERSION=1.0.0
DEBUG=True
ENVIRONMENT=development

# 文件上传配置
MAX_UPLOAD_SIZE=10485760
ALLOWED_EXTENSIONS=xlsx,xls,csv
UPLOAD_PATH=./data/uploads
EXPORT_PATH=./data/exports

# 匹配算法配置
PHONE_WEIGHT=100
NAME_WEIGHT=80
KTT_WEIGHT=60
ADDRESS_WEIGHT=40
MATCH_THRESHOLD=70
FUZZY_THRESHOLD=80

# 日志配置
LOG_LEVEL=INFO
LOG_PATH=./logs

# 分页配置
DEFAULT_PAGE_SIZE=20
MAX_PAGE_SIZE=100

# 缓存配置
CACHE_TIMEOUT=300
USER_CACHE_TIMEOUT=1800
BLACKLIST_CACHE_TIMEOUT=3600
"""
    
    env_file = Path("blacklist-backend/.env")
    if not env_file.exists():
        env_file.write_text(env_content, encoding='utf-8')
        print("✅ 已创建 .env 文件")
    else:
        print("✅ .env 文件已存在")

def start_backend_service():
    """启动后端服务"""
    print("\n🚀 启动后端服务...")
    
    # 切换到后端目录
    backend_dir = Path("blacklist-backend")
    if not backend_dir.exists():
        print("❌ 后端目录不存在")
        return False
    
    # 检查是否有Python进程在运行
    try:
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe'], 
                              capture_output=True, text=True)
        if 'python.exe' in result.stdout:
            print("⚠️  检测到Python进程正在运行，可能后端服务已启动")
    except:
        pass
    
    # 启动后端服务
    try:
        print("正在启动后端服务...")
        print("🌐 服务地址: http://127.0.0.1:8000")
        print("📚 API文档: http://127.0.0.1:8000/docs")
        print("⏹️  按 Ctrl+C 停止服务")
        print("-" * 50)
        
        # 使用uvicorn启动服务
        cmd = [sys.executable, "-m", "uvicorn", "app.main:app", 
               "--host", "127.0.0.1", "--port", "8000", "--reload"]
        
        subprocess.run(cmd, cwd=backend_dir)
        
    except KeyboardInterrupt:
        print("\n👋 服务已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        return False
    
    return True

def test_api_endpoints():
    """测试API端点"""
    print("\n🧪 测试API端点...")
    
    base_url = "http://127.0.0.1:8000"
    
    # 等待服务启动
    print("等待服务启动...")
    time.sleep(3)
    
    # 测试根路径
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        print(f"✅ 根路径: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"❌ 根路径测试失败: {e}")
        return False
    
    # 测试健康检查
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"✅ 健康检查: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")
    
    # 测试API文档
    try:
        response = requests.get(f"{base_url}/docs", timeout=5)
        print(f"✅ API文档: {response.status_code}")
    except Exception as e:
        print(f"❌ API文档测试失败: {e}")
    
    return True

def main():
    """主函数"""
    print("🔧 黑名单管理系统后端问题修复工具")
    print("=" * 50)
    
    # 检查Python环境
    if not check_python_environment():
        print("\n❌ Python环境检查失败，请先安装必要的包")
        return
    
    # 创建环境变量文件
    create_env_file()
    
    # 检查数据库连接
    if not check_database_connection():
        print("\n❌ 数据库连接失败，请检查数据库配置")
        print("建议:")
        print("1. 检查数据库服务器是否运行")
        print("2. 检查网络连接")
        print("3. 检查数据库凭据")
        return
    
    print("\n✅ 所有检查通过，准备启动后端服务")
    
    # 启动后端服务
    start_backend_service()

if __name__ == "__main__":
    main()
