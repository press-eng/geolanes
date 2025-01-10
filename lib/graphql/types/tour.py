from datetime import datetime
from typing import List, Optional

import strawberry

from lib.graphql.types.venture import Venture


@strawberry.type
class Tour:
    id: str
    title: str
    ventures: List[Venture]
    status: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    adult_count: Optional[int] = None
    child_count: Optional[int] = None
    picture_url: Optional[str] = None
