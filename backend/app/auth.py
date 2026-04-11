from traceback import print_exc
from argon2.exceptions import VerifyMismatchError
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
from typing import Annotated
import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import Session, select

from .db import get_session
from .schemas import Customer, Staff


SECRET_KEY = "292f0bacbed56f35a7704ee2be369469bc2abf270e0d13042678ce5f67710fae"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/customer/token")

def create_access_token(data: dict, expires_delta: timedelta | None):
    to_encode = data.copy()
    if expires_delta is not None:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_customer_from_token(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Session = Depends(get_session),
) -> Customer:
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception

    try:
        statement = select(Customer).where(Customer.username == username)
        customer = session.exec(statement).one_or_none()
        if customer is None:
            raise credentials_exception
    except:
        print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")

    return customer


async def get_staff_from_token(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Session = Depends(get_session),
) -> Staff:
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception
    
    try:
        statement = select(Staff).where(Staff.username == username)
        staff = session.exec(statement).one_or_none()
        if staff is None:
            raise credentials_exception
    except:
        print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
    return staff

class Token(BaseModel):
    access_token: str
    token_type: str