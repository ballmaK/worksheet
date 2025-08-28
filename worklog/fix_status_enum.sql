-- 修复tasks表的status字段枚举值
-- 添加缺失的'assigned'状态

-- 方法1: 修改枚举类型（推荐）
ALTER TABLE tasks MODIFY COLUMN status ENUM('pending', 'assigned', 'in_progress', 'review', 'completed', 'cancelled') NOT NULL DEFAULT 'pending';

-- 方法2: 如果方法1失败，先删除枚举约束，再重新添加
-- ALTER TABLE tasks MODIFY COLUMN status VARCHAR(20) NOT NULL DEFAULT 'pending';
-- ALTER TABLE tasks MODIFY COLUMN status ENUM('pending', 'assigned', 'in_progress', 'review', 'completed', 'cancelled') NOT NULL DEFAULT 'pending';

-- 验证修改结果
SHOW COLUMNS FROM tasks LIKE 'status'; 