# 家庭物品跟踪系统 (Home Assets Trace)

一个轻量级的家庭物品管理系统，支持物品登记、分类管理、过期提醒等功能。

## 功能特性

- 用户注册/登录（多用户支持）
- 物品管理（增删改查）
- 分类管理
- **房间管理** - 按房间组织物品
- **家庭管理** - 支持多家庭/多人共享
- 过期物品追踪（筛选已过期/即将过期物品）
- ~~过期提醒~~ **[TODO]** 邮件/推送提醒功能
- 按名称、分类、房间、家庭、过期状态筛选
- 响应式设计，支持移动端访问

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + TypeScript + Vite + TailwindCSS + Pinia |
| 后端 | Python + FastAPI + SQLAlchemy |
| 数据库 | SQLite / PostgreSQL |
| 认证 | JWT Token |
| 部署 | Docker Compose |

## 家庭管理

系统支持多家庭管理，允许多个用户共享同一个家庭空间。

### 核心概念

- **家庭 (Family)**: 一个共享空间，包含多个成员和物品
- **家庭成员 (FamilyMember)**: 属于某个家庭的用户，可分配不同角色
- **角色权限**:
  - `owner` - 所有者，可管理家庭和成员
  - `admin` - 管理员，可管理家庭和成员
  - `member` - 普通成员，只能查看和添加物品

### 功能说明

- 每个用户注册后自动创建一个默认家庭
- 家庭所有者可以邀请其他用户加入
- 物品可设置为私有（仅自己可见）或家庭共享
- 支持按家庭筛选物品列表

## 物品字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | 是 | 物品名称 |
| quantity | int | 是 | 数量 |
| price | float | 否 | 价格（默认 0.0） |
| purchase_date | date | 否 | 购买日期 |
| expiry_date | date | 否 | 过期时间 |
| category_id | int | 否 | 分类ID |
| room_id | int | 否 | 房间ID |
| family_id | int | 否 | 所属家庭ID |
| location | string | 否 | 存放位置 |
| notes | string | 否 | 备注 |
| usage | string | 否 | 用途 |
| purchase_channel | string | 否 | 购买途径 |
| is_private | bool | 否 | 仅自己可见（默认 false） |

## 快速开始

### 方式一：Docker 部署（推荐）

**前置条件**：安装 Docker 和 Docker Compose

```bash
# 克隆项目
git clone https://github.com/rardoomooto/home-assets-trace.git
cd home-assets-trace

# 创建环境变量文件
cp .env.example .env

# 修改 SECRET_KEY（生产环境必须修改）
# 编辑 .env 文件，设置一个复杂的密钥

# 创建数据目录
mkdir -p data

# 构建并启动
docker-compose up -d --build

# 访问
http://localhost:8080
```

### 方式二：本地开发

**前置条件**：安装 Python 3.11+ 和 Node.js 18+

#### 后端

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 启动
uvicorn app.main:app --reload --port 8000
```

#### 前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 访问
http://localhost:3000
```

## 项目结构

```
home-assets-trace/
├── backend/                # FastAPI 后端
│   ├── app/
│   │   ├── models/         # 数据模型
│   │   ├── schemas/        # Pydantic 模型
│   │   ├── routers/        # API 路由
│   │   ├── auth/           # 认证模块
│   │   ├── config.py       # 配置
│   │   ├── database.py     # 数据库连接
│   │   └── main.py         # 入口文件
│   └── requirements.txt
├── frontend/               # Vue 3 前端
│   ├── src/
│   │   ├── api/            # API 调用
│   │   ├── components/     # 组件
│   │   ├── router/         # 路由
│   │   ├── stores/         # Pinia 状态管理
│   │   ├── types/          # TypeScript 类型
│   │   └── views/          # 页面
│   └── package.json
├── docker-compose.yml
├── Dockerfile.backend
├── Dockerfile.frontend
├── nginx.conf
└── README.md
```

## API 接口

### 认证接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/auth/register` | POST | 用户注册 |
| `/api/auth/login` | POST | 用户登录 |
| `/api/auth/me` | GET | 获取当前用户信息 |

### 物品接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/items` | GET | 获取物品列表（支持筛选） |
| `/api/items` | POST | 创建物品 |
| `/api/items/{id}` | GET | 获取物品详情 |
| `/api/items/{id}` | PUT | 更新物品 |
| `/api/items/{id}` | DELETE | 删除物品 |

### 分类接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/categories` | GET | 获取分类列表 |
| `/api/categories` | POST | 创建分类 |
| `/api/categories/{id}` | GET | 获取分类详情 |
| `/api/categories/{id}` | PUT | 更新分类 |
| `/api/categories/{id}` | DELETE | 删除分类 |

