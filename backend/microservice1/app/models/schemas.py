from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from enum import Enum

class OrderStatus(str, Enum):
    pending = "pending"
    confirmed = "confirmed"
    preparing = "preparing"
    delivered = "delivered"
    cancelled = "cancelled"

class PaymentMethod(str, Enum):
    cash = "cash"
    card = "card"
    transfer = "transfer"

class UserBase(BaseModel):
    name: str
    email: EmailStr
    phone_number: Optional[str] = None
    address: Optional[str] = None

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None

class User(UserBase):
    id: int 
    created_at: datetime

    class Config:
        from_attributes = True

class ProductBase(BaseModel):
    name: str
    price: float
    calories: Optional[int] = None

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    calories: Optional[int] = None

class Product(ProductBase):
    id: int  
    created_at: datetime

    class Config:
        from_attributes = True

class OrderBase(BaseModel):
    user_id: int  
    product_id: int
    status: OrderStatus = OrderStatus.pending
    total_price: float
    payment_method: PaymentMethod = PaymentMethod.cash

class OrderCreate(OrderBase):
    pass

class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None
    total_price: Optional[float] = None
    payment_method: Optional[PaymentMethod] = None

class Order(OrderBase):
    id: int  
    order_date: datetime

    class Config:
        from_attributes = True

class OrderWithDetails(Order):
    user_name: str
    product_name: str