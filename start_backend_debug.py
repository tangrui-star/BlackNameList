#!/usr/bin/env python3
"""
调试模式启动后端服务
"""
import sys
import os
import traceback
from pathlib import Path

def setup_environment():
    """设置环境"""
    # 设置工作目录
    backend_dir = Path("blacklist-backend")
    if not backend_dir.exists():
        print("❌ 后端目录不存在")
        return False
    
    os.chdir(backend_dir)
    sys.path.insert(0, str(backend_dir.absolute()))
    
    print(f"📁 工作目录: {os.getcwd()}")
    return True

def test_imports():
    """测试导入"""
    print("🔍 测试模块导入...")
    
    try:
        # 测试基础模块
        from app.core.config import settings
        print("✅ 配置模块导入成功")
        
        from app.core.database import test_connection, init_db
        print("✅ 数据库模块导入成功")
        
        from app.core.security import verify_password, create_access_token
        print("✅ 安全模块导入成功")
        
        from app.core.exceptions import BlacklistException
        print("✅ 异常模块导入成功")
        
        # 测试模型
        from app.models import user, blacklist, order, screening
        print("✅ 模型模块导入成功")
        
        # 测试API路由
        from app.api.v1 import auth, users, blacklist, screening, admin, roles, orders, blacklist_check
        print("✅ API路由模块导入成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 模块导入失败: {e}")
        traceback.print_exc()
        return False

def test_database():
    """测试数据库"""
    print("\n🗄️ 测试数据库连接...")
    
    try:
        from app.core.database import test_connection, init_db
        
        if test_connection():
            print("✅ 数据库连接成功")
            init_db()
            print("✅ 数据库初始化成功")
            return True
        else:
            print("⚠️ 数据库连接失败，但继续启动")
            return True
            
    except Exception as e:
        print(f"⚠️ 数据库操作异常: {e}")
        print("继续启动应用...")
        return True

def start_server():
    """启动服务器"""
    print("\n🚀 启动后端服务...")
    
    try:
        import uvicorn
        from app.main import app
        
        print("✅ FastAPI应用创建成功")
        print("🌐 服务地址: http://127.0.0.1:8000")
        print("📚 API文档: http://127.0.0.1:8000/docs")
        print("⏹️  按 Ctrl+C 停止服务")
        print("-" * 50)
        
        uvicorn.run(
            app,
            host="127.0.0.1",
            port=8000,
            reload=True,
            log_level="info"
        )
        
    except Exception as e:
        print(f"❌ 服务器启动失败: {e}")
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("🔧 调试模式启动后端服务")
    print("=" * 50)
    
    # 设置环境
    if not setup_environment():
        return
    
    # 测试导入
    if not test_imports():
        print("\n❌ 模块导入失败，请检查代码")
        return
    
    # 测试数据库
    test_database()
    
    # 启动服务器
    start_server()

if __name__ == "__main__":
    main()
