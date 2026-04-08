from __future__ import annotations

import json
from dataclasses import fields, is_dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

from sqlalchemy import Column, JSON
from sqlmodel import Field, SQLModel, Session, create_engine, delete, select


def to_jsonable(value: Any) -> Any:
    if is_dataclass(value):
        result: dict[str, Any] = {}
        for field in fields(value):
            if field.name.startswith("_"):
                continue
            result[field.name] = to_jsonable(getattr(value, field.name))
        return result

    if isinstance(value, (datetime, date)):
        return value.isoformat()

    if isinstance(value, dict):
        return {key: to_jsonable(item) for key, item in value.items()}

    if isinstance(value, list):
        return [to_jsonable(item) for item in value]

    return value


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class AppConfig(SQLModel, table=True):
    name: str = Field(primary_key=True)
    branch_counter: int = 1
    customer_counter: int = 1
    staff_counter: int = 1
    item_counter: int = 1
    ingredient_counter: int = 1
    order_counter: int = 1
    payment_counter: int = 1
    delivery_counter: int = 1
    receipt_counter: int = 1
    promo_counter: int = 1
    tracking_counter: int = 1
    delivery_eta_hours: int = 1
    loyalty_points: dict[str, int] = Field(default_factory=dict, sa_column=Column(JSON, nullable=False))
    order_ratings: dict[str, list[int]] = Field(default_factory=dict, sa_column=Column(JSON, nullable=False))
    updated_at: datetime = Field(default_factory=_utc_now)


class BranchRow(SQLModel, table=True):
    branch_id: str = Field(primary_key=True)
    location: str
    pos_config: str
    inventory_ids: list[str] = Field(default_factory=list, sa_column=Column(JSON, nullable=False))


class InventoryRow(SQLModel, table=True):
    ingredient_id: str = Field(primary_key=True)
    stock_level: int
    reorder_point: int


class MenuItemRow(SQLModel, table=True):
    item_id: str = Field(primary_key=True)
    name: str
    price: float
    is_available: bool


class CustomerRow(SQLModel, table=True):
    customer_id: str = Field(primary_key=True)
    username: str
    password_hash: str
    full_name: str
    email: str
    phone: str
    loyalty_status: str
    tier_points: int
    order_ids: list[str] = Field(default_factory=list, sa_column=Column(JSON, nullable=False))


class StaffRow(SQLModel, table=True):
    staff_id: str = Field(primary_key=True)
    user_id: str
    username: str
    roles: list[str] = Field(default_factory=list, sa_column=Column(JSON, nullable=False))
    password_hash: str
    branch_id: str
    staff_kind: str
    station: str | None = None
    pos_terminal_id: str | None = None


class PromotionRow(SQLModel, table=True):
    promo_id: str = Field(primary_key=True)
    discount_type: str
    valid_until: date
    discount_value: float
    applicable_item_ids: list[str] = Field(default_factory=list, sa_column=Column(JSON, nullable=False))


class OrderRow(SQLModel, table=True):
    order_id: str = Field(primary_key=True)
    status: str
    order_type: str
    total_amount: float
    customer_id: str
    branch_id: str
    promotion_id: str | None = None
    discount_amount: float = 0.0
    payment_id: str | None = None
    delivery_id: str | None = None
    items: list[dict[str, Any]] = Field(default_factory=list, sa_column=Column(JSON, nullable=False))


class PaymentRow(SQLModel, table=True):
    payment_id: str = Field(primary_key=True)
    amount: float
    status: str
    method: str
    order_id: str
    receipt_id: str | None = None


class DeliveryRow(SQLModel, table=True):
    tracking_id: str = Field(primary_key=True)
    delivery_id: str
    order_id: str
    status: str
    eta: str


class ReceiptRow(SQLModel, table=True):
    receipt_id: str = Field(primary_key=True)
    payment_id: str
    amount: float
    issued_at: datetime