### 房间接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/rooms` | GET | 获取房间列表 |
| `/api/rooms` | POST | 创建房间 |
| `/api/rooms/{id}` | GET | 获取房间详情 |
| `/api/rooms/{id}` | PUT | 更新房间 |
| `/api/rooms/{id}` | DELETE | 删除房间 |
| `/api/rooms/{id}/items` | GET | 获取房间内的物品 |

### 家庭接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/families` | GET | 获取用户所属的家庭列表 |
| `/api/families` | POST | 创建新家庭 |
| `/api/families/{id}` | GET | 获取家庭详情 |
| `/api/families/{id}` | PUT | 更新家庭信息 |
| `/api/families/{id}` | DELETE | 删除家庭 |
| `/api/families/{id}/members` | POST | 添加家庭成员 |
| `/api/families/{id}/members/{user_id}` | DELETE | 移除家庭成员 |

### 物品筛选参数

| 参数 | 类型 | 说明 |
|------|------|------|
| name | string | 按名称模糊搜索 |
| category_id | int | 按分类筛选 |
| room_id | int | 按房间筛选 |
| family_id | int | 按家庭筛选 |
| expired | bool | 筛选已过期物品 |
| expiring_soon | bool | 筛选30天内过期物品 |
| skip | int | 分页偏移 |
| limit | int | 每页数量 |

## 数据备份

### SQLite 备份

SQLite 数据库文件位于 `data/home_assets.db`，备份该文件即可。

```bash
# 备份
cp data/home_assets.db data/home_assets_backup_$(date +%Y%m%d).db

# 恢复
cp data/home_assets_backup_20240101.db data/home_assets.db
docker-compose restart
```

### PostgreSQL 备份

使用 `pg_dump` 和 `pg_restore` 进行备份和恢复。

```bash
# 备份
docker exec home-assets-db pg_dump -U postgres home_assets > backup_$(date +%Y%m%d).sql

# 恢复
docker exec -i home-assets-db psql -U postgres home_assets < backup_20240101.sql
```

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| SECRET_KEY | JWT 密钥 | your-secret-key-change-me-in-production |
| DATABASE_URL | 数据库连接（直接指定，优先级最高） | None |
| DATABASE_TYPE | 数据库类型：sqlite 或 postgresql | sqlite |
| POSTGRES_USER | PostgreSQL 用户名 | postgres |
| POSTGRES_PASSWORD | PostgreSQL 密码 | postgres |
| POSTGRES_HOST | PostgreSQL 主机（Docker 中为 db） | localhost |
| POSTGRES_PORT | PostgreSQL 端口 | 5432 |
| POSTGRES_DB | PostgreSQL 数据库名 | home_assets |

### 数据库配置说明

本系统支持 SQLite 和 PostgreSQL 两种数据库，通过环境变量进行配置：

#### 使用 SQLite（默认）
```bash
# 默认配置，无需额外设置
DATABASE_TYPE=sqlite
# 或者直接指定
DATABASE_URL=sqlite:///./data/home_assets.db
```

#### 使用 PostgreSQL
```bash
# 方式一：通过 DATABASE_TYPE 自动构建 URL
DATABASE_TYPE=postgresql
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_HOST=db  # Docker 中使用服务名
POSTGRES_PORT=5432
POSTGRES_DB=home_assets

# 方式二：直接指定完整 URL
DATABASE_URL=postgresql://postgres:password@db:5432/home_assets
```

**注意**：如果同时设置了 `DATABASE_URL` 和 `DATABASE_TYPE`，`DATABASE_URL` 优先级更高。

## 常见问题

### 1. 端口冲突

- **Docker 部署**：前端默认使用 8080 端口，后端 8000 端口，数据库 5432 端口
- **本地开发**：前端默认使用 3000 端口，后端使用 8000 端口

如需修改端口，编辑对应服务的端口映射配置：

### 2. 数据持久化

- **SQLite**：数据存储在 `./data` 目录，确保该目录有正确的读写权限
- **PostgreSQL**：数据存储在 Docker 卷 `postgres_data` 中，由 Docker 自动管理

### 3. 忘记密码

目前没有密码找回功能，可以重新注册一个新账户。

### 4. 选择 SQLite 还是 PostgreSQL？

- **SQLite**：适合个人使用、开发测试，部署简单，无需额外服务
- **PostgreSQL**：适合多用户、生产环境，支持并发访问和更复杂查询

## License

MIT
