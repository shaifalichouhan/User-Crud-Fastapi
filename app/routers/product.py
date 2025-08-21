from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import stripe
import os
from uuid import uuid4

from app import models, schemas
from app.database import get_db
from app.auth.deps import get_current_user, is_admin_user
from app.models.user import User
from app.models.product import Product as DBProduct
from app.config import STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET
from app.utils.email_utils import send_invoice_email

router = APIRouter(prefix="/products", tags=["Products"])

stripe.api_key = STRIPE_SECRET_KEY

# Upload dir
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(os.path.dirname(BASE_DIR), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Get all products
@router.get("/", response_model=List[schemas.Product])
def get_products(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(models.Product).all()

# Get single product
@router.get("/{product_id}", response_model=schemas.Product)
def get_product(product_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

# Create product with image upload
@router.post("/", response_model=schemas.Product)
def create_product(
    name: str = Form(...),
    description: Optional[str] = Form(None),
    price: float = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(is_admin_user)
):
    ext = os.path.splitext(image.filename)[1]
    filename = f"{uuid4().hex}{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    with open(filepath, "wb") as f:
        f.write(image.file.read())

    image_url = f"/uploads/{filename}"

    db_product = models.Product(
        name=name,
        description=description,
        price=price,
        image=image_url
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

# Update product (optional new image)
@router.put("/{product_id}", response_model=schemas.Product)
def update_product(
    product_id: int,
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    price: Optional[float] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(is_admin_user)
):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if name:
        product.name = name
    if description:
        product.description = description
    if price:
        product.price = price
    if image:
        ext = os.path.splitext(image.filename)[1]
        filename = f"{uuid4().hex}{ext}"
        filepath = os.path.join(UPLOAD_DIR, filename)
        with open(filepath, "wb") as f:
            f.write(image.file.read())
        product.image = f"/uploads/{filename}"

    db.commit()
    db.refresh(product)
    return product

# Delete product
@router.delete("/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db), current_user: User = Depends(is_admin_user)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    db.commit()
    return {"message": "Product deleted successfully"}

# Stripe Checkout Session
@router.post("/checkout-session/{product_id}")
def checkout_session(product_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    product = db.query(DBProduct).filter(DBProduct.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    try:
        checkout_session = stripe.checkout.Session.create(
            customer_email=current_user.email,
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': product.name,
                        'description': product.description,
                    },
                    'unit_amount': int(product.price * 100),
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url="http://localhost:8000/docs",
            cancel_url="http://localhost:8000/docs",
        )
        return {"checkout_url": checkout_session.url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Stripe Webhook
@router.post("/webhook")
async def stripe_webhook(request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        customer_email = session.get("customer_email", "test@example.com")
        html_content = f"""
        <h3>Thank you for your payment!</h3>
        <p>Session ID: {session['id']}</p>
        <p>Amount Paid: {session['amount_total'] / 100} USD</p>
        """
        send_invoice_email(customer_email, "Invoice - Payment Successful", html_content)
    return {"status": "success"}
