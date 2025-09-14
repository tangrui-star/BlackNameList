# 黑名单管理系统 (Blacklist Management System)

## 项目概述

这是一个基于前后端分离架构的黑名单管理系统，用于帮助商家识别和防范欺诈行为。系统采用现代化的技术栈，提供完整的用户管理、权限控制、黑名单数据管理和订单筛查功能。

## 技术栈

### 后端
- **框架**: FastAPI (Python 3.13+)
- **数据库**: MySQL 9.1
- **ORM**: SQLAlchemy 2.0
- **认证**: JWT + OAuth2
- **数据处理**: Pandas + NumPy
- **文本匹配**: fuzzywuzzy + regex

### 前端
- **框架**: Vue 3 + TypeScript
- **构建工具**: Vite
- **UI框架**: Element Plus
- **状态管理**: Pinia
- **路由**: Vue Router 4
- **HTTP客户端**: Axios

## 项目结构

```
BlackNameList/
├── blacklist-backend/          # 后端项目
│   ├── app/
│   │   ├── api/               # API路由
│   │   ├── core/              # 核心配置
│   │   ├── models/            # 数据模型
│   │   ├── schemas/           # 数据模式
│   │   ├── services/          # 业务逻辑
│   │   └── utils/             # 工具函数
│   ├── tests/                 # 测试文件
│   └── migrations/            # 数据库迁移
├── blacklist-frontend/         # 前端项目
│   ├── src/
│   │   ├── components/        # 组件
│   │   ├── views/             # 页面
│   │   ├── stores/            # 状态管理
│   │   └── router/            # 路由配置
│   └── public/                # 静态资源
├── data/                      # 数据文件
│   ├── blacklist/             # 黑名单数据
│   ├── uploads/               # 上传文件
│   ├── exports/               # 导出文件
│   └── templates/             # 模板文件
└── docs/                      # 文档
```

## 核心功能

### 1. 用户管理
- 用户注册/登录
- 基于角色的权限控制
- 用户信息管理

### 2. 黑名单管理
- 黑名单数据的增删改查
- Excel文件导入/导出
- 数据验证和清洗

### 3. 订单筛查
- 文件上传和解析
- 智能匹配算法
- 结果展示和导出

### 4. 系统管理
- 数据统计和可视化
- 系统配置管理
- 操作日志和审计

## 匹配策略

系统采用四层优先级匹配策略：

1. **联系电话匹配** (优先级最高) - 精确匹配
2. **下单名字匹配** (优先级第二) - 模糊匹配
3. **ktt名字匹配** (优先级第三) - 模糊匹配
4. **下单地址匹配** (优先级最低) - 模糊匹配

## 开发环境要求

- Python 3.13+
- Node.js 18+
- MySQL 8.0+
- Git

## 快速开始

### 1. 克隆项目
```bash
git clone <repository-url>
cd BlackNameList
```

### 2. 后端设置
```bash
cd blacklist-backend
pip install -r requirements.txt
```

### 3. 前端设置
```bash
cd blacklist-frontend
npm install
```

### 4. 数据库设置
```bash
# 创建数据库
mysql -u root -p
CREATE DATABASE blacklist_system;
```

### 5. 启动服务
```bash
# 启动后端
cd blacklist-backend
uvicorn app.main:app --reload

# 启动前端
cd blacklist-frontend
npm run dev
```

## 开发计划

- [x] 项目结构搭建
- [ ] 数据库设计和创建
- [ ] 后端API开发
- [ ] 前端界面开发
- [ ] 核心功能实现
- [ ] 测试和部署

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证。

