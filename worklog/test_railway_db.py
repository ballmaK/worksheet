#!/usr/bin/env python3
"""
Railway 数据库连接测试脚本
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

def test_database_connection():
    """测试数据库连接"""
    print("🔍 Railway 数据库连接测试")
    print("=" * 50)
    
    # 获取环境变量
    db_host = os.getenv("MYSQLHOST", os.getenv("DB_HOST", "localhost"))
    db_port = os.getenv("MYSQLPORT", os.getenv("DB_PORT", "3306"))
    db_user = os.getenv("MYSQLUSER", os.getenv("DB_USER", "root"))
    db_password = os.getenv("MYSQLPASSWORD", os.getenv("DB_PASSWORD", ""))
    db_name = os.getenv("MYSQLDATABASE", os.getenv("DB_NAME", "work_log"))
    
    print(f"数据库主机: {db_host}")
    print(f"数据库端口: {db_port}")
    print(f"数据库用户: {db_user}")
    print(f"数据库名称: {db_name}")
    print(f"密码: {'*' * len(db_password) if db_password else '未设置'}")
    
    # 构建数据库URL
    database_url = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}?charset=utf8mb4"
    
    try:
        # 创建数据库引擎
        print("\n正在连接数据库...")
        engine = create_engine(database_url, echo=False)
        
        # 测试连接
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 as test"))
            row = result.fetchone()
            print(f"✅ 数据库连接成功！测试查询结果: {row[0]}")
            
            # 检查数据库版本
            result = conn.execute(text("SELECT VERSION() as version"))
            row = result.fetchone()
            print(f"✅ MySQL版本: {row[0]}")
            
            # 检查当前数据库
            result = conn.execute(text("SELECT DATABASE() as current_db"))
            row = result.fetchone()
            print(f"✅ 当前数据库: {row[0]}")
            
            # 检查表是否存在
            result = conn.execute(text("SHOW TABLES"))
            tables = result.fetchall()
            if tables:
                print(f"✅ 发现 {len(tables)} 个表:")
                for table in tables:
                    print(f"  - {table[0]}")
            else:
                print("ℹ️  数据库中没有表，需要运行数据库迁移")
        
        return True
        
    except SQLAlchemyError as e:
        print(f"❌ 数据库连接失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 未知错误: {e}")
        return False

def check_environment_variables():
    """检查环境变量"""
    print("\n🔍 环境变量检查")
    print("=" * 30)
    
    required_vars = [
        "MYSQLHOST", "MYSQLPORT", "MYSQLUSER", 
        "MYSQLPASSWORD", "MYSQLDATABASE"
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {value if var != 'MYSQLPASSWORD' else '*' * len(value)}")
        else:
            print(f"❌ {var}: 未设置")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n⚠️  缺少以下环境变量: {', '.join(missing_vars)}")
        print("请确保在Railway中正确配置了MySQL环境变量")
        return False
    
    return True

def main():
    """主函数"""
    print("🚀 Railway 数据库连接测试工具")
    print("=" * 50)
    
    # 检查环境变量
    env_ok = check_environment_variables()
    
    if not env_ok:
        print("\n❌ 环境变量配置不完整，无法进行连接测试")
        sys.exit(1)
    
    # 测试数据库连接
    connection_ok = test_database_connection()
    
    print("\n" + "=" * 50)
    if connection_ok:
        print("🎉 数据库连接测试成功！")
        print("\n📋 下一步:")
        print("1. 运行数据库迁移: alembic upgrade head")
        print("2. 启动后端服务")
        print("3. 测试API接口")
    else:
        print("❌ 数据库连接测试失败！")
        print("\n🔧 故障排除:")
        print("1. 检查Railway MySQL服务是否正常运行")
        print("2. 确认环境变量配置正确")
        print("3. 检查网络连接")
        sys.exit(1)

if __name__ == "__main__":
    main()
