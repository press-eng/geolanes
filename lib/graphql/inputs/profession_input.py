from typing import Optional

import strawberry


@strawberry.input
class ProfessionInput:
    page: Optional[int] = strawberry.UNSET
