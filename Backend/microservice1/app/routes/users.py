from fastapi import APIRouter, Depends, HTTPException, status
import mysql.connector
from app.database import get_db
from app.crud.users import UserCRUD
from app.models.schemas import User, UserCreate, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, conn = Depends(get_db)):
    try:
        new_user = UserCRUD.create_user(conn, user)
        if new_user:
            return new_user
        raise HTTPException(status_code=400, detail="Error creating user")
    except mysql.connector.Error as e:
        if "Duplicate entry" in str(e):
            raise HTTPException(status_code=400, detail="Email already exists")
        raise HTTPException(status_code=500, detail="Database error")

@router.get("/", response_model=list[User])
def get_users(conn = Depends(get_db)):
    try:
        users = UserCRUD.get_users(conn)
        return users
    except mysql.connector.Error:
        raise HTTPException(status_code=500, detail="Database error")

@router.get("/{user_id}", response_model=User)
def get_user(user_id: str, conn = Depends(get_db)):
    try:
        user = UserCRUD.get_user_by_id(conn, user_id)
        if user:
            return user
        raise HTTPException(status_code=404, detail="User not found")
    except mysql.connector.Error:
        raise HTTPException(status_code=500, detail="Database error")

@router.put("/{user_id}", response_model=User)
def update_user(user_id: str, user: UserUpdate, conn = Depends(get_db)):
    try:
        updated_user = UserCRUD.update_user(conn, user_id, user)
        if updated_user:
            return updated_user
        raise HTTPException(status_code=404, detail="User not found")
    except mysql.connector.Error as e:
        if "Duplicate entry" in str(e):
            raise HTTPException(status_code=400, detail="Email already exists")
        raise HTTPException(status_code=500, detail="Database error")

@router.delete("/{user_id}")
def delete_user(user_id: str, conn = Depends(get_db)):
    try:
        success = UserCRUD.delete_user(conn, user_id)
        if success:
            return {"message": "User deleted successfully"}
        raise HTTPException(status_code=404, detail="User not found")
    except mysql.connector.Error:
        raise HTTPException(status_code=500, detail="Database error")