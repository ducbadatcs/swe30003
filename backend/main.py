from typing import Any
from models import CartItem, Product, User
from fastapi import FastAPI, status, HTTPException, Form, Depends
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import  Session, SQLModel, create_engine, select
import traceback

# for setting up users
from argon2 import PasswordHasher
ph = PasswordHasher()

SECRET_KEY = "f8eac36bbb9f0b336456d67f95fc4804d8b5fbccb0faf880a9c31af9d0d122b8"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
ALGORITHM="HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

app = FastAPI()
app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# setup SQL
engine = create_engine("sqlite:///database.db")
SQLModel.metadata.create_all(engine)


@app.post("/create-product")
def create_product(name: str, price: int):
    try:
        with Session(engine) as session:
            product = Product(name=name, price=price)
            session.add(product)
            session.commit()
        return {"status_code": 200, "detail": "Product added successfully"}
    except:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=traceback.format_exc()
        )
        


@app.get("/products")
def get_product_list():
    try:
        with Session(engine) as session:
            statement = select(Product)
            results = session.exec(statement).all()
            return results
    except:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=traceback.format_exc()
        )
        

@app.get("/products/{id}")
def get_product_by_id(id: int) -> Product | None:
    try:
        with Session(engine) as session:
            statement = select(Product).where(Product.id == id)
            results = session.exec(statement)
            product = results.one_or_none()
            if product is None:
                raise HTTPException(status_code=404, detail="Product not found")
            return product
    except HTTPException:
        raise
    except:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=traceback.format_exc()
        )
        
@app.delete("/delete-product")
def delete_product_with_id(id: int):
    try:
        with Session(engine) as session:
            product = get_product_by_id(id)
            if product is not None:
                session.delete(product)
                session.commit()
        return {"status_code": status.HTTP_200_OK, "detail": "Product deleted successfully"}
    except:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=traceback.format_exc()
        )
        
@app.get("/list-users")
def get_users():
    try:
        with Session(engine) as session:
            statement = select(User)
            results = session.exec(statement)
            return results.all()
    except:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=traceback.format_exc())

@app.get("/get-user")
def get_user_with_username(username: str) -> User | None:
    try:
        with Session(engine) as session:
            statement = select(User).where(User.username == username)
            results = session.exec(statement)
            return results.one_or_none()
    except:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=traceback.format_exc()
        ) 
        

# Users
@app.post("/register")
def register(username: str = Form(...), password: str = Form(...)):
    try:
        hash = ph.hash(password)
        with Session(engine) as session:
            user = User(username=username, password=hash)
            if get_user_with_username(username) is not None:
                return {
                    "status_code": status.HTTP_403_FORBIDDEN,
                    "detail": "Username already exists!"
                }
            session.add(user)
            session.commit()
        return {"status_code": status.HTTP_201_CREATED, "detail": "User registered successfully"}
    except:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=traceback.format_exc()
        )

def create_access_token(data: dict[Any, Any], expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication")
        user = get_user_with_username(username)
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return user

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/login")
def login(username: str = Form(...), password: str = Form(...)):
    try:
        user = get_user_with_username(username)
        if user is None:
            raise HTTPException(status_code=403, detail="Incorrect username or password")
        if not ph.verify(user.password, password):
            raise HTTPException(status_code=403, detail="Incorrect username or password")
        access_token = create_access_token(
            data={"sub": user.username},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
    except:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=traceback.format_exc()
        )
            


# cart
@app.post("/cart/add")
def add_to_cart(product_id: int = Form(...), current_user: User = Depends(get_current_user)):
    try:
        with Session(engine) as session:
            statement = select(CartItem).where(
                CartItem.username == current_user.username, 
                CartItem.product_id == product_id
            
            )
            
            item = session.exec(statement).one_or_none()
            if item is not None: item.quantity += 1
            else: item = CartItem(
                username=current_user.username,
                product_id=product_id,
                quantity=1
            )
            session.add(item)
            session.commit()
        return {"status_code": status.HTTP_200_OK, "detail": "Product added"}
    except:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=traceback.format_exc()
        )

@app.get("/cart")
def get_cart(current_user: User = Depends(get_current_user)):
    try: 
        with Session(engine) as session:
            statement = select(CartItem).where(
                CartItem.username == current_user.username
            )
            items = session.exec(statement).all()
            return items
    except:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=traceback.format_exc()
        )
        
@app.delete("/cart/remove")
def remove_from_cart(product_id: int, current_user: User = Depends(get_current_user)):
    try: 
        with Session(engine) as session:
            statement = select(CartItem).where(
                CartItem.username == current_user.username,
                CartItem.product_id == product_id
            )
            item = session.exec(statement).one_or_none()
            if item is not None:
                session.delete(item)
                session.commit()
        return {"status_code": status.HTTP_200_OK, "detail": "Item removed"}
    except:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=traceback.format_exc()
        )