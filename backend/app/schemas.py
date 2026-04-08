from __future__ import annotations
from markdown_it.rules_block import table
from sqlmodel import SQLModel

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


class Branch(SQLModel, table=True):
    id: str = Field(min_length=1, primary_key=True)
    name: str = Field(min_length=1)
    address: str = Field(min_length=1)


class Customer(SQLModel, table=True):
    email: str = Field(min_length=1, primary_key=True)
    full_name: str = Field(min_length=1)
    password: str = Field(min_length=1)
    


class Staff(SQLModel, table=True):
    id: str = Field(min_length=1, primary_key=True)
    username: str = Field(min_length=1)
    password: str = Field(min_length=1)
    role: Literal["staff", "kitchen", "cashier", "manager"] = Field(default="staff", min_length=1)
    location: str = Field(foreign_key="branch.id")


class MenuItem(SQLModel, table=True):
    id: str = Field(min_length=1, primary_key=True)
    name: str = Field(min_length=1)
    price: float = Field(ge=0)


class BranchInventory(SQLModel, table=True):
    branch_id: str = Field(min_length=1, foreign_key="branch.id")
    item_id: str = Field(min_length=1, foreign_key="menuitem.id")
    quantity: int = Field(ge=0)


class InventoryUpdate(BaseModel):
    stock_level: int = Field(ge=0)
    reorder_point: int | None = Field(default=None, ge=0)


class OrderItem(BaseModel):
    email: str = Field(foreign_key="customer.email")
    branch: str = Field(foreign_key="branch.id")
    item: str = Field(foreign_key="menuitem.id")


class OrderStatusUpdate(BaseModel):
    status: Literal[
        "pending",
        "confirmed",
        "preparing",
        "ready",
        "paid",
        "out_for_delivery",
        "delivered",
        "cancelled",
    ]


class DeliveryCreate(BaseModel):
    eta_hours: int = Field(default=1, ge=0)


class PromotionCreate(BaseModel):
    code: str = Field(min_length=1)
    discount_type: Literal["percentage", "fixed"]
    discount_value: float = Field(gt=0)
    valid_until: date
    applicable_item_ids: list[str] = Field(default_factory=list)
    is_active: bool = True
