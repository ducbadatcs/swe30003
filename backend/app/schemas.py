from __future__ import annotations
from sqlalchemy.sql.operators import ge
import uuid

from enum import Enum

from datetime import date
from typing import Literal

from pydantic import BaseModel
from sqlmodel import Field, SQLModel
from uuid import UUID, uuid4

class Branch(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(min_length=1)
    address: str = Field(min_length=1)


class Customer(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(min_length=1)
    # full_name: str = Field(min_length=1)
    password: str = Field(min_length=1)
    

class StaffRoleEnum(str, Enum):
    STAFF = "staff"
    KITCHEN = "kitchen"
    CASHIER = "cashier"
    MANAGER = "manager"

class Staff(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(min_length=1)
    password: str = Field(min_length=1)
    role: StaffRoleEnum = Field(default=StaffRoleEnum.STAFF, min_length=1)
    branch_id: int = Field(foreign_key="branch.id")


class MenuItem(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(min_length=1)
    price: float = Field(ge=0)


class BranchInventory(SQLModel, table=True):
    branch_id: int = Field(min_length=1, foreign_key="branch.id", primary_key=True)
    item_id: int = Field(min_length=1, foreign_key="menuitem.id", primary_key=True)
    quantity: int = Field(ge=0)

class OrderStatusEnum(str, Enum):
    PENDING = "pending",
    CONFIRMED = "confirmed",
    PAID = "paid",
    PREPARING = "preparing",
    READY = "ready",
    OUT_FOR_DELIVERY = "out_for_delivery",
    DELIVERED = "delivered",
    CANCELLED = "cancelled",
    

class OrderItem(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    customer_id: str = Field(foreign_key="customer.id")
    branch_id: int = Field(foreign_key="branch.id")
    item_id: int = Field(foreign_key="menuitem.id")
    status: OrderStatusEnum = Field(default = OrderStatusEnum.PENDING, min_length=1)

class DeliveryCreate(BaseModel):
    eta_hours: int = Field(default=1, ge=0)


class PromotionCreate(BaseModel):
    id: int | None = Field(default=None, primary_key=True)
    code: str = Field(min_length=1)
    percent: float = Field(ge=0, le=100)
