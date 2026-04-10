from sqlalchemy.sql.functions import user
from sqlmodel import Session, select, or_
from fastapi import Depends, FastAPI, HTTPException, APIRouter
from traceback import print_exc
from ..db import get_session
from ..schemas import Branch, Staff, StaffRoleEnum
from argon2 import PasswordHasher

# we need this
from .branches import get_branch_by_id

staff_router = APIRouter(prefix="/staffs")

ph = PasswordHasher()

@staff_router.post("/register-staff")
def register_staff(
	username: str, password: str, role: StaffRoleEnum, branch_id: int,
    session: Session = Depends(get_session)
):
    try:
        branch = get_branch_by_id(branch_id)
        if branch is None:
            raise HTTPException(status_code = 404, detail = f"Branch with ID {id} not found")
        staff = Staff(username=username, password=ph.hash(password), role=role, branch_id = branch_id)
        session.add(staff)
        session.commit()
        return {"status_code": 200, "detail": f"Added Staff with ID {staff.id}"}
    except:
        raise HTTPException(status_code=500, detail="Internal Server Error")
        print_exc()
        
@staff_router.get("/list-staffs")
def list_staffs(
	session: Session = Depends(get_session)
):
    try:
        statement = select(Staff)
        results = session.exec(statement).all()
        return list(results)
    except:
        print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")
        
@staff_router.post("/get-staff-by-id")
def get_staff_by_id(
	id: int, 
	session: Session = Depends(get_session)
) -> Staff | None:
    try:
        statement = select(Staff).where(Staff.id == id)
        result = session.exec(statement).one_or_none()
        return result
    except:
        print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
def get_staff_by_username(
    username: int,
    session: Session = Depends(get_session)
):
    try:
        statement = select(Staff).where(Staff.username == username)
        result = session.exec(statement).one_or_none()
        return result
    except:
        print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")
        
@staff_router.delete(path="/unregister-staff")
def unregister_staff(
	id: int,
    session: Session = Depends(get_session)
):
    try:
        staff = get_staff_by_id(id)
        if staff is None:
            raise HTTPException(status_code = 404, detail = f"Staff with ID {id} not found")
        session.delete(staff)
        session.commit()
        return {"status_code": 200, "detail": f"Unregistered Staff with ID {id}"}
    except:
        print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")