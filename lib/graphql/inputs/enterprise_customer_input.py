from datetime import datetime
from typing import List, Optional

import strawberry


@strawberry.input
class CreateEnterpriseCustomerInput:
    name: str
    email: str
    password: Optional[str] = None
    otp: Optional[str] = None
    otp_created_at: Optional[datetime] = None
    avatar_url: Optional[str] = None
    address: Optional[str] = None
    address_latitude: Optional[float] = None
    address_longitude: Optional[float] = None
    is_private: Optional[bool] = None
    other_contact_name: str
    other_contact_number: str
    customer_id: str
    role: str
    price_plan: str
    country_state: str
    permanently_deactivated: Optional[bool] = None
    deactivated: Optional[bool] = None


@strawberry.input
class UpdateEnterpriseCustomerInput:
    id: str
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    other_contact_name: Optional[str] = None
    other_contact_number: Optional[str] = None
    role: Optional[str] = None
    customer_status: Optional[str] = None
    price_plan: Optional[str] = None
    country_state: Optional[str] = None
    updated_at: Optional[datetime] = strawberry.UNSET
    is_deleted: Optional[bool] = strawberry.UNSET
    deleted_at: Optional[datetime] = strawberry.UNSET
    # otp: Optional[str] = None
    # otp_created_at: Optional[datetime] = strawberry.UNSET
    # address: Optional[str] = None
    # address_latitude: Optional[float] = None
    # address_longitude: Optional[float] = None
    # is_private: Optional[bool] = strawberry.UNSET
    # customer_id: Optional[str] = None
    # permanently_deactivated: Optional[bool] = strawberry.UNSET
    # deactivated: Optional[bool] = strawberry.UNSET


@strawberry.input
class entCustomerPaginationInput:
    page: int = 1
    customer_status: Optional[str] = None
    date: Optional[str] = None
    search_text: Optional[str] = None
    export_type: Optional[str] = None
    id: Optional[str] = None


@strawberry.input
class customerBulkOperationInput:
    page: int = 1
    ids: List[str]
    operation: str


@strawberry.input
class UpdateEnterpriseCustomerPasswordInput:
    id: str
    password: str
