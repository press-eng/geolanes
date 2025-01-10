from lib.graphql.inputs.city_input import CityInput
from lib.graphql.types.city_page import CityPage


async def read_cities(cities: CityInput):
    return CityPage(
        items=[],
        page=1,
        total=0,
    )
