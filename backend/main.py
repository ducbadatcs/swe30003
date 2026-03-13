from models import Product
from fastapi import FastAPI, status, HTTPException 
from sqlmodel import  Session, SQLModel, create_engine, select
import traceback


app = FastAPI()

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
    except Exception:
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
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=traceback.format_exc()
        )






#with Session(engine) as session:
#    statement = select(Hero).where(Hero.name == "Spider-Boy")
#    hero = session.exec(statement).first()
#    print(hero)

