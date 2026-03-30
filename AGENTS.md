# AGENTS.md - 智能编程代理编码规范

本文件为在该仓库中工作的智能编程代理提供编码规范指南。

## 项目概览

**家庭物品追踪系统** - Vue 3 前端 + FastAPI 后端的家庭物品管理系统。

| 层级 | 技术 |
|-------|------------|
| 前端 | Vue 3 + TypeScript + Vite + TailwindCSS + Pinia |
| 后端 | Python FastAPI + SQLAlchemy + Pydantic |
| 数据库 | SQLite |
| 认证 | JWT Token |

---

## 构建、测试和开发命令

### 前端

```bash
npm install                    # 安装依赖
npm run dev                    # 开发服务器端口 3000 (代理 /api 到 8000)
npm run build                  # vue-tsc && vite build
npm run type-check             # vue-tsc --noEmit
npm run test                   # vitest run
npm run test --watch           # vitest watch 模式
npm run test -- src/stores/item.test.ts  # 运行单个测试文件
```

### 后端

```bash
cd backend
python -m venv venv && venv\Scripts\activate  # Windows
# 或: source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000     # API 服务端口 8000
pytest -v                                      # 运行测试
```

### Docker
```bash
docker-compose up -d --build   # 前端: http://localhost:8080
```

---

## 代码风格规范

### TypeScript / Vue 3

#### 导入和路径别名
- 使用 `@/` 别名 (映射到 `src/`): `import { useItemStore } from '@/stores/item'`
- 在 `src/types/index.ts` 中定义接口

#### TypeScript (严格模式已启用)
- 禁止使用 `any`; 使用 proper types 或 `unknown`
- `noUnusedLocals: true`, `noUnusedParameters: true`

#### Vue 组件
- 使用 `<script setup lang="ts">` 实现 Composition API
- 单文件结构: `<script>`, `<template>`, `<style>`

#### Pinia 状态管理 (Composition API 风格)
```typescript
export const useItemStore = defineStore('item', () => {
  const items = ref<Item[]>([])
  const loading = ref(false)
  async function fetchItems(params?: ItemQueryParams) { ... }
  return { items, loading, fetchItems, ... }
})
```

#### API 层
- 放在 `src/api/*.ts` 中，导出类型化的 create/update/query 参数接口

#### 命名规范
- 文件: kebab-case (`item-form.vue`)
- 组件: PascalCase (`ItemForm.vue`)
- 类型: PascalCase (`Item`, `ItemCreate`)
- 变量: camelCase (`fetchItems`)

#### 错误处理
- 使用 try/finally 处理 loading 状态
- 后端返回具有正确状态码的 HTTPException

### Python / FastAPI

#### 项目结构
```
backend/app/
├── models/         # SQLAlchemy 模型
├── schemas/        # Pydantic 模型
├── routers/        # API 路由处理器
├── auth/           # 认证模块
├── config.py
└── main.py
```

#### 规范
- 所有参数和返回值使用类型提示
- 使用 Pydantic v2 模型 (`model_dump()`, `model_validate()`)
- 遵循 RESTful 规范: `GET /items`, `POST /items`, `PUT /items/{id}`
- 使用依赖注入: `Depends(get_current_user)`, `Depends(get_db)`
- 数据库操作使用 try/except 配合 db.rollback()
- 查询时使用 `user_id` 过滤以实现多用户数据隔离

### CSS / TailwindCSS
- 使用 Tailwind 工具类
- 响应式前缀: `sm:`, `lg:`

---

## 关键配置文件

### 前端
- `tsconfig.json` - 严格 TypeScript, `@/` 路径别名
- `vitest.config.ts` - jsdom 环境, setupFiles: `tests/setup.ts`
- `tailwind.config.js`

### 后端
- `requirements.txt` - FastAPI, SQLAlchemy, pytest

---

## 常见陷阱

1. **禁止使用 `any`** - 始终使用正确的 TypeScript 类型
2. **不要忽略严格错误** - 提交前修复
3. **使用 `@/` 别名** - 不使用相对路径如 `../../stores/item`
4. **处理 loading 状态** - 在 finally 块中重置
5. **使用事务提交** - 失败时回滚
6. **使用 user_id 过滤** - 实现多用户数据隔离

---

## 快速参考

| 任务 | 命令 |
|------|---------|
| 前端开发 | `npm run dev` (3000) |
| 后端开发 | `uvicorn app.main:app --reload` (8000) |
| 前端测试 | `npm run test` |
| 后端测试 | `pytest` |
| 类型检查 | `npm run type-check` |