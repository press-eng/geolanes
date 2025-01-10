from typing import List, Optional

import strawberry

from lib.graphql.inputs.coordinate_input import CoordinateInput


@strawberry.input
class CreateAttractionInput:
    title: str
    images: Optional[List[str]] = strawberry.UNSET
    attraction_category: Optional[strawberry.ID] = strawberry.UNSET
    sightseeing_id: Optional[str] = strawberry.UNSET
    address: Optional[str] = strawberry.UNSET
    city: Optional[str] = strawberry.UNSET
    country: Optional[str] = strawberry.UNSET
    zip_code: Optional[str] = strawberry.UNSET
    lat: Optional[float] = strawberry.UNSET
    lng: Optional[float] = strawberry.UNSET
    always_open: Optional[bool] = strawberry.UNSET
    opening_time: Optional[str] = strawberry.UNSET
    closing_time: Optional[str] = strawberry.UNSET
    contact_number: Optional[str] = strawberry.UNSET
    centre_offset: Optional[int] = strawberry.UNSET
    description: Optional[str] = strawberry.UNSET
    restaurant_count: Optional[int] = strawberry.UNSET
    accomodation_count: Optional[int] = strawberry.UNSET
    is_source_representative: Optional[bool] = strawberry.UNSET
