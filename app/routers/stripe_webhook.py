from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.config import STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET
from app.models.product import Product as DBProduct
import stripe
from app.utils.email import send_invoice_email
from app.utils.pdf_generator import generate_invoice_pdf

router = APIRouter(
    prefix="/products",
    tags=["Stripe Webhook"]
)

stripe.api_key = STRIPE_SECRET_KEY
@router.post("/checkout-session/{product_id}")
def checkout_session(product_id: int, db: Session = Depends(get_db)):
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
            success_url="http://localhost:8000/docs",
            cancel_url="http://localhost:8000/docs",
        )
        return {"checkout_url": checkout_session.url}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

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
        
        try:
            amount_paid = session.get("amount_total", 0) / 100
            customer_email = session.get("customer_details", {}).get("email")
            print("Customer email:", customer_email)
            print("Amount paid:", amount_paid)

            # PDF Generate 
            pdf_path = generate_invoice_pdf(session["id"], amount_paid)
            print("PDF generated at:", pdf_path)

            # Email send
            send_invoice_email(
                to_email=customer_email or "test@example.com",
                subject="Invoice - Payment Successful",
                html_content=f"""
                    <h3>Thank you for your payment!</h3>
                    <p>Session ID: {session['id']}</p>
                    <p>Amount Paid: {amount_paid} USD</p>
                """,
                pdf_path=pdf_path
            )
        except Exception as e:
            print("ERROR inside webhook logic:", e)

    return {"status": "success"}
