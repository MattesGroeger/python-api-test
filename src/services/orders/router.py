from fastapi import APIRouter, HTTPException, Depends
from typing import List
from .models import Order, OrderCreate, OrderItem
from datetime import datetime
from src.services.auth.service import get_current_user
from src.services.auth.models import User

router = APIRouter()

# In-memory storage for demo purposes
orders_db = {}
order_id_counter = 1

@router.post("/", response_model=Order)
async def create_order(order: OrderCreate, current_user: User = Depends(get_current_user)):
    global order_id_counter
    order_id = order_id_counter
    order_id_counter += 1
    
    # Calculate total amount (in a real app, this would fetch product prices)
    total_amount = sum(item.quantity * 10.0 for item in order.items)  # Placeholder price
    
    new_order = Order(
        id=order_id,
        items=order.items,
        customer_name=order.customer_name,
        customer_email=order.customer_email,
        total_amount=total_amount,
        status="pending",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    orders_db[order_id] = new_order
    return new_order

@router.get("/", response_model=List[Order])
async def list_orders(current_user: User = Depends(get_current_user)):
    return list(orders_db.values())

@router.get("/{order_id}", response_model=Order)
async def get_order(order_id: int, current_user: User = Depends(get_current_user)):
    if order_id not in orders_db:
        raise HTTPException(status_code=404, detail="Order not found")
    return orders_db[order_id]

@router.put("/{order_id}/status", response_model=Order)
async def update_order_status(order_id: int, status: str, current_user: User = Depends(get_current_user)):
    if order_id not in orders_db:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order = orders_db[order_id]
    order.status = status
    order.updated_at = datetime.now()
    return order 