-- 初始化默认用户和角色数据

-- 1. 插入默认权限
INSERT IGNORE INTO permissions (name, resource, action, description, created_at, updated_at) VALUES
('user_read', 'user', 'read', '查看用户', NOW(), NOW()),
('user_write', 'user', 'write', '编辑用户', NOW(), NOW()),
('user_delete', 'user', 'delete', '删除用户', NOW(), NOW()),
('blacklist_read', 'blacklist', 'read', '查看黑名单', NOW(), NOW()),
('blacklist_write', 'blacklist', 'write', '编辑黑名单', NOW(), NOW()),
('blacklist_delete', 'blacklist', 'delete', '删除黑名单', NOW(), NOW()),
('screening_read', 'screening', 'read', '查看筛查', NOW(), NOW()),
('screening_write', 'screening', 'write', '执行筛查', NOW(), NOW()),
('admin_read', 'admin', 'read', '查看系统管理', NOW(), NOW()),
('admin_write', 'admin', 'write', '系统管理', NOW(), NOW());

-- 2. 插入默认角色
INSERT IGNORE INTO roles (name, description, permissions, created_at, updated_at) VALUES
('超级管理员', '拥有所有权限', '["user_read", "user_write", "user_delete", "blacklist_read", "blacklist_write", "blacklist_delete", "screening_read", "screening_write", "admin_read", "admin_write"]', NOW(), NOW()),
('管理员', '拥有大部分权限', '["user_read", "user_write", "blacklist_read", "blacklist_write", "blacklist_delete", "screening_read", "screening_write", "admin_read"]', NOW(), NOW()),
('操作员', '拥有基本操作权限', '["blacklist_read", "blacklist_write", "screening_read", "screening_write"]', NOW(), NOW()),
('只读用户', '只能查看数据', '["blacklist_read", "screening_read"]', NOW(), NOW());

-- 3. 插入默认管理员用户
-- 密码是 admin123 的 bcrypt 哈希值
INSERT IGNORE INTO users (username, email, password_hash, full_name, phone, role_id, is_active, created_at, updated_at) 
SELECT 'admin', 'admin@blacklist.com', '$2b$12$ORlpE/u3Vt7mA6NCEZ8qoO.jUJbaaZ.4xlmkfQqRSain534THyY7m', '系统管理员', '13800138000', r.id, 1, NOW(), NOW()
FROM roles r WHERE r.name = '超级管理员';

-- 4. 插入测试操作员用户
-- 密码是 operator123 的 bcrypt 哈希值
INSERT IGNORE INTO users (username, email, password_hash, full_name, phone, role_id, is_active, created_at, updated_at) 
SELECT 'operator', 'operator@blacklist.com', '$2b$12$ORlpE/u3Vt7mA6NCEZ8qoO.jUJbaaZ.4xlmkfQqRSain534THyY7m', '操作员', '13800138001', r.id, 1, NOW(), NOW()
FROM roles r WHERE r.name = '操作员';
