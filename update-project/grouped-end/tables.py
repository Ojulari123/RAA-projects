from sqlalchemy import create_engine, Column, Integer, String, LargeBinary, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

engine = create_engine("sqlite:///customer.db", connect_args={"check_same_thread": False})
Local_Session = sessionmaker(bind=engine)
Base = declarative_base()

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
    product_name = Column(String(256),nullable=True)
    product_content = Column(LargeBinary,nullable=True)
    product_price = Column(Integer,nullable=True)
    product_description = Column(String(256),nullable=True)

Base.metadata.create_all(engine)

def get_db():
    db = Local_Session()
    try:
        yield db
    finally:
        db.close()
