from typing import Optional

from lib import config
from lib.graphql.inputs.hobby_input import HobbyInput
from lib.graphql.types.error import Error
from lib.graphql.types.tag import Tag
from lib.graphql.types.tag_page import TagPage
from lib.models.hobby_model import HobbyModel


async def read_hobbies(hobbies: Optional[HobbyInput] = None):
    hobbies = hobbies or HobbyInput(page=1)

    try:
        searched_hobbies = (
            await HobbyModel.find_all()
            .skip((hobbies.page - 1) * config.PAGE_SIZE)
            .limit(config.PAGE_SIZE)
            .to_list()
        )
        total_records = await HobbyModel.find_all().count()

        return TagPage(
            items=[Tag(id=str(h.id), label=h.label) for h in searched_hobbies],
            page=hobbies.page,
            total=total_records,
        )

    except Exception as e:
        print(e)
        return Error(status=500, message="Something went wrong!")
