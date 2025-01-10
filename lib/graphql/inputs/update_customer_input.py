from typing import List, Optional

import strawberry


@strawberry.input
class UpdateCustomerInput:
    password: Optional[str] = strawberry.UNSET
    phone: Optional[str] = strawberry.UNSET
    gender: Optional[str] = strawberry.UNSET
    profession: Optional[str] = strawberry.UNSET
    hobbies: Optional[List[str]] = strawberry.UNSET
    sightseeing: Optional[List[str]] = strawberry.UNSET
    avatar_url: Optional[str] = strawberry.UNSET
    fcm_token: Optional[str] = strawberry.UNSET
    headline: Optional[str] = strawberry.UNSET
    bio: Optional[str] = strawberry.UNSET
    address: Optional[str] = strawberry.UNSET
    append_contacts: Optional[List[str]] = strawberry.UNSET
    notification_events: Optional[List[strawberry.ID]] = strawberry.UNSET
    name: Optional[str] = strawberry.UNSET
    description: Optional[str] = strawberry.UNSET
    email: Optional[str] = strawberry.UNSET
    language_country_iso_code: Optional[str] = strawberry.UNSET
    currency_country_iso_code: Optional[str] = strawberry.UNSET
    travelling_unit_code: Optional[str] = strawberry.UNSET
    is_private: Optional[bool] = strawberry.UNSET
