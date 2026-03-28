Plan: Update models/__init__.py to export Room with safe import.
- Implemented guarded import to export Room when available, falling back gracefully if Room is not defined in this environment.
- Adjusted __all__ to include Room when present.
- Rationale: Mirror existing export approach for User/Category/Item; ensure Room can be imported by routers/modules when defined.

Notes:
- This patch is compatible with environments where Room is defined in backend/app/models/models.py.
- Local environment currently lacks Room definition; guarded ImportError prevents hard failures.
