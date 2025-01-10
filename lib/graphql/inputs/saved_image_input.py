from typing import Optional

import strawberry


@strawberry.input
class SavedImageInput:
    page: Optional[int] = strawberry.UNSET
