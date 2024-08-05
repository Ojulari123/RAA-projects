from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas import ConvoClass
from tables import Convo,User
from func import auth_current_user, get_db, role_checker
from typing import List

convo_router = APIRouter()

@convo_router.post("/conversation", response_model=ConvoClass)
async def convo(text: ConvoClass, db: Session = Depends(get_db), user: User = Depends(auth_current_user)):
    user_inst = db.query(User).filter(User.username == text.customer_username).first()
    if not user_inst:
        raise HTTPException(status_code=400, detail="You have to sign-in")
    convo = Convo(customer_username=text.customer_username, admin_message=text.admin_message, customer_message=text.customer_message, customer_user_id=user_inst.id)
    db.add(convo)
    db.commit()
    db.refresh(convo)
    return {"conversation": convo}

@convo_router.get("/retrieve-current-conversation", response_model=ConvoClass)
async def current_conversation(user: User = Depends(auth_current_user), db: Session = Depends(get_db)):
    last_convo = db.query(Convo).order_by(Convo.id.desc()).first()
    return {"conversation": last_convo}

@convo_router.get("/retrieve-conversation", response_model=List[ConvoClass])
async def conversation(user: User = Depends(auth_current_user), db: Session = Depends(get_db)):
    convos = db.query(Convo).all()
    return {"conversation": convos}

@convo_router.get("/retrieve-conversation/{user_id}", response_model=List[ConvoClass])
async def retrieve_conversation_token(user_id: int, user: User = Depends(auth_current_user), db: Session = Depends(get_db)):
    await role_checker(required_role="admin", user=user)
    user_convo_query = db.query(Convo).join(Convo.customer_user).filter(Convo.customer_user_id == user_id).all()
    return {"conversation": user_convo_query}

@convo_router.get("/retrieve-conversation-username/{username}", response_model=List[ConvoClass])
async def retrieve_conversation_username(username: str, user: User = Depends(auth_current_user), db: Session = Depends(get_db)):
    await role_checker(required_role="admin", user=user)
    user_convo_query = db.query(Convo).join(Convo.customer_user).filter(User.username == username).all()
    return {"conversation": user_convo_query}
