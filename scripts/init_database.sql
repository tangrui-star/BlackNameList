-- 黑名单管理系统数据库初始化脚本
-- 创建数据库和所有表结构

-- 创建数据库
CREATE DATABASE IF NOT EXISTS blacklist 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE blacklist;

-- 1. 权限表
CREATE TABLE IF NOT EXISTS permissions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) UNIQUE NOT NULL COMMENT '权限名称',
    resource VARCHAR(50) NOT NULL COMMENT '资源名称',
    action VARCHAR(50) NOT NULL COMMENT '操作类型',
    description TEXT COMMENT '权限描述',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='权限表';

-- 2. 角色表
CREATE TABLE IF NOT EXISTS roles (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) UNIQUE NOT NULL COMMENT '角色名称',
    description TEXT COMMENT '角色描述',
    permissions JSON COMMENT '权限列表',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='角色表';

-- 3. 用户表
CREATE TABLE IF NOT EXISTS users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL COMMENT '用户名',
    email VARCHAR(100) UNIQUE NOT NULL COMMENT '邮箱',
    password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希',
    full_name VARCHAR(100) COMMENT '全名',
    phone VARCHAR(20) COMMENT '电话号码',
    role_id INT COMMENT '角色ID',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    last_login TIMESTAMP NULL COMMENT '最后登录时间',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE SET NULL,
    INDEX idx_username (username),
    INDEX idx_email (email),
    INDEX idx_role_id (role_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- 4. 黑名单主表
CREATE TABLE IF NOT EXISTS blacklist (
    id INT PRIMARY KEY AUTO_INCREMENT,
    ktt_name VARCHAR(100) COMMENT 'KTT名字',
    wechat_name VARCHAR(100) COMMENT '微信名字',
    wechat_id VARCHAR(100) COMMENT '微信号',
    order_name_phone TEXT COMMENT '下单名字和电话',
    phone_numbers JSON COMMENT '提取的电话号码列表',
    order_address1 TEXT COMMENT '下单地址1',
    order_address2 TEXT COMMENT '下单地址2',
    blacklist_reason TEXT COMMENT '入黑名单原因',
    risk_level ENUM('low', 'medium', 'high') DEFAULT 'medium' COMMENT '风险等级',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    created_by INT COMMENT '创建用户ID',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_ktt_name (ktt_name),
    INDEX idx_phone_numbers ((CAST(phone_numbers AS CHAR(255) ARRAY))),
    INDEX idx_risk_level (risk_level),
    INDEX idx_created_at (created_at),
    FULLTEXT idx_order_name_phone (order_name_phone),
    FULLTEXT idx_address (order_address1, order_address2)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='黑名单主表';

-- 5. 黑名单变更历史表
CREATE TABLE IF NOT EXISTS blacklist_history (
    id INT PRIMARY KEY AUTO_INCREMENT,
    blacklist_id INT NOT NULL COMMENT '黑名单ID',
    action ENUM('create', 'update', 'delete') NOT NULL COMMENT '操作类型',
    old_data JSON COMMENT '原始数据',
    new_data JSON COMMENT '新数据',
    changed_by INT COMMENT '操作用户ID',
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (blacklist_id) REFERENCES blacklist(id) ON DELETE CASCADE,
    FOREIGN KEY (changed_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_blacklist_id (blacklist_id),
    INDEX idx_action (action),
    INDEX idx_changed_at (changed_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='黑名单变更历史表';

-- 6. 筛查任务表
CREATE TABLE IF NOT EXISTS screening_tasks (
    id INT PRIMARY KEY AUTO_INCREMENT,
    task_name VARCHAR(200) NOT NULL COMMENT '任务名称',
    file_name VARCHAR(255) NOT NULL COMMENT '文件名',
    file_path VARCHAR(500) COMMENT '文件路径',
    total_records INT DEFAULT 0 COMMENT '总记录数',
    processed_records INT DEFAULT 0 COMMENT '已处理记录数',
    matched_records INT DEFAULT 0 COMMENT '匹配记录数',
    status ENUM('pending', 'processing', 'completed', 'failed') DEFAULT 'pending' COMMENT '任务状态',
    error_message TEXT COMMENT '错误信息',
    created_by INT COMMENT '创建用户ID',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL COMMENT '完成时间',
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_status (status),
    INDEX idx_created_by (created_by),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='筛查任务表';

-- 7. 筛查结果表
CREATE TABLE IF NOT EXISTS screening_results (
    id INT PRIMARY KEY AUTO_INCREMENT,
    task_id INT NOT NULL COMMENT '任务ID',
    blacklist_id INT NOT NULL COMMENT '黑名单ID',
    order_data JSON COMMENT '订单数据',
    match_type ENUM('phone', 'name', 'ktt_name', 'address') NOT NULL COMMENT '匹配类型',
    match_score DECIMAL(5,2) COMMENT '匹配分数',
    match_details TEXT COMMENT '匹配详情',
    risk_level ENUM('low', 'medium', 'high') DEFAULT 'medium' COMMENT '风险等级',
    is_verified BOOLEAN DEFAULT FALSE COMMENT '是否已验证',
    verified_by INT COMMENT '验证用户ID',
    verified_at TIMESTAMP NULL COMMENT '验证时间',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES screening_tasks(id) ON DELETE CASCADE,
    FOREIGN KEY (blacklist_id) REFERENCES blacklist(id) ON DELETE CASCADE,
    FOREIGN KEY (verified_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_task_id (task_id),
    INDEX idx_blacklist_id (blacklist_id),
    INDEX idx_match_type (match_type),
    INDEX idx_risk_level (risk_level),
    INDEX idx_match_score (match_score)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='筛查结果表';

-- 8. 系统配置表
CREATE TABLE IF NOT EXISTS system_configs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    config_key VARCHAR(100) UNIQUE NOT NULL COMMENT '配置键',
    config_value TEXT COMMENT '配置值',
    description TEXT COMMENT '配置描述',
    config_type ENUM('string', 'number', 'boolean', 'json') DEFAULT 'string' COMMENT '配置类型',
    is_editable BOOLEAN DEFAULT TRUE COMMENT '是否可编辑',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='系统配置表';

-- 9. 操作日志表
CREATE TABLE IF NOT EXISTS operation_logs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT COMMENT '用户ID',
    action VARCHAR(100) NOT NULL COMMENT '操作类型',
    resource_type VARCHAR(50) COMMENT '资源类型',
    resource_id VARCHAR(50) COMMENT '资源ID',
    details JSON COMMENT '操作详情',
    ip_address VARCHAR(45) COMMENT 'IP地址',
    user_agent TEXT COMMENT '用户代理',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_action (action),
    INDEX idx_resource_type (resource_type),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='操作日志表';

-- 插入初始数据

-- 插入权限数据
INSERT INTO permissions (name, resource, action, description) VALUES
('user.read', 'user', 'read', '查看用户'),
('user.create', 'user', 'create', '创建用户'),
('user.update', 'user', 'update', '更新用户'),
('user.delete', 'user', 'delete', '删除用户'),
('blacklist.read', 'blacklist', 'read', '查看黑名单'),
('blacklist.create', 'blacklist', 'create', '创建黑名单'),
('blacklist.update', 'blacklist', 'update', '更新黑名单'),
('blacklist.delete', 'blacklist', 'delete', '删除黑名单'),
('blacklist.import', 'blacklist', 'import', '导入黑名单'),
('blacklist.export', 'blacklist', 'export', '导出黑名单'),
('screening.read', 'screening', 'read', '查看筛查任务'),
('screening.create', 'screening', 'create', '创建筛查任务'),
('screening.execute', 'screening', 'execute', '执行筛查任务'),
('admin.system', 'system', 'manage', '系统管理'),
('admin.config', 'config', 'manage', '配置管理'),
('admin.logs', 'logs', 'read', '查看日志');

-- 插入角色数据
INSERT INTO roles (name, description, permissions) VALUES
('超级管理员', '系统完全控制权限', '["user.read", "user.create", "user.update", "user.delete", "blacklist.read", "blacklist.create", "blacklist.update", "blacklist.delete", "blacklist.import", "blacklist.export", "screening.read", "screening.create", "screening.execute", "admin.system", "admin.config", "admin.logs"]'),
('管理员', '用户管理、黑名单管理、系统配置', '["user.read", "user.create", "user.update", "blacklist.read", "blacklist.create", "blacklist.update", "blacklist.import", "blacklist.export", "screening.read", "screening.create", "screening.execute", "admin.config", "admin.logs"]'),
('操作员', '黑名单管理、订单筛查', '["blacklist.read", "blacklist.create", "blacklist.update", "blacklist.import", "screening.read", "screening.create", "screening.execute"]'),
('查看者', '仅可查看数据', '["blacklist.read", "screening.read"]');

-- 插入默认管理员用户 (密码: admin123)
INSERT INTO users (username, email, password_hash, full_name, role_id) VALUES
('admin', 'admin@blacklist.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBd5J5J8.5.5.5.5.5.5.5', '系统管理员', 1);

-- 插入系统配置
INSERT INTO system_configs (config_key, config_value, description, config_type) VALUES
('system.name', '黑名单管理系统', '系统名称', 'string'),
('system.version', '1.0.0', '系统版本', 'string'),
('match.phone_weight', '100', '电话号码匹配权重', 'number'),
('match.name_weight', '80', '姓名匹配权重', 'number'),
('match.ktt_weight', '60', 'KTT名字匹配权重', 'number'),
('match.address_weight', '40', '地址匹配权重', 'number'),
('match.threshold', '70', '匹配阈值', 'number'),
('file.max_size', '10485760', '文件最大大小(字节)', 'number'),
('file.allowed_types', '["xlsx", "xls", "csv"]', '允许的文件类型', 'json');

-- 创建视图：黑名单统计
CREATE VIEW blacklist_stats AS
SELECT 
    COUNT(*) as total_count,
    COUNT(CASE WHEN risk_level = 'high' THEN 1 END) as high_risk_count,
    COUNT(CASE WHEN risk_level = 'medium' THEN 1 END) as medium_risk_count,
    COUNT(CASE WHEN risk_level = 'low' THEN 1 END) as low_risk_count,
    COUNT(CASE WHEN created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY) THEN 1 END) as recent_count
FROM blacklist 
WHERE is_active = TRUE;

-- 创建视图：用户统计
CREATE VIEW user_stats AS
SELECT 
    COUNT(*) as total_users,
    COUNT(CASE WHEN is_active = TRUE THEN 1 END) as active_users,
    COUNT(CASE WHEN last_login >= DATE_SUB(NOW(), INTERVAL 30 DAY) THEN 1 END) as recent_login_users
FROM users;

COMMIT;

