from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, create_engine, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, Session,relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

app = FastAPI()

SECRET_KEY = "admin"

engine = create_engine("sqlite:///customer.db", connect_args={"check_same_thread": False})
Local_Session = sessionmaker(bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "User"
    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    email = Column(String(200))
    username = Column(String(100),unique=True)
    password = Column(String(100),nullable=False)
    token = Column(String(100),unique=True)
    date = Column(DateTime, default=datetime.now)

    username_relationship = relationship("Convo", primaryjoin = "User.username == Convo.customer_username", back_populates = "username_rel")
    token_relationship = relationship("Convo", primaryjoin = "User.token == Convo.user_token", back_populates = "token_rel")

class Convo(Base):
    __tablename__ = "Conversation"
    id = Column(Integer, primary_key=True, autoincrement=True)
    admin = Column(String(2000))
    customer = Column(String(2000))
    customer_username = Column(String(100),ForeignKey("User.username"))
    user_token = Column(String(100),ForeignKey("User.token"))
    date = Column(DateTime, default=datetime.now)

    username_rel = relationship("User", foreign_keys = [customer_username], back_populates = "username_relationship")
    token_rel = relationship("User", foreign_keys = [user_token], back_populates = "token_relationship")

class UserClass(BaseModel):
    first_name: str
    last_name: str
    email: str
    username: str
    password: str


class convoClass(BaseModel):
    customer_username: str
    admin: str
    customer: str

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
    return db.query(User).filter(User.username.ilike(username)).first()

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

@app.post("/customer-info")
async def get_customer_info(user:UserClass, db:Session = Depends(get_db)):
     
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Already existing username")
     
    token_auth = f"{user.username}{user.last_name}{datetime.now()}"

    user_details= User(
        first_name = user.first_name,
        last_name = user.last_name,
        email = user.email,
        username = user.username,
        password = user.password,
        token = token_auth,
        date = datetime.now()
    )

    db.add(user_details)
    db.commit()
    db.refresh(user_details)
    return{"message":user_details}

@app.get("/retrieve-customer-details")
async def retrieve_all_customer_details(db: Session = Depends(get_db)):
    customer_details = db.query(User).all()
    customer_details_list = []
    
    for customer in customer_details:
        load_customer_details = {
            "id": customer.id,
            "first_name": customer.first_name,
            "last_name": customer.last_name,
            "email": customer.email,
            "username": customer.username,
        }
        customer_details_list.append(load_customer_details)

    return {"customer_details": customer_details_list}


@app.get("/retrieve-customer/{username}")
async def retrieve_customer_info(username: str, db: Session = Depends(get_db)):
    customer_details = db.query(User).filter(User.username==username).all()
    return {"customer Info" : customer_details}

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
async def convo(text: convoClass, db: Session = Depends(get_db)):
    convo_username = db.query(Convo).filter(Convo.customer_username==text.customer_username)

    if db.query(Convo).filter(Convo.customer_username == text.customer_username).first():
        raise HTTPException(status_code=400, detail="Already existing username")

    if convo_username:
        User.token = Convo.user_token
        convo = Convo(customer_username=text.customer_username, admin=text.admin, customer=text.customer)

    convo = Convo(customer_username=text.customer_username, admin=text.admin, customer=text.customer)

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

@app.get("/retrieve-conversation/{token}")
async def retrieve_conversation_token(token: str, db: Session = Depends(get_db)):
    convo_query = db.query(Convo).filter(Convo.user_token==token).all()
    return {"conversation": convo_query}


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