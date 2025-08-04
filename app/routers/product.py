from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List
import stripe

from app import models, schemas
from app.database import get_db
from app.auth.deps import get_current_user, is_admin_user
from app.models.user import User 
from app.models.product import Product as DBProduct
from app.config import STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET
from app.utils.email import send_invoice_email

router = APIRouter(
    prefix="/products",
    tags=["Products"]
)

stripe.api_key = STRIPE_SECRET_KEY

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
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db), current_user: User = Depends(is_admin_user)):
    db_product = models.Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

# Update product (only admin)
@router.put("/{product_id}", response_model=schemas.Product)
def update_product(product_id: int, updated_product: schemas.ProductUpdate, db: Session = Depends(get_db), current_user: User = Depends(is_admin_user)):
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
def delete_product(product_id: int, db: Session = Depends(get_db), current_user: User = Depends(is_admin_user)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    db.commit()
    return {"message": "Product deleted successfully"}

# Stripe Checkout Session (logged-in user email used)
@router.post("/checkout-session/{product_id}")
def checkout_session(product_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    product = db.query(DBProduct).filter(DBProduct.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    try:
        checkout_session = stripe.checkout.Session.create(
            customer_email=current_user.email,  # send real user email
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
            success_url="http://localhost:8000/docs",
            cancel_url="http://localhost:8000/docs",
        )
        return {"checkout_url": checkout_session.url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Stripe Webhook
@router.post("/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        print("Payment successful for session:", session["id"])

        customer_email = session.get("customer_email", "test@example.com")
        html_content = f"""
        <h3>Thank you for your payment!</h3>
        <p>Session ID: {session['id']}</p>
        <p>Amount Paid: {session['amount_total'] / 100} USD</p>
        """
        send_invoice_email(customer_email, "Invoice - Payment Successful", html_content)
        print("Payment successful and email sent.")

    return {"status": "success"}
