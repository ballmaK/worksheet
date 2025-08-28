-- 修复任务状态字段长度
-- 将status字段修改为VARCHAR(20)以支持所有状态值

ALTER TABLE tasks MODIFY COLUMN status VARCHAR(20) NOT NULL DEFAULT 'pending';

-- 验证修改
DESCRIBE tasks; 