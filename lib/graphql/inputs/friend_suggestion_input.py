from typing import List, Optional

import strawberry

from lib.graphql.inputs.coordinate_input import CoordinateInput


@strawberry.input
class FriendSuggestionInput:
    just_coordinates: Optional[CoordinateInput] = strawberry.UNSET
    just_contacts: Optional[bool] = strawberry.UNSET
    just_facebook: Optional[bool] = strawberry.UNSET
    search: Optional[str] = strawberry.UNSET
    page: Optional[int] = strawberry.UNSET
