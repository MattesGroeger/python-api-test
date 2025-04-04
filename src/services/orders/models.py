from pydantic import BaseModel
from typing import List
from datetime import datetime

class OrderItem(BaseModel):
    product_id: int
    quantity: int

class OrderBase(BaseModel):
    items: List[OrderItem]
    customer_name: str
    customer_email: str

class OrderCreate(OrderBase):
    pass

class Order(OrderBase):
    id: int
    total_amount: float
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 