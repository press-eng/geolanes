from datetime import datetime
from typing import List, Optional

import strawberry

from lib.graphql.types.venture import Venture


@strawberry.type
class TourSuggestion:
    ventures: List[Venture]
    start_date: datetime
    end_date: datetime
