-- 修复 work_logs 表的 end_time 字段，允许 null 值
ALTER TABLE work_logs MODIFY COLUMN end_time DATETIME NULL; 