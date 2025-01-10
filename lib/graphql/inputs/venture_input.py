from datetime import datetime

import strawberry


@strawberry.input
class VentureInput:
    attraction: str
    time: datetime