class SQLModelStateStore:
    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.engine = create_engine(
            f"sqlite:///{self.db_path}",
            connect_args={"check_same_thread": False},
        )
        SQLModel.metadata.create_all(self.engine)

    def load(self, name: str = "default") -> dict[str, Any] | None:
        with Session(self.engine) as session:
            config = session.get(AppConfig, name)
            if config is None:
                return None

            snapshot: dict[str, Any] = {
                "counters": {
                    "branch": config.branch_counter,
                    "customer": config.customer_counter,
                    "staff": config.staff_counter,
                    "item": config.item_counter,
                    "ingredient": config.ingredient_counter,
                    "order": config.order_counter,
                    "payment": config.payment_counter,
                    "delivery": config.delivery_counter,
                    "receipt": config.receipt_counter,
                    "promo": config.promo_counter,
                    "tracking": config.tracking_counter,
                },
                "delivery_eta_hours": config.delivery_eta_hours,
                "branches": {
                    row.branch_id: {
                        "location": row.location,
                        "posConfig": row.pos_config,
                        "inventoryIds": list(row.inventory_ids),
                    }
                    for row in session.exec(select(BranchRow)).all()
                },
                "inventory": {
                    row.ingredient_id: {
                        "stockLevel": row.stock_level,
                        "reorderPoint": row.reorder_point,
                    }
                    for row in session.exec(select(InventoryRow)).all()
                },
                "menu_items": {
                    row.item_id: {
                        "name": row.name,
                        "price": row.price,
                        "isAvailable": row.is_available,
                    }
                    for row in session.exec(select(MenuItemRow)).all()
                },
                "customers": {},
                "staff": {},
                "promotions": {},
                "orders": {},
                "payments": {},
                "deliveries": {},
                "receipts": {},
                "loyalty_points": dict(config.loyalty_points),
                "order_ratings": {order_id: list(ratings) for order_id, ratings in config.order_ratings.items()},
            }

            for row in session.exec(select(CustomerRow)).all():
                snapshot["customers"][row.customer_id] = {
                    "customer": {
                        "username": row.username,
                        "roles": ["customer"],
                        "password_hash": row.password_hash,
                        "profile": {
                            "full_name": row.full_name,
                            "email": row.email,
                            "phone": row.phone,
                        },
                        "loyaltyStatus": row.loyalty_status,
                        "order_ids": list(row.order_ids),
                    },
                    "tier_points": row.tier_points,
                }

            for row in session.exec(select(StaffRow)).all():
                payload: dict[str, Any] = {
                    "username": row.username,
                    "roles": list(row.roles),
                    "password_hash": row.password_hash,
                    "staffId": row.staff_id,
                    "branchId": row.branch_id,
                    "_kind": row.staff_kind,
                }
                if row.station is not None:
                    payload["station"] = row.station
                if row.pos_terminal_id is not None:
                    payload["posTerminalId"] = row.pos_terminal_id
                snapshot["staff"][row.staff_id] = payload

            for row in session.exec(select(PromotionRow)).all():
                snapshot["promotions"][row.promo_id] = {
                    "discountType": row.discount_type,
                    "validUntil": row.valid_until.isoformat(),
                    "discountValue": row.discount_value,
                    "applicableItemIds": list(row.applicable_item_ids),
                }

            for row in session.exec(select(OrderRow)).all():
                snapshot["orders"][row.order_id] = {
                    "status": row.status,
                    "orderType": row.order_type,
                    "totalAmount": row.total_amount,
                    "customerId": row.customer_id,
                    "branchId": row.branch_id,
                    "promotionId": row.promotion_id,
                    "discountAmount": row.discount_amount,
                    "paymentId": row.payment_id,
                    "deliveryId": row.delivery_id,
                    "items": [dict(item) for item in row.items],
                }

            for row in session.exec(select(PaymentRow)).all():
                snapshot["payments"][row.payment_id] = {
                    "amount": row.amount,
                    "status": row.status,
                    "method": row.method,
                    "orderId": row.order_id,
                    "receiptId": row.receipt_id,
                }

            for row in session.exec(select(DeliveryRow)).all():
                snapshot["deliveries"][row.tracking_id] = {
                    "delivery_id": row.delivery_id,
                    "order_id": row.order_id,
                    "tracking_id": row.tracking_id,
                    "status": row.status,
                    "eta": row.eta,
                }

            for row in session.exec(select(ReceiptRow)).all():
                snapshot["receipts"][row.receipt_id] = {
                    "payment_id": row.payment_id,
                    "amount": row.amount,
                    "issued_at": row.issued_at.isoformat(),
                }

            return snapshot

    def save(self, snapshot: dict[str, Any], name: str = "default") -> None:
        counters = snapshot.get("counters", {})
        with Session(self.engine) as session:
            for model in (
                ReceiptRow,
                DeliveryRow,
                PaymentRow,
                OrderRow,
                PromotionRow,
                StaffRow,
                CustomerRow,
                MenuItemRow,
                InventoryRow,
                BranchRow,
                AppConfig,
            ):
                session.exec(delete(model))

            session.add(
                AppConfig(
                    name=name,
                    branch_counter=int(counters.get("branch", 1)),
                    customer_counter=int(counters.get("customer", 1)),
                    staff_counter=int(counters.get("staff", 1)),
                    item_counter=int(counters.get("item", 1)),
                    ingredient_counter=int(counters.get("ingredient", 1)),
                    order_counter=int(counters.get("order", 1)),
                    payment_counter=int(counters.get("payment", 1)),
                    delivery_counter=int(counters.get("delivery", 1)),
                    receipt_counter=int(counters.get("receipt", 1)),
                    promo_counter=int(counters.get("promo", 1)),
                    tracking_counter=int(counters.get("tracking", 1)),
                    delivery_eta_hours=int(snapshot.get("delivery_eta_hours", 1)),
                    loyalty_points=dict(snapshot.get("loyalty_points", {})),
                    order_ratings={order_id: list(ratings) for order_id, ratings in snapshot.get("order_ratings", {}).items()},
                )
            )

            for branch_id, payload in snapshot.get("branches", {}).items():
                session.add(
                    BranchRow(
                        branch_id=branch_id,
                        location=payload["location"],
                        pos_config=payload["posConfig"],
                        inventory_ids=list(payload.get("inventoryIds", [])),
                    )
                )

            for ingredient_id, payload in snapshot.get("inventory", {}).items():
                session.add(
                    InventoryRow(
                        ingredient_id=ingredient_id,
                        stock_level=int(payload["stockLevel"]),
                        reorder_point=int(payload["reorderPoint"]),
                    )
                )

            for item_id, payload in snapshot.get("menu_items", {}).items():
                session.add(
                    MenuItemRow(
                        item_id=item_id,
                        name=payload["name"],
                        price=float(payload["price"]),
                        is_available=bool(payload["isAvailable"]),
                    )
                )

            for customer_id, payload in snapshot.get("customers", {}).items():
                customer = payload["customer"]
                profile = customer["profile"]
                session.add(
                    CustomerRow(
                        customer_id=customer_id,
                        username=customer["username"],
                        password_hash=customer["password_hash"],
                        full_name=profile["full_name"],
                        email=profile["email"],
                        phone=profile["phone"],
                        loyalty_status=customer["loyaltyStatus"],
                        tier_points=int(payload.get("tier_points", 0)),
                        order_ids=list(customer.get("order_ids", [])),
                    )
                )

            for staff_id, payload in snapshot.get("staff", {}).items():
                session.add(
                    StaffRow(
                        staff_id=staff_id,
                        user_id=staff_id,
                        username=payload["username"],
                        roles=list(payload.get("roles", [])),
                        password_hash=payload["password_hash"],
                        branch_id=payload["branchId"],
                        staff_kind=payload.get("_kind", payload.get("roles", ["staff"])[0].title()),
                        station=payload.get("station"),
                        pos_terminal_id=payload.get("posTerminalId"),
                    )
                )

            for promo_id, payload in snapshot.get("promotions", {}).items():
                session.add(
                    PromotionRow(
                        promo_id=promo_id,
                        discount_type=payload["discountType"],
                        valid_until=date.fromisoformat(payload["validUntil"]),
                        discount_value=float(payload["discountValue"]),
                        applicable_item_ids=list(payload.get("applicableItemIds", [])),
                    )
                )

            for order_id, payload in snapshot.get("orders", {}).items():
                session.add(
                    OrderRow(
                        order_id=order_id,
                        status=payload["status"],
                        order_type=payload["orderType"],
                        total_amount=float(payload.get("totalAmount", 0.0)),
                        customer_id=payload["customerId"],
                        branch_id=payload["branchId"],
                        promotion_id=payload.get("promotionId"),
                        discount_amount=float(payload.get("discountAmount", 0.0)),
                        payment_id=payload.get("paymentId"),
                        delivery_id=payload.get("deliveryId"),
                        items=[dict(item) for item in payload.get("items", [])],
                    )
                )

            for payment_id, payload in snapshot.get("payments", {}).items():
                session.add(
                    PaymentRow(
                        payment_id=payment_id,
                        amount=float(payload["amount"]),
                        status=payload["status"],
                        method=payload["method"],
                        order_id=payload["orderId"],
                        receipt_id=payload.get("receiptId"),
                    )
                )

            for delivery in snapshot.get("deliveries", {}).values():
                session.add(
                    DeliveryRow(
                        tracking_id=delivery["tracking_id"],
                        delivery_id=delivery["delivery_id"],
                        order_id=delivery["order_id"],
                        status=delivery["status"],
                        eta=delivery["eta"],
                    )
                )

            for receipt_id, payload in snapshot.get("receipts", {}).items():
                session.add(
                    ReceiptRow(
                        receipt_id=receipt_id,
                        payment_id=payload["payment_id"],
                        amount=float(payload["amount"]),
                        issued_at=datetime.fromisoformat(payload["issued_at"]),
                    )
                )

            session.commit()
