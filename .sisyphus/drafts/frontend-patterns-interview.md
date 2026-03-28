# Draft: Frontend Codebase Patterns Interview

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
  - /D:/3_Code/opencode_workspace/home-assets-trace/frontend/src/router/index.ts
- Core domain resources and views (examples):
  - /D:/3_Code/opencode_workspace/home-assets-trace/frontend/src/views/Login.vue
  - /D:/3_Code/opencode_workspace/home-assets-trace/frontend/src/views/Register.vue
  - /D:/3_Code/opencode_workspace/home-assets-trace/frontend/src/views/Home.vue
  - /D:/3_Code/opencode_workspace/home-assets-trace/frontend/src/views/Items.vue
- Data UI glue (Item/Category):
  - /D:/3_Code/opencode_workspace/home-assets-trace/frontend/src/api/item.ts
  - /D:/3_Code/opencode_workspace/home-assets-trace/frontend/src/api/category.ts
  - /D:/3_Code/opencode_workspace/home-assets-trace/frontend/src/stores/item.ts
- UI scaffolding and style:
  - /D:/3_Code/opencode_workspace/home-assets-trace/frontend/src/style.css

Notes:
- Paths use POSIX-style representation for readability in this draft, aligned with prior analyses.

## Open Questions
- Should we also map backend code patterns to ensure end-to-end coherence?
- Do you want an interview cheat-sheet built from these patterns with concrete questions?
- Shall we draft a starter plan for adding tests (backend pytest, frontend Vitest) and CI wiring now?

## Scope Boundaries
- IN: Frontend codebase architecture, layer patterns, and file-level responsibilities in src/.
- OUT: Backend codebase patterns, unless requested, and any non-front-end tooling patterns.

## Next Steps
- Upon your confirmation, I can generate a formal Plan (Phase 3 skeleton) and an interview guide, and optionally expand to backend patterns.
