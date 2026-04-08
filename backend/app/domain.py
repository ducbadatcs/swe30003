from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from hashlib import sha256
from typing import Any


@dataclass
class CustomerProfile:
    full_name: str
    email: str
    phone: str


@dataclass
class PerformanceRecord:
    completed_orders: int
    average_preparation_minutes: float
    average_rating: float


@dataclass
class DashboardData:
    branch_count: int
    customer_count: int
    staff_count: int
    menu_item_count: int
    active_order_count: int
    revenue_today: float
    recent_orders: list[dict[str, Any]]


@dataclass
class DeliveryRecord:
    delivery_id: str
    order_id: str
    tracking_id: str
    status: str
    eta: str


@dataclass
class OrderLine:
    menu_item_id: str
    name: str
    quantity: int
    unit_price: float

    @property
    def total(self) -> float:
        return round(self.quantity * self.unit_price, 2)


@dataclass
class Receipt:
    receipt_id: str
    payment_id: str
    amount: float
    issued_at: datetime

    def generatePDF(self) -> str:
        return (
            f"Receipt {self.receipt_id}\n"
            f"Payment: {self.payment_id}\n"
            f"Amount: ${self.amount:.2f}\n"
            f"Issued: {self.issued_at.isoformat()}"
        )

    def sendViaSMS(self) -> None:
        return None


@dataclass
class UserAccount(ABC):
    user_id: str
    username: str
    roles: list[str]
    password_hash: str
    is_logged_in: bool = field(default=False, init=False)

    def login(self, password: str) -> bool:
        authenticated = self.password_hash == sha256(password.encode("utf-8")).hexdigest()
        self.is_logged_in = authenticated
        return authenticated

    def logout(self) -> None:
        self.is_logged_in = False


@dataclass
class Customer(UserAccount):
    profile: CustomerProfile
    loyaltyStatus: str
    order_ids: list[str] = field(default_factory=list)

    def getOrderHistory(self) -> list[Order]:
        state = getattr(self, "_state", None)
        if state is None:
            return []
        return [state.orders[order_id] for order_id in self.order_ids if order_id in state.orders]


@dataclass
class Staff(UserAccount, ABC):
    staffId: str
    branchId: str

    def trackPerformance(self) -> PerformanceRecord:
        state = getattr(self, "_state", None)
        if state is None:
            return PerformanceRecord(completed_orders=0, average_preparation_minutes=0.0, average_rating=0.0)
        return state.calculate_staff_performance(self.staffId)


@dataclass
class KitchenStaff(Staff):
    station: str

    def updateOrderStatus(self, orderId: str, status: str) -> None:
        state = getattr(self, "_state", None)
        if state is None:
            raise RuntimeError("Kitchen staff is not attached to application state")
        state.update_order_status(orderId, status)


@dataclass
class Cashier(Staff):
    posTerminalId: str

    def processSale(self, orderId: str) -> Payment:
        state = getattr(self, "_state", None)
        if state is None:
            raise RuntimeError("Cashier is not attached to application state")
        return state.process_payment(orderId, "card")


@dataclass
class Manager(Staff):
    def viewDashboard(self) -> DashboardData:
        state = getattr(self, "_state", None)
        if state is None:
            raise RuntimeError("Manager is not attached to application state")
        return state.dashboard()

    def updateMenuItem(self, itemId: str) -> None:
        state = getattr(self, "_state", None)
        if state is None:
            raise RuntimeError("Manager is not attached to application state")
        state.toggle_menu_item(itemId)


@dataclass
class MenuItem:
    itemId: str
    name: str
    price: float
    isAvailable: bool

    def getCurrentPrice(self) -> float:
        return round(self.price, 2)


@dataclass
class Inventory:
    ingredientId: str
    stockLevel: int
    reorderPoint: int

    def updateStock(self, quantity: int) -> None:
        self.stockLevel = quantity


@dataclass
class PaymentMethod(ABC):
    method_name: str = "generic"

    @abstractmethod
    def processPayment(self, amount: float) -> bool:
        raise NotImplementedError


