from typing import Optional

from lib.graphql.inputs.attraction_category_input import AttractionCategoryInput
from lib.graphql.types.tag_page import TagPage


async def read_attraction_categories(
    categories: Optional[AttractionCategoryInput] = None,
):
    return TagPage(
        items=[],
        page=categories.page,
        total=0,
    )
