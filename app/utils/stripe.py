import stripe
from app.config import STRIPE_SECRET_KEY


stripe.api_key = STRIPE_SECRET_KEY

def create_checkout_session(product_name: str, product_price: int, currency="usd"):
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": currency,
                        "product_data": {
                            "name": product_name,
                        },
                        "unit_amount": product_price * 100,  
                    },
                    "quantity": 1,
                },
            ],
            mode="payment",
            success_url="https://localhost:8000/docs",
            cancel_url="https://localhost:8000/docs",
        )
        return session.url
    except Exception as e:
        raise Exception(f"Stripe Checkout creation failed: {e}")
