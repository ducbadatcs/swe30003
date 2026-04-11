# Restaurant Operations Platform

Full-stack restaurant operations dashboard built with FastAPI, React, and Vite.

## Stack

- Backend: Python + FastAPI + SQLModel
- Frontend: React + Vite + TypeScript

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
fastapi dev
```

The API runs at `http://localhost:8000`, and a Swagger Interface to test them can be accessed at `http://localhost:8000/docs`.

### Frontend

```bash
cd frontend
pnpm install
pnpm run dev
```

The frontend interface can then be accessed at `http://localhost:5173/`
