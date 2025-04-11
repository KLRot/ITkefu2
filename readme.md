# 数智IT客服派单平台

## 项目介绍

数智IT客服派单平台是一个基于 FastAPI 和 Vue3 开发的现代化工单管理系统。系统采用前后端分离架构，提供了完整的工单生命周期管理、多角色权限控制、数据统计分析等功能。

## 功能特点

### 工单管理
- 工单创建、分配、处理、完成、归档全流程管理
- 自定义问题类型管理
- 工单优先级设置
- 自动工单归档
- 工单状态实时追踪
- 批量导出Excel

### 用户管理
- 多角色权限控制（管理员/普通用户）
- 用户创建与管理
- 个人信息维护
- 密码修改

### 数据分析
- 工单状态分布统计
- 问题类型分布分析
- 处理时效分析
- 数据可视化展示

### 系统设置
- 系统参数配置
- 问题类型管理
- 自动归档时间设置

## 技术架构

### 后端技术栈
- 核心框架：FastAPI 0.104.1
- ORM：Tortoise-ORM 0.20.0
- 数据库：SQLite
- 认证：JWT
- 定时任务：APScheduler 3.10.4

### 前端技术栈
- 核心框架：Vue 3.3.9
- UI组件：Element Plus 2.4.3
- 状态管理：Pinia 2.1.7
- 路由：Vue Router 4.2.5
- HTTP客户端：Axios
- 构建工具：Vite 4.3.9

## 快速开始

### 使用Docker部署

1. 拉取镜像：
```bash
docker pull caojinlong/itkefu:v1.0.0
```

2. 创建docker-compose.yml：
```yaml
services:
  app:
    container_name: itkefu
    image: caojinlong/itkefu:v1.0.0
    ports:
      - "80:80"
      - "443:443"
      - "8000:8000"
    volumes:
      - db_data:/backend/data
      - ./ssl:/etc/nginx/ssl
    environment:
      - DATABASE_URL=sqlite://./data/db.sqlite3

volumes:
  db_data:
```

3. 启动服务：
```bash
docker-compose up -d
```

### 本地开发环境搭建

1. 后端开发环境：
```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 初始化管理员账户
python -m app.init_admin

# 启动开发服务器
uvicorn app.main:app --reload --port 8000
```

2. 前端开发环境：
```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

## 系统配置

### 1. 环境变量配置

环境变量可以通过以下几种方式设置：

#### 方式一：使用 .env 文件（推荐）
在项目根目录创建 `.env` 文件：
```bash
# 数据库配置
DATABASE_URL=sqlite://./data/db.sqlite3

# JWT配置
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=11520  # 8天

# 跨域配置
BACKEND_CORS_ORIGINS=["*"]

# 其他配置
PROJECT_NAME=数智IT客服派单平台
VERSION=1.0.0
API_V1_STR=/api/v1 
```

#### 方式二：Docker环境变量
在 `docker-compose.yml` 中配置：
```yaml
services:
  app:
    environment:
      - DATABASE_URL=sqlite://./data/db.sqlite3
      - SECRET_KEY=your-secret-key-here
      - ACCESS_TOKEN_EXPIRE_MINUTES=11520
      - BACKEND_CORS_ORIGINS=["*"]
```

#### 方式三：系统环境变量
在系统中直接设置：
```bash
# Linux/Mac
export DATABASE_URL=sqlite://./data/db.sqlite3
export SECRET_KEY=your-secret-key-here

# Windows (PowerShell)
$env:DATABASE_URL = "sqlite://./data/db.sqlite3"
$env:SECRET_KEY = "your-secret-key-here"
```

#### 环境变量说明
| 变量名 | 说明 | 默认值 | 示例 |
|--------|------|--------|------|
| DATABASE_URL | 数据库连接URL | sqlite://./data/db.sqlite3 | sqlite://./data/db.sqlite3 |
| SECRET_KEY | JWT密钥 | 自动生成 | your-secret-key-here |
| ACCESS_TOKEN_EXPIRE_MINUTES | Token过期时间(分钟) | 11520 | 11520 |
| BACKEND_CORS_ORIGINS | 跨域允许的源 | ["*"] | ["http://localhost:3000"] |
| PROJECT_NAME | 项目名称 | 数智IT客服派单平台 | 数智IT客服派单平台 |
| VERSION | 版本号 | 1.0.0 | 1.0.0 |
| API_V1_STR | API前缀 | /api/v1 | /api/v1 |

### 2. Nginx配置
- 默认端口：80(HTTP)、443(HTTPS)
- SSL证书配置
- 反向代理设置

### 3. 系统参数
- 工单自动归档时间：可在系统设置中配置
- 问题类型：支持自定义添加/删除

## 使用指南

### 1. 登录系统
- 默认管理员账号：admin
- 默认密码：admin123
- 首次登录建议修改默认密码

### 2. 工单管理
- 创建工单：填写工单基本信息
- 工单分配：管理员分配或用户自主签收
- 工单处理：更新处理进度和解决方案
- 工单完成：填写解决方案并完成工单
- 工单归档：系统自动归档已完成工单

### 3. 统计分析
- 查看工单状态分布
- 查看问题类型分布
- 导出统计数据

### 4. 系统管理
- 用户管理：创建、编辑、删除用户
- 问题类型管理：添加、删除问题类型
- 系统设置：配置系统参数

## 开发指南

### 1. 目录结构
```
├── app/                # 后端代码
│   ├── api/           # API接口
│   ├── core/          # 核心配置
│   ├── models/        # 数据模型
│   ├── schemas/       # 数据验证
│   └── services/      # 业务逻辑
├── frontend/          # 前端代码
│   ├── src/          # 源代码
│   ├── public/       # 静态资源
│   └── package.json  # 项目配置
└── docker/           # Docker配置
```

### 2. API文档
- 访问地址：http://localhost:8000/docs
- 包含所有API接口说明和测试功能

### 3. 开发规范
- 代码风格：遵循PEP8规范
- 提交规范：采用约定式提交规范
- 分支管理：采用Git Flow工作流

## 常见问题

### 1. 部署相关
- Q: 如何修改默认端口？
- A: 修改docker-compose.yml中的端口映射

- Q: 如何配置HTTPS？
- A: 将SSL证书放置在./ssl目录下

### 2. 使用相关
- Q: 如何重置管理员密码？
- A: 使用Python脚本手动更新数据库

- Q: 工单数据如何备份？
- A: 备份data目录下的SQLite数据库文件

## 更新日志

### v1.0.0 (2024-02-24)
- 🎉 首次发布
- ✨ 完整的工单管理功能
- 👥 多用户权限管理
- 📊 数据统计分析
- 🔄 自动工单归档
- 🐳 Docker容器化部署

## 许可证

MIT License



