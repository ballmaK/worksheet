-- 检查当前工作日志类型分布
SELECT work_type, COUNT(*) as count 
FROM work_logs 
GROUP BY work_type;

-- 检查当前任务类型分布
SELECT task_type, COUNT(*) as count 
FROM tasks 
GROUP BY task_type;

-- 检查数据库表结构中的枚举定义
SHOW CREATE TABLE work_logs;
SHOW CREATE TABLE tasks;

-- 检查枚举类型的定义
SELECT COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE, COLUMN_DEFAULT
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_NAME IN ('work_logs', 'tasks') 
AND COLUMN_NAME IN ('work_type', 'task_type');

-- 修改work_logs表的work_type列的枚举定义
ALTER TABLE work_logs 
MODIFY COLUMN work_type ENUM('feature', 'bug', 'improvement', 'documentation', 'meeting', 'research', 'other') 
NOT NULL DEFAULT 'feature';

-- 修改tasks表的task_type列的枚举定义
ALTER TABLE tasks 
MODIFY COLUMN task_type ENUM('feature', 'bug', 'improvement', 'documentation', 'meeting', 'research', 'other') 
NOT NULL DEFAULT 'feature';

-- 更新work_logs表中的现有数据
UPDATE work_logs SET work_type = 'feature' WHERE work_type IN ('dev', 'development');
UPDATE work_logs SET work_type = 'bug' WHERE work_type IN ('test', 'testing', 'bug_fix');
UPDATE work_logs SET work_type = 'improvement' WHERE work_type = 'design';

-- 验证结果
SELECT 'work_logs' as table_name, work_type, COUNT(*) as count FROM work_logs GROUP BY work_type
UNION ALL
SELECT 'tasks' as table_name, task_type, COUNT(*) as count FROM tasks GROUP BY task_type; 