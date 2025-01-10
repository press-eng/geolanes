from lib.graphql.types.tour import Tour
from lib.graphql.types.venture import Venture
from lib.helpers.attraction_helper import attraction_model_to_type
from lib.models.attraction_model import AttractionModel
from lib.models.dto.tour_venture_dto import TourVentureDto
from lib.models.tour_model import TourModel


async def tour_model_to_type(model: TourModel) -> Tour:
    return Tour(
        id=str(model.id),
        title=model.title,
        status=model.status,
        ventures=[await _venture_model_to_type(v) for v in (model.ventures or [])],
        start_date=model.start_date,
        end_date=model.end_date,
        adult_count=model.adult_count,
        child_count=model.child_count,
        picture_url=model.picture_url,
    )


async def _venture_model_to_type(model: TourVentureDto) -> Venture:
    attraction_model = await AttractionModel.get(model.attraction_id)
    if attraction_model is None:
        return None
    return Venture(
        time=model.time,
        attraction=await attraction_model_to_type(attraction_model),
    )
