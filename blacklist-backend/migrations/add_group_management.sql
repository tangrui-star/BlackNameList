-- 分组管理功能数据库迁移脚本
-- 创建时间: 2025-09-14

-- 1. 创建分组表
CREATE TABLE IF NOT EXISTS groups (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL COMMENT '分组名称',
    description TEXT COMMENT '分组描述',
    file_name VARCHAR(255) COMMENT '原始文件名',
    file_path VARCHAR(500) COMMENT '文件路径',
    total_orders INT DEFAULT 0 COMMENT '订单总数',
    checked_orders INT DEFAULT 0 COMMENT '已检测订单数',
    blacklist_matches INT DEFAULT 0 COMMENT '黑名单匹配数',
    status ENUM('active', 'archived', 'deleted') DEFAULT 'active' COMMENT '分组状态',
    created_by INT COMMENT '创建者ID',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否激活',
    
    INDEX idx_name (name),
    INDEX idx_status (status),
    INDEX idx_created_by (created_by),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='订单分组表';

-- 2. 为订单表添加分组ID字段
ALTER TABLE orders 
ADD COLUMN group_id INT COMMENT '所属分组ID' AFTER id,
ADD INDEX idx_group_id (group_id);

-- 3. 添加外键约束
ALTER TABLE orders 
ADD CONSTRAINT fk_orders_group_id 
FOREIGN KEY (group_id) REFERENCES groups(id) 
ON DELETE SET NULL ON UPDATE CASCADE;

-- 4. 创建分组统计视图（可选）
CREATE VIEW group_statistics AS
SELECT 
    g.id,
    g.name,
    g.description,
    g.file_name,
    g.total_orders,
    g.checked_orders,
    g.blacklist_matches,
    g.status,
    g.created_at,
    g.updated_at,
    COUNT(o.id) as actual_orders,
    COUNT(CASE WHEN o.is_blacklist_checked = TRUE THEN 1 END) as actual_checked,
    COUNT(CASE WHEN o.blacklist_risk_level IS NOT NULL AND o.blacklist_risk_level != 'none' THEN 1 END) as actual_matches
FROM groups g
LEFT JOIN orders o ON g.id = o.group_id AND o.is_active = TRUE
WHERE g.is_active = TRUE
GROUP BY g.id, g.name, g.description, g.file_name, g.total_orders, g.checked_orders, g.blacklist_matches, g.status, g.created_at, g.updated_at;

-- 5. 插入示例数据
INSERT INTO groups (name, description, file_name, status, created_by) VALUES
('测试分组1', '第一个测试分组', 'test_orders_1.xlsx', 'active', 1),
('测试分组2', '第二个测试分组', 'test_orders_2.xlsx', 'active', 1),
('历史分组', '历史数据分组', 'historical_orders.xlsx', 'archived', 1);
