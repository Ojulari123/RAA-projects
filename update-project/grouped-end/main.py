from fastapi import FastAPI
from user import user_router
from product import product_router
from convo import convo_router

app = FastAPI()


app.include_router(user_router, prefix="/users", tags=["users"])
app.include_router(product_router, prefix="/products", tags=["products"])
app.include_router(convo_router, prefix="/conversations", tags=["conversations"])
