from typing import Annotated, Union

import strawberry

from lib.graphql.types.error import Error
from lib.graphql.types.tag_page import TagPage

TagPageResponse = Annotated[Union[TagPage, Error], strawberry.union("TagPageResponse")]
