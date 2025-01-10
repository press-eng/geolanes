from datetime import datetime
from typing import Any, Dict, List, Optional

import strawberry

from lib.graphql.types.error import Error
from lib.models.other_contact_model import OtherContact


@strawberry.type
class OtherContact:
    name: str
    contact_number: str


@strawberry.type
class EnterpriseCustomer:
    id: strawberry.ID
    name: str
    email: str
    avatar_url: Optional[str] = None
    customer_id: str
    role: str
    customer_status: str
    account_type: str
    price_plan: str
    country_state: str
    other_contact_info: Optional[OtherContact] = None
    is_deleted: Optional[bool] = False
    deleted_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_at: Optional[datetime] = None


@strawberry.type
class PaginatedEntCustomerList:
    status: int
    message: str
    page: int
    total_count: int
    data: List[EnterpriseCustomer]


@strawberry.type
class EnterpriseCustomerResponse:
    status: int
    message: str
    customer: EnterpriseCustomer


CustomerResponseWithError = strawberry.union(
    "EnterpriseCustomerResponse", (EnterpriseCustomerResponse, Error)
)

AllCustomerResponse = strawberry.union(
    "AllCustomerResponse", (EnterpriseCustomerResponse, PaginatedEntCustomerList, Error)
)

BulkCustomerResponse = strawberry.union(
    "BulkCustomerResponse", (PaginatedEntCustomerList, Error)
)
