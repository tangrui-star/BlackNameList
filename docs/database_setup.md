# 数据库配置文档

## 数据库连接信息

- **服务器地址**: 47.109.97.153
- **端口**: 3306
- **用户名**: root
- **密码**: Root@2025!
- **数据库名**: blacklist

## 数据库结构

### 主要表结构

1. **users** - 用户表
   - 存储系统用户信息
   - 包含管理员账户

2. **roles** - 角色表
   - 定义用户角色和权限
   - 包含4个预定义角色

3. **permissions** - 权限表
   - 定义系统权限
   - 包含16个预定义权限

4. **blacklist** - 黑名单主表
   - 存储黑名单记录
   - 支持多种匹配字段

5. **blacklist_history** - 黑名单变更历史表
   - 记录黑名单的增删改操作

6. **screening_tasks** - 筛查任务表
   - 管理订单筛查任务

7. **screening_results** - 筛查结果表
   - 存储筛查匹配结果

8. **system_configs** - 系统配置表
   - 存储系统配置参数

9. **operation_logs** - 操作日志表
   - 记录用户操作日志

### 视图

- **blacklist_stats** - 黑名单统计视图
- **user_stats** - 用户统计视图

## 默认管理员账户

- **用户名**: admin
- **密码**: admin123
- **邮箱**: admin@blacklist.com
- **角色**: 超级管理员

## 系统配置

系统已预配置以下参数：

- 系统名称: 黑名单管理系统
- 系统版本: 1.0.0
- 电话号码匹配权重: 100
- 姓名匹配权重: 80
- KTT名字匹配权重: 60
- 地址匹配权重: 40
- 匹配阈值: 70

## 验证脚本

项目提供了以下数据库相关脚本：

1. **connect_server_db.py** - 连接服务器数据库
2. **setup_database.py** - 初始化数据库和表结构
3. **verify_database.py** - 验证数据库配置
4. **test_mysql_connection.py** - 测试MySQL连接

## 使用方法

### 连接数据库
```bash
python scripts/connect_server_db.py
```

### 初始化数据库
```bash
python scripts/setup_database.py
```

### 验证数据库
```bash
python scripts/verify_database.py
```

## 注意事项

1. 请确保服务器网络连接正常
2. 默认管理员密码请及时修改
3. 定期备份数据库数据
4. 生产环境请使用强密码

## 故障排除

如果遇到连接问题，请检查：

1. 服务器是否可访问
2. 用户名和密码是否正确
3. 端口是否开放
4. 网络连接是否正常
5. MySQL服务是否正常运行
