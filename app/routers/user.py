from fastapi import status, HTTPException, APIRouter
from pydantic import BaseModel, EmailStr
from psycopg2.errorcodes import UNIQUE_VIOLATION
from psycopg2 import errors
from passlib.context import CryptContext
from ..database import cursor, conn


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter(
    tags=['Users']
)

class UserCreate(BaseModel):
    email: EmailStr
    password: str


@router.get("/users")
def get_users():
    cursor.execute("""
    SELECT email, id, created_at FROM users
    """)
    users = cursor.fetchall()
    return {"data": users}




@router.post("/users")
def create_user(user: UserCreate):
    user.password = pwd_context.hash(user.password)
    try:
        cursor.execute("""
        INSERT INTO users (email, password)
        VALUES (%s, %s) RETURNING email, id, created_at
        """, (user.email, user.password))
        new_user = cursor.fetchone()
        conn.commit()
        return {"data": new_user}
    except errors.lookup(UNIQUE_VIOLATION) as e:
        conn.rollback()
        return {("email %s is already taken")%(user.email)}




@router.get("/users/{id}", status_code=status.HTTP_201_CREATED)
def get_user(id : int):
    cursor.execute("""
    SELECT email, id, created_at FROM users
    WHERE id = %s
    """, (str(id),))
    user = cursor.fetchone()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail = f"user with id: {str(id)} not found")
    return {"data": user}













