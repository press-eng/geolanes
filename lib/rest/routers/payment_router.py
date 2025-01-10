import stripe
from fastapi import HTTPException, Request
from fastapi.routing import APIRouter

from lib import config
from lib.models.payment_model import PaymentModel

stripe.api_key = config.STRIPE_SECRET_KEY

router = APIRouter()

stripe_webhook_secret = config.STRIPE_WEBHOOK_SECRET


@router.post("/stripe-webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, stripe_webhook_secret
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        raise HTTPException(status_code=400, detail="Invalid signature")

    if event["type"] == "payment_intent.succeeded":
        payment_intent = event["data"]["object"]
        searched_payment = await PaymentModel.find_one(
            {"payment_intent_id": payment_intent["id"]}
        )
        if searched_payment:
            searched_payment.status = "succeeded"
            await searched_payment.save()
            return {"status": "success"}

    elif event["type"] == "payment_intent.payment_failed":
        payment_intent = event["data"]["object"]
        searched_payment = await PaymentModel.find_one(
            {"payment_intent_id": payment_intent["id"]}
        )
        if searched_payment:
            searched_payment.status = "failed"
            await searched_payment.save()
            return {"status": "failed"}
    else:
        return {"status": "unknown event"}
