from email.policy import HTTP
from sqlalchemy.orm import selectin_polymorphic
from importlib.resources import path

from typing import Any, cast

from sqlmodel import Session, select, or_
from fastapi import Depends, FastAPI, HTTPException, APIRouter
from traceback import print_exc
from ..db import get_session
from ..schemas import MenuItem, Branch, BranchInventory
from ..auth import get_staff_from_token
from ..schemas import Staff

menu_router = APIRouter(prefix="/menu")


@menu_router.post(path="/create-menu-item")
def create_menu_item(
    name: str, price: float, 
    session: Session = Depends(get_session)
):
    
    try:
        menu_item = MenuItem(name=name, price=price)
        session.add(menu_item)
        session.commit()
        return {"status_code": 200, "detail": "Menu Item Added successfully"}
    except:
        print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")
    

def get_item_by_id(
    item_id: int, 
    session: Session
) -> MenuItem | None:
    try:
        statement = select(MenuItem).where(MenuItem.id == item_id)
        results = session.exec(statement)
        return results.one_or_none()
    except:
        print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")

@menu_router.get("/list-menu-items")    
def list_menu_items(
	session: Session = Depends(get_session)
):
    try:
        statement = select(MenuItem)
        results = session.exec(statement)
        return list(results)
    except:
        print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@menu_router.get("/get-item-by-name")
def get_item_by_name(
	name: str,
	session: Session = Depends(get_session)
):
    try:
        statement = select(MenuItem).where(
            cast(Any, MenuItem.name).like(f"%{name.lower()}%")
        )
        results = session.exec(statement)
        return results.one_or_none()
    except:
        print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")

    
@menu_router.get("/get-item-in-inventory")
def get_item_in_inventory(
	item_id: int, branch_id: int, 
	session: Session = Depends(get_session)
) -> BranchInventory | None:
    try:
        item = get_item_by_id(item_id, session)
        if item is None: 
            raise HTTPException(status_code=404, detail="Item Not Found")
        
        statement = select(BranchInventory).where(
                BranchInventory.branch_id == branch_id, 
                BranchInventory.item_id == item_id
            )
        result = session.exec(statement).one_or_none()
        return result
    except:
        print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@menu_router.get("/list-item-in-inventory")
def list_item_in_inventory(
	branch_id: int,
	session: Session = Depends(get_session)
):
    try:
        statement = select(BranchInventory).where(
			BranchInventory.branch_id == branch_id
		)
        result = session.exec(statement)
        return list(result)
    except:
        print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")

@menu_router.get("/find-item-in-branch")
def count_item_in_branch(
    item_id: int, branch_id: int,
    session: Session = Depends(get_session)
) -> int | None:
    # note that returning None is when item doesn't exist in the inventory, 0 if exists but no quantity
    try:
        item = get_item_in_inventory(item_id, branch_id, session)
        if item is None:
            return None
        return item.quantity
    except:
        print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")

@menu_router.patch(path="/restock-menu-item")
def stock_menu_item(
    item_id: int, branch_id: int, quantity: int,
    session: Session = Depends(get_session),
    staff: Staff = Depends(get_staff_from_token),
):
    try:
        if staff.branch_id != branch_id:
            raise HTTPException(
                status_code=403,
                detail="You can only restock items for your own branch",
            )

        item = get_item_by_id(item_id, session)
        if item is None: 
            raise HTTPException(status_code=404, detail="Item Not Found")
        
        if count_item_in_branch(item_id, branch_id, session) is None:
            # add item
            inventory = BranchInventory(branch_id=branch_id, item_id=item_id, quantity=quantity)
            session.add(inventory)
            session.commit()
        else:
            result = get_item_in_inventory(item_id, branch_id, session)
            if result is None: 
                raise AssertionError("Result should have been available")
            result.quantity += quantity
            
            session.add(result)
            session.commit()
            session.refresh(result)
        return {"status_code": 200, "detail": "Item stocked to branch"}
    except HTTPException:
        raise
    except:
        print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")
    

    
@menu_router.delete("/delete-menu-item")
def delete_menu_item(
    item_id: int,
    session: Session = Depends(get_session)
):
    try:
        item = get_item_by_id(item_id, session)
        if item is None:
            raise HTTPException(status_code = 404, detail = "Menu Item with ID not found")
        session.delete(item)
        session.commit()
        return {"status_code": 200, "detail": "Item deleted successfully"}
    except:
        print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")