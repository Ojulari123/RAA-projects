from fastapi import Depends, FastAPI
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, create_engine, DateTime
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import json
app = FastAPI()

SECRET_KEY = "admin"

engine = create_engine("sqlite:///customer.db", connect_args={"check_same_thread": False})
Local_Session = sessionmaker(bind=engine)
Base = declarative_base()

class Convo(Base):
    __tablename__ = "customer"
    id = Column(Integer, primary_key=True, autoincrement=True)
    admin = Column(String(2000))
    customer = Column(String(2000))
    date = Column(DateTime, default=datetime.now)

class convoClass(BaseModel):
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

conversation_dict = {}
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

@app.post("/conversation")
async def convo(text: convoClass, db: Session = Depends(get_db)):
    convo = Convo(admin=text.admin, customer=text.customer)
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

@app.delete("/delete-conversation/{conversation_id}")
async def delete_select_conversation(conversation_id: int, db: Session = Depends(get_db)):
    db.query(Convo).filter(Convo.id == conversation_id).delete()
    db.commit()
    return {"message": f"Conversation {conversation_id} has been deleted"}

@app.delete("/delete-current-conversation")
async def delete_current_conversations(db: Session = Depends(get_db)):
    db.query(Convo).delete()
    db.commit()
    conversation_dict.clear()
    return {"message": "Current conversation have been deleted"}

@app.delete("/delete-conversation")
async def delete_conversations(db: Session = Depends(get_db)):
    db.query(Convo).delete()
    db.commit()
    return {"message": "All conversations have been deleted"}