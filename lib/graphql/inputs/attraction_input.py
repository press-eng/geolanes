from typing import Optional, List

import strawberry

from lib.graphql.inputs.coordinate_input import CoordinateInput


@strawberry.input
class AttractionInput:
    area_name: Optional[str] = strawberry.UNSET
    page: Optional[int] = 1
    just_recommended: Optional[bool] = strawberry.UNSET
    just_alphabetical: Optional[bool] = strawberry.UNSET
    just_downtown_first: Optional[bool] = strawberry.UNSET
    rating: Optional[int] = strawberry.UNSET
    max_centre_offset: Optional[int] = strawberry.UNSET
    sightseeing: Optional[List[str]] = strawberry.UNSET
    search: Optional[str] = strawberry.UNSET
    id: Optional[strawberry.ID] = strawberry.UNSET
    coordinates: Optional[CoordinateInput] = strawberry.UNSET
    pet_friendly: Optional[bool] = strawberry.UNSET
    child_friendly: Optional[bool] = strawberry.UNSET
    lgbtq_friendly: Optional[bool] = strawberry.UNSET
    custom_sightseeing: Optional[str] = strawberry.UNSET
