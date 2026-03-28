# 房间管理功能 - 实施计划

## TL;DR
> **Summary**: 添加 Room 管理功能，实现房间与物品的关联，支持房间的增删改查
> **Deliverables**: Room 模型/API/UI，物品与房间关联，按房间筛选
> **Effort**: Medium
> **Parallel**: YES - 3 Waves
> **Critical Path**: 后端Model → 路由注册 → 前端API → UI集成

## Context
### Original Request
添加房间管理，在添加或修改物品时可选择所属房间

### Interview Summary
- Room 是预定义的房间列表（类似 Category）
- 物品需要 room_id 外键关联
- 房间管理使用模态框添加（同 Category 模式）
- 物品列表需要显示房间名称
- 物品表单需要房间选择下拉框
- 物品列表需要支持按房间筛选

### Metis Review (gaps addressed)
- 已确认需要区分已有的 `location` 字段（自由文本）和 `room_id`（预定义房间）
- 确认使用相同的 CRUD 模式（类似 Category）
- 确认需要更新导航栏添加房间管理入口

## Work Objectives
### Core Objective
实现完整的房间管理功能，支持房间的增删改查，并与物品建立关联关系

### Deliverables
- Room 数据模型和关系
- Room CRUD API
- Room 管理页面
- 物品表单中的房间选择
- 物品列表中的房间显示和筛选

### Definition of Done
- Room 表创建并有测试数据
- Room API 测试通过
- 房间管理页面功能完整
- 物品表单可保存房间关联
- 物品列表显示房间并支持筛选

### Must Have
- Room 模型（name, user_id）
- Room 端点（GET/POST/PUT/DELETE）
- Room 前端页面（同 Category 风格）
- Item 添加 room_id 字段
- 物品列表显示房间名称

### Must NOT Have
- Room 的额外字段（如描述、图标）- 保持简单
- Room 排序功能
- Room 与其他实体的复杂关联

## Verification Strategy
> 后端测试：启动服务 -> 创建/更新/删除房间 -> 验证响应
> 前端测试：操作房间管理 -> 添加物品选择房间 -> 查看列表筛选

## TODOs

### Wave 1: 后端模型与基础结构

- [ ] 1. 更新 models/models.py 添加 Room 模型

  **What to do**:
  - 添加 Room 类（id, name, user_id, created_at）
  - 在 User 添加 rooms 关系
  - 在 Item 添加 room_id 外键和 room 关系

  **Must NOT do**: 添加额外字段到 Room

  **Recommended Agent Profile**:
  - Category: `unspecified-low` — Reason: 简单模型添加
  - Skills: `[]` — 无特殊需求

  **References**:
  - Pattern: `backend/app/models/models.py:21-30` — Category 模式

  **Acceptance Criteria**:
  - [ ] Room 类定义正确，包含所有字段
  - [ ] User 和 Item 关系更新完成

  **QA Scenarios**:
  ```
  Scenario: 模型导入测试
    Tool: Bash
    Steps: cd backend && python -c "from app.models.models import Room; print('Room imported')"
    Expected: 输出 "Room imported" 无错误
    Evidence: 系统输出
  ```

  **Commit**: YES | Message: `feat(models): add Room model with relationships` | Files: `[backend/app/models/models.py]`

- [ ] 2. 创建 room schemas

  **What to do**:
  - 创建 backend/app/schemas/room.py
  - 定义 RoomBase, RoomCreate, RoomUpdate, RoomResponse

  **Recommended Agent Profile**:
  - Category: `unspecified-low` — Reason: 简单 schemas 生成
  - Skills: `[]`

  **References**:
  - Pattern: `backend/app/schemas/category.py:6-24` — Category schemas 模式

  **Acceptance Criteria**:
  - [ ] 包含所有必要的 schema 类
  - [ ] 从属性启用

  **QA Scenarios**:
  ```
  Scenario: schemas 导入测试
    Tool: Bash
    Steps: cd backend && python -c "from app.schemas.room import RoomCreate; print('ok')"
    Expected: 输出 "ok" 无错误
    Evidence: 系统输出
  ```

  **Commit**: YES | Message: `feat(schemas): add Room schemas` | Files: `[backend/app/schemas/room.py]`

