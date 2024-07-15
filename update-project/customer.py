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

    username_relationship = relationship("Convo", primaryjoin="User.username == Convo.customer_username", back_populates="username_rel")
    token_relationship = relationship("Convo", primaryjoin="User.token == Convo.user_token", back_populates="token_rel")

class Convo(Base):
    __tablename__ = "Conversation"
    id = Column(Integer, primary_key=True, autoincrement=True)
    admin = Column(String(2000))
    customer = Column(String(2000))
    customer_username = Column(String(100),ForeignKey("User.username"),unique=True)
    user_token = Column(String(100),ForeignKey("User.token"),unique=True)
    date = Column(DateTime, default=datetime.now)

    username_rel = relationship("User", foreign_keys=[customer_username], back_populates="username_relationship")
    token_rel = relationship("User", foreign_keys=[user_token], back_populates="token_relationship")

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
    return {"conversation": customer_details}


@app.get("/retrieve-customer/{username}")
async def retrieve_customer_info(username: str, db: Session = Depends(get_db)):
    customer_details = db.query(User).filter(User.username==username).all()
    return {"customer Info" : customer_details}

@app.delete("/delete-customer/{customer_id}")
async def delete_select_customer(customer_id: int, db: Session = Depends(get_db)):
    db.query(User).filter(User.id == customer_id).delete()
    db.commit()
    return {"message": f"Conversation {customer_id} has been deleted"}

@app.delete("/delete-customers")
async def delete_customers(db: Session = Depends(get_db)):
    db.query(User).delete()
    db.commit()
    return {"message": "Customers has been deleted"}

@app.post("/conversation")
async def convo(text: convoClass, db: Session = Depends(get_db)):
    convo_username = db.query(Convo).filter(Convo.customer_username==text.customer_username).first()

    if db.query(Convo).filter(Convo.customer_username == text.customer_username).first():
        raise HTTPException(status_code=400, detail="Already existing username")

    if convo_username:
        User.token = convo_username.user_token
        convo = Convo(customer_username=text.customer_username, admin=text.admin, customer=text.customer)

    convo = Convo(customer_username=text.customer_username, admin=text.admin, customer=text.customer)

    db.add(convo)
    db.commit()
    db.refresh(convo)
    return {"conversation": convo}

@app.get("/retrieve-conversation/{customer_username}")
async def retrieve_conversation_username(username: str, db: Session = Depends(get_db)):
    conversation_query = db.query(Convo).filter(Convo.customer_username==username).all()
    return {"customer Info" : conversation_query}

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
    convo_query = db.query(Convo).filter(Convo.user_token==token).all()
    return {"conversation": convo_query}

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

