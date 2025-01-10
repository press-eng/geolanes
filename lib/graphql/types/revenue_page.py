from typing import List

import strawberry

from lib.graphql.types.revenue import Revenue


@strawberry.type
class RevenuePage:
    monthly_revenues: List[Revenue]
    grand_total: float
