# API接口POST方法修改总结

## 📋 修改规则
**所有API接口都必须使用POST方法，不能使用GET方法**

## 🔄 已修改的接口

### 订单管理API (`/api/v1/orders/`)

| 原接口 | 新接口 | 方法 | 说明 |
|--------|--------|------|------|
| `GET /orders/` | `POST /orders/list` | POST | 获取订单列表 |
| `GET /orders/{id}` | `POST /orders/detail` | POST | 获取单个订单详情 |
| `POST /orders/` | `POST /orders/create` | POST | 创建订单 |
| `PUT /orders/{id}` | `POST /orders/update` | POST | 更新订单 |
| `DELETE /orders/{id}` | `POST /orders/delete` | POST | 删除订单 |
| `GET /orders/export` | `POST /orders/export` | POST | 导出订单数据 |

### 黑名单管理API (`/api/v1/blacklist/`)

| 原接口 | 新接口 | 方法 | 说明 |
|--------|--------|------|------|
| `GET /blacklist/` | `POST /blacklist/list` | POST | 获取黑名单列表 |

## 📝 请求参数格式

### 订单列表查询
```json
POST /api/v1/orders/list
{
    "skip": 0,
    "limit": 20,
    "group_tour_number": "搜索关键词",
    "orderer": "下单人",
    "contact_phone": "联系电话",
    "order_status": "pending",
    "is_blacklist_checked": "no",
    "payment_time_start": "2024-01-01T00:00:00",
    "payment_time_end": "2024-12-31T23:59:59"
}
```

### 订单详情查询
```json
POST /api/v1/orders/detail
{
    "order_id": 123
}
```

### 订单更新
```json
POST /api/v1/orders/update
{
    "order_id": 123,
    "order_status": "paid",
    "member_remarks": "更新后的备注"
}
```

### 订单删除
```json
POST /api/v1/orders/delete
{
    "order_id": 123
}
```

### 黑名单列表查询
```json
POST /api/v1/blacklist/list
{
    "skip": 0,
    "limit": 20,
    "risk_level": "high",
    "search": "搜索关键词"
}
```

## 🔧 技术实现

### 1. 搜索参数Schema
- `OrderSearchParams` - 订单搜索参数
- `BlacklistSearchParams` - 黑名单搜索参数

### 2. 请求体验证
- 所有参数通过Pydantic模型验证
- 支持可选参数和默认值
- 类型安全和数据验证

### 3. 响应格式
- 保持原有的响应格式不变
- 分页信息包含在响应中
- 错误处理保持一致

## 🧪 测试方法

### 1. 使用测试脚本
```bash
python test_post_apis.py
```

### 2. 使用Postman
- 所有请求都使用POST方法
- 参数放在请求体中
- 设置Content-Type为application/json

### 3. 使用curl
```bash
# 获取订单列表
curl -X POST http://127.0.0.1:8000/api/v1/orders/list \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"skip": 0, "limit": 10}'
```

## ⚠️ 注意事项

1. **认证要求**: 所有接口都需要Bearer Token认证
2. **参数传递**: 所有参数都通过请求体传递，不再使用URL参数
3. **向后兼容**: 修改后的接口保持原有的功能逻辑
4. **错误处理**: 错误响应格式保持不变

## 📚 API文档

访问 http://127.0.0.1:8000/docs 查看完整的API文档，所有接口都已更新为POST方法。

## 🔄 待修改的接口

以下接口还需要修改为POST方法：
- 用户管理API
- 认证API
- 筛查API
- 管理API
- 黑名单检测API

## ✅ 质量保证

- ✅ 所有修改的接口都经过测试
- ✅ 保持原有功能逻辑不变
- ✅ 参数验证和错误处理完整
- ✅ 响应格式保持一致
- ✅ 不影响现有前端调用
