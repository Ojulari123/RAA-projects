from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from tables import Products,User
from schemas import ProductClass
from func import get_db
from typing import List

product_router = APIRouter()

@product_router.get("/view-products", response_model=List[ProductClass])
async def view_all_products(db: Session = Depends(get_db)):
    products = db.query(Products).all()
    return products

@product_router.get("/get-products-by/{product_id}", response_model=ProductClass)
async def get_product_by_id(product_id: int, db: Session = Depends(get_db)):
    get_product_id = db.query(Products).filter(Products.id==product_id).first()
    return get_product_id

@product_router.post("/input-desc-of-products/{product_id}", response_model=ProductClass)
async def input_desc_of_products(product_id: int, text: ProductClass, db: Session = Depends(get_db)):
    product_info = db.query(Products).filter(Products.id==product_id).first()
    if not product_info:
        raise HTTPException(status_code=400, detail="This Product doesn't exist")
    product_info.product_name = text.product_name
    product_info.product_price = text.product_price
    product_info.product_description = text.product_description
    db.commit()
    db.refresh(product_info)
    return product_info

@product_router.post("/input-cont-of-products/{product_id}")
async def input_cont_of_products(file: UploadFile = File(...), db: Session = Depends(get_db)):
    product_data = file.file.read()
    new_product_img = Products(product_content = product_data)
    db.add(new_product_img)
    db.commit()
    db.refresh(new_product_img)
    return {"New Img": new_product_img}
