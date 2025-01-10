from datetime import datetime

import strawberry

from lib.graphql.types.attraction import Attraction


@strawberry.type
class Venture:
    time: datetime
    attraction: Attraction
