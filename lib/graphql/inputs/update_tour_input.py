from datetime import datetime
from typing import List, Optional

import strawberry

from lib.graphql.inputs.venture_input import VentureInput


@strawberry.input
class UpdateTourInput:
    id: str
    title: Optional[str] = strawberry.UNSET
    start_date: Optional[datetime] = strawberry.UNSET
    end_date: Optional[datetime] = strawberry.UNSET
    ventures: Optional[List[VentureInput]] = strawberry.UNSET
    status: Optional[str] = strawberry.UNSET
    adult_count: Optional[int] = strawberry.UNSET
    child_count: Optional[int] = strawberry.UNSET
    confirmed: Optional[bool] = strawberry.UNSET
    picture_url: Optional[str] = strawberry.UNSET
