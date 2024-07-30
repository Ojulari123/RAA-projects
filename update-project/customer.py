from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, create_engine, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timedelta, UTC
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse
import os
from dotenv import load_dotenv
# from fastapi.templating import Jinja2Templates

load_dotenv()
ALGORITHM = os.getenv("ALGORITHM")
SECRET_KEY = os.getenv("SECRET_KEY")
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

engine = create_engine("sqlite:///customer.db", connect_args={"check_same_thread": False})
Local_Session = sessionmaker(bind=engine)
Base = declarative_base()
# templates =Jinja2Templates(directory="Templates")


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class User(Base):
    __tablename__ = "User"
    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(256))
    last_name = Column(String(256))
    email = Column(String(256))
    username = Column(String(256), unique=True)
    password = Column(String(256), nullable=False)
    role = Column(String(50), default="user")
    date = Column(DateTime, default=datetime.now)

    username_relationship = relationship("Convo", primaryjoin="User.username == Convo.customer_username", back_populates="username_rel")
    id_relationship = relationship("Convo", primaryjoin="User.id == Convo.customer_user_id", back_populates="customer_user")

class Convo(Base):
    __tablename__ = "Conversation"
    id = Column(Integer, primary_key=True, autoincrement=True)
    admin_message = Column(String(2000))
    customer_message = Column(String(2000))
    customer_username = Column(String(256), ForeignKey("User.username"), nullable=False)
    date = Column(DateTime, default=datetime.now)
    customer_user_id = Column(ForeignKey("User.id"))
    customer_user = relationship("User", foreign_keys=[customer_user_id], back_populates="id_relationship")
    username_rel = relationship("User", foreign_keys=[customer_username], back_populates="username_relationship")
    

class Products(Base):
    __tablename__ = "Products"
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_name = Column(String(256), nullable=False)
    product_price = Column(Integer, nullable=False)

class UserSignUpInfo(BaseModel):
    first_name: str
    last_name: str
    email: str
    username: str
    password: str

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

Base.metadata.create_all(engine)

app = FastAPI()

def get_db():
    db = Local_Session()
    try:
        yield db
    finally:
        db.close()

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

async def auth_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    print(datetime.now(), expire, expires_delta)
    to_encode.update({"exp": expire})
    print(to_encode)
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username.ilike(f'%{username}%')).first()

async def auth_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(payload)
        username: str = payload.get("sub")
        if username is None:
            raise credential_exception
        token_data = TokenData(username=username)
    except JWTError as e:
        print(e)
        raise credential_exception
    user = get_user_by_username(db, username=token_data.username)
    print(user)
    if user is None:
        raise credential_exception
    return user

async def role_checker(required_role: str, user: User):
    if user.role != required_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource"
        )
    return user

@app.get("/", response_class=HTMLResponse)
def root():
    return """
   <html>
        <head>
            <title>Sign-In</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    background-color: #f4f4f4;
                }
                .container {
                    max-width: 400px;
                    width: 100%;
                    padding: 20px;
                    background: #fff;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                    border-radius: 8px;
                }
                h1 {
                    margin-bottom: 20px;
                    font-size: 24px;
                    text-align: center;
                }
                .form-group {
                    margin-bottom: 15px;
                }
                .form-group label {
                    display: block;
                    margin-bottom: 5px;
                }
                .form-group input {
                    width: 100%;
                    padding: 10px;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                }
                .form-group button {
                    width: 100%;
                    padding: 10px;
                    background-color: #28a745;
                    border: none;
                    border-radius: 4px;
                    color: #fff;
                    font-size: 16px;
                    cursor: pointer;
                }
                .form-group button:hover {
                    background-color: #218838;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Sign In</h1>
                <form action="/token" method="post">
                    <div class="form-group">
                        <label for="username">Username</label>
                        <input type="text" id="username" name="username" required>
                    </div>
                    <div class="form-group">
                        <label for="password">Password</label>
                        <input type="password" id="password" name="password" required>
                    </div>
                    <div class="form-group">
                        <button type="submit">Sign In</button>
                    </div>
                </form>
            </div>
        </body>
    </html>
    """

@app.get("/products")
async def view_all_products(db: Session = Depends(get_db)):
    products = db.query(Products).all()
    return products

