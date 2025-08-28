import sys
import os

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from app.database import engine
from sqlalchemy import text

def fix_enum_case():
    """修复枚举大小写问题，统一为小写"""
    print("=== 开始修复枚举大小写问题 ===")
    
    with engine.connect() as conn:
        # 1. 检查当前状态
        print("1. 检查当前数据库状态...")
        result = conn.execute(text("SELECT DISTINCT status FROM task"))
        current_statuses = [row[0] for row in result]
        print(f"当前状态值: {current_statuses}")
        
        # 2. 更新数据库中的状态为大写对应的枚举值
        print("\n2. 更新数据库中的状态值...")
        
        # 定义状态映射（大写 -> 小写）
        status_mapping = {
            'PENDING': 'pending',
            'ASSIGNED': 'assigned', 
            'IN_PROGRESS': 'in_progress',
            'REVIEW': 'review',
            'COMPLETED': 'completed',
            'CANCELLED': 'cancelled'
        }
        
        # 更新每个状态
        for old_status, new_status in status_mapping.items():
            if old_status in current_statuses:
                result = conn.execute(text(f"UPDATE task SET status = '{new_status}' WHERE status = '{old_status}'"))
                print(f"更新 {old_status} -> {new_status}: {result.rowcount} 条记录")
        
        # 3. 修改数据库字段的枚举类型定义
        print("\n3. 修改数据库字段的枚举类型定义...")
        
        # 先删除旧的枚举类型约束
        try:
            conn.execute(text("ALTER TABLE task MODIFY status VARCHAR(20)"))
            print("已移除旧的枚举约束")
        except Exception as e:
            print(f"移除枚举约束时出错: {e}")
        
        # 重新添加枚举约束（小写）
        try:
            enum_values = "','".join(status_mapping.values())
            sql = f"ALTER TABLE task MODIFY status ENUM('{enum_values}') NOT NULL DEFAULT 'pending'"
            conn.execute(text(sql))
            print("已添加新的枚举约束（小写）")
        except Exception as e:
            print(f"添加枚举约束时出错: {e}")
        
        # 4. 验证修复结果
        print("\n4. 验证修复结果...")
        result = conn.execute(text("SELECT DISTINCT status FROM task"))
        final_statuses = [row[0] for row in result]
        print(f"修复后的状态值: {final_statuses}")
        
        # 检查字段定义
        result = conn.execute(text("SHOW COLUMNS FROM task LIKE 'status'"))
        for row in result:
            print(f"字段定义: {row}")
        
        conn.commit()
        print("\n=== 修复完成 ===")

if __name__ == "__main__":
    fix_enum_case() 