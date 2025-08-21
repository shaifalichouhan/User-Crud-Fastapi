from app import models
from .conftest import create_user, get_token

def test_checkout_session_mock(client, monkeypatch, db_session):
    user = create_user(db_session, "pay@example.com", "pass")
    token = get_token(client, user.email, "pass")

    product = models.Product(name="Bottle", description="desc", price=5.0, image="/uploads/img.jpg")
    db_session.add(product)
    db_session.commit()

    def mock_checkout_session_create(**kwargs):
        return type("obj", (object,), {"url": "http://mock-checkout.com"})

    monkeypatch.setattr("stripe.checkout.Session.create", mock_checkout_session_create)

    response = client.post(f"/products/checkout-session/{product.id}",
                           headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert "checkout_url" in response.json()
