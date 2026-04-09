from idna.codec import search_function
from sqlalchemy.exc import StatementError
from importlib.resources import path
from fastapi.openapi.utils import status_code_ranges
from traceback import print_exc
from typing import Any

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, SQLModel, select, or_

from .db import engine, get_session
from .schemas import Branch, Customer, MenuItem, Staff, BranchInventory, OrderItem

app = FastAPI(title="Restaurant Operations API", version="2.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post(path="/register-branch")
def register_branch(
    id: str, name: str, address: str,
    session: Session = Depends(get_session)
):
    branch = Branch(id=id, name=name, address=address)
    try:
        session.add(branch)
        session.commit()
        return {"status_code": 200, "detail": "Branch registered successfully"}
    except:
        raise HTTPException(status_code=500, detail="Internal Server Error")
        print_exc()
    

@app.get(path="/find-branches")
def find_branches(
    name: str, address: str,
    session: Session = Depends(get_session)
):
    
    try:
        statement = select(Branch).where(
            or_(
                name.lower() in Branch.name.lower(), 
                address.lower() in Branch.address.lower()))
        results = session.exec(statement)
        return results
    except:
        raise HTTPException(status_code=500, detail="Internal Server Error")
        print_exc()
    

@app.delete(path="/unregister-branch")
def unregister_branch(
    id: str, 
    session: Session = Depends(get_session)
):
    try:
        statement = select(Branch).where(Branch.id == id)
        result = session.exec(statement).one_or_none()
        if result is None:
            raise HTTPException(status_code = 404, detail = "Brand ID not found")
        session.delete(result)
        return {"status_code": 200, "detail": "Brand Unregistering complete"}
    except:
        raise HTTPException(status_code=500, detail="Internal Server Error")
        print_exc()

# customers
@app.post(path="/register-customer")
def register_customer(
    email: str, full_name: str, password: str, 
    session: Session = Depends(get_session)
):
    
    customer = Customer(email=email, full_name=full_name, password=password)
    try:
        session.add(customer)
        session.commit()
        return {"status_code": 200, "detail": "Customer registered successfully"}
    except:
        raise HTTPException(status_code=500, detail="Internal Server Error")
        print_exc()
    

@app.get("/get-customer-by-email")
def get_customer_by_email(
    email: str,
    session: Session = Depends(get_session)
):
    try:
        statement = select(Customer).where(Customer.email.lower() == email.lower())
        result = session.exec(statement).one_or_none()
        if result is None:
            raise HTTPException(status_code=404, detail="Customer Not Found")
        
        return {"status_code": 200, "detail": "Customer found"}
    except:
        raise HTTPException(status_code=500, detail="Internal Server Error")
        print_exc()

# menu items

@app.post(path="/create-menu-item")
def create_menu_item(
    id: str, name: str, price: float, 
    session: Session = Depends(get_session)
):
    menu_item = MenuItem(id=id, name=name, price=price)
    try:
        session.add(menu_item)
        session.commit()
    except:
        raise HTTPException(status_code=500, detail="Internal Server Error")
        print_exc()
    return {"status_code": 200, "detail": "Menu Item Added successfully"}

def get_item_by_id(
    item_id: str, 
    session: Session = Depends(get_session)
) -> MenuItem | None:
    try:
        statement = select(MenuItem).where(MenuItem.id == item_id)
        results = session.exec(statement)
        return results.one_or_none()
    except:
        raise HTTPException(status_code=500, detail="Internal Server Error")
        print_exc()
        
@app.get("/find-item-in-branch")
def count_item_in_branch(
    item_id: str, branch_id: str,
    session: Session = Depends(get_session)
) -> int | None:
    # note that returning None is when item doesn't exist in the inventory, 0 if exists but no quantity
    try:
        statement = select(BranchInventory).where(
            BranchInventory.item_id == item_id,
            BranchInventory.branch_id == branch_id
        )
        results = session.exec(statement)
        if results.one_or_none() is None:
            return None
        return results.one().quantity
    except:
        raise HTTPException(status_code=500, detail="Internal Server Error")
        print_exc()

@app.patch(path="/restock-menu-item")
def stock_menu_item(
    item_id: str, branch_id: str, quantity: int,
    session: Session = Depends(get_session)
):
    try:
        item = get_item_by_id(item_id, session)
        if item is None: 
            raise HTTPException(status_code=404, detail="Item Not Found")
        
        if count_item_in_branch(item_id, branch_id, session) is None:
            # add item
            inventory = BranchInventory(branch_id=branch_id, item_id=item_id, quantity=quantity)
            session.add(inventory)
            session.commit()
        else:
            statement = select(BranchInventory).where(
                BranchInventory.branch_id == branch_id, 
                BranchInventory.item_id == item_id
            )
            result = session.exec(statement).one_or_none()
            if result is None: 
                raise AssertionError("Result should have been available")
            result.quantity += quantity
            session.add(result)
            session.commit()
            session.refresh(result)
            return {"status_code": 200, "detail": "Item stocked to branch"}
    except:
        raise HTTPException(status_code=500, detail="Internal Server Error")
        print_exc()
    
    
@app.delete("/delete-menu-item")
def delete_menu_item(
    item_id: str,
    session: Session = Depends(get_session)
):
    try:
        item = get_item_by_id(item_id)
        if item is None:
            raise HTTPException(status_code = 404, detail = "Menu Item with ID not found")
        session.delete(item)
        session.commit()
        return {"status_code": 200, "detail": "Item deleted successfully"}
    except:
        raise HTTPException(status_code=500, detail="Internal Server Error")
        print_exc()

# order
@app.post("/order/{customer_email}/{branch_id}/")
def make_order(
    customer_email: str, branch_id: str, items: dict[str, int]):
    try:
        total = 0
        for item_id, quantity in items.items():
            item = get_item_by_id(item_id)
            if item is None:
                raise HTTPException(
                    status_code=400,
                    detail=f"Item with id {item_id} not found in menu"
                )
                
            count = count_item_in_branch(item_id, branch_id)
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
                
            price = item.price
            order = OrderItem(customer_email=customer_email, branch_id=branch_id)
            total += price * quantity
            
        return {
            "status_code": 200,
            "total_price": total,
            "detail": "Order completed"
        }
    except:
        raise HTTPException(status_code=500, detail="Internal Server Error")
        print_exc()
        
    