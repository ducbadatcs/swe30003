from concurrent.interpreters import create

from typing import Annotated
from argon2.exceptions import VerifyMismatchError
from sqlmodel import Session, select, or_
from fastapi import Depends, FastAPI, HTTPException, APIRouter, Form
from traceback import print_exc
from ..db import get_session
from ..schemas import Branch, Staff, StaffRoleEnum
from ..auth import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, get_staff_from_token, Token
from datetime import timedelta
from pydantic import BaseModel
from argon2 import PasswordHasher

# we need this
from .branches import get_branch_by_id

staff_router = APIRouter(prefix="/staffs")

ph = PasswordHasher()

@staff_router.post("/register-staff")
def register_staff(
	username: str = Form(...), password: str = Form(...), role: StaffRoleEnum = StaffRoleEnum.STAFF, branch_id: int = 1,
    session: Session = Depends(get_session)
):
    try:
        branch = get_branch_by_id(branch_id, session)
        if branch is None:
            raise HTTPException(status_code = 404, detail = f"Branch with ID {id} not found")
        
        if get_staff_by_username(username, session) is not None:
            raise HTTPException(status_code = 404, detail = f"Staff with username already exists")
        staff = Staff(username=username, password=ph.hash(password), role=role, branch_id = branch_id)
        session.add(staff)
        session.commit()
        return {"status_code": 200, "detail": f"Added Staff with ID {staff.id}"}
    except:
        print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")
        
        
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
        
@staff_router.get("/get-staff-by-id")
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
    
@staff_router.get("/get-staff-by-username")
def get_staff_by_username(
    username: str,
    session: Session = Depends(get_session)
) -> Staff | None:
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
    
@staff_router.post("/verify-staff")
def verify_staff(
    username: str = Form(...), password: str = Form(...),
    session: Session = Depends(get_session)
):
    try:
        staff = get_staff_by_username(username, session)
        if staff is None:
            raise HTTPException(status_code=404, detail="Staff with Username Not Found")
    except Exception as e:
        raise e
    except:
        print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@staff_router.post("/token", response_model=Token)
def login_staff(
    username: str = Form(...),
    password: str = Form(...),
    session: Session = Depends(get_session)
):
    staff = get_staff_by_username(username, session)
    if staff is None:
        raise HTTPException(status_code=404, detail="Staff not found")
    
    try:
        ph.verify(staff.password, password)
    except VerifyMismatchError:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    access_token = create_access_token(
        data={"sub": staff.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return Token(access_token=access_token, token_type="bearer")

@staff_router.get("/current-staff")
async def get_current_staff(
    staff: Annotated[Staff, Depends(get_staff_from_token)]
):
    return staff