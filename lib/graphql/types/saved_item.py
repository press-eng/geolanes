from datetime import datetime

import strawberry


@strawberry.type
class SavedItem:
    id: str
    item_json: str
    type: str
    created_at: datetime
