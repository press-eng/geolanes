import logging

from lib.graphql.inputs.state_input import StateInput
from lib.graphql.types.error import Error
from lib.graphql.types.state import State
from lib.graphql.types.state_page import StatePage
from lib.services import gemini_client


async def read_states(state: StateInput):
    try:
        states = await gemini_client.get_popular_states(state.country_name)
        return StatePage(
            items=[
                State(
                    name=s["name"],
                    country=state.country_name,
                )
                for s in states
                if s.get("name")
            ],
            page=1,
            total=0,
        )

    except Exception as e:
        logging.error(e)
        return Error(status=500, message="Something went wrong!")
