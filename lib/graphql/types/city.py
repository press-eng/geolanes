import strawberry

from lib.graphql.types.tag import Tag


@strawberry.type
class City:
    id: str = strawberry.field(deprecation_reason="")
    label: str
    country: Tag
