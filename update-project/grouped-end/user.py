from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from tables import User
from typing import List
from schemas import UserSignUpInfo, UserResponse, Token, TokenResponse
from func import auth_user, auth_current_user, get_db, get_password_hash, create_access_token, create_refresh_token, get_user_by_username, role_checker
from datetime import datetime,timedelta
from dotenv import load_dotenv
import os

user_router = APIRouter()

load_dotenv()
ALGORITHM = os.getenv("ALGORITHM")
SECRET_KEY = os.getenv("SECRET_KEY")
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

@user_router.post("/customer-info", response_model=Token)
async def add_customer_info(user: UserSignUpInfo, db: Session = Depends(get_db)):
    if get_user_by_username(db, user.username):
        raise HTTPException(status_code=400, detail="Existing username")
    password_hash = get_password_hash(user.password)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    user_details = User(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        username=user.username,
        password=password_hash,
        role="user",
        date=datetime.now()
    )
    db.add(user_details)
    db.commit()
    db.refresh(user_details)
    return {"access_token": access_token, "token_type": "bearer"}

@user_router.post("/add-admin-profile", response_model=Token)
async def add_admin_profile(text: UserSignUpInfo, db: Session = Depends(get_db)):
    if get_user_by_username(db, text.username):
        raise HTTPException(status_code=400, detail="Existing username")
    password_hash = get_password_hash(text.password)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": text.username}, expires_delta=access_token_expires)
    admin_profile = User(
        first_name=text.first_name,
        last_name=text.last_name,
        email=text.email,
        username=text.username,
        password=password_hash,
        role="admin",
        date=datetime.now()
    )
    db.add(admin_profile)
    db.commit()
    db.refresh(admin_profile)
    return {"access_token": access_token, "token_type": "bearer"}

@user_router.post("/token", response_model=TokenResponse)
async def sign_in(user: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user_auth = await auth_user(db, user.username, user.password)
    if not user_auth:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password", headers={"WWW-Authenticate": "Bearer"})
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    access_token = create_access_token(data={"sub": user_auth.username}, expires_delta=access_token_expires)
    refresh_token = create_refresh_token(data={"sub": user_auth.username}, expires_delta=refresh_token_expires)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token, expires_in=ACCESS_TOKEN_EXPIRE_MINUTES)

@user_router.get("/retrieve-all-customer-details", response_model=List[UserResponse])
async def retrieve_all_customer_details(db: Session = Depends(get_db), user: User = Depends(auth_current_user)):
    await role_checker(required_role="admin", user=user)
    customer_details_list = db.query(User).all()
    return customer_details_list

@user_router.get("/retrieve-customer-detail/{username}", response_model=UserResponse)
async def retrieve_customer_detail_by_username(username: str, db: Session = Depends(get_db), user: User = Depends(auth_current_user)):
    await role_checker(required_role="admin", user=user)
    customer_details = db.query(User).filter(User.username == username).first()
    return customer_details

@user_router.post("/change-role/{id}")
async def change_role(id: int, role: str, db: Session = Depends(get_db), user: User = Depends(auth_current_user)):
    await role_checker(required_role="admin", user=user)
    role_query = db.query(User).filter(User.id == id).first()
    if not role_query:
        raise HTTPException(status_code=404, detail="User not found")
    role_query.role = role
    db.commit()
    db.refresh(role_query)
    return {"message": "User Role Updated"}

@user_router.delete("/delete-customer/{customer_id}")
async def delete_select_customer(customer_id: int, db: Session = Depends(get_db), user: User = Depends(auth_current_user)):
    await role_checker(required_role="admin", user=user)
    db.query(User).filter(User.id == customer_id).delete()
    db.commit()
    return {"message": f"Customer {customer_id} has been deleted"}

@user_router.delete("/delete-customers")
async def delete_customers(db: Session = Depends(get_db), user: User = Depends(auth_current_user)):
    await role_checker(required_role="admin", user=user)
    db.query(User).delete()
    db.commit()
    return {"message": "Customers have been deleted"}
