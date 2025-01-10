from datetime import datetime, timezone
from typing import Annotated, Dict, List, Optional

import pymongo
from beanie import Document, Indexed, Link
from pydantic import Field

from lib.models.other_contact_model import OtherContact


class EnterpriseCustomerModel(Document):
    name: Annotated[str, Indexed(index_type=pymongo.TEXT)]
    email: Optional[str] = None
    other_contact_info: Optional[Dict[str, str]] = Field(
        default_factory=dict
    )  # Use default_factory for mutable types

    customer_id: Optional[str] = None
    role: Optional[str] = None
    account_type: Optional[str] = "Enterprise"
    price_plan: Optional[str] = None
    country_state: Optional[str] = None
    avatar_url: Optional[str] = None
    customer_status: Optional[str] = None

    password: Optional[bytes] = None
    otp: Optional[str] = None
    otp_created_at: Optional[datetime] = None
    address: Optional[str] = None
    address_latitude: Optional[float] = None
    address_longitude: Optional[float] = None
    is_private: Optional[bool] = None
    permanently_deactivated: Optional[bool] = None
    deactivated: Optional[bool] = None

    is_deleted: Optional[bool] = False
    deleted_at: Optional[datetime] = None

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "enterprise_customers"
