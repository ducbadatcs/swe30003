# Restaurant Operations Platform

Full-stack restaurant operations dashboard built with FastAPI, React, and Vite.

## Stack

- Backend: Python + FastAPI
- Frontend: React + Vite
- Data: SQLite-backed snapshot storage for branches, customers, staff, menu items, inventory, orders, payments, promotions, loyalty, and delivery

## Project Layout

- `backend/app/main.py` contains the FastAPI application.
- `frontend/` contains the Vite React client.
- `frontend/vite.config.js` proxies `/api` requests to the backend during development.

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
- Menu item creation and availability toggles
- Inventory updates
- Customer creation and loyalty redemption
- Promotion creation
- Branch, staff, and class-catalog views

## Notes

The backend persists its app snapshot in `backend/app/restaurant.sqlite3`. If you want to move from snapshot storage to a normalized relational schema later, the domain layer is already separated enough to support that without redesigning the UI.
