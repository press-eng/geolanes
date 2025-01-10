from lib.graphql.types.payment import Payment
from lib.models.payment_model import PaymentModel


async def payment_model_to_type(model: PaymentModel) -> Payment:
    return Payment(
        id=str(model.id),
        client_secret=None,
        status=model.status,
        amount=model.amount,
        currency=model.currency,
        updated_at=model.updated_at,
    )
