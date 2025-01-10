from typing import Any, Dict, Optional

import strawberry
from babel import numbers
from beanie import PydanticObjectId
from beanie.operators import In
from iso_language_codes import language_name
from pycountry import countries
from strawberry.types import Info

from lib.graphql.types.customer import Customer
from lib.graphql.types.customer_public import CustomerPublic
from lib.graphql.types.tag import Tag
from lib.helpers.notification_event_helper import notification_event_model_to_type
from lib.models.customer_model import CustomerModel
from lib.models.hobby_model import HobbyModel
from lib.models.notification_event_model import NotificationEventModel
from lib.models.profession_model import ProfessionModel
from lib.models.sightseeing_model import SightseeingModel
from lib.services import myjwt
from lib.travelling_units import travelling_units


def remove_unset_or_none(data: Dict[str, Any]) -> Dict[str, Any]:
    """Remove keys with values that are UNSET or None."""
    return {
        key: value
        for key, value in data.items()
        if value is not None and value is not strawberry.UNSET
    }


async def customer_model_to_type(model: CustomerModel) -> Customer:
    # Fetch related entities if needed
    profession = (
        await ProfessionModel.get(model.profession) if model.profession else None
    )
    profession_tag = (
        Tag(id=str(profession.id), label=profession.label) if profession else None
    )

    hobbies = await HobbyModel.find(
        In(HobbyModel.id, [PydanticObjectId(h) for h in model.hobbies or []])
    ).to_list()

    sightseeing = await SightseeingModel.find(
        In(SightseeingModel.id, [PydanticObjectId(s) for s in model.sightseeing or []])
    ).to_list()

    notification_preferences = await NotificationEventModel.find(
        In(
            NotificationEventModel.id,
            [PydanticObjectId(n) for n in model.notification_event_ids or []],
        )
    ).to_list()

    # Create the Customer object
    customer_data = {
        "id": str(model.id),
        "name": model.name,
        "jwt": myjwt.encode({"customerId": str(model.id)}),
        "email": model.email,
        "phone": model.phone,
        "gender": model.gender,
        "profession": profession_tag,
        "hobbies": [Tag(id=str(h.id), label=h.label) for h in hobbies],
        "sightseeing": [Tag(id=str(s.id), label=s.label) for s in sightseeing],
        "avatar_url": model.avatar_url,
        "notification_events": [
            notification_event_model_to_type(n) for n in notification_preferences
        ],
        "headline": model.headline,
        "bio": model.bio,
        "address": model.address,
        "description": model.description,
        "language": (
            Tag(
                id=model.language_country_iso_code,
                label=_language_from_iso_code(model.language_country_iso_code),
            )
            if model.language_country_iso_code
            else None
        ),
        "currency": (
            Tag(
                id=model.currency_country_iso_code,
                label=_currency_from_iso_code(model.currency_country_iso_code),
            )
            if model.currency_country_iso_code
            else None
        ),
        "travelling_unit": (
            Tag(
                id=model.travelling_unit_code,
                label=travelling_units[model.travelling_unit_code],
            )
            if model.travelling_unit_code
            else None
        ),
        "is_private": model.is_private,
    }

    # Clean data by removing UNSET or None values
    cleaned_data = remove_unset_or_none(customer_data)

    return Customer(**cleaned_data)


def _language_from_iso_code(language_country_iso_code):
    [language_code, country_code] = language_country_iso_code.split("-")
    country = countries.get(alpha_2=country_code)
    return f"{language_name(language_code)}, {country.name}"


def _currency_from_iso_code(currency_country_iso_code):
    [currency_code, country_code] = currency_country_iso_code.split("-")
    country = countries.get(alpha_2=country_code)
    return f"{numbers.get_currency_name(currency_code)}, {country.name}"


async def get_verified_customer(info: Info) -> Optional[CustomerModel]:
    auth_header = info.context["request"].headers.get("Authorization") or ""
    token = auth_header[len("Bearer ") :]
    if token:
        try:
            json = myjwt.decode(token)
            searched_customer = await CustomerModel.find(
                CustomerModel.id == PydanticObjectId(json["customerId"]),
                In(CustomerModel.deactivated, [False, None]),
            ).first_or_none()
            if searched_customer:
                return searched_customer

        except:
            pass

    return None


def customer_model_to_public_type(model: CustomerModel) -> CustomerPublic:
    return CustomerPublic(
        id=model.id,
        name=model.name,
        email=model.email,
        avatar_url=model.avatar_url,
    )


def replace_unset_with_false(data: dict) -> dict:
    """Replace all instances of UNSET with appropriate defaults."""
    return {
        key: (False if key == "is_private" and value is strawberry.UNSET else value)
        for key, value in data.items()
    }
