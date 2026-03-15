from models import Product, User
from fastapi import FastAPI, status, HTTPException 
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import  Session, SQLModel, create_engine, select
import traceback

# for setting up users
from argon2 import PasswordHasher
ph = PasswordHasher()

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
        
@app.delete("/delete-product")
def delete_product_with_id(id: int):
    try:
        with Session(engine) as session:
            statement = select(Product).where(Product.id == id)
            results = session.exec(statement)
            product = results.one()
            session.delete(product)
            session.commit()
        return {"status_code": 200, "detail": "Product deleted successfully"}
    except:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=traceback.format_exc()
        )


# Users
@app.post("/register")
def register(username: str, password: str):
    try:
        hash = ph.hash(password)
        with Session(engine) as session:
            user = User(username=username, password=hash)
            session.add(user)
            session.commit()
        return {"status_code": 200, "detail": "User registered successfully"}
    except:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=traceback.format_exc()
        )




#with Session(engine) as session:
#    statement = select(Hero).where(Hero.name == "Spider-Boy")
#    hero = session.exec(statement).first()
#    print(hero)

