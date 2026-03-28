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

## 代理任务确认机制

**确保每个代理都按照分配给它的任务目标完成了，必须有确认机制。**

### 确认流程

1. **任务完成后必须验证** - 代理报告完成时，必须通过以下方式确认：
   - 运行 `lsp_diagnostics` 检查修改文件是否有类型错误
   - 读取修改后的文件，确认内容确实已变更
   - 运行相关测试确保通过

2. **禁止仅凭代理报告确认完成** - 代理可能误报完成状态，必须实际验证：
   ```typescript
   // ❌ 错误：仅信任代理报告
   agent.report("已完成修改")
   // 直接标记任务完成

   // ✅ 正确：验证后再确认
   agent.report("已完成修改")
   read(filePath)  // 确认文件内容
   lsp_diagnostics(filePath)  // 检查类型错误
   runTests()  // 运行测试
   // 确认无误后再标记任务完成
   ```

3. **多代理并行任务的验证** - 当多个代理并行工作时：
   - 收集所有代理结果后，逐一验证每个代理的输出
   - 检查文件修改时间戳或内容是否确实变更
   - 运行完整测试套件确保无回归

### 常见问题

- **代理说"已修改"但文件未变** - 必须读取文件确认
- **代理说"测试通过"但实际失败** - 必须运行测试确认
- **代理说"类型检查通过"但有错误** - 必须运行 `lsp_diagnostics` 确认

---

## 缓存注意事项

**前后端涉及缓存时需要特别注意，考虑缓存对新特性的兼容、影响。**

### 前端缓存

1. **Pinia Store 缓存** - 当使用 Map 或对象缓存数据时：
   - 添加新数据后，缓存可能过期
   - 修改数据后，缓存可能不一致
   - 删除数据后，缓存可能残留

2. **缓存失效策略** - 必须在以下场景考虑缓存刷新：
   ```typescript
   // ❌ 错误：缓存存在就跳过
   if (cache.has(id)) return cache.get(id)

   // ✅ 正确：支持强制刷新
   if (!forceRefresh && cache.has(id)) return cache.get(id)
   // 重新获取数据并更新缓存
   const freshData = await fetchData(id)
   cache.set(id, freshData)
   return freshData
   ```

3. **数据关联更新** - 当实体 A 关联实体 B 时：
   - 创建/更新/删除 B 后，A 的关联缓存需要刷新
   - 例如：添加物品后，房间的物品列表缓存需要刷新

### 后端缓存

1. **数据库查询缓存** - SQLAlchemy 默认会话级别缓存：
   - 同一会话中多次查询相同数据可能返回缓存结果
   - 修改数据后需要 `db.refresh()` 或重新查询

2. **N+1 查询与缓存** - 使用 `joinedload` 或 `subqueryload` 时：
   - 确保关联数据是最新的
   - 考虑是否需要每次都加载关联数据

### 测试要求

- 缓存相关功能必须测试以下场景：
  - 首次加载（缓存为空）
  - 重复加载（缓存已存在）
  - 数据变更后加载（缓存需要刷新）
  - 关联数据变更后加载（关联缓存需要刷新）

---

## 测试要求

**每次新增特性或修改代码后，必须为新增/修改的内容编写相应的单元测试。**

- 新增功能 → 在 `src/` 同级目录或 `tests/` 下创建对应的测试文件
- 修改逻辑 → 补充或更新对应的测试用例，确保覆盖变更场景
- 测试文件命名规范：
  - 前端: `{module}.test.ts` (如 `stores/item.test.ts`, `api/item.test.ts`)
  - 后端: `test_{module}.py` (如 `tests/test_items.py`)
- 运行新增的测试确保通过后再提交

---

## 快速参考

| 任务 | 命令 |
|------|---------|
| 前端开发 | `npm run dev` (3000) |
| 后端开发 | `uvicorn app.main:app --reload` (8000) |
| 前端测试 | `npm run test` |
| 后端测试 | `pytest` |
| 类型检查 | `npm run type-check` |