from fastapi import APIRouter, Depends, HTTPException, status
import mysql.connector
from app.database import get_db
from app.crud.products import ProductCRUD
from app.models.schemas import Product, ProductCreate, ProductUpdate

router = APIRouter(prefix="/products", tags=["products"])

@router.post("/", response_model=Product, status_code=status.HTTP_201_CREATED)
def create_product(product: ProductCreate, conn = Depends(get_db)):
    try:
        new_product = ProductCRUD.create_product(conn, product)
        if new_product:
            return new_product
        raise HTTPException(status_code=400, detail="Error creating product")
    except mysql.connector.Error:
        raise HTTPException(status_code=500, detail="Database error")

@router.get("/", response_model=list[Product])
def get_products(conn = Depends(get_db)):
    try:
        products = ProductCRUD.get_products(conn)
        return products
    except mysql.connector.Error:
        raise HTTPException(status_code=500, detail="Database error")

@router.get("/{product_id}", response_model=Product)
def get_product(product_id: str, conn = Depends(get_db)):
    try:
        product = ProductCRUD.get_product_by_id(conn, product_id)
        if product:
            return product
        raise HTTPException(status_code=404, detail="Product not found")
    except mysql.connector.Error:
        raise HTTPException(status_code=500, detail="Database error")

@router.put("/{product_id}", response_model=Product)
def update_product(product_id: str, product: ProductUpdate, conn = Depends(get_db)):
    try:
        updated_product = ProductCRUD.update_product(conn, product_id, product)
        if updated_product:
            return updated_product
        raise HTTPException(status_code=404, detail="Product not found")
    except mysql.connector.Error:
        raise HTTPException(status_code=500, detail="Database error")

@router.delete("/{product_id}")
def delete_product(product_id: str, conn = Depends(get_db)):
    try:
        success = ProductCRUD.delete_product(conn, product_id)
        if success:
            return {"message": "Product deleted successfully"}
        raise HTTPException(status_code=404, detail="Product not found")
    except mysql.connector.Error:
        raise HTTPException(status_code=500, detail="Database error")