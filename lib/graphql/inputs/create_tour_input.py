from datetime import datetime
from typing import List, Optional

import strawberry

from lib.graphql.inputs.venture_input import VentureInput


@strawberry.input
class CreateTourInput:
    title: str
    start_date: Optional[datetime] = strawberry.UNSET
    end_date: Optional[datetime] = strawberry.UNSET
    ventures: Optional[List[VentureInput]] = strawberry.UNSET
    adult_count: Optional[int] = strawberry.UNSET
    child_count: Optional[int] = strawberry.UNSET
