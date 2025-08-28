-- 修改work_logs表字段名称
-- 将description字段改为content
ALTER TABLE work_logs CHANGE COLUMN description content TEXT NOT NULL;

-- 将hours_spent字段改为duration
ALTER TABLE work_logs CHANGE COLUMN hours_spent duration FLOAT NOT NULL DEFAULT 0.0;

-- 添加title字段（如果不存在）
ALTER TABLE work_logs ADD COLUMN title VARCHAR(255) NULL;

-- 更新title字段，使用content作为默认值
UPDATE work_logs SET title = content WHERE title IS NULL OR title = '';

-- 显示修改后的表结构
DESCRIBE work_logs; 