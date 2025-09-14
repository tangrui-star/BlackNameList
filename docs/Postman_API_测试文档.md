# 黑名单管理系统 API 测试文档

## 基础信息
- **基础URL**: `http://127.0.0.1:8000`
- **API版本**: v1
- **认证方式**: Bearer Token (JWT)
- **内容类型**: `application/json`

## 环境变量设置
在 Postman 中设置以下环境变量：
- `base_url`: `http://127.0.0.1:8000`
- `access_token`: (登录后获取)
- `refresh_token`: (登录后获取)

---

## 1. 系统健康检查

### 1.1 健康检查
- **方法**: `GET`
- **URL**: `{{base_url}}/health`
- **描述**: 检查系统状态和数据库连接
- **请求头**: 无
- **响应示例**:
```json
{
  "status": "healthy",
  "database": "connected",
  "version": "1.0.0"
}
```

### 1.2 根路径
- **方法**: `GET`
- **URL**: `{{base_url}}/`
- **描述**: 获取系统基本信息
- **请求头**: 无
- **响应示例**:
```json
{
  "message": "欢迎使用黑名单管理系统",
  "version": "1.0.0",
  "status": "running"
}
```

---

## 2. 用户认证 API

### 2.1 用户登录
- **方法**: `POST`
- **URL**: `{{base_url}}/api/v1/auth/login`
- **描述**: 用户登录获取访问令牌
- **请求头**: 
  - `Content-Type: application/json`
