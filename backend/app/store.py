from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any, cast

from .persistence import SQLModelStateStore, to_jsonable
from .domain import (
    Branch,
    CashPayment,
    Cashier,
    CardPayment,
    ClassCatalogItem,
    Customer,
    CustomerProfile,
    DashboardData,
    DeliveryRecord,
    DeliveryService,
    EWalletPayment,
    Inventory,
    KitchenStaff,
    LoyaltyService,
    Manager,
    MenuItem,
    Order,
    OrderLine,
    Payment,
    PaymentMethod,
    PaymentProcessor,
    PerformanceRecord,
    Promotion,
    Receipt,
)


@dataclass
class CustomerRecord:
    customer: Customer
    tier_points: int = 0


@dataclass
class CounterState:
    value: int


class AppState:
    def __init__(self) -> None:
        self._branch_ids = CounterState(1)
        self._customer_ids = CounterState(1)
        self._staff_ids = CounterState(1)
        self._item_ids = CounterState(1)
        self._ingredient_ids = CounterState(1)
        self._order_ids = CounterState(1)
        self._payment_ids = CounterState(1)
        self._delivery_ids = CounterState(1)
        self._receipt_ids = CounterState(1)
        self._promo_ids = CounterState(1)
        self._tracking_ids = CounterState(1)

        self._snapshot_store = SQLModelStateStore(Path(__file__).with_name("restaurant.sqlite3"))

        self.branches: dict[str, Branch] = {}
        self.inventory: dict[str, Inventory] = {}
        self.menu_items: dict[str, MenuItem] = {}
        self.orders: dict[str, Order] = {}
        self.payments: dict[str, Payment] = {}
        self.deliveries: dict[str, DeliveryRecord] = {}
        self.receipts: dict[str, Receipt] = {}
        self.promotions: dict[str, Promotion] = {}
        self.customers: dict[str, CustomerRecord] = {}
        self.staff: dict[str, Any] = {}
        self.loyalty_points: dict[str, int] = {}
        self.order_ratings: dict[str, list[int]] = {}
        self.delivery_eta_hours = 1
        self._persistence_suspended = False

        self.payment_processor = PaymentProcessor()
        self.delivery_service = DeliveryService()
        self.loyalty_service = LoyaltyService()

        self._attach_services()
        self._persistence_suspended = True
        snapshot = self._snapshot_store.load()
        try:
            if snapshot is None:
                self._seed()
                self._persistence_suspended = False
                self._persist()
            else:
                self._restore_snapshot(snapshot)
        finally:
            self._persistence_suspended = False

    def _attach_services(self) -> None:
        self.payment_processor._state = cast(Any, self)
        self.delivery_service._state = cast(Any, self)
        self.loyalty_service._state = cast(Any, self)

    @staticmethod
    def _hash_password(password: str) -> str:
        return sha256(password.encode("utf-8")).hexdigest()

    def _attach_state(self, entity: Any) -> Any:
        entity._state = self
        return entity

    def _next_id(self, prefix: str, counter: CounterState) -> str:
        value = counter.value
        counter.value += 1
        return f"{prefix}-{value:03d}"

    def _persist(self) -> None:
        if self._persistence_suspended:
            return
        self._snapshot_store.save(self._snapshot())

    def _snapshot(self) -> dict[str, Any]:
        return {
            "counters": {
                "branch": self._branch_ids.value,
                "customer": self._customer_ids.value,
                "staff": self._staff_ids.value,
                "item": self._item_ids.value,
                "ingredient": self._ingredient_ids.value,
                "order": self._order_ids.value,
                "payment": self._payment_ids.value,
                "delivery": self._delivery_ids.value,
                "receipt": self._receipt_ids.value,
                "promo": self._promo_ids.value,
                "tracking": self._tracking_ids.value,
            },
            "delivery_eta_hours": self.delivery_eta_hours,
            "branches": to_jsonable(self.branches),
            "inventory": to_jsonable(self.inventory),
            "menu_items": to_jsonable(self.menu_items),
            "orders": to_jsonable(self.orders),
            "payments": to_jsonable(self.payments),
            "deliveries": to_jsonable(self.deliveries),
            "receipts": to_jsonable(self.receipts),
            "promotions": to_jsonable(self.promotions),
            "customers": to_jsonable(self.customers),
            "staff": to_jsonable(self.staff),
            "loyalty_points": to_jsonable(self.loyalty_points),
            "order_ratings": to_jsonable(self.order_ratings),
        }

    def _restore_snapshot(self, snapshot: dict[str, Any]) -> None:
        counters = snapshot.get("counters", {})
        self._branch_ids.value = int(counters.get("branch", 1))
        self._customer_ids.value = int(counters.get("customer", 1))
        self._staff_ids.value = int(counters.get("staff", 1))
        self._item_ids.value = int(counters.get("item", 1))
        self._ingredient_ids.value = int(counters.get("ingredient", 1))
        self._order_ids.value = int(counters.get("order", 1))
        self._payment_ids.value = int(counters.get("payment", 1))
        self._delivery_ids.value = int(counters.get("delivery", 1))
        self._receipt_ids.value = int(counters.get("receipt", 1))
        self._promo_ids.value = int(counters.get("promo", 1))
        self._tracking_ids.value = int(counters.get("tracking", 1))

        self.delivery_eta_hours = int(snapshot.get("delivery_eta_hours", 1))

        self.branches = {
            branch_id: Branch(
                branchId=branch_id,
                location=payload["location"],
                posConfig=payload["posConfig"],
                inventoryIds=list(payload.get("inventoryIds", [])),
            )
            for branch_id, payload in snapshot.get("branches", {}).items()
        }
        self.inventory = {
            ingredient_id: Inventory(
                ingredientId=ingredient_id,
                stockLevel=int(payload["stockLevel"]),
                reorderPoint=int(payload["reorderPoint"]),
            )
            for ingredient_id, payload in snapshot.get("inventory", {}).items()
        }
        self.menu_items = {
            item_id: MenuItem(
                itemId=item_id,
                name=payload["name"],
                price=float(payload["price"]),
                isAvailable=bool(payload["isAvailable"]),
            )
            for item_id, payload in snapshot.get("menu_items", {}).items()
        }
        self.customers = {}
        for customer_id, payload in snapshot.get("customers", {}).items():
            customer = Customer(
                user_id=customer_id,
                username=payload["customer"]["username"],
                roles=list(payload["customer"]["roles"]),
                password_hash=payload["customer"]["password_hash"],
                profile=CustomerProfile(**payload["customer"]["profile"]),
                loyaltyStatus=payload["customer"]["loyaltyStatus"],
                order_ids=list(payload["customer"].get("order_ids", [])),
            )
            self._attach_state(customer)
            self.customers[customer_id] = CustomerRecord(customer=customer, tier_points=int(payload.get("tier_points", 0)))
        self.staff = {}
        for staff_id, payload in snapshot.get("staff", {}).items():
            kind = payload.get("_kind", payload.get("roles", ["staff"])[0].title())
            common = {
                "user_id": staff_id,
                "username": payload["username"],
                "roles": list(payload["roles"]),
                "password_hash": payload["password_hash"],
                "staffId": payload["staffId"],
                "branchId": payload["branchId"],
            }
            if kind == "Manager":
                staff = Manager(**common)
            elif kind == "Cashier":
                staff = Cashier(**common, posTerminalId=payload["posTerminalId"])
            else:
                staff = KitchenStaff(**common, station=payload["station"])
            self._attach_state(staff)
            self.staff[staff_id] = staff

        self.promotions = {}
        for promo_id, payload in snapshot.get("promotions", {}).items():
            promo = Promotion(
                promoId=promo_id,
                discountType=payload["discountType"],
                validUntil=date.fromisoformat(payload["validUntil"]),
                discountValue=float(payload["discountValue"]),
                applicableItemIds=list(payload.get("applicableItemIds", [])),
            )
            self._attach_state(promo)
            self.promotions[promo_id] = promo

        self.orders = {}
        for order_id, payload in snapshot.get("orders", {}).items():
            order = Order(
                orderId=order_id,
                status=payload["status"],
                orderType=payload["orderType"],
                totalAmount=float(payload.get("totalAmount", 0.0)),
                customerId=payload["customerId"],
                branchId=payload["branchId"],
                items=[
                    OrderLine(
                        menu_item_id=item["menu_item_id"],
                        name=item["name"],
                        quantity=int(item["quantity"]),
                        unit_price=float(item["unit_price"]),
                    )
                    for item in payload.get("items", [])
                ],
                promotionId=payload.get("promotionId"),
                discountAmount=float(payload.get("discountAmount", 0.0)),
                paymentId=payload.get("paymentId"),
                deliveryId=payload.get("deliveryId"),
            )
            self.orders[order_id] = order

        self.payments = {
            payment_id: Payment(
                paymentId=payment_id,
                amount=float(payload["amount"]),
                status=payload["status"],
                method=payload["method"],
                orderId=payload["orderId"],
                receiptId=payload.get("receiptId"),
            )
            for payment_id, payload in snapshot.get("payments", {}).items()
        }
        self.deliveries = {
            record["tracking_id"]: DeliveryRecord(
                delivery_id=record["delivery_id"],
                order_id=record["order_id"],
                tracking_id=record["tracking_id"],
                status=record["status"],
                eta=record["eta"],
            )
            for record in snapshot.get("deliveries", {}).values()
        }
        self.receipts = {
            receipt_id: Receipt(
                receipt_id=receipt_id,
                payment_id=payload["payment_id"],
                amount=float(payload["amount"]),
                issued_at=datetime.fromisoformat(payload["issued_at"]),
            )
            for receipt_id, payload in snapshot.get("receipts", {}).items()
        }
        self.loyalty_points = {customer_id: int(points) for customer_id, points in snapshot.get("loyalty_points", {}).items()}
        self.order_ratings = {order_id: [int(rating) for rating in ratings] for order_id, ratings in snapshot.get("order_ratings", {}).items()}

        self.payment_processor._state = cast(Any, self)
        self.delivery_service._state = cast(Any, self)
        self.loyalty_service._state = cast(Any, self)

        for customer_id in self.customers:
            self.update_customer_tier(customer_id)

    def _seed(self) -> None:
        branch_a = self.create_branch("Downtown Kitchen", "POS-A1")
        branch_b = self.create_branch("Riverside Cafe", "POS-B1")

        burger = self.create_menu_item("Burger", 12.5, True)
        fries = self.create_menu_item("Fries", 5.5, True)
        latte = self.create_menu_item("Latte", 6.0, True)
        salad = self.create_menu_item("Seasonal Salad", 9.75, False)
        pasta = self.create_menu_item("Pasta", 14.25, True)

        self.create_inventory_record(branch_a.branchId, burger.itemId, 120, 30)
        self.create_inventory_record(branch_a.branchId, fries.itemId, 80, 20)
        self.create_inventory_record(branch_b.branchId, latte.itemId, 60, 15)
        self.create_inventory_record(branch_b.branchId, salad.itemId, 35, 12)
        self.create_inventory_record(branch_b.branchId, pasta.itemId, 50, 18)

        alice = self.create_customer(
            username="alice",
            password="password123",
            full_name="Alice Tan",
            email="alice@example.com",
            phone="0412 555 010",
        )
        ben = self.create_customer(
            username="ben",
            password="password123",
            full_name="Ben Wong",
            email="ben@example.com",
            phone="0412 555 011",
        )
        clara = self.create_customer(
            username="clara",
            password="password123",
            full_name="Clara Ng",
            email="clara@example.com",
            phone="0412 555 012",
        )

        manager = Manager(
            user_id=self._next_id("usr", self._staff_ids),
            username="manager",
            roles=["manager"],
            password_hash=self._hash_password("password123"),
            staffId="STF-001",
            branchId=branch_a.branchId,
        )
        cashier = Cashier(
            user_id=self._next_id("usr", self._staff_ids),
            username="cashier",
            roles=["cashier"],
            password_hash=self._hash_password("password123"),
            staffId="STF-002",
            branchId=branch_a.branchId,
            posTerminalId="POS-A1",
        )
        kitchen = KitchenStaff(
            user_id=self._next_id("usr", self._staff_ids),
            username="kitchen",
            roles=["kitchen"],
            password_hash=self._hash_password("password123"),
            staffId="STF-003",
            branchId=branch_b.branchId,
            station="Hot Line",
        )
        self.staff[manager.staffId] = self._attach_state(manager)
        self.staff[cashier.staffId] = self._attach_state(cashier)
        self.staff[kitchen.staffId] = self._attach_state(kitchen)

        self.create_promotion("SPRING10", "percent", date.today() + timedelta(days=21), 10.0, [burger.itemId, pasta.itemId])
        self.create_promotion("WELCOME5", "fixed", date.today() + timedelta(days=30), 5.0, [])

        order_1 = self.create_order(
            customer_id=alice.customer.user_id,
            branch_id=branch_a.branchId,
            order_type="dine-in",
            items=[{"menu_item_id": burger.itemId, "quantity": 2}, {"menu_item_id": fries.itemId, "quantity": 1}],
            promotion_id="promo-001",
        )
        order_2 = self.create_order(
            customer_id=ben.customer.user_id,
            branch_id=branch_b.branchId,
            order_type="pickup",
            items=[{"menu_item_id": latte.itemId, "quantity": 2}, {"menu_item_id": salad.itemId, "quantity": 1}],
        )
        order_3 = self.create_order(
            customer_id=clara.customer.user_id,
            branch_id=branch_a.branchId,
            order_type="delivery",
            items=[{"menu_item_id": pasta.itemId, "quantity": 1}, {"menu_item_id": fries.itemId, "quantity": 2}],
            promotion_id="promo-002",
        )

        self.update_order_status(order_2.orderId, "preparing")
        self.update_order_status(order_3.orderId, "ready-for-pickup")
        self.process_payment(order_1.orderId, CashPayment())
        self.process_payment(order_2.orderId, CardPayment())
        self.process_payment(order_3.orderId, EWalletPayment())
        self.schedule_delivery(order_3.orderId)

        self.credit_points(alice.customer.user_id, order_1)
        self.credit_points(ben.customer.user_id, order_2)
        self.credit_points(clara.customer.user_id, order_3)

    def create_branch(self, location: str, pos_config: str) -> Branch:
        branch = Branch(
            branchId=self._next_id("br", self._branch_ids),
            location=location,
            posConfig=pos_config,
        )
        self.branches[branch.branchId] = branch
        self._persist()
        return branch

    def create_inventory_record(self, branch_id: str, menu_item_id: str, stock_level: int, reorder_point: int) -> Inventory:
        ingredient_id = self._next_id("ing", self._ingredient_ids)
        inventory = Inventory(ingredientId=ingredient_id, stockLevel=stock_level, reorderPoint=reorder_point)
        self.inventory[inventory.ingredientId] = inventory
        self.branches[branch_id].inventoryIds.append(inventory.ingredientId)
        self._persist()
        return inventory

    def create_menu_item(self, name: str, price: float, is_available: bool) -> MenuItem:
        item = MenuItem(itemId=self._next_id("item", self._item_ids), name=name, price=round(price, 2), isAvailable=is_available)
        self.menu_items[item.itemId] = item
        self._persist()
        return item

    def toggle_menu_item(self, item_id: str) -> MenuItem:
        item = self.menu_items[item_id]
        item.isAvailable = not item.isAvailable
        self._persist()
        return item

    def update_menu_item(self, item_id: str, *, name: str | None = None, price: float | None = None, is_available: bool | None = None) -> MenuItem:
        item = self.menu_items[item_id]
        if name is not None:
            item.name = name
        if price is not None:
            item.price = round(price, 2)
        if is_available is not None:
            item.isAvailable = is_available
        self._persist()
        return item

    def create_customer(self, username: str, password: str, full_name: str, email: str, phone: str) -> CustomerRecord:
        user_id = self._next_id("usr", self._customer_ids)
        customer = Customer(
            user_id=user_id,
            username=username,
            roles=["customer"],
            password_hash=self._hash_password(password),
            profile=CustomerProfile(full_name=full_name, email=email, phone=phone),
            loyaltyStatus="Bronze",
        )
        self._attach_state(customer)
        record = CustomerRecord(customer=customer, tier_points=0)
        self.customers[user_id] = record
        self.loyalty_points[user_id] = 0
        self._persist()
        return record

    def authenticate_customer(self, username: str, password: str) -> CustomerRecord | None:
        password_hash = self._hash_password(password)
        for record in self.customers.values():
            customer = record.customer
            if customer.username == username and customer.password_hash == password_hash:
                return record
        return None

    def get_customer(self, customer_id: str) -> CustomerRecord:
        return self.customers[customer_id]

    def create_promotion(self, promo_code: str, discount_type: str, valid_until: date, discount_value: float, applicable_item_ids: list[str]) -> Promotion:
        promo = Promotion(
            promoId=self._next_id("promo", self._promo_ids),
            discountType=discount_type,
            validUntil=valid_until,
            discountValue=discount_value,
            applicableItemIds=applicable_item_ids,
        )
        self._attach_state(promo)
        self.promotions[promo.promoId] = promo
        self._persist()
        return promo

    def create_order(self, customer_id: str, branch_id: str, order_type: str, items: list[dict[str, Any]], promotion_id: str | None = None) -> Order:
        order_lines: list[OrderLine] = []
        for item in items:
            menu_item = self.menu_items[item["menu_item_id"]]
            order_lines.append(
                OrderLine(
                    menu_item_id=menu_item.itemId,
                    name=menu_item.name,
                    quantity=int(item["quantity"]),
                    unit_price=menu_item.price,
                )
            )
        order = Order(
            orderId=self._next_id("ord", self._order_ids),
            status="pending",
            orderType=order_type,
            totalAmount=0.0,
            customerId=customer_id,
            branchId=branch_id,
            items=order_lines,
            promotionId=promotion_id,
        )
        if promotion_id and promotion_id in self.promotions:
            promo = self.promotions[promotion_id]
            order.discountAmount = promo.calculateDiscount(order)
        order.totalAmount = order.calculateTotal()
        self.orders[order.orderId] = order
        self.customers[customer_id].customer.order_ids.append(order.orderId)
        self._persist()
        return order

    def update_order_status(self, order_id: str, status: str) -> Order:
        order = self.orders[order_id]
        order.updateStatus(status)
        self._persist()
        return order

    def execute_payment(self, order_id: str, method: PaymentMethod) -> Payment:
        order = self.orders[order_id]
        amount = order.calculateTotal()
        payment_id = self._next_id("pay", self._payment_ids)
        payment_status = "completed" if method.processPayment(amount) else "failed"
        payment = Payment(
            paymentId=payment_id,
            amount=amount,
            status=payment_status,
            method=method.method_name,
            orderId=order_id,
        )
        if payment_status == "completed":
            receipt = Receipt(
                receipt_id=self._next_id("rcp", self._receipt_ids),
                payment_id=payment.paymentId,
                amount=amount,
                issued_at=datetime.now(timezone.utc),
            )
            self.receipts[receipt.receipt_id] = receipt
            payment.receiptId = receipt.receipt_id
            if order.status != "delivered":
                order.status = "paid"
        self.payments[payment.paymentId] = payment
        order.paymentId = payment.paymentId
        order.totalAmount = amount
        self._persist()
        return payment

    def process_payment(self, order_id: str, method: PaymentMethod | str) -> Payment:
        payment_method = self._resolve_payment_method(method)
        payment = self.execute_payment(order_id, payment_method)
        if payment.status == "completed":
            order = self.orders[order_id]
            self.credit_points(order.customerId, order)
        return payment

    def _resolve_payment_method(self, method: PaymentMethod | str) -> PaymentMethod:
        if isinstance(method, PaymentMethod):
            return method
        mapping: dict[str, PaymentMethod] = {
            "cash": CashPayment(),
            "card": CardPayment(),
            "ewallet": EWalletPayment(),
        }
        return mapping.get(method, CardPayment())

    def schedule_delivery(self, order_id: str) -> DeliveryRecord:
        order = self.orders[order_id]
        delivery = DeliveryRecord(
            delivery_id=self._next_id("del", self._delivery_ids),
            order_id=order_id,
            tracking_id=self._next_id("trk", self._tracking_ids),
            status="scheduled",
            eta=(datetime.now(timezone.utc) + timedelta(hours=self.delivery_eta_hours)).isoformat(),
        )
        self.deliveries[delivery.tracking_id] = delivery
        order.deliveryId = delivery.delivery_id
        order.status = "out-for-delivery"
        self._persist()
        return delivery

    def get_delivery_status(self, tracking_id: str) -> str:
        delivery = self.deliveries.get(tracking_id)
        return delivery.status if delivery else "unknown"

    def credit_points(self, customer_id: str, order: Order) -> None:
        points = max(int(order.calculateTotal() // 5), 1)
        self.loyalty_points[customer_id] = self.loyalty_points.get(customer_id, 0) + points
        self.update_customer_tier(customer_id)
        self._persist()

    def redeem_points(self, customer_id: str, points: int) -> bool:
        current = self.loyalty_points.get(customer_id, 0)
        if points <= 0 or current < points:
            return False
        self.loyalty_points[customer_id] = current - points
        self.update_customer_tier(customer_id)
        self._persist()
        return True

    def update_customer_tier(self, customer_id: str) -> None:
        points = self.loyalty_points.get(customer_id, 0)
        customer = self.customers[customer_id].customer
        if points >= 100:
            customer.loyaltyStatus = "Platinum"
        elif points >= 50:
            customer.loyaltyStatus = "Gold"
        elif points >= 20:
            customer.loyaltyStatus = "Silver"
        else:
            customer.loyaltyStatus = "Bronze"
        self.customers[customer_id].tier_points = points
        self._persist()

    def calculate_staff_performance(self, staff_id: str) -> PerformanceRecord:
        completed_orders = sum(1 for order in self.orders.values() if order.status in {"paid", "delivered", "completed"})
        avg_prep = 14.5 if completed_orders else 0.0
        avg_rating = 4.6 if completed_orders else 0.0
        return PerformanceRecord(completed_orders=completed_orders, average_preparation_minutes=avg_prep, average_rating=avg_rating)

    def dashboard(self) -> DashboardData:
        recent_orders = sorted(self.orders.values(), key=lambda order: order.orderId, reverse=True)[:5]
        revenue_today = round(sum(payment.amount for payment in self.payments.values() if payment.status == "completed"), 2)
        return DashboardData(
            branch_count=len(self.branches),
            customer_count=len(self.customers),
            staff_count=len(self.staff),
            menu_item_count=len(self.menu_items),
            active_order_count=sum(1 for order in self.orders.values() if order.status not in {"delivered", "cancelled"}),
            revenue_today=revenue_today,
            recent_orders=[self.order_to_dict(order) for order in recent_orders],
        )

    def branch_overview(self) -> list[dict[str, Any]]:
        return [
            {
                "branchId": branch.branchId,
                "location": branch.location,
                "posConfig": branch.posConfig,
                "inventoryCount": len(branch.inventoryIds),
            }
            for branch in self.branches.values()
        ]

    def customer_overview(self) -> list[dict[str, Any]]:
        data = []
        for record in self.customers.values():
            customer = record.customer
            data.append(
                {
                    "customerId": customer.user_id,
                    "username": customer.username,
                    "fullName": customer.profile.full_name,
                    "email": customer.profile.email,
                    "phone": customer.profile.phone,
                    "loyaltyStatus": customer.loyaltyStatus,
                    "points": record.tier_points,
                    "orderCount": len(customer.order_ids),
                }
            )
        return data

    def staff_overview(self) -> list[dict[str, Any]]:
        result: list[dict[str, Any]] = []
        for staff in self.staff.values():
            performance = staff.trackPerformance()
            result.append(
                {
                    "staffId": staff.staffId,
                    "username": staff.username,
                    "role": staff.roles[0],
                    "branchId": staff.branchId,
                    "performance": {
                        "completedOrders": performance.completed_orders,
                        "averagePreparationMinutes": performance.average_preparation_minutes,
                        "averageRating": performance.average_rating,
                    },
                }
            )
        return result

    def menu_item_overview(self) -> list[dict[str, Any]]:
        return [
            {
                "itemId": item.itemId,
                "name": item.name,
                "price": item.getCurrentPrice(),
                "isAvailable": item.isAvailable,
            }
            for item in self.menu_items.values()
        ]

    def inventory_overview(self) -> list[dict[str, Any]]:
        return [
            {
                "ingredientId": inventory.ingredientId,
                "stockLevel": inventory.stockLevel,
                "reorderPoint": inventory.reorderPoint,
                "status": "low" if inventory.stockLevel <= inventory.reorderPoint else "ok",
            }
            for inventory in self.inventory.values()
        ]

    def order_overview(self) -> list[dict[str, Any]]:
        return [self.order_to_dict(order) for order in sorted(self.orders.values(), key=lambda order: order.orderId, reverse=True)]

    def order_to_dict(self, order: Order) -> dict[str, Any]:
        customer = self.customers[order.customerId].customer
        payment = self.payments.get(order.paymentId) if order.paymentId else None
        delivery = None
        if order.deliveryId:
            delivery = next((record for record in self.deliveries.values() if record.order_id == order.orderId), None)
        return {
            "orderId": order.orderId,
            "status": order.status,
            "orderType": order.orderType,
            "totalAmount": order.calculateTotal(),
            "customerId": order.customerId,
            "customerName": customer.profile.full_name,
            "branchId": order.branchId,
            "promotionId": order.promotionId,
            "discountAmount": order.discountAmount,
            "payment": None if payment is None else {
                "paymentId": payment.paymentId,
                "amount": payment.amount,
                "status": payment.status,
                "method": payment.method,
                "receiptId": payment.receiptId,
            },
            "delivery": None if delivery is None else {
                "deliveryId": delivery.delivery_id,
                "trackingId": delivery.tracking_id,
                "status": delivery.status,
                "eta": delivery.eta,
            },
            "items": [
                {
                    "menuItemId": line.menu_item_id,
                    "name": line.name,
                    "quantity": line.quantity,
                    "unitPrice": line.unit_price,
                    "total": line.total,
                }
                for line in order.items
            ],
        }

    def promotion_overview(self) -> list[dict[str, Any]]:
        return [
            {
                "promoId": promotion.promoId,
                "discountType": promotion.discountType,
                "validUntil": promotion.validUntil.isoformat(),
                "discountValue": promotion.discountValue,
                "applicableItemIds": promotion.applicableItemIds,
            }
            for promotion in self.promotions.values()
        ]

    def update_inventory(self, ingredient_id: str, stock_level: int, reorder_point: int | None = None) -> Inventory:
        inventory = self.inventory[ingredient_id]
        inventory.updateStock(stock_level)
        if reorder_point is not None:
            inventory.reorderPoint = reorder_point
        self._persist()
        return inventory

    def customer_portal(self, customer_id: str) -> dict[str, Any]:
        customer_record = self.customers[customer_id]
        customer = customer_record.customer
        orders = [self.order_to_dict(order) for order in self.orders.values() if order.customerId == customer_id]
        return {
            "customer": {
                "customerId": customer.user_id,
                "username": customer.username,
                "fullName": customer.profile.full_name,
                "email": customer.profile.email,
                "phone": customer.profile.phone,
                "loyaltyStatus": customer.loyaltyStatus,
                "points": customer_record.tier_points,
            },
            "menuItems": self.menu_item_overview(),
            "promotions": self.promotion_overview(),
            "orders": orders,
            "branches": self.branch_overview(),
        }

    def class_catalog(self) -> list[ClassCatalogItem]:
        return [
            ClassCatalogItem("UserAccount", "abstract", "Base account with login and logout behaviour."),
            ClassCatalogItem("Customer", "entity", "Customer profile, loyalty status, and order history."),
            ClassCatalogItem("Staff", "abstract", "Shared staff identity and performance tracking."),
            ClassCatalogItem("KitchenStaff", "entity", "Kitchen role that updates order status."),
            ClassCatalogItem("Cashier", "entity", "POS role that processes sales."),
            ClassCatalogItem("Manager", "entity", "Supervisory role for menu and branch operations."),
            ClassCatalogItem("MenuItem", "entity", "Sellable menu record with live price and availability."),
            ClassCatalogItem("Inventory", "entity", "Ingredient stock and reorder thresholds."),
            ClassCatalogItem("Order", "entity", "Order lifecycle, total calculation, and payment linkage."),
            ClassCatalogItem("DeliveryService", "service", "Schedules deliveries and tracks shipments."),
            ClassCatalogItem("Payment", "entity", "Captured payment, status, and receipt linkage."),
            ClassCatalogItem("PaymentMethod", "interface", "Common payment contract for cash, card, and e-wallet."),
            ClassCatalogItem("PaymentProcessor", "service", "Executes payment against an order."),
            ClassCatalogItem("Receipt", "entity", "Receipt content and message delivery helpers."),
            ClassCatalogItem("Promotion", "entity", "Discount rules and promo validation."),
            ClassCatalogItem("LoyaltyService", "service", "Credits, redeems, and tiers customer loyalty points."),
            ClassCatalogItem("Branch", "entity", "Branch profile and inventory ownership."),
        ]