@app.post("/input-new-products")
async def input_new_products(text: ProductClass, db: Session = Depends(get_db)):
    new_product_query = db.query(Products).filter(Products.product_name==text.product_name).first()
    if new_product_query:
        raise HTTPException(status_code=400, detail="Existing product")
    new_product = Products(
        product_name=text.product_name,
        product_price=text.product_price
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return {"message": "New Product Added!"}

@app.post("/customer-info", response_model=Token)
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

@app.post("/token", response_model=TokenResponse)
async def sign_in(user: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user_auth = await auth_user(db, user.username, user.password)
    if not user_auth:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect username or password", headers={"WWW-Authenticate": "Bearer"})
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    access_token = create_access_token(data={"sub": user_auth.username}, expires_delta=access_token_expires)
    refresh_token = create_refresh_token(data={"sub": user_auth.username}, expires_delta=refresh_token_expires)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES
    )
@app.post("/add-admin-profile")
async def add_admin_profile(text: UserSignUpInfo, db: Session = Depends(get_db)):
    if get_user_by_username(db, text.username):
        raise HTTPException(status_code=400, detail="Existing username")

    password_hash = get_password_hash(text.password)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": text.username}, expires_delta=access_token_expires)

    admin_profile = User(
        first_name = text.first_name,
        last_name = text.last_name,
        email = text.email,
        username = text.username,
        password = password_hash,
        role = "admin",
        date = datetime.now()
    )

    db.add(admin_profile)
    db.commit()
    db.refresh(admin_profile)
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/change-role/{id}")
async def change_role(id: int, role: str, db: Session = Depends(get_db), user: User = Depends(auth_current_user)):
    await role_checker(required_role="admin", user=user)
    role_query = db.query(User).filter(User.id == id).first()
    if not role_query:
        raise HTTPException(status_code=404, detail="User not found")
    role_query.role = role
    db.commit()
    db.refresh(role_query)
    return {"message": "User Role Updated"}

@app.get("/retrieve-all-customer-details")
async def retrieve_all_customer_details(db: Session = Depends(get_db), user: User = Depends(auth_current_user)):
    await role_checker(required_role="admin", user=user)
    customer_details = db.query(User).all()
    return {"conversation": customer_details}

@app.get("/retrieve-customer-detail/{username}")
async def retrieve_customer_detail_by_username(username: str, db: Session = Depends(get_db), user: User = Depends(auth_current_user)):
    await role_checker(required_role="admin", user=user)
    customer_details = db.query(User).filter(User.username == username).all()
    return {"customer Info": customer_details}

@app.delete("/delete-customer/{customer_id}")
async def delete_select_customer(customer_id: int, db: Session = Depends(get_db), user: User = Depends(auth_current_user)):
    await role_checker(required_role="admin", user=user)
    db.query(User).filter(User.id == customer_id).delete()
    db.commit()
    return {"message": f"Customer {customer_id} has been deleted"}

@app.delete("/delete-customers")
async def delete_customers(db: Session = Depends(get_db), user: User = Depends(auth_current_user)):
    await role_checker(required_role="admin", user=user)
    db.query(User).delete()
    db.commit()
    return {"message": "Customers have been deleted"}

@app.post("/conversation")
async def convo(text: ConvoClass, db: Session = Depends(get_db), user: User = Depends(auth_current_user)):
    user_inst = db.query(User).filter(User.username == text.customer_username).first()
    if not user_inst:
        raise HTTPException(status_code=400, detail="You have to sign-in")

    convo = Convo(customer_username=text.customer_username, admin_message=text.admin_message, customer_message=text.customer_message,customer_user_id=user_inst.id)

    db.add(convo)
    db.commit()
    db.refresh(convo)
    return {"conversation": convo}

@app.get("/retrieve-current-conversation")
async def current_conversation(user: User = Depends(auth_current_user), db: Session = Depends(get_db)):
    last_convo = db.query(Convo).order_by(Convo.id.desc()).first()
    return {"conversation": last_convo}

@app.get("/retrieve-conversation")
async def conversation(user: User = Depends(auth_current_user), db: Session = Depends(get_db)):
    convos = db.query(Convo).all()
    return {"conversation": convos}

@app.get("/retrieve-conversation/{user_id}")
async def retrieve_conversation_token(user_id: int, user: User = Depends(auth_current_user), db: Session = Depends(get_db)):
    await role_checker(required_role="admin", user=user)
    user_convo_query = db.query(Convo).join(Convo.customer_user).filter(Convo.customer_user_id == user_id).all()
    return {"conversation": user_convo_query}

@app.get("/retrieve-conversation-username/{username}")
async def retrieve_conversation_username(username: str, user: User = Depends(auth_current_user), db: Session = Depends(get_db)):
    await role_checker(required_role="admin", user=user)
    convo_usernamequery = db.query(Convo).filter(Convo.customer_username == username).all()
    return {"conversation": convo_usernamequery}

@app.delete("/delete-conversation/{conversation_id}")
async def delete_select_conversation(conversation_id: int, user: User = Depends(auth_current_user), db: Session = Depends(get_db)):
    await role_checker(required_role="admin", user=user)
    db.query(Convo).filter(Convo.id == conversation_id).delete()
    db.commit()
    return {"message": f"Conversation {conversation_id} has been deleted"}

@app.delete("/delete-current-conversation")
async def delete_current_conversations(user: User = Depends(auth_current_user), db: Session = Depends(get_db)):
    await role_checker(required_role="admin", user=user)
    db.query(Convo).delete()
    db.commit()
    return {"message": "Current conversations have been deleted"}

@app.delete("/delete-conversation")
async def delete_conversations(user: User = Depends(auth_current_user), db: Session = Depends(get_db)):
    await role_checker(required_role="admin", user=user)
    db.query(Convo).delete()
    db.commit()
    return {"message": "All conversations have been deleted"}