- [ ] 3. 创建 room router

  **What to do**:
  - 创建 backend/app/routers/room.py
  - 实现 GET/POST/PUT/DELETE 端点
  - 用户隔离验证

  **Recommended Agent Profile**:
  - Category: `unspecified-low` — Reason: 标准 CRUD 路由
  - Skills: `[]`

  **References**:
  - Pattern: `backend/app/routers/category.py:13-95` — Category router 完整实现

  **Acceptance Criteria**:
  - [ ] 四个 CRUD 端点正确实现
  - [ ] 用户隔离正确

  **Commit**: YES | Message: `feat(router): add Room CRUD endpoints` | Files: `[backend/app/routers/room.py]`

- [ ] 4. 注册 room router

  **What to do**:
  - 在 backend/app/main.py 导入并注册 room_router
  - 导出 Room 模型

  **Recommended Agent Profile**:
  - Category: `quick` — Reason: 简单注册
  - Skills: `[]`

  **References**:
  - Pattern: `backend/app/main.py:4-14` — router 注册模式

  **Acceptance Criteria**:
  - [ ] room_router 在 main.py 中注册

  **Commit**: YES | Message: `feat(main): register room router` | Files: `[backend/app/main.py, backend/app/models/__init__.py]`

### Wave 2: 物品集成

- [ ] 5. 更新 item schemas 添加 room_id

  **What to do**:
  - 在 ItemBase 添加 room_id: Optional[int]
  - 在 ItemUpdate 添加 room_id: Optional[int]

  **Must NOT do**: 修改 ItemResponse（自动包含）

  **Recommended Agent Profile**:
  - Category: `quick` — Reason: 简单字段添加
  - Skills: `[]`

  **References**:
  - Pattern: `backend/app/schemas/item.py:12` — category_id 位置

  **Acceptance Criteria**:
  - [ ] room_id 字段正确添加到 ItemBase 和 ItemUpdate

  **Commit**: YES | Message: `feat(schemas): add room_id to ItemCreate/Update` | Files: `[backend/app/schemas/item.py]`

- [ ] 6. 更新 item router 添加房间筛选

  **What to do**:
  - 在 get_items 添加 room_id 查询参数
  - 实现按 room_id 筛选逻辑

  **Recommended Agent Profile**:
  - Category: `quick` — Reason: 标准筛选逻辑
  - Skills: `[]`

  **References**:
  - Pattern: `backend/app/routers/item.py:36-39` — category_id 筛选模式

  **Acceptance Criteria**:
  - [ ] room_id 参数正确解析
  - [ ] 筛选逻辑正确应用

  **QA Scenarios**:
  ```
  Scenario: 物品获取包含房间
    Tool: Bash
    Steps: curl -X GET "http://localhost:8000/api/items?room_id=1" -H "Authorization: Bearer $TOKEN"
    Expected: 返回 200 和物品列表
    Evidence: API 响应状态码
  ```

  **Commit**: YES | Message: `feat(router): add room filtering to items` | Files: `[backend/app/routers/item.py]`

### Wave 3: 前端实现

- [ ] 7. 添加 Room 类型定义

  **What to do**:
  - 在 frontend/src/types/index.ts 添加 Room 接口

  **Recommended Agent Profile**:
  - Category: `quick` — Reason: 简单类型定义
  - Skills: `[]`

  **References**:
  - Pattern: `frontend/src/types/index.ts:8-14` — Category 接口

  **Acceptance Criteria**:
  - [ ] Room 接口正确定义

  **Commit**: YES | Message: `feat(types): add Room type` | Files: `[frontend/src/types/index.ts]`

- [ ] 8. 创建 room API

  **What to do**:
  - 创建 frontend/src/api/room.ts
  - 实现 getAll, create, update, delete 方法

  **Recommended Agent Profile**:
  - Category: `unspecified-low` — Reason: 标准 API 封装
  - Skills: `[]`

  **References**:
  - Pattern: `frontend/src/api/category.ts:12-23` — Category API 模式

  **Acceptance Criteria**:
  - [ ] 四个 API 方法正确实现

  **Commit**: YES | Message: `feat(api): add Room API client` | Files: `[frontend/src/api/room.ts]`

- [ ] 9. 创建 room store

  **What to do**:
  - 创建 frontend/src/stores/room.ts
  - 实现状态管理和方法

  **Recommended Agent Profile**:
  - Category: `unspecified-low` — Reason: 标准 Pinia store
  - Skills: `[]`

  **References**:
  - Pattern: `frontend/src/stores/category.ts:6-46` — Category store 完整实现

  **Acceptance Criteria**:
  - [ ] Room store 功能完整

  **Commit**: YES | Message: `feat(store): add Room Pinia store` | Files: `[frontend/src/stores/room.ts]`

