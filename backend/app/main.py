from fastapi.openapi.utils import status_code_ranges
from traceback import print_exc
from typing import Any

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, SQLModel, select, or_

from .db import engine, get_session
from .schemas import Branch, Customer, MenuItem, Staff, BranchInventory

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
    name: str, address: str,
    session: Session = Depends(get_session)
):
    branch = Branch(name=name, address=address)
    try:
        session.add(branch)
    except:
        raise HTTPException(status_code=500, detail="Internal Server Error")
        print_exc()
    return {"status_code": 200, "detail": "Branch registered successfully"}

@app.get(path="/find-branch")
def find_branch(
    name: str, address: str,
    session: Session = Depends(get_session)
):
    
    try:
        statement = select(Branch).where(
            or_(
                name.lower() in Branch.name.lower(), 
                address.lower() in Branch.address.lower()))
        results = session.exec(statement)
    except:
        raise HTTPException(status_code=500, detail="Internal Server Error")
        print_exc()
    return results

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
    except:
        raise HTTPException(status_code=500, detail="Internal Server Error")
        print_exc()
    return {"status_code": 200, "detail": "Customer registered successfully"}

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
    except:
        raise HTTPException(status_code=500, detail="Internal Server Error")
        print_exc()
    return {"status_code": 200, "detail": "Item stocked"}
    

@app.post("/order/{customer_id}/{branch_id}")
def make_order(customer: Customer, branch: Branch, items: list[MenuItem]):
    pass