# Restaurant Operations Platform

Full-stack restaurant operations dashboard built with FastAPI, React, and Vite.

## Stack

- Backend: Python + FastAPI + SQLModel
- Frontend: React + Vite + TypeScript
- Data: SQLite-backed relational schema for branches, customers, staff, menu items, inventory, orders, payments, promotions, loyalty, and delivery

## Run Locally

To run the project locally, you are required to have the following software packages installed:

- Python
- `uv` (for backend)
- `pnpm` (for frontend)

### Backend

From the repository root:

```bash
cd backend
uv venv .
source .venv/bin/activate
cd app
uv run fastapi dev
```

The API runs at `http://127.0.0.1:8000`, and can be accessed at `http://127.0.0.1:8000/docs`.

### Frontend

```bash
cd frontend
pnpm install
pnpm run dev
```
