from argon2.exceptions import VerifyMismatchError


from sqlmodel import Session, select, or_
from fastapi import Depends, FastAPI, HTTPException, APIRouter, Form

from traceback import print_exc
from argon2 import PasswordHasher


from ..db import get_session
from ..schemas import Customer

from ..auth import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from datetime import timedelta
from pydantic import BaseModel

ph = PasswordHasher()

customer_router = APIRouter(prefix="/customer")

@customer_router.post(path="/register-customer")
def register_customer(
    username: str = Form(...), password: str = Form(...), 
    session: Session = Depends(get_session)
):
    try:
        if get_customer_by_username(username, session) is not None:
            raise HTTPException(status_code=403, detail="User already exists")      
        customer = Customer(username=username, password=ph.hash(password))
        session.add(customer)
        session.commit()
        return {"status_code": 200, "detail": "Customer registered successfully"}
    except Exception as e:
        raise e
    except:
        print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@customer_router.get("/get-customer-by-username")
def get_customer_by_username(
    username: str,
    session: Session = Depends(get_session)
) -> Customer | None:
    try:
        statement = select(Customer).where(
            Customer.username == username
        )
        result = session.exec(statement).one_or_none()
        return result
    except:
        print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@customer_router.get(path="/list-customers")
def list_customers(
    session: Session = Depends(get_session)
):
    try:
        statement = select(Customer)
        result = session.exec(statement)
        return list(result)
    except:
        print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")

@customer_router.delete(path="/unregister-customer")
def unregister_customer(
    username: str, 
    session: Session = Depends(get_session)
):
    try:
        customer = get_customer_by_username(username)
        if customer is None:
            raise HTTPException(status_code=404, detail="Customer Not Found")
        session.delete(customer)
        session.commit()
        return {"status_code": 200, "detail": "Customer unregistered successfully"}
    except:
        print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@customer_router.post("/verify-customer")
def verify_customer(
    username: str = Form(...), password: str = Form(...),
    session: Session = Depends(get_session)
):
    try:
        customer = get_customer_by_username(username, session)
        if customer is None:
            raise HTTPException(status_code=404, detail="User with Username Not Found")
        
        try:
            ph.verify(customer.password, password)
        except VerifyMismatchError:
            raise HTTPException(status_code=403, detail="error: wrong username or password")
        
        return {"status_code": 200, "detail": "Verify ok!"}
    except Exception as e:
        raise e
    except:
        print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")
# menu items

class Token(BaseModel):
    access_token: str
    token_type: str

@customer_router.post("/token", response_model=Token)
def login_customer(
    username: str = Form(...),
    password: str = Form(...),
    session: Session = Depends(get_session),
):
    customer = get_customer_by_username(username, session)
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")

    try:
        ph.verify(customer.password, password)
    except VerifyMismatchError:
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    access_token = create_access_token(
        data={"sub": customer.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return Token(access_token=access_token, token_type="bearer")