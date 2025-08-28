-- 检查工作日志状态分布
SELECT work_status, COUNT(*) as count 
FROM work_logs 
GROUP BY work_status;

-- 查看具体的工作日志记录
SELECT id, work_status, work_type, content, created_at 
FROM work_logs 
ORDER BY created_at DESC 
LIMIT 10;

-- 检查是否有NULL值
SELECT COUNT(*) as null_count 
FROM work_logs 
WHERE work_status IS NULL;

-- 检查数据库表结构
SHOW CREATE TABLE work_logs;

-- 检查枚举类型的定义
SELECT COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE, COLUMN_DEFAULT
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_NAME = 'work_logs' 
AND COLUMN_NAME = 'work_status'; 