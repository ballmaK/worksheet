-- 检查当前工作日志状态分布
SELECT work_status, COUNT(*) as count 
FROM work_logs 
GROUP BY work_status;

-- 检查数据库表结构中的枚举定义
SHOW CREATE TABLE work_logs;

-- 检查枚举类型的定义
SELECT COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE, COLUMN_DEFAULT
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_NAME = 'work_logs' 
AND COLUMN_NAME = 'work_status';

-- 修改work_status列的枚举定义
ALTER TABLE work_logs 
MODIFY COLUMN work_status ENUM('in_progress', 'completed', 'blocked', 'on_hold') 
NOT NULL DEFAULT 'in_progress';

-- 更新现有的数据（如果有大写值）
UPDATE work_logs SET work_status = 'in_progress' WHERE work_status = 'IN_PROGRESS';
UPDATE work_logs SET work_status = 'completed' WHERE work_status = 'COMPLETED';
UPDATE work_logs SET work_status = 'blocked' WHERE work_status = 'BLOCKED';
UPDATE work_logs SET work_status = 'on_hold' WHERE work_status = 'ON_HOLD';

-- 验证结果
SELECT work_status, COUNT(*) as count FROM work_logs GROUP BY work_status; 