# Draft: Frontend Codebase Patterns Analysis

## Requirements (confirmed)
- Map codebase patterns focusing on src/ for the frontend. Identify directory structure, registration patterns, API layer, state management (Pinia), routing guards, and views. Provide file paths with descriptions as evidence for architecture decisions.
- Produce concrete, interview-ready observations that can anchor planning discussions and future work.

## Technical Decisions
- Architecture observed: separation of concerns across API layer (src/api), state management (src/stores), views (src/views), routing (src/router), and types (src/types).
- Authentication flow relies on a centralized auth store (Token in localStorage) and an Axios interceptor in api/index.ts for attaching tokens and handling 401s.
- Route guards gate access to authenticated routes via router/index.ts with meta flags (auth/guest).
- File naming conventions are consistent: auth.ts, item.ts, category.ts in api/stores; Register.vue/Login.vue in views; ItemForm.vue/Categories.vue in views; types/index.ts for shared interfaces.
- Data flow is strongly typed via TypeScript interfaces across API responses and store actions.
- Primary design pattern: modular, scalable CRUD structure per resource (Item, Category) with dedicated stores and API wrappers.

## Research Findings (highlights with file paths)
- Frontend API surface and auth flow:
  - /D:/3_Code/opencode_workspace/home-assets-trace/frontend/src/api/index.ts
  - /D:/3_Code/opencode_workspace/home-assets-trace/frontend/src/api/auth.ts
  - /D:/3_Code/opencode_workspace/home-assets-trace/frontend/src/stores/auth.ts
- Data models and types:
  - /D:/3_Code/opencode_workspace/home-assets-trace/frontend/src/types/index.ts
- Core app bootstrap and routing:
  - /D:/3_Code/opencode_workspace/home-assets-trace/frontend/src/main.ts
  - /D:/3_Code/opencode_workspace/home-assets-trace/frontend/src/App.vue
  - /D:/3_Code/opencode_workspace/home-assets-trace/frontend/src/router/index.ts
- Core domain resources and views (examples):
  - /D:/3_Code/opencode_workspace/home-assets-trace/frontend/src/views/Login.vue
  - /D:/3_Code/opencode_workspace/home-assets-trace/frontend/src/views/Register.vue
  - /D:/3_Code/opencode_workspace/home-assets-trace/frontend/src/views/Home.vue
  - /D:/3_Code/opencode_workspace/home-assets-trace/frontend/src/views/Items.vue
  - /D:/3_Code/opencode_workspace/home-assets-trace/frontend/src/stores/item.ts
- Data UI glue (Item/Category):
  - /D:/3_Code/opencode_workspace/home-assets-trace/frontend/src/api/item.ts
  - /D:/3_Code/opencode_workspace/home-assets-trace/frontend/src/api/category.ts
  - /D:/3_Code/opencode_workspace/home-assets-trace/frontend/src/stores/category.ts
- UI scaffolding and style:
  - /D:/3_Code/opencode_workspace/home-assets-trace/frontend/src/style.css

> Note: Paths have been converted to POSIX-like form for readability in this draft. Evidence supports a frontend-first architecture with a consistent layer separation.

## Open Questions
- Should we also map backend codebase patterns (API design, models, routers) to provide end-to-end architectural coherence?
- Do you want an initial interview cheat-sheet built from these patterns (talking points, common questions, and example quotes from files)?
- Would you like me to produce a starter plan for adding tests (backend with pytest, frontend with Vitest) and CI wiring now, based on these patterns?

## Scope Boundaries
- IN: Frontend codebase architecture, layer patterns, and file-level responsibilities in src/.
- OUT: Backend codebase patterns, unless requested, and any non-front-end tooling patterns.

## Next Steps
- If you approve, I can generate a focused interview outline and a starter plan (.sisyphus/plans/{name}.md) that translates these observations into concrete tasks and QA scenarios.
- Alternatively, I can extend the map to backend patterns and create a unified plan covering both layers.
