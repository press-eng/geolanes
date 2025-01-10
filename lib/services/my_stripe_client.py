import stripe

from lib import config

stripe.api_key = config.STRIPE_SECRET_KEY


async def create_stripe_payment_intent(customer_id: str, amount: int, currency: str):
    try:
        intent = stripe.PaymentIntent.create(
            amount=amount, currency=currency, metadata={"customer_id": customer_id}
        )
        return intent
    except Exception as e:
        raise Exception(f"Stripe API error: {str(e)}")
