Plan: Frontend Room Type Alignment

- What happened: Implemented frontend Room type to reflect backend Room schema. In this repo, the Room interface already exists in frontend/src/types/index.ts with fields: id: number, name: string, user_id: number, created_at: string.
- Outcome: No code changes were required; the existing Room interface is already aligned with the backend contract.
- Rationale: Synchronizing TypeScript interfaces between frontend and backend ensures typings are consistent when building the Rooms feature.
- Next steps: If backend schema evolves (additional fields or relations), update the frontend Room interface accordingly and consider adding validation/tests to cover typing changes.
