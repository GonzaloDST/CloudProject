from fastapi import APIRouter, Depends, HTTPException, status, Query
import mysql.connector
from app.database import get_db
from app.crud.orders import OrderCRUD
from app.models.schemas import Order, OrderCreate, OrderUpdate, OrderWithDetails, OrderStatus

router = APIRouter(prefix="/orders", tags=["orders"])

@router.post("/", response_model=OrderWithDetails, status_code=status.HTTP_201_CREATED)
def create_order(order: OrderCreate, conn = Depends(get_db)):
    try:
        new_order = OrderCRUD.create_order(conn, order)
        if new_order:
            return new_order
        raise HTTPException(status_code=400, detail="Error creating order")
    except mysql.connector.Error:
        raise HTTPException(status_code=500, detail="Database error")

@router.get("/", response_model=list[OrderWithDetails])
def get_orders(
    status: OrderStatus = Query(None, description="Filter by order status"),
    user_id: str = Query(None, description="Filter by user ID"),
    conn = Depends(get_db)
):
    try:
        if status:
            orders = OrderCRUD.get_orders_by_status(conn, status)
        elif user_id:
            orders = OrderCRUD.get_orders_by_user(conn, user_id)
        else:
            orders = OrderCRUD.get_orders(conn)
        return orders
    except mysql.connector.Error:
        raise HTTPException(status_code=500, detail="Database error")

@router.get("/{order_id}", response_model=OrderWithDetails)
def get_order(order_id: str, conn = Depends(get_db)):
    try:
        order = OrderCRUD.get_order_by_id(conn, order_id)
        if order:
            return order
        raise HTTPException(status_code=404, detail="Order not found")
    except mysql.connector.Error:
        raise HTTPException(status_code=500, detail="Database error")

@router.put("/{order_id}", response_model=OrderWithDetails)
def update_order(order_id: str, order: OrderUpdate, conn = Depends(get_db)):
    try:
        updated_order = OrderCRUD.update_order(conn, order_id, order)
        if updated_order:
            return updated_order
        raise HTTPException(status_code=404, detail="Order not found")
    except mysql.connector.Error:
        raise HTTPException(status_code=500, detail="Database error")

@router.delete("/{order_id}")
def delete_order(order_id: str, conn = Depends(get_db)):
    try:
        success = OrderCRUD.delete_order(conn, order_id)
        if success:
            return {"message": "Order deleted successfully"}
        raise HTTPException(status_code=404, detail="Order not found")
    except mysql.connector.Error:
        raise HTTPException(status_code=500, detail="Database error")