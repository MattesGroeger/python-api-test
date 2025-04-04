from fastapi import APIRouter, HTTPException
from typing import List
from .models import Product, ProductCreate
from datetime import datetime

router = APIRouter()

# In-memory storage for demo purposes
products_db = {}
product_id_counter = 1

@router.post("/", response_model=Product)
async def create_product(product: ProductCreate):
    global product_id_counter
    product_id = product_id_counter
    product_id_counter += 1
    
    new_product = Product(
        id=product_id,
        name=product.name,
        description=product.description,
        price=product.price,
        stock=product.stock,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    products_db[product_id] = new_product
    return new_product

@router.get("/", response_model=List[Product])
async def list_products():
    return list(products_db.values())

@router.get("/{product_id}", response_model=Product)
async def get_product(product_id: int):
    if product_id not in products_db:
        raise HTTPException(status_code=404, detail="Product not found")
    return products_db[product_id]

@router.put("/{product_id}", response_model=Product)
async def update_product(product_id: int, product: ProductCreate):
    if product_id not in products_db:
        raise HTTPException(status_code=404, detail="Product not found")
    
    existing_product = products_db[product_id]
    updated_product = Product(
        id=product_id,
        name=product.name,
        description=product.description,
        price=product.price,
        stock=product.stock,
        created_at=existing_product.created_at,
        updated_at=datetime.now()
    )
    
    products_db[product_id] = updated_product
    return updated_product

@router.delete("/{product_id}")
async def delete_product(product_id: int):
    if product_id not in products_db:
        raise HTTPException(status_code=404, detail="Product not found")
    del products_db[product_id]
    return {"message": "Product deleted successfully"} 