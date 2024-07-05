from fastapi import Depends, FastAPI
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, create_engine, DateTime
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

app = FastAPI()

SECRET_KEY = "admin"

engine = create_engine("sqlite:///customer.db",connect_args= {"check_same_thread": False})
Local_Session = sessionmaker(bind=engine)
Base = declarative_base()

class Convo(Base):
    __tablename__ = "conversation"
    id = Column(Integer,primary_key=True)
    admin = Column(String(2000))
    customer = Column(String(2000))
    date = Column(DateTime, default=datetime.now)


class Message(BaseModel):
    message: str

class convoClass(BaseModel):
    admin: str
    customer: str

PRODUCTS = [
    {"id" : 1, "product" : "Black Tees","Price" : "45"},
    {"id" : 2, "product" : "White Tees","Price" : "45"},
    {"id" : 3, "product" : "Blue Jeans","Price" : "65"},
    {"id" : 4, "product" : "Black Jeans","Price" : "65"},
    {"id" : 5, "product" : "Red Hoodie","Price" : "55"},
    {"id" : 6, "product" : "Purple Sweater","Price" : "65"}
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

@app.put("/conversation")
async def convo(text: convoClass, db: Session = Depends(get_db)):
    convo = Convo(admin=text.admin, customer=text.customer)
    db.add(convo)
    db.commit()
    db.refresh(convo)
    return {"conversation": convo}

@app.get("/retrieve-conversation")
async def conversation(db: Session = Depends(get_db)):
    convos = db.query(Convo).all()
    return{"conversation": convos}

@app.delete("/delete-conversation/{customer_id}")
async def delete_select_conversation(customer_id: int, db: Session = Depends(get_db)):
    db.query(Convo).filter(Convo.id == customer_id).delete()
    db.commit()

@app.delete("/delete-conversation")
async def delete_conversations(db: Session = Depends(get_db)):
    db.query(Convo).delete()
    db.commit()
    return {"message": "All conversations have been deleted"}