from datetime import datetime
from pydantic import BaseModel
from typing import Optional

class UserSignUpInfo(BaseModel):
    first_name: str
    last_name: str
    email: str
    username: str
    password: str

class UserResponse(BaseModel):
    first_name: str
    last_name: str
    email: str
    username: str

    class Config:
        orm_mode = True

class ConvoClass(BaseModel):
    admin_message: str
    customer_message: str
    customer_username: str

class SignIn(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int

class UserInDB(BaseModel):
    id: int
    username: str
    password: str

class ProductClass(BaseModel):
    product_name: str = None
    product_price: Optional[int] = None
    product_description: Optional[str] = None
