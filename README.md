# Restaurant Operations Platform

Full-stack restaurant operations dashboard built with FastAPI, React, and Vite.

## Stack

- Backend: Python + FastAPI + SQLModel
- Frontend: React + Vite + TypeScript
- Data: SQLite-backed relational schema for branches, customers, staff, menu items, inventory, orders, payments, promotions, loyalty, and delivery

## Project Layout

- `backend/app/main.py` contains the FastAPI application.
- `backend/app/models.py` defines the SQLModel tables and `backend/app/schemas.py` defines request payloads.
- `frontend/` contains the Vite React client.
- `frontend/vite.config.ts` proxies `/api` requests to the backend during development.
- `frontend/src/main.tsx`, `frontend/src/App.tsx`, and `frontend/src/api.ts` contain the TypeScript frontend entrypoints.

## Run Locally

### Backend

From the repository root:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

If you already have `backend/.venv`, you can skip creating it and just activate it before starting the server.

The API runs at `http://127.0.0.1:8000`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The app runs at `http://localhost:5173` and forwards `/api` requests to `http://127.0.0.1:8000`.

## Available Features

- Dashboard summary and live order actions
- Customer portal with menu browsing, order placement, loyalty, and order history
- Customer sign-up through the API-backed portal form
- Menu item creation and availability toggles
- Inventory updates
- Customer creation and loyalty redemption
- Promotion creation
- Branch, staff, and class-catalog views

## Notes

The backend now persists its data in `backend/app/restaurant_api.sqlite3` through SQLModel tables and direct REST endpoints.

Customer records can also be created through `POST /api/customers`, which writes through the same persistence path used by the seeded demo accounts.
