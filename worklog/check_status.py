from app.database import engine
from sqlalchemy import text

# 检查数据库中的状态值
print("=== 检查数据库中的状态值 ===")
with engine.connect() as conn:
    result = conn.execute(text("SELECT DISTINCT status FROM task"))
    statuses = [row[0] for row in result]
    print("数据库中的状态值:", statuses)
    
    # 检查字段定义
    print("\n=== 检查status字段定义 ===")
    result = conn.execute(text("SHOW COLUMNS FROM task LIKE 'status'"))
    for row in result:
        print("字段定义:", row)
    
    # 检查有多少条记录使用小写状态
    print("\n=== 检查小写状态记录 ===")
    result = conn.execute(text("SELECT COUNT(*) as count FROM task WHERE status = 'in_progress'"))
    count = result.fetchone()[0]
    print(f"使用 'in_progress' 的记录数: {count}")
    
    # 检查所有状态的使用情况
    print("\n=== 各状态使用情况 ===")
    result = conn.execute(text("SELECT status, COUNT(*) as count FROM task GROUP BY status"))
    for row in result:
        print(f"状态 '{row[0]}': {row[1]} 条记录") 