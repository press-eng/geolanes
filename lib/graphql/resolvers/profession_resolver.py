from typing import Optional

from lib import config
from lib.graphql.inputs.profession_input import ProfessionInput
from lib.graphql.types.error import Error
from lib.graphql.types.tag import Tag
from lib.graphql.types.tag_page import TagPage
from lib.models.profession_model import ProfessionModel


async def read_professions(professions: Optional[ProfessionInput] = None):
    professions = professions or ProfessionInput(page=1)

    try:
        searched_professions = (
            await ProfessionModel.find_all()
            .skip((professions.page - 1) * config.PAGE_SIZE)
            .limit(config.PAGE_SIZE)
            .to_list()
        )
        total_records = await ProfessionModel.find_all().count()

        return TagPage(
            items=[Tag(id=str(p.id), label=p.label) for p in searched_professions],
            page=professions.page,
            total=total_records,
        )

    except Exception as e:
        print(e)
        return Error(status=500, message="Something went wrong!")
