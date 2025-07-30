from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app import models, schemas
from app.database import get_db
from app.auth.deps import get_current_user
from app.auth.deps import is_admin_user
from app.models.user import User 
import stripe
from app.config import STRIPE_SECRET_KEY
from app.models.product import Product as DBProduct

router = APIRouter(
    prefix="/products",
    tags=["Products"]
)

# Get all products (everyone can see)
@router.get("/", response_model=List[schemas.Product])
def get_products(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(models.Product).all()

# Get single product by ID (everyone can see)
@router.get("/{product_id}", response_model=schemas.Product)
def get_product(product_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

# Create product (only admin)
@router.post("/", response_model=schemas.Product)
def create_product(
    product: schemas.ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(is_admin_user)
):
    db_product = models.Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

# Update product (only admin)
@router.put("/{product_id}", response_model=schemas.Product)
def update_product(
    product_id: int,
    updated_product: schemas.ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(is_admin_user)
):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    for field, value in updated_product.dict(exclude_unset=True).items():
        setattr(product, field, value)
    db.commit()
    db.refresh(product)
    return product

# Delete product (only admin)
@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(is_admin_user)
):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    db.commit()
    return {"message": "Product deleted successfully"}


stripe.api_key = STRIPE_SECRET_KEY
@router.post("/create-checkout-session/{product_id}")
def create_checkout_session(product_id: int, db: Session = Depends(get_db)):
    product = db.query(DBProduct).filter(DBProduct.id == product_id).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': product.name,
                            'description': product.description,
                        },
                        'unit_amount': int(product.price * 100),  
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url="http://localhost:8000/success",
            cancel_url="http://localhost:8000/cancel",
        )
        return {"checkout_url": checkout_session.url}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))