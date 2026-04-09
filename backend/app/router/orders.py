from pydantic_core import ErrorDetails
from cmath import e
from sqlalchemy.testing.pickleable import Order
from sqlalchemy.exc import StatementError
from sqlalchemy.orm import exc
from sqlmodel import Session, select, or_
from fastapi import Depends, FastAPI, HTTPException, APIRouter
from traceback import print_exc
from ..db import get_session
from ..schemas import Branch, OrderItem, BranchInventory, OrderStatusEnum

from .menu import get_item_by_id, count_item_in_branch, get_item_in_inventory
from .branches import get_branch_by_id

order_router = APIRouter(prefix="/orders")

@order_router.post("/make-order/")
def make_order(
    customer_id: str, branch_id: int, items: dict[int, int],
    session: Session = Depends(get_session)
):
    try:
        total = 0
        for item_id, quantity in items.items():
            item = get_item_by_id(item_id, session)
            if item is None:
                raise HTTPException(
                    status_code=400,
                    detail=f"Item with id {item_id} not found in menu"
                )
                
            count = count_item_in_branch(item_id, branch_id, session)
            if count is None:
                raise HTTPException(
                    status_code=400,
                    detail=f"Item {item_id} is not stocked in branch {branch_id}",
                )

            if count < quantity:
                raise HTTPException(
                    status_code=400,
                    detail=f"Not enough stock for item {item_id}",
                )
            
            # update new quantity
            inventory_item = get_item_in_inventory(item_id, branch_id, session)
            assert inventory_item is not None, "Item shouldn't be None"
            inventory_item.quantity -= count
            session.add(inventory_item)
            session.commit()
            session.refresh(inventory_item), session
                
            item = get_item_by_id(item_id, session)
            assert item is not None, "Item shouldn't be None"
            price = item.price
            order = OrderItem(customer_id=customer_id, branch_id=branch_id, item_id=item_id)
            total += price * quantity
            
        return {
            "status_code": 200,
            "total_price": total,
            "detail": f"Created Order with ID {order.id}"
        }
    except HTTPException as e:
        raise e
    except Exception:
        print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")
        
        
    
@order_router.get("/list-order")
def list_order(
    session: Session = Depends(get_session)
):
    try:
        statement = select(OrderItem)
        results = session.exec(statement)
        return list(results)
    except:
        print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")
        
@order_router.get("/list-order-in-branch")
def list_order_in_branch(
    branch_id: int,
    session: Session = Depends(get_session)
):
    try:
        branch = get_branch_by_id(branch_id)
        if branch is None:
            raise HTTPException(status_code=404, detail=f"Branch ID with {branch_id} not found")
        statement = select(OrderItem).where(OrderItem.branch_id == branch_id)
        results = session.exec(statement)
        return list(results)
    except:
        print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")
    

@order_router.get("/get-order-item-by-id")
def get_order_item_by_id(
    id: int,
    session: Session = Depends(get_session)
) -> OrderItem | None:
    try:
        statement = select(OrderItem).where(OrderItem.id == id)
        result = session.exec(statement).one_or_none()
        return result
    except:
        print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")

@order_router.patch("/change-order-status")
def change_order_status(
    id: int, status: OrderStatusEnum,
    session: Session = Depends(get_session)
):
    try:
        order_item = get_order_item_by_id(id)
        if order_item is None:
            raise HTTPException(status_code=404, detail="Order not found")
        order_item.status = status
        session.add(order_item)
        session.commit()
        session.refresh(order_item)
        return {"status_code": 200, "detail": f"Status updated to {status}"}
    except HTTPException as e:
        raise e
    except:
        print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")
        