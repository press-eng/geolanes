import jwt
from beanie import PydanticObjectId
from bson import ObjectId
from fastapi import HTTPException, Request
from fastapi.routing import APIRouter

from lib import config
from lib.graphql.types.error import Error
from lib.models.enterprise_customer_model import EnterpriseCustomerModel

SECRET_KEY = config.JWT_SECRET

router = APIRouter()


def decode_token(token: str) -> str:
    try:
        # Decode the JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        customer_id = payload.get("customer_id")

        if not customer_id:
            raise ValueError("Customer ID not found in token")

        print("*** Extracted Customer ID: ", customer_id)
        return customer_id

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.get("/{token}", response_model=EnterpriseCustomerModel)
async def get_campaign(token: str):
    # Extract customer_id from the token
    customer_id = decode_token(token)

    # Fetch customer from the database
    customer = await EnterpriseCustomerModel.find_one({"customer_id": customer_id})

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    print("*** Found Customer: ", customer)  # Debug log
    return customer
