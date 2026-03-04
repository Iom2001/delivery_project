from typing import Optional

from pydantic import BaseModel


class SignUpModel(BaseModel):
    id: Optional[int] = None
    username: str
    email: str
    password: str
    is_staff: Optional[bool]
    is_active: Optional[bool]

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "username": "Shaxzod",
                "email": "xusainov.shaxzod@gmail.com",
                "password": "Qwerty1234",
                "is_staff": False,
                "is_active": True,
            }
        }


class Settings(BaseModel):
    authjwt_secret_key: str = '35c458d35631b6b0b465466faf935291a3ce67f327d24a06057e85a2217884e2'


class LoginModel(BaseModel):
    username_or_email: str
    password: str


class OrderModel(BaseModel):
    id: Optional[int] = None
    quantity: int
    order_status: Optional[str] = "PENDING"
    user_id: Optional[int] = None
    product_id: int

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "quantity": 1
            }
        }


class OrderStatusModel(BaseModel):
    order_status: Optional[str] = "PENDING"

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "order_statuses": "PENDING"
            }
        }


class ProductModel(BaseModel):
    id:Optional[int] = None
    name:str
    price:int

    class Config:
        orm_model = True
        schema_extra = {
            "example": {
                "name": "test",
                "price": 1000
            }
        }