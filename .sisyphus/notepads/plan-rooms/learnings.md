Learnings from task: The /rooms route was already present and aligned.
File paths verified:
- frontend/src/router/index.ts contains:
  - Route: /rooms -> Rooms.vue with meta: { auth: true }
- frontend/src/views/Rooms.vue exists and uses room store to fetch rooms
No code changes required. If future changes needed, I can adjust auth guard or add tests.
