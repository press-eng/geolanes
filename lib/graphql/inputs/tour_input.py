from typing import Optional

import strawberry


@strawberry.input
class TourInput:
    status: Optional[str] = None
    page: Optional[int] = None
