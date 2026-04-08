from __future__ import annotations

from datetime import date
from typing import Any, Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .domain import CashPayment, CardPayment, EWalletPayment
from .store import AppState

app = FastAPI(title="Restaurant Operations Platform", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

state = AppState()


class CustomerCreate(BaseModel):
    username: str
    password: str
    full_name: str = Field(min_length=1)
    email: str
    phone: str


class MenuItemCreate(BaseModel):
    name: str
    price: float = Field(ge=0)
    is_available: bool = True


class MenuItemUpdate(BaseModel):
    name: str | None = None
    price: float | None = Field(default=None, ge=0)
    is_available: bool | None = None


class InventoryUpdate(BaseModel):
    stock_level: int = Field(ge=0)
    reorder_point: int | None = Field(default=None, ge=0)


class OrderLineInput(BaseModel):
    menu_item_id: str
    quantity: int = Field(ge=1)


class OrderCreate(BaseModel):
    customer_id: str
    branch_id: str
    order_type: Literal["dine-in", "pickup", "delivery"] = "dine-in"
    items: list[OrderLineInput]
    promotion_id: str | None = None


class OrderStatusUpdate(BaseModel):
    status: str


class PromotionCreate(BaseModel):
    discount_type: Literal["percent", "fixed"]
    valid_until: date
    discount_value: float = Field(gt=0)
    applicable_item_ids: list[str] = []


class PaymentProcessRequest(BaseModel):
    method: Literal["cash", "card", "ewallet"]


class LoyaltyRedeemRequest(BaseModel):
    customer_id: str
    points: int = Field(gt=0)


class CustomerLogin(BaseModel):
    username: str
    password: str


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/dashboard")
def get_dashboard() -> Any:
    return state.dashboard()


@app.get("/api/model-map")
def get_model_map() -> list[dict[str, str]]:
    return [item.__dict__ for item in state.class_catalog()]


@app.get("/api/branches")
def get_branches() -> list[dict[str, Any]]:
    return state.branch_overview()


@app.get("/api/staff")
def get_staff() -> list[dict[str, Any]]:
    return state.staff_overview()


@app.get("/api/customers")
def get_customers() -> list[dict[str, Any]]:
    return state.customer_overview()


@app.post("/api/auth/login")
def login_customer(payload: CustomerLogin) -> dict[str, Any]:
    record = state.authenticate_customer(payload.username, payload.password)
    if record is None:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    customer = record.customer
    return {
        "customerId": customer.user_id,
        "username": customer.username,
        "fullName": customer.profile.full_name,
        "email": customer.profile.email,
        "phone": customer.profile.phone,
        "loyaltyStatus": customer.loyaltyStatus,
        "points": record.tier_points,
    }


@app.get("/api/customer-portal/{customer_id}")
def get_customer_portal(customer_id: str) -> dict[str, Any]:
    if customer_id not in state.customers:
        raise HTTPException(status_code=404, detail="Customer not found")
    return state.customer_portal(customer_id)


@app.post("/api/customers")
def create_customer(payload: CustomerCreate) -> dict[str, Any]:
    record = state.create_customer(
        username=payload.username,
        password=payload.password,
        full_name=payload.full_name,
        email=payload.email,
        phone=payload.phone,
    )
    return {
        "customerId": record.customer.user_id,
        "username": record.customer.username,
        "fullName": record.customer.profile.full_name,
        "email": record.customer.profile.email,
        "phone": record.customer.profile.phone,
        "loyaltyStatus": record.customer.loyaltyStatus,
        "points": record.tier_points,
    }


@app.get("/api/menu-items")
def get_menu_items() -> list[dict[str, Any]]:
    return state.menu_item_overview()


@app.post("/api/menu-items")
def create_menu_item(payload: MenuItemCreate) -> dict[str, Any]:
    item = state.create_menu_item(payload.name, payload.price, payload.is_available)
    return {"itemId": item.itemId, "name": item.name, "price": item.price, "isAvailable": item.isAvailable}


@app.patch("/api/menu-items/{item_id}")
def patch_menu_item(item_id: str, payload: MenuItemUpdate) -> dict[str, Any]:
    if item_id not in state.menu_items:
        raise HTTPException(status_code=404, detail="Menu item not found")
    item = state.update_menu_item(item_id, name=payload.name, price=payload.price, is_available=payload.is_available)
    return {"itemId": item.itemId, "name": item.name, "price": item.price, "isAvailable": item.isAvailable}


@app.get("/api/inventory")
def get_inventory() -> list[dict[str, Any]]:
    return state.inventory_overview()


@app.patch("/api/inventory/{ingredient_id}")
def patch_inventory(ingredient_id: str, payload: InventoryUpdate) -> dict[str, Any]:
    if ingredient_id not in state.inventory:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    inventory = state.update_inventory(ingredient_id, payload.stock_level, payload.reorder_point)
    return {
        "ingredientId": inventory.ingredientId,
        "stockLevel": inventory.stockLevel,
        "reorderPoint": inventory.reorderPoint,
    }


@app.get("/api/orders")
def get_orders() -> list[dict[str, Any]]:
    return state.order_overview()


@app.post("/api/orders")
def create_order(payload: OrderCreate) -> dict[str, Any]:
    if payload.customer_id not in state.customers:
        raise HTTPException(status_code=404, detail="Customer not found")
    if payload.branch_id not in state.branches:
        raise HTTPException(status_code=404, detail="Branch not found")
    for line in payload.items:
        if line.menu_item_id not in state.menu_items:
            raise HTTPException(status_code=404, detail=f"Menu item {line.menu_item_id} not found")
    order = state.create_order(
        customer_id=payload.customer_id,
        branch_id=payload.branch_id,
        order_type=payload.order_type,
        items=[line.model_dump() for line in payload.items],
        promotion_id=payload.promotion_id,
    )
    return state.order_to_dict(order)


@app.patch("/api/orders/{order_id}/status")
def update_order_status(order_id: str, payload: OrderStatusUpdate) -> dict[str, Any]:
    if order_id not in state.orders:
        raise HTTPException(status_code=404, detail="Order not found")
    order = state.update_order_status(order_id, payload.status)
    return state.order_to_dict(order)


@app.post("/api/orders/{order_id}/payment")
def process_payment(order_id: str, payload: PaymentProcessRequest) -> dict[str, Any]:
    if order_id not in state.orders:
        raise HTTPException(status_code=404, detail="Order not found")
    method_map = {
        "cash": CashPayment(),
        "card": CardPayment(),
        "ewallet": EWalletPayment(),
    }
    payment = state.process_payment(order_id, method_map[payload.method])
    return {
        "paymentId": payment.paymentId,
        "amount": payment.amount,
        "status": payment.status,
        "method": payment.method,
        "orderId": payment.orderId,
        "receiptId": payment.receiptId,
    }


@app.post("/api/orders/{order_id}/delivery")
def schedule_delivery(order_id: str) -> dict[str, Any]:
    if order_id not in state.orders:
        raise HTTPException(status_code=404, detail="Order not found")
    delivery = state.schedule_delivery(order_id)
    return delivery.__dict__


@app.get("/api/promotions")
def get_promotions() -> list[dict[str, Any]]:
    return state.promotion_overview()


@app.post("/api/promotions")
def create_promotion(payload: PromotionCreate) -> dict[str, Any]:
    promotion = state.create_promotion(
        promo_code="generated",
        discount_type=payload.discount_type,
        valid_until=payload.valid_until,
        discount_value=payload.discount_value,
        applicable_item_ids=payload.applicable_item_ids,
    )
    return {
        "promoId": promotion.promoId,
        "discountType": promotion.discountType,
        "validUntil": promotion.validUntil.isoformat(),
        "discountValue": promotion.discountValue,
        "applicableItemIds": promotion.applicableItemIds,
    }


@app.post("/api/loyalty/redeem")
def redeem_points(payload: LoyaltyRedeemRequest) -> dict[str, Any]:
    if payload.customer_id not in state.customers:
        raise HTTPException(status_code=404, detail="Customer not found")
    redeemed = state.redeem_points(payload.customer_id, payload.points)
    return {
        "customerId": payload.customer_id,
        "redeemed": redeemed,
        "points": state.loyalty_points.get(payload.customer_id, 0),
        "loyaltyStatus": state.customers[payload.customer_id].customer.loyaltyStatus,
    }


@app.get("/api/loyalty/{customer_id}")
def get_loyalty(customer_id: str) -> dict[str, Any]:
    if customer_id not in state.customers:
        raise HTTPException(status_code=404, detail="Customer not found")
    customer = state.customers[customer_id].customer
    return {
        "customerId": customer_id,
        "points": state.loyalty_points.get(customer_id, 0),
        "loyaltyStatus": customer.loyaltyStatus,
    }
