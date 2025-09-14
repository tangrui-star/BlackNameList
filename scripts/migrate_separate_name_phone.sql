-- 分离姓名和电话号码的数据库迁移脚本
-- 将 order_name_phone 字段分离为 order_name 和 phone_numbers

USE blacklist;

-- 1. 添加新的字段
ALTER TABLE blacklist 
ADD COLUMN order_name VARCHAR(200) COMMENT '下单人姓名' AFTER wechat_id,
ADD COLUMN phone VARCHAR(20) COMMENT '主要电话号码' AFTER order_name;

-- 2. 创建临时表来存储分离后的数据
CREATE TEMPORARY TABLE temp_blacklist_data AS
SELECT 
    id,
    ktt_name,
    wechat_name,
    wechat_id,
    order_name_phone,
    phone_numbers,
    order_address1,
    order_address2,
    blacklist_reason,
    risk_level,
    is_active,
    created_by,
    created_at,
    updated_at
FROM blacklist;

-- 3. 更新数据，从 order_name_phone 中提取姓名和电话号码
UPDATE blacklist b
JOIN temp_blacklist_data t ON b.id = t.id
SET 
    b.order_name = CASE 
        WHEN t.order_name_phone IS NOT NULL AND t.order_name_phone != '' THEN
            -- 提取姓名部分（去除电话号码）
            TRIM(REGEXP_REPLACE(t.order_name_phone, '[0-9\\s\\-\\+\\(\\)]+', ''))
        ELSE NULL
    END,
    b.phone = CASE 
        WHEN t.order_name_phone IS NOT NULL AND t.order_name_phone != '' THEN
            -- 提取第一个电话号码
            REGEXP_SUBSTR(t.order_name_phone, '1[3-9][0-9]{9}')
        ELSE NULL
    END
WHERE t.order_name_phone IS NOT NULL AND t.order_name_phone != '';

-- 4. 更新 phone_numbers JSON 字段，确保包含主要电话号码
UPDATE blacklist 
SET phone_numbers = JSON_ARRAY(phone)
WHERE phone IS NOT NULL AND phone != '' 
AND (phone_numbers IS NULL OR JSON_LENGTH(phone_numbers) = 0);

-- 5. 添加索引
ALTER TABLE blacklist 
ADD INDEX idx_order_name (order_name),
ADD INDEX idx_phone (phone);

-- 6. 删除临时表
DROP TEMPORARY TABLE temp_blacklist_data;

-- 7. 显示更新结果统计
SELECT 
    '数据分离完成' as status,
    COUNT(*) as total_records,
    COUNT(order_name) as records_with_name,
    COUNT(phone) as records_with_phone,
    COUNT(CASE WHEN order_name IS NOT NULL AND phone IS NOT NULL THEN 1 END) as records_with_both
FROM blacklist;
