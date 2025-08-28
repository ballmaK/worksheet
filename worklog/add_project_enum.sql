-- 向messages表的message_type字段添加'project'枚举值
-- 注意：MySQL中修改ENUM需要重新定义整个字段

-- 1. 先备份messages表（可选）
-- CREATE TABLE messages_backup AS SELECT * FROM messages;

-- 2. 修改message_type字段，添加'project'枚举值
ALTER TABLE messages 
MODIFY COLUMN message_type ENUM('task','team','worklog','system','user','project') NOT NULL;

-- 3. 同样修改message_templates表的message_type字段
ALTER TABLE message_templates 
MODIFY COLUMN message_type ENUM('task','team','worklog','system','user','project') NOT NULL;

-- 4. 验证修改结果
SELECT COLUMN_NAME, COLUMN_TYPE 
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_SCHEMA = 'worksheet' 
AND TABLE_NAME = 'messages' 
AND COLUMN_NAME = 'message_type'; 