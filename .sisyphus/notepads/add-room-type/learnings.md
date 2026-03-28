# Learnings: Add Room Type to Frontend Types

- Implemented a new Room interface in frontend/src/types/index.ts to align with backend Room model.
- Room fields added: id (number), name (string), user_id (number), created_at (string).
- Ensured no renaming of existing interfaces (User, Category, Item) to maintain compatibility.
- Purpose: support Rooms feature dropdowns and item-room relations; allows referencing Room type across the frontend.
- Validation plan (next steps): reference Room in Item or Rooms components as needed; consider adding RoomList or API typings if required.

Opened questions / future work (if any):
- Do we want to expose Room in API response types (e.g., Room[] in some endpoints) or keep as isolated type for now?
- Should we convert snake_case fields to camelCase for frontend consumption, or keep as-is for backend parity?

Plan owner: Oh My OpenCode / Sisyphus
