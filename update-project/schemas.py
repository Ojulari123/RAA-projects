from pydantic import BaseModel
from typing import List

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

class ConvoClass(BaseModel):
    customer_username: str
    admin_message: str
    customer_message: str

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
    token_type: str = "Bearer"
    expires_in: int

class UserInDB(UserSignUpInfo):
    hashed_password: str

class ProductClass(BaseModel):
    product_name: str
    product_price: int
    product_description: str