-- 检查工作日志表中的枚举值
SELECT work_type, COUNT(*) as count 
FROM work_logs 
GROUP BY work_type;

-- 检查数据库表结构中的枚举定义
SHOW CREATE TABLE work_logs;

-- 检查枚举类型的定义
SELECT COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE, COLUMN_DEFAULT
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_NAME = 'work_logs' 
AND COLUMN_NAME = 'work_type'; 