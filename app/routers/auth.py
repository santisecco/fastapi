from fastapi import APIRouter, Depends, status, HTTPException, Response
from fastapi.params import Body
from ..database import conn, cursor
from .. import oauth2
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from typing import List

class Token(BaseModel):
    access_token: str
    token_type: str

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter(tags=['Authentication'])

class UserLogin(BaseModel):
    email: EmailStr
    password: str

@router.post('/login', response_model=Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends()):
    cursor.execute("""
        SELECT * FROM users
        WHERE email = %s
        """, (user_credentials.username,))
    
    user = cursor.fetchone()
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail = "Invalid credentials")
  
    if not (pwd_context.verify(user_credentials.password, user['password'])):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail = "Invalid credentials")
    

    access_token = oauth2.create_access_token(data = {"user_id": user['id']})
  
    return {"access_token": access_token, "token_type": "bearer"}

