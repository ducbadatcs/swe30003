from importlib.resources import path
from traceback import print_exc
from typing import Any

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, SQLModel, select, or_

from .db import engine, get_session
from .schemas import Branch, Customer, MenuItem, Staff, BranchInventory, OrderItem

# routers
from .router.branches import branch_router
from .router.customers import customer_router
from .router.menu import menu_router
from .router.staffs import staff_router
from .router.orders import order_router

app = FastAPI(title="Restaurant Operations API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SQLModel.metadata.create_all(engine)

app.include_router(branch_router)
app.include_router(customer_router)
app.include_router(menu_router)
app.include_router(staff_router)
app.include_router(order_router)

