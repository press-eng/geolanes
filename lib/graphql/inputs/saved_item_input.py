from typing import Optional

import strawberry


@strawberry.input
class SavedItemInput:
    page: Optional[int] = strawberry.UNSET
    type: Optional[str] = strawberry.UNSET
