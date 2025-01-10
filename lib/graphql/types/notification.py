from datetime import datetime
from typing import Optional

import strawberry


@strawberry.type
class Notification:
    id: strawberry.ID
    type: str
    title_html: str
    read: bool = False
    flagged: bool
    time: datetime
    message: Optional[str] = None
    download_url: Optional[str] = None
    tour_id: Optional[strawberry.ID] = None
