from datetime import datetime

import strawberry


@strawberry.type
class SavedImage:
    id: strawberry.ID
    image: str
    created_at: datetime