- [ ] 10. 创建 Rooms 页面

  **What to do**:
  - 创建 frontend/src/views/Rooms.vue
  - 复制 Categories.vue 的结构和功能
  - 修改文案和变量名为 room

  **Must NOT do**: 修改功能逻辑

  **Recommended Agent Profile**:
  - Category: `visual-engineering` — Reason: UI 组件创建
  - Skills: `[]`

  **References**:
  - Pattern: `frontend/src/views/Categories.vue:1-163` — 完整页面结构

  **Acceptance Criteria**:
  - [ ] 页面功能完整，创建/编辑/删除正常工作

  **Commit**: YES | Message: `feat(ui): add Rooms management page` | Files: `[frontend/src/views/Rooms.vue]`

- [ ] 11. 添加 Rooms 路由

  **What to do**:
  - 在 router/index.ts 添加 Rooms 路由

  **Recommended Agent Profile**:
  - Category: `quick` — Reason: 简单路由添加
  - Skills: `[]`

  **References**:
  - Pattern: `frontend/src/router/index.ts:44-48` — Categories 路由

  **Acceptance Criteria**:
  - [ ] /rooms 路由正确注册

  **Commit**: YES | Message: `feat(router): add Rooms route` | Files: `[frontend/src/router/index.ts]`

- [ ] 12. 更新 App.vue 导航

  **What to do**:
  - 在导航栏添加"房间管理"链接

  **Recommended Agent Profile**:
  - Category: `visual-engineering` — Reason: UI 修改
  - Skills: `[]`

  **References**:
  - Pattern: `frontend/src/App.vue:27-30` — 分类链接位置

  **Acceptance Criteria**:
  - [ ] 导航添加房间管理入口

  **Commit**: YES | Message: `feat(ui): add Rooms link to navigation` | Files: `[frontend/src/App.vue]`

- [ ] 13. 更新 ItemForm 添加房间选择

  **What to do**:
  - 导入并使用 useRoomStore
  - 在分类下拉框后添加房间下拉框
  - 更新 form 添加 room_id 字段
  - onMounted 加载房间列表

  **Recommended Agent Profile**:
  - Category: `visual-engineering` — Reason: 表单增强
  - Skills: `[]`

  **References**:
  - Pattern: `frontend/src/views/ItemForm.vue:138-146` — 分类下拉框实现

  **Acceptance Criteria**:
  - [ ] 房间下拉框正确显示所有房间
  - [ ] 保存物品时正确设置 room_id

  **Commit**: YES | Message: `feat(form): add room selection to item form` | Files: `[frontend/src/views/ItemForm.vue]`

- [ ] 14. 更新 Items 页面支持房间

  **What to do**:
  - 导入 useRoomStore
  - 在筛选栏添加房间下拉框
  - 在列表添加房间列
  - 实现按房间筛选逻辑

  **Recommended Agent Profile**:
  - Category: `visual-engineering` — Reason: 列表增强
  - Skills: `[]`

  **References**:
  - Pattern: `frontend/src/views/Items.vue:136-146` — 分类列和筛选

  **Acceptance Criteria**:
  - [ ] 房间筛选正确工作
  - [ ] 列表显示房间名称

  **QA Scenarios**:
  ```
  Scenario: 物品列表显示房间
    Tool: Bash
    Steps: 启动前端 -> 添加物品选择房间 -> 查看列表
    Expected: 列表显示房间名称，筛选功能有效
    Evidence: 手动测试通过
  ```

  **Commit**: YES | Message: `feat(list): add room filter and display to items list` | Files: `[frontend/src/views/Items.vue]`

## Final Verification Wave (MANDATORY — after ALL implementation tasks)
> 4 review agents run in PARALLEL. ALL must APPROVE. Present consolidated results to user and get explicit "okay" before completing.
> **Do NOT auto-proceed after verification. Wait for user's explicit approval before marking work complete.**
> **Never mark F1-F4 as checked before getting user's okay.** Rejection or user feedback -> fix -> re-run -> present again -> wait for okay.
- [ ] F1. Plan Compliance Audit — oracle
- [ ] F2. Code Quality Review — unspecified-high
- [ ] F3. Real Manual QA — unspecified-high
- [ ] F4. Scope Fidelity Check — deep

## Commit Strategy
每个 TODO 完成后独立提交，便于追踪进度和回滚

## Success Criteria
- Room 数据表创建并有测试数据
- Room API 所有端点测试通过
- 房间管理页增删改查功能正常
- 物品保存时关联房间正确
- 物品列表显示房间并支持筛选
