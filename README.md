# 家庭物品跟踪系统 (Home Assets Trace)

一个轻量级的家庭物品管理系统，支持物品登记、分类管理、过期提醒等功能。

## 功能特性

- 用户注册/登录（多用户支持）
- 物品管理（增删改查）
- 分类管理
- 过期物品追踪与提醒
- 按名称、分类、过期状态筛选
- 响应式设计，支持移动端访问

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + TypeScript + Vite + TailwindCSS |
| 后端 | Python + FastAPI + SQLAlchemy |
| 数据库 | SQLite |
| 认证 | JWT Token |
| 部署 | Docker Compose |

## 物品字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | 是 | 物品名称 |
| quantity | int | 是 | 数量 |
| price | float | 是 | 价格 |
| purchase_date | date | 否 | 购买日期 |
| expiry_date | date | 否 | 过期时间 |
| category_id | int | 否 | 分类ID |
| location | string | 否 | 存放位置 |
| notes | string | 否 | 备注 |
| usage | string | 否 | 用途 |
| purchase_channel | string | 否 | 购买途径 |

## 快速开始

### 方式一：Docker 部署（推荐）

**前置条件**：安装 Docker 和 Docker Compose

```bash
# 克隆项目
git clone <your-repo-url>
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

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/auth/register` | POST | 用户注册 |
| `/api/auth/login` | POST | 用户登录 |
| `/api/auth/me` | GET | 获取当前用户信息 |
| `/api/items` | GET | 获取物品列表（支持筛选） |
| `/api/items` | POST | 创建物品 |
| `/api/items/{id}` | GET | 获取物品详情 |
| `/api/items/{id}` | PUT | 更新物品 |
| `/api/items/{id}` | DELETE | 删除物品 |
| `/api/categories` | GET | 获取分类列表 |
| `/api/categories` | POST | 创建分类 |
| `/api/categories/{id}` | PUT | 更新分类 |
| `/api/categories/{id}` | DELETE | 删除分类 |

### 物品筛选参数

| 参数 | 类型 | 说明 |
|------|------|------|
| name | string | 按名称模糊搜索 |
| category_id | int | 按分类筛选 |
| expired | bool | 筛选已过期物品 |
| expiring_soon | bool | 筛选30天内过期物品 |
| skip | int | 分页偏移 |
| limit | int | 每页数量 |

## 数据备份

SQLite 数据库文件位于 `data/home_assets.db`，备份该文件即可。

```bash
# 备份
cp data/home_assets.db data/home_assets_backup_$(date +%Y%m%d).db

# 恢复
cp data/home_assets_backup_20240101.db data/home_assets.db
docker-compose restart
```

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| SECRET_KEY | JWT 密钥 | your-secret-key-change-me-in-production |
| DATABASE_URL | 数据库连接 | sqlite:///./data/home_assets.db |

## 常见问题

### 1. 端口冲突

如果 8080 端口被占用，修改 `docker-compose.yml` 中的端口映射：

```yaml
ports:
  - "3000:80"  # 将 8080 改为其他端口
```

### 2. 数据持久化

数据存储在 `./data` 目录，确保该目录有正确的读写权限。

### 3. 忘记密码

目前没有密码找回功能，可以重新注册一个新账户。

## License

MIT