@dataclass
class CashPayment(PaymentMethod):
    method_name: str = "cash"

    def processPayment(self, amount: float) -> bool:
        return amount >= 0


@dataclass
class CardPayment(PaymentMethod):
    method_name: str = "card"

    def processPayment(self, amount: float) -> bool:
        return amount >= 0


@dataclass
class EWalletPayment(PaymentMethod):
    method_name: str = "ewallet"

    def processPayment(self, amount: float) -> bool:
        return amount >= 0


@dataclass
class Payment:
    paymentId: str
    amount: float
    status: str
    method: str
    orderId: str
    receiptId: str | None = None


@dataclass
class Order:
    orderId: str
    status: str
    orderType: str
    totalAmount: float
    customerId: str
    branchId: str
    items: list[OrderLine] = field(default_factory=list)
    promotionId: str | None = None
    discountAmount: float = 0.0
    paymentId: str | None = None
    deliveryId: str | None = None

    def updateStatus(self, newStatus: str) -> None:
        self.status = newStatus

    def calculateTotal(self) -> float:
        subtotal = sum(item.total for item in self.items)
        return round(max(subtotal - self.discountAmount, 0.0), 2)


@dataclass
class Promotion:
    promoId: str
    discountType: str
    validUntil: date
    discountValue: float
    applicableItemIds: list[str] = field(default_factory=list)
    _state: Any = field(default=None, repr=False, compare=False)

    def validatePromo(self, orderId: str) -> bool:
        state = getattr(self, "_state", None)
        if state is None:
            return False
        order = state.orders.get(orderId)
        return order is not None and self.validUntil >= date.today()

    def calculateDiscount(self, order: Order) -> float:
        if self.validUntil < date.today():
            return 0.0
        subtotal = sum(line.total for line in order.items)
        if self.discountType == "percent":
            return round(subtotal * (self.discountValue / 100.0), 2)
        return round(min(self.discountValue, subtotal), 2)


@dataclass
class Branch:
    branchId: str
    location: str
    posConfig: str
    inventoryIds: list[str] = field(default_factory=list)


@dataclass
class PaymentProcessor:
    _state: Any = field(default=None, repr=False, compare=False)

    def executePayment(self, orderId: str, method: PaymentMethod) -> Payment:
        state = getattr(self, "_state", None)
        if state is None:
            raise RuntimeError("Payment processor is not attached to application state")
        return state.execute_payment(orderId, method)


@dataclass
class DeliveryService:
    _state: Any = field(default=None, repr=False, compare=False)

    def scheduleDelivery(self, orderId: str) -> DeliveryRecord:
        state = getattr(self, "_state", None)
        if state is None:
            raise RuntimeError("Delivery service is not attached to application state")
        return state.schedule_delivery(orderId)

    def getTrackingStatus(self, trackingId: str) -> str:
        state = getattr(self, "_state", None)
        if state is None:
            return "unknown"
        return state.get_delivery_status(trackingId)


@dataclass
class LoyaltyService:
    _state: Any = field(default=None, repr=False, compare=False)

    def creditPoints(self, customerId: str, order: Order) -> None:
        state = getattr(self, "_state", None)
        if state is None:
            raise RuntimeError("Loyalty service is not attached to application state")
        state.credit_points(customerId, order)

    def redeemPoints(self, customerId: str, points: int) -> bool:
        state = getattr(self, "_state", None)
        if state is None:
            raise RuntimeError("Loyalty service is not attached to application state")
        return state.redeem_points(customerId, points)

    def updateTier(self, customerId: str) -> None:
        state = getattr(self, "_state", None)
        if state is None:
            raise RuntimeError("Loyalty service is not attached to application state")
        state.update_customer_tier(customerId)


@dataclass
class PromotionSummary:
    promoId: str
    discountType: str
    validUntil: str
    discountValue: float
    applicableItemIds: list[str]


@dataclass
class ClassCatalogItem:
    name: str
    category: str
    description: str
