from sqlmodel import Field, SQLModel, table

class Product(SQLModel, table=True):
    id: int | None = Field(default= None, primary_key=True)
    name: str
    price: int


class User(SQLModel, table=True):
    username: str = Field(primary_key=True)
    password: str
    
    
class CartItem(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    username: str = Field(foreign_key="user.username")
    product_id: int = Field(foreign_key="product.id")

    quantity: int