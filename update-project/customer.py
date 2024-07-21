from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, create_engine, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

SECRET_KEY = "865b6bfe49f145e4c06db40a93a31f8431976be040db72c68f0653997fc3c2a4"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

engine = create_engine("sqlite:///customer.db", connect_args={"check_same_thread": False})
Local_Session = sessionmaker(bind=engine)
Base = declarative_base()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class User(Base):
    __tablename__ = "User"
    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    email = Column(String(200))
    username = Column(String(100), unique=True)
    password = Column(String(100), nullable=False)
    token = Column(String(2000), unique=True, nullable=False)
    date = Column(DateTime, default=datetime.now)

    username_relationship = relationship("Convo", primaryjoin="User.username == Convo.customer_username", back_populates="username_rel")
    token_relationship = relationship("Convo", primaryjoin="User.token == Convo.user_token", back_populates="token_rel")

class Convo(Base):
    __tablename__ = "Conversation"
    id = Column(Integer, primary_key=True, autoincrement=True)
    admin = Column(String(2000))
    customer = Column(String(2000))
    customer_username = Column(String(100), ForeignKey("User.username"), nullable=False)
    user_token = Column(String(2000), ForeignKey("User.token"), nullable=False)
    date = Column(DateTime, default=datetime.now)

    username_rel = relationship("User", foreign_keys=[customer_username], back_populates="username_relationship")
    token_rel = relationship("User", foreign_keys=[user_token], back_populates="token_relationship")

class UserClass(BaseModel):
    first_name: str
    last_name: str
    email: str
    username: str
    password: str

class ConvoClass(BaseModel):
    customer_username: str
    admin: str
    customer: str

class SignIn(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str

class UserInDB(UserClass):
    hashed_password: str

PRODUCTS = [
    {"id": 1, "product": "Black Tees", "Price": "45"},
    {"id": 2, "product": "White Tees", "Price": "45"},
    {"id": 3, "product": "Blue Jeans", "Price": "65"},
    {"id": 4, "product": "Black Jeans", "Price": "65"},
    {"id": 5, "product": "Red Hoodie", "Price": "55"},
    {"id": 6, "product": "Purple Sweater", "Price": "65"}
]

Base.metadata.create_all(engine)

app = FastAPI()

def get_db():
    db = Local_Session()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def root():
    return "Welcome"

@app.get("/products")
def products():
    return PRODUCTS

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

@app.post("/customer-info", response_model=Token)
async def get_customer_info(user: UserClass, db: Session = Depends(get_db)):
    if get_user_by_username(db, user.username):
        raise HTTPException(status_code=400, detail="Already existing username")

    password_hash = get_password_hash(user.password)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)

    user_details = User(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        username=user.username,
        password=password_hash,
        token=access_token,
        date=datetime.now()
    )

    db.add(user_details)
    db.commit()
    db.refresh(user_details)
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/sign-in")
async def sign_in(user: SignIn, db: Session = Depends(get_db)):
    user_auth = await auth_user(db, user.username, user.password)
    if not user_auth:
          raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                              detail="Incorrect username or password", headers={"WWW-Authenticate": "Bearer"})
    return{"message" : "Customer logged in"}

@app.get("/retrieve-customer-details")
async def retrieve_all_customer_details(db: Session = Depends(get_db)):
    customer_details = db.query(User).all()
    return {"conversation": customer_details}

@app.get("/retrieve-customer/{username}")
async def retrieve_customer_info(username: str, db: Session = Depends(get_db)):
    customer_details = db.query(User).filter(User.username == username).all()
    return {"customer Info": customer_details}

@app.delete("/delete-customer/{customer_id}")
async def delete_select_customer(customer_id: int, db: Session = Depends(get_db)):
    db.query(User).filter(User.id == customer_id).delete()
    db.commit()
    return {"message": f"Conversation {customer_id} has been deleted"}

@app.delete("/delete-customers")
async def delete_customers(db: Session = Depends(get_db)):
    db.query(User).delete()
    db.commit()
    return {"message": "Customers have been deleted"}

@app.post("/conversation")
async def convo(text: ConvoClass, db: Session = Depends(get_db)):
    user_inst = db.query(User).filter(User.username == text.customer_username).first()
    if not user_inst:
        raise HTTPException(status_code=400, detail="You have to sign-in")

    convo = Convo(customer_username=text.customer_username, admin=text.admin, customer=text.customer, user_token=user_inst.token)

    db.add(convo)
    db.commit()
    db.refresh(convo)
    return {"conversation": convo}

@app.get("/retrieve-current-conversation")
async def current_conversation(db: Session = Depends(get_db)):
    last_convo = db.query(Convo).order_by(Convo.id.desc()).first()
    return {"conversation": last_convo}

@app.get("/retrieve-conversation")
async def conversation(db: Session = Depends(get_db)):
    convos = db.query(Convo).all()
    return {"conversation": convos}

@app.get("/retrieve-conversation/{token}")
async def retrieve_conversation_token(token: str, db: Session = Depends(get_db)):
    convo_query = db.query(Convo).filter(Convo.user_token == token).all()
    return {"conversation": convo_query}

@app.get("/retrieve-conversation-username/{username}")
async def retrieve_conversation_username(username: str, db: Session = Depends(get_db)):
    convo_usernamequery = db.query(Convo).filter(Convo.customer_username == username).all()
    return {"conversation": convo_usernamequery}

@app.delete("/delete-conversation/{conversation_id}")
async def delete_select_conversation(conversation_id: int, db: Session = Depends(get_db)):
    db.query(Convo).filter(Convo.id == conversation_id).delete()
    db.commit()
    return {"message": f"Conversation {conversation_id} has been deleted"}

@app.delete("/delete-current-conversation")
async def delete_current_conversations(db: Session = Depends(get_db)):
    db.query(Convo).delete()
    db.commit()
    return {"message": "Current conversation have been deleted"}

@app.delete("/delete-conversation")
async def delete_conversations(db: Session = Depends(get_db)):
    db.query(Convo).delete()
    db.commit()
    return {"message": "All conversations have been deleted"}

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

async def auth_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False

    return user

def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def auth_current_user(db: Session, token: str = Depends(oauth2_scheme)):
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credential_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credential_exception
    user = get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credential_exception
    return user

async def get_active_current_user(current_user: UserInDB = Depends(auth_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