- **请求体**:
```json
{
  "username": "admin",
  "password": "admin123"
}
```
- **响应示例**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@blacklist.com",
    "full_name": "系统管理员",
    "phone": "13800138000",
    "role_id": 1,
    "is_active": true,
    "last_login": "2025-09-14 12:00:00",
    "created_at": "2025-09-14T10:00:00",
    "updated_at": "2025-09-14T12:00:00"
  }
}
```

### 2.2 刷新访问令牌
- **方法**: `POST`
- **URL**: `{{base_url}}/api/v1/auth/refresh`
- **描述**: 使用刷新令牌获取新的访问令牌
- **请求头**: 
  - `Content-Type: application/json`
- **请求体**:
```json
{
  "refresh_token": "{{refresh_token}}"
}
```

### 2.3 获取当前用户信息
- **方法**: `GET`
- **URL**: `{{base_url}}/api/v1/auth/me`
- **描述**: 获取当前登录用户信息
- **请求头**: 
  - `Authorization: Bearer {{access_token}}`

### 2.4 用户注册
- **方法**: `POST`
- **URL**: `{{base_url}}/api/v1/auth/register`
- **描述**: 用户注册
- **请求头**: 
  - `Content-Type: application/json`
- **请求体**:
```json
{
  "username": "newuser",
  "email": "newuser@example.com",
  "password": "password123",
  "full_name": "新用户",
  "phone": "13800138000"
}
```
- **响应示例**:
```json
{
  "id": 5,
  "username": "newuser",
  "email": "newuser@example.com",
  "full_name": "新用户",
  "phone": "13800138000",
  "role_id": 3,
  "is_active": true,
  "last_login": null,
  "created_at": "2025-09-14T12:22:08",
  "updated_at": "2025-09-14T12:22:08"
}
```

### 2.5 用户登出
- **方法**: `POST`
- **URL**: `{{base_url}}/api/v1/auth/logout`
- **描述**: 用户登出
- **请求头**: 
  - `Authorization: Bearer {{access_token}}`

---

## 3. 黑名单管理 API

### 3.1 获取黑名单列表
- **方法**: `GET`
- **URL**: `{{base_url}}/api/v1/blacklist`
- **描述**: 获取黑名单记录列表
- **请求头**: 
  - `Authorization: Bearer {{access_token}}`
- **查询参数**:
  - `page`: 页码 (默认: 1)
  - `size`: 每页数量 (默认: 10)
  - `search`: 搜索关键词
  - `risk_level`: 风险等级 (low/medium/high)
  - `sort_by`: 排序字段
  - `sort_order`: 排序方向 (asc/desc)

### 3.2 获取单个黑名单记录
- **方法**: `GET`
- **URL**: `{{base_url}}/api/v1/blacklist/{id}`
- **描述**: 获取指定ID的黑名单记录
- **请求头**: 
  - `Authorization: Bearer {{access_token}}`
- **路径参数**:
  - `id`: 黑名单记录ID

### 3.3 创建黑名单记录
- **方法**: `POST`
- **URL**: `{{base_url}}/api/v1/blacklist`
- **描述**: 创建新的黑名单记录
- **请求头**: 
  - `Authorization: Bearer {{access_token}}`
  - `Content-Type: application/json`
- **请求体**:
```json
{
  "ktt_name": "张三",
  "wechat_id": "zhangsan123",
  "order_name": "李四",
  "phone": "13800138000",
  "order_name_phone": "李四 13800138000",
  "phone_numbers": ["13800138000", "13900139000"],
  "address1": "北京市朝阳区",
  "address2": "上海市浦东新区",
  "reason": "恶意退款",
  "risk_level": "high",
  "notes": "多次恶意退款，影响店铺运营"
}
```

### 3.4 更新黑名单记录
- **方法**: `PUT`
- **URL**: `{{base_url}}/api/v1/blacklist/{id}`
- **描述**: 更新指定ID的黑名单记录
- **请求头**: 
  - `Authorization: Bearer {{access_token}}`
  - `Content-Type: application/json`
- **路径参数**:
  - `id`: 黑名单记录ID
- **请求体**: 同创建请求体

### 3.5 删除黑名单记录
- **方法**: `DELETE`
- **URL**: `{{base_url}}/api/v1/blacklist/{id}`
- **描述**: 删除指定ID的黑名单记录
- **请求头**: 
  - `Authorization: Bearer {{access_token}}`

### 3.6 批量删除黑名单记录
- **方法**: `POST`
- **URL**: `{{base_url}}/api/v1/blacklist/batch-delete`
- **描述**: 批量删除黑名单记录
- **请求头**: 
  - `Authorization: Bearer {{access_token}}`
  - `Content-Type: application/json`
- **请求体**:
```json
{
  "ids": [1, 2, 3, 4, 5]
}
```

### 3.7 导入Excel数据
- **方法**: `POST`
- **URL**: `{{base_url}}/api/v1/blacklist/import`
- **描述**: 从Excel文件导入黑名单数据
- **请求头**: 
  - `Authorization: Bearer {{access_token}}`
- **请求体**: `multipart/form-data`
  - `file`: Excel文件

### 3.8 导出Excel数据
- **方法**: `GET`
- **URL**: `{{base_url}}/api/v1/blacklist/export`
- **描述**: 导出黑名单数据为Excel文件
- **请求头**: 
  - `Authorization: Bearer {{access_token}}`
- **查询参数**:
  - `format`: 导出格式 (xlsx/csv)
  - `search`: 搜索条件

### 3.9 获取黑名单历史记录
- **方法**: `GET`
- **URL**: `{{base_url}}/api/v1/blacklist/{id}/history`
- **描述**: 获取指定黑名单记录的修改历史
- **请求头**: 
  - `Authorization: Bearer {{access_token}}`

---

## 4. 用户管理 API

### 4.1 获取用户列表
- **方法**: `POST`
- **URL**: `{{base_url}}/api/v1/users/list`
- **描述**: 获取用户列表（管理员权限）
- **请求头**: 
  - `Authorization: Bearer {{access_token}}`
  - `Content-Type: application/json`
- **请求体**:
```json
{
  "skip": 0,
  "limit": 20,
  "role_id": "",
  "is_active": "",
  "search": ""
}
```
- **参数说明**:
  - `skip`: 跳过的记录数（分页）
  - `limit`: 每页数量
  - `role_id`: 角色ID筛选（可选）
  - `is_active`: 激活状态筛选（可选）
  - `search`: 搜索关键词（可选）

### 4.2 创建用户
- **方法**: `POST`
- **URL**: `{{base_url}}/api/v1/users`
- **描述**: 创建新用户（管理员权限）
- **请求头**: 
  - `Authorization: Bearer {{access_token}}`
  - `Content-Type: application/json`
- **请求体**:
```json
{
  "username": "newuser",
  "email": "newuser@example.com",
  "password": "password123",
  "full_name": "新用户",
  "phone": "13800138000",
  "role_id": 3,
  "is_active": true
}
```

### 4.3 更新用户
- **方法**: `PUT`
- **URL**: `{{base_url}}/api/v1/users/{id}`
- **描述**: 更新用户信息（管理员权限）
- **请求头**: 
  - `Authorization: Bearer {{access_token}}`
  - `Content-Type: application/json`

### 4.4 删除用户
- **方法**: `DELETE`
- **URL**: `{{base_url}}/api/v1/users/{id}`
- **描述**: 删除用户（管理员权限）
- **请求头**: 
  - `Authorization: Bearer {{access_token}}`

---

## 5. 角色管理 API

### 5.1 获取角色列表
- **方法**: `POST`
- **URL**: `{{base_url}}/api/v1/roles/list`
- **描述**: 获取角色列表（需要认证）
- **请求头**: 
  - `Authorization: Bearer {{access_token}}`
  - `Content-Type: application/json`
- **请求体**:
```json
{}
```
- **响应示例**:
```json
[
  {
    "id": 1,
    "name": "超级管理员",
    "description": "系统完全控制权限",
    "permissions": [
      "user.read",
      "user.create",
      "user.update",
      "user.delete",
      "blacklist.read",
      "blacklist.create",
      "blacklist.update",
      "blacklist.delete",
      "blacklist.import",
      "blacklist.export",
      "screening.read",
      "screening.create",
      "screening.execute",
      "admin.system",
      "admin.config",
      "admin.logs"
    ],
    "is_active": true,
    "created_at": "2025-09-14T10:35:35",
    "updated_at": "2025-09-14T10:35:35"
  }
]
```

---

## 6. 订单筛查 API

### 6.1 获取筛查任务列表
- **方法**: `GET`
- **URL**: `{{base_url}}/api/v1/screening`
- **描述**: 获取筛查任务列表
- **请求头**: 
  - `Authorization: Bearer {{access_token}}`

### 6.2 创建筛查任务
- **方法**: `POST`
- **URL**: `{{base_url}}/api/v1/screening`
- **描述**: 创建新的筛查任务
- **请求头**: 
  - `Authorization: Bearer {{access_token}}`
  - `Content-Type: application/json`
- **请求体**:
```json
{
  "name": "订单筛查任务1",
  "description": "筛查恶意订单",
  "file_path": "/uploads/orders.xlsx",
  "match_rules": {
    "match_name": true,
    "match_phone": true,
    "match_address": false
  }
}
```

### 6.3 获取筛查结果
- **方法**: `GET`
- **URL**: `{{base_url}}/api/v1/screening/{task_id}/results`
- **描述**: 获取指定任务的筛查结果
- **请求头**: 
  - `Authorization: Bearer {{access_token}}`

---

## 7. 系统管理 API

### 7.1 获取系统统计
- **方法**: `GET`
- **URL**: `{{base_url}}/api/v1/admin/stats`
- **描述**: 获取系统统计数据（管理员权限）
- **请求头**: 
  - `Authorization: Bearer {{access_token}}`

### 7.2 获取操作日志
- **方法**: `GET`
- **URL**: `{{base_url}}/api/v1/admin/logs`
- **描述**: 获取系统操作日志（管理员权限）
- **请求头**: 
  - `Authorization: Bearer {{access_token}}`
- **查询参数**:
  - `page`: 页码
  - `size`: 每页数量
  - `user_id`: 用户ID筛选
  - `action`: 操作类型筛选
  - `start_date`: 开始日期
  - `end_date`: 结束日期

---

## 8. 错误响应格式

所有API在出错时都会返回统一的错误格式：

```json
{
  "detail": "错误描述信息"
}
```

常见HTTP状态码：
- `200`: 成功
- `201`: 创建成功
- `400`: 请求参数错误
- `401`: 未授权（需要登录）
- `403`: 禁止访问（权限不足）
- `404`: 资源不存在
- `422`: 数据验证错误
- `500`: 服务器内部错误

---

## 9. 测试步骤建议

### 9.1 基础测试流程
1. 测试健康检查接口
2. 测试用户登录接口
3. 使用获取的token测试需要认证的接口
4. 测试黑名单CRUD操作
5. 测试用户管理功能（POST方法）
6. 测试角色管理功能（POST方法）
7. 测试筛查功能

### 9.2 测试数据
- **管理员账户**: `admin` / `admin123`
- **操作员账户**: `operator` / `operator123`

### 9.3 注意事项
- 所有需要认证的接口都需要在请求头中包含 `Authorization: Bearer {token}`
- **用户列表和角色列表接口使用POST方法**，参数通过请求体传递
- 文件上传接口使用 `multipart/form-data` 格式
- 分页参数从0开始（skip参数）
- 时间格式使用ISO 8601标准

---

## 10. Postman Collection 导入

您可以将以下JSON保存为 `.json` 文件，然后在Postman中导入：

```json
{
  "info": {
    "name": "黑名单管理系统 API",
    "description": "黑名单管理系统的完整API测试集合",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "variable": [
    {
      "key": "base_url",
      "value": "http://127.0.0.1:8000"
    },
    {
      "key": "access_token",
      "value": ""
    }
  ],
  "item": [
    {
      "name": "系统健康检查",
      "item": [
        {
          "name": "健康检查",
          "request": {
            "method": "GET",
            "header": [],
            "url": {
              "raw": "{{base_url}}/health",
              "host": ["{{base_url}}"],
              "path": ["health"]
            }
          }
        }
      ]
    },
    {
      "name": "用户认证",
      "item": [
        {
          "name": "用户登录",
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"username\": \"admin\",\n  \"password\": \"admin123\"\n}"
            },
            "url": {
              "raw": "{{base_url}}/api/v1/auth/login",
              "host": ["{{base_url}}"],
              "path": ["api", "v1", "auth", "login"]
            }
          },
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "if (pm.response.code === 200) {",
                  "    const response = pm.response.json();",
                  "    pm.environment.set('access_token', response.access_token);",
                  "    pm.environment.set('refresh_token', response.refresh_token);",
                  "}"
                ]
              }
            }
          ]
        }
      ]
    }
  ]
}
```

这个文档提供了完整的API测试指南，您可以直接在Postman中使用这些接口进行测试。
